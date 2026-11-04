import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import { copyFileSync, cpSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, readdirSync, renameSync, rmSync, symlinkSync, unlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const platform = `${process.platform}-${process.arch}`;
const nodes = {
  'darwin-arm64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
    sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' },
  'linux-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz',
    sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' },
};
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
function fingerprint(root) {
  const digest = createHash('sha256');
  const visit = (path, prefix = '') => {
    for (const name of readdirSync(path).sort()) {
      const relative = `${prefix}${name}`, target = join(path, name), stat = lstatSync(target);
      digest.update(relative).update(String(stat.mode & 0o777));
      if (stat.isDirectory()) visit(target, `${relative}/`);
      else { assert.ok(stat.isFile() && !stat.isSymbolicLink()); digest.update(readFileSync(target)); }
    }
  };
  visit(root); return digest.digest('hex');
}
function databaseFacts(factory) {
  const database = new DatabaseSync(join(factory, 'history.sqlite'), { readOnly: true });
  try {
    const domain = {};
    for (const { name } of database.prepare("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT IN ('owner_claims','observation_events','sqlite_sequence') ORDER BY name").all()) {
      assert.match(name, /^[a-z_]+$/);
      domain[name] = database.prepare(`SELECT * FROM ${name} ORDER BY rowid`).all();
    }
    return { domain, events: database.prepare('SELECT kind,data FROM observation_events ORDER BY cursor').all(),
      claims: database.prepare('SELECT id,token,data FROM owner_claims').all() };
  } finally { database.close(); }
}

async function scenario(baseline, work, admission = true) {
  const node = nodes[platform];
  assert.ok(node, 'native dependency claim qualification requires Darwin arm64 or Linux x64');
  assert.equal(process.version, node.version, 'exact pinned Node required');
  const archive = process.env.FACTORY_TEST_NODE_ARCHIVE, cache = process.env.FACTORY_TEST_NPM_CACHE_SEED;
  const python = process.env.FACTORY_TEST_PYTHON;
  assert.ok(archive && existsSync(archive), 'exact pinned Node archive required');
  assert.ok(cache && existsSync(join(cache, '_cacache')), 'offline npm cache seed required');
  assert.ok(python && existsSync(python), 'selected Python required');
  assert.ok(process.env.FACTORY_ATOMIC_PYTHON, 'selected atomic publication Python required');
  assert.equal(realpathSync(process.env.FACTORY_ATOMIC_PYTHON), realpathSync(python));
  const pythonVersion = spawnSync(python, ['-I', '-c', 'import sys; print(".".join(map(str, sys.version_info[:3])))'], { encoding: 'utf8' });
  assert.equal(pythonVersion.status, 0, pythonVersion.stderr);
  assert.equal(pythonVersion.stdout.trim(), '3.13.14', 'exact qualified Python required');
  assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-dependency-claim-native-')));
  const repository = createRepository(), root = realpathSync(repository.path), common = join(root, '.git');
  try {
    const descriptor = join(container, 'selection.json'); let bundle = join(container, 'bundle');
    writeFileSync(descriptor, JSON.stringify({ version: '1.2.3', platform, node }));
    const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
      '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
    assert.equal(packaged.status, 0, packaged.stderr);
    let manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
    const home = join(container, 'home'); mkdirSync(home, { mode: 0o700 });
    const env = { PATH: process.env.PATH, HOME: home, TMPDIR: container, TMP: container, TEMP: container };
    const installed = spawnSync(python, [resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py'),
      'install', '--repository', root, '--bundle-root', bundle, '--manifest-sha256', manifestSha256,
      '--node-archive', realpathSync(archive), '--offline', '--offline-cache-seed', realpathSync(cache)],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024, env });
    assert.equal(installed.status, 0, `public install failed: ${installed.stderr}`);
    if (baseline === 'upgraded') {
      bundle = join(container, 'upgrade-bundle');
      writeFileSync(descriptor, JSON.stringify({ version: '1.2.4', platform, node }));
      const packagedUpgrade = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
        '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
      assert.equal(packagedUpgrade.status, 0, packagedUpgrade.stderr);
      manifestSha256 = JSON.parse(packagedUpgrade.stdout).manifestSha256;
      const upgraded = spawnSync(python, [resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py'),
        'upgrade', '--repository', root, '--bundle-root', bundle, '--manifest-sha256', manifestSha256,
        '--node-archive', realpathSync(archive), '--offline', '--offline-cache-seed', realpathSync(cache)],
      { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024, env });
      assert.equal(upgraded.status, 0, `public upgrade failed: ${upgraded.stderr}`);
    }
    const factory = join(common, 'factory'), compiler = join(factory, 'toolchain/node_modules/typescript/bin/tsc');
    unlinkSync(compiler);
    if (baseline === 'upgraded') { const changed = join(factory, 'toolchain/node_modules/undici-types/package.json'); writeFileSync(changed, Buffer.concat([readFileSync(changed), Buffer.from('\n')])); }
    const api = await import('../dist/dependency-maintenance.js');
    const { currentOwner } = await import('../dist/native/process.js');
    const { openRepositoryStore, openDependencyMaintenanceStore } = await import('../dist/store.js');
    const maintenance = await import('../dist/maintenance.js');
    const source = { mode: 'repair', bundleRoot: bundle, manifestSha256 };
    const writer = openRepositoryStore(common);
    try {
      const run = await writer.createRun(); // Keep this connection open so committed source data remains in WAL.
      const plan = await api.inspectDependencyMaintenanceSelection(root, source);
      assert.deepEqual(plan.toolchain.missing, ['node_modules/typescript/bin/tsc']);
      assert.deepEqual(plan.toolchain.changed, baseline === 'upgraded' ? ['node_modules/undici-types/package.json'] : []);
      const owner = currentOwner(), handle = admission ? await api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner) : null;
      assert.ok(lstatSync(join(factory, 'history.sqlite-wal')).size > 0);
      await work({ api, maintenance, handle, root, common, factory, container, writer, run, openDependencyMaintenanceStore, bundle, manifestSha256, plan, env, archive, cache, python });
    } finally { writer.close(); }
  } finally { repository.dispose(); rmSync(container, { recursive: true, force: true }); }
}

test('genuine verified backup requires an authenticated private candidate request', async () => scenario('installed', async c => {
  await c.api.prepareDependencyBackup(c.root, c.handle);
  const candidate = await import('../dist/dependency-candidate.js');
  await assert.rejects(candidate.prepareDependencyCandidate('not-yet-available-request', c.handle));
  assert.equal((await c.api.inspectDependencyMaintenance(c.root, c.handle.operationId)).candidateAttempted, false);
}));

for (const baseline of ['installed', 'upgraded']) test(`genuine ${baseline} authenticated private bridge prepares only the exact toolchain`, async () => scenario(baseline, async c => {
  const before = databaseFacts(c.factory), live = { install: fingerprint(join(c.factory, 'install')),
    toolchain: fingerprint(join(c.factory, 'toolchain')), authoring: fingerprint(join(c.root, '.factory')),
    source: readFileSync(join(c.root, 'tracked.txt')), index: readFileSync(join(c.common, 'index')), cache:fingerprint(c.cache), bundle:fingerprint(c.bundle) };
  const bridge = `import importlib.util,json,sys
p=${JSON.stringify(resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py'))}
s=importlib.util.spec_from_file_location('factory_installer',p); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)
with m.prepare_install_selection(${JSON.stringify(c.bundle)}, ${JSON.stringify(c.manifestSha256)}, ${JSON.stringify(realpathSync(c.archive))}) as prepared:
 r=m.prepare_dependency_candidate(prepared,${JSON.stringify(c.root)},${JSON.stringify(c.plan.selectionDigest)},True,${JSON.stringify(realpathSync(c.cache))})
 print(json.dumps(r,separators=(',',':')))
`;
  const prepared = spawnSync(c.python, ['-I', '-c', bridge], { env: c.env, encoding: 'utf8', timeout: 600_000, maxBuffer: 64 * 1024 });
  assert.equal(prepared.status, 0, `${prepared.stderr} event kinds: ${JSON.stringify(databaseFacts(c.factory).events.map(row => row.kind))}`);
  const result = JSON.parse(prepared.stdout);
  assert.deepEqual(Object.keys(result).sort(), ['candidateBound','candidateDigest','claimId','operationId','receiptSha256','repositoryId']);
  assert.equal(result.candidateBound, true); assert.ok(Buffer.byteLength(prepared.stdout) < 4096);
  const facts = await c.api.inspectDependencyMaintenance(c.root, result.operationId);
  assert.equal(facts.backupBound, true); assert.equal(facts.candidateBound, true);
  const candidate = join(c.factory, `dependency-candidate-${result.operationId}`);
  assert.deepEqual(readdirSync(candidate).sort(), ['candidate-attempt.json','candidate-receipt.json','toolchain']);
  assert.ok(existsSync(join(candidate, 'toolchain/node_modules/typescript/bin/tsc')));
  const after = databaseFacts(c.factory);
  assert.deepEqual(after.domain, before.domain); assert.deepEqual(after.events.slice(0,before.events.length),before.events);
  assert.deepEqual(after.events.slice(before.events.length).map(row=>row.kind), ['maintenance.started','maintenance.backup_attempted',
    'maintenance.backup_attempt_bound','maintenance.backup_bound','maintenance.candidate_attempted','maintenance.candidate_attempt_bound','maintenance.candidate_bound']);
  assert.equal(fingerprint(join(c.factory,'install')), live.install); assert.equal(fingerprint(join(c.factory,'toolchain')),live.toolchain);
  assert.equal(fingerprint(join(c.root,'.factory')),live.authoring); assert.deepEqual(readFileSync(join(c.root,'tracked.txt')),live.source);
  assert.deepEqual(readFileSync(join(c.common,'index')),live.index); assert.equal(fingerprint(c.cache),live.cache); assert.equal(fingerprint(c.bundle),live.bundle); assert.equal(existsSync(join(c.factory,'controller-staging',result.operationId)),false);
}, false));

function runCandidateDriver(c, body, modulePath = null, seed = true) {
  const driver = `import assert from 'node:assert/strict'; import * as fs from 'node:fs'; import {join,dirname} from 'node:path';
    import {pathToFileURL} from 'node:url'; import {spawnSync} from 'node:child_process'; import {DatabaseSync} from 'node:sqlite';
    const requestPath=process.argv[1], request=JSON.parse(fs.readFileSync(requestPath));
    const root=request.repository, common=join(root,'.git'), factory=join(common,'factory');
    const api=await import(pathToFileURL(join(request.snapshot.bundleRoot,'dist/dependency-maintenance.js')));
    const candidate=await import(${modulePath ? JSON.stringify(pathToFileURL(modulePath).href) : "pathToFileURL(join(request.snapshot.bundleRoot,'dist/dependency-candidate.js'))"});
    let privateToken=''; try {
      const source={mode:'repair',bundleRoot:request.source.bundleRoot,manifestSha256:request.source.manifestSha256};
      const plan=await api.inspectDependencyMaintenanceSelection(root,source);
      const handle=await api.admitDependencyMaintenance(root,source,plan.selectionDigest); privateToken=handle.token;
      const backup=await api.prepareDependencyBackup(root,handle);
      const backupPath=join(factory,'maintenance-backups',handle.operationId,backup.backupId,'history.sqlite');
      ${body}
      process.stdout.write(JSON.stringify({ok:true,operationId:handle.operationId}));
    } catch(error) {
      const message=String(error.message).replaceAll(privateToken || 'unavailable-token','[redacted]');
      fs.writeFileSync(join(request.stageRoot,'fixture-diagnostic.json'),JSON.stringify({name:error.name,message}),{mode:0o600});
      throw error;
    }`;
  const program = `import importlib.util,json,sys,uuid,os\np=${JSON.stringify(resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py'))}\ns=importlib.util.spec_from_file_location('factory_installer',p); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\nwith m.prepare_install_selection(${JSON.stringify(c.bundle)},${JSON.stringify(c.manifestSha256)},${JSON.stringify(realpathSync(c.archive))}) as prepared:\n stage=prepared.stage\n seeded=m.private_npm_inputs(stage,True,${seed ? JSON.stringify(realpathSync(c.cache)) : 'None'})\n node_tree=m.extracted_node_tree(prepared.extracted_node_root,prepared.receipt['platform'])\n request={'schema':1,'requestId':str(uuid.uuid4()),'repository':${JSON.stringify(c.root)},'dependencySelectionDigest':${JSON.stringify(c.plan.selectionDigest)},'npm':{'offline':True},'stageRoot':str(stage.root),'stageIdentity':f'{stage.root.lstat().st_dev}:{stage.root.lstat().st_ino}','source':{'bundleRoot':str(prepared.source_bundle_root),'manifestSha256':prepared.manifest_sha256,'nodeArchivePath':str(prepared.source_node_archive)},'snapshot':{'bundleRoot':str(prepared.snapshot_bundle_root),'nodeArchivePath':str(prepared.snapshot_node_archive),'extractedNodeRoot':str(prepared.extracted_node_root),'nodeTree':node_tree}}\n request_path=stage.root/'dependency-preparer-request.json'\n with stage.create('dependency-preparer-request.json') as output:\n  output.write((json.dumps(request,separators=(',',':'),sort_keys=True)+'\\n').encode()); output.flush(); os.fsync(output.fileno())\n prepared.revalidate_sources(); stage.check('')\n try:\n  result=m.bounded_child([str(prepared.extracted_node_root/'bin/node'),'--input-type=module','-e',${JSON.stringify(driver)},str(request_path)],stage,timeout_seconds=300)\n  (stage.root/'fixture-diagnostic.json').unlink(missing_ok=True)\n  prepared.revalidate_sources(); m.adopt_npm_outputs(stage,seeded); stage.check(''); print(result.decode())\n except BaseException:\n  stage.preserved=True\n  diagnostic=stage.root/'fixture-diagnostic.json'\n  if diagnostic.exists(): print(diagnostic.read_text(),file=sys.stderr)\n  raise\n`;
  const result = spawnSync(c.python, ['-I','-c',program], {env:c.env,encoding:'utf8',timeout:600_000,maxBuffer:64*1024});
  assert.equal(result.status,0,result.stderr); return JSON.parse(result.stdout);
}

test('candidate exact claim races, immutable backup history and retained inventory tampering refuse', async () => scenario('installed', async c => {
  const before=databaseFacts(c.factory), live=fingerprint(join(c.factory,'toolchain'));
  const result=runCandidateDriver(c, `
    await assert.rejects(candidate.prepareDependencyCandidate(requestPath,{...handle,token:'stale'}),/claim|token/);
    const db=new DatabaseSync(join(factory,'history.sqlite'));
    const originalClaim=db.prepare('SELECT data FROM owner_claims WHERE id=?').get(handle.claimId).data;
    const completion=db.prepare("SELECT cursor,data FROM observation_events WHERE kind='install.completed' ORDER BY cursor DESC LIMIT 1").get();
    try {
      const changed=JSON.parse(originalClaim); changed.maintenance.selectionDigest='a'.repeat(64);
      db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(JSON.stringify(changed),handle.claimId);
      await assert.rejects(candidate.prepareDependencyCandidate(requestPath,handle),/claimed original|selection/);
      db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(originalClaim,handle.claimId);
      const event=JSON.parse(completion.data);event.at='2000-01-01T00:00:00.000Z';db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(JSON.stringify(event),completion.cursor);
      await assert.rejects(candidate.prepareDependencyCandidate(requestPath,handle),/completion changed/);
    } finally {db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(originalClaim,handle.claimId);db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(completion.data,completion.cursor);db.close();}
    const otherProgram="const requestPath=process.argv[1],handle=JSON.parse(await new Promise(r=>{let b='';process.stdin.on('data',c=>b+=c);process.stdin.on('end',()=>r(b));}));const request=JSON.parse((await import('node:fs')).readFileSync(requestPath));const {pathToFileURL}=await import('node:url');const api=await import(pathToFileURL(request.snapshot.bundleRoot+'/dist/dependency-candidate.js'));try{await api.prepareDependencyCandidate(requestPath,handle);process.exitCode=2;}catch(e){if(!String(e.message).includes('exact live claim owner'))throw e;process.stdout.write('refused');}";
    const other=spawnSync(process.execPath,['--input-type=module','-e',otherProgram,requestPath],{input:JSON.stringify(handle),encoding:'utf8'});assert.equal(other.status,0,other.stderr);assert.equal(other.stdout,'refused');
    for(const path of [join(request.snapshot.bundleRoot,'toolchain/package.json'),request.snapshot.nodeArchivePath,join(request.snapshot.extractedNodeRoot,'lib/node_modules/npm/bin/npm-cli.js')]){const bytes=fs.readFileSync(path);try{fs.writeFileSync(path,Buffer.from('tampered authenticated source'));await assert.rejects(candidate.prepareDependencyCandidate(requestPath,handle),/release|archive|Node|bundle|source|hash/);}finally{fs.writeFileSync(path,bytes);}}
    const bytes=fs.readFileSync(backupPath);try{fs.writeFileSync(backupPath,'tampered');await assert.rejects(candidate.prepareDependencyCandidate(requestPath,handle),/backup/);}finally{fs.writeFileSync(backupPath,bytes);}
    const raced=await Promise.allSettled([candidate.prepareDependencyCandidate(requestPath,handle),candidate.prepareDependencyCandidate(requestPath,handle)]);
    assert.equal(raced.filter(r=>r.status==='fulfilled').length,1);assert.equal(raced.filter(r=>r.status==='rejected').length,1);
    const prepared=raced.find(r=>r.status==='fulfilled').value;
    assert.equal((await candidate.verifyDependencyCandidate(root,handle)).candidateBound,true);
    await assert.rejects(candidate.prepareDependencyCandidate(requestPath,handle),/already allocated/);
    const target=join(prepared.candidatePath,'toolchain/node_modules/typescript/bin/tsc'), original=fs.readFileSync(target);
    try{fs.writeFileSync(target,'damaged');await assert.rejects(api.inspectDependencyMaintenance(root,handle.operationId),/candidate/);}finally{fs.writeFileSync(target,original);}
    const moved=target+'.held';fs.renameSync(target,moved);try{fs.copyFileSync(moved,target);fs.chmodSync(target,0o700);await assert.rejects(api.inspectDependencyMaintenance(root,handle.operationId),/identities/);fs.unlinkSync(target);fs.symlinkSync(moved,target);await assert.rejects(api.inspectDependencyMaintenance(root,handle.operationId),/linked/);}finally{if(fs.existsSync(target))fs.unlinkSync(target);fs.renameSync(moved,target);}
    for(const name of ['candidate-attempt.json','candidate-receipt.json']){const path=join(prepared.candidatePath,name),old=fs.readFileSync(path);try{fs.writeFileSync(path,Buffer.concat([old,Buffer.from(' ')]));await assert.rejects(api.inspectDependencyMaintenance(root,handle.operationId),/candidate/);}finally{fs.writeFileSync(path,old);}}
    const extra=join(prepared.candidatePath,'foreign');fs.writeFileSync(extra,'foreign',{mode:0o600});try{await assert.rejects(api.inspectDependencyMaintenance(root,handle.operationId),/candidate/);}finally{fs.unlinkSync(extra);}
    const events=new DatabaseSync(join(factory,'history.sqlite'));
    try{
      for(const kind of ['maintenance.started','maintenance.candidate_attempted']){const row=events.prepare('SELECT cursor,data FROM observation_events WHERE kind=? ORDER BY cursor DESC LIMIT 1').get(kind);try{const data=JSON.parse(row.data);data.at='2000-01-01T00:00:00.000Z';events.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(JSON.stringify(data),row.cursor);await assert.rejects(api.inspectDependencyMaintenance(root,handle.operationId),/historical events|event bytes/);}finally{events.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(row.data,row.cursor);}}
      const inserted=events.prepare("INSERT INTO observation_events(kind,data) VALUES ('maintenance.candidate_attempted','{}')").run();try{await assert.rejects(api.inspectDependencyMaintenance(root,handle.operationId),/event count/);}finally{events.prepare('DELETE FROM observation_events WHERE cursor=?').run(inserted.lastInsertRowid);}
    }finally{events.close();}
    assert.equal((await api.inspectDependencyMaintenance(root,handle.operationId)).candidateBound,true);
  `);
  const after=databaseFacts(c.factory);assert.deepEqual(after.domain,before.domain);assert.equal(fingerprint(join(c.factory,'toolchain')),live);
  assert.equal((await c.maintenance.inspectMaintenance(c.root)).intent.dependencies.candidateBound,true);
  assert.equal((await c.api.inspectDependencyMaintenance(c.root,result.operationId)).candidateBound,true);
}, false));

for(const fault of ['collision','allocated-partial','npm-failed','npm-closure','extra-package','linked-output','oversized-output','offline-missing','late-candidate'])
  test(`candidate ${fault} retains one attempt and never retries or adopts`,async()=>scenario('installed',async c=>{
    const before=databaseFacts(c.factory),live={install:fingerprint(join(c.factory,'install')),toolchain:fingerprint(join(c.factory,'toolchain'))};
    let modulePath=null;
    if(!['collision','allocated-partial','offline-missing'].includes(fault)){
      const copied=join(c.container,'trusted-runner-fault');mkdirSync(copied,{mode:0o700});cpSync(join(packageRoot,'dist'),join(copied,'dist'),{recursive:true});writeFileSync(join(copied,'package.json'),' {"type":"module"}');
      if(fault==='late-candidate'){
        // Trusted-helper mutation seam: real evidence, followed by one exact owned-file change.
        // It models a change after observation; it does not authenticate altered release code.
        const path=join(copied,'dist/install-candidate.js');let code=readFileSync(path,'utf8').replace('export function scanOwnedTree(', 'function realScanOwnedTree(');
        code+=`\nconst fixtureMutated=new Set();export function scanOwnedTree(root,domain,excludeReceipt=false){const result=realScanOwnedTree(root,domain,excludeReceipt);if(dirname(dirname(root))===${JSON.stringify(c.factory)}&&basename(root)==='toolchain'&&/^dependency-candidate-[0-9a-f-]{36}$/.test(basename(dirname(root)))&&!fixtureMutated.has(root)){fixtureMutated.add(root);const fd=openSync(join(root,'node_modules/typescript/bin/tsc'),constants.O_WRONLY|constants.O_TRUNC);try{writeSync(fd,Buffer.from('late candidate corruption'));}finally{closeSync(fd);}}return result;}\n`;writeFileSync(path,code);
      }else{
      const path=join(copied,'dist/install-preparation.js');let code=readFileSync(path,'utf8').replace('export async function runManagedInstallCommand(', 'async function originalManagedInstallCommand(');
      const effect=fault==='npm-failed'?`fs.writeFileSync(join(cwd,'partial'),'partial',{mode:0o600});throw new Error('trusted fixture npm failed');`:
        fault==='npm-closure'?`return originalManagedInstallCommand(executable,['-e',"require('node:child_process').spawn(process.execPath,['-e','setTimeout(()=>{},15000)'],{stdio:'ignore'}).unref()"],cwd,env);`:
        fault==='extra-package'?`await originalManagedInstallCommand(executable,args,cwd,env);fs.mkdirSync(join(cwd,'node_modules/foreign'),{mode:0o700});`:
        fault==='linked-output'?`await originalManagedInstallCommand(executable,args,cwd,env);fs.symlinkSync('typescript',join(cwd,'node_modules/foreign'));`:
        `await originalManagedInstallCommand(executable,args,cwd,env);const path=join(cwd,'node_modules/oversized');fs.writeFileSync(path,'',{mode:0o600});fs.truncateSync(path,129*1024*1024);`;
      code+=`\nexport async function runManagedInstallCommand(executable,args,cwd,env){const fs=await import('node:fs');${effect}}\n`;writeFileSync(path,code);}
      modulePath=join(copied,'dist/dependency-candidate.js');
    }
    const result=runCandidateDriver(c,`
      ${fault==='collision'?`const path=join(factory,'dependency-candidate-'+handle.operationId);fs.mkdirSync(path,{mode:0o700});fs.writeFileSync(join(path,'foreign'),'foreign',{mode:0o600});`:''}
      ${fault==='allocated-partial'?`{ const {randomUUID}=await import('node:crypto');const {openDependencyMaintenanceStore}=await import(pathToFileURL(join(request.snapshot.bundleRoot,'dist/store.js')));const store=openDependencyMaintenanceStore(common);try{await store.reserveDependencyCandidateAttempt(handle,randomUUID(),()=>{});}finally{store.close();}const path=join(factory,'dependency-candidate-'+handle.operationId);fs.mkdirSync(path,{mode:0o700});fs.writeFileSync(join(path,'partial'),'unbound partial',{mode:0o600}); }`:''}
      await assert.rejects(candidate.prepareDependencyCandidate(requestPath,handle),/EEXIST|already allocated|npm failed|managed process group|managed command|package set|link|bytes exceed|expected toolchain closure/,'late or invalid candidate must refuse before binding');
      ${fault==='late-candidate'?`assert.equal(fs.readFileSync(join(factory,'dependency-candidate-'+handle.operationId,'toolchain/node_modules/typescript/bin/tsc'),'utf8'),'late candidate corruption');`:''}
      const facts=await api.inspectDependencyMaintenance(root,handle.operationId);assert.equal(facts.backupBound,true);assert.equal(facts.candidateAttempted,true);assert.equal(facts.candidateBound,false);
      await assert.rejects(candidate.prepareDependencyCandidate(requestPath,handle),/already allocated/);
      ${fault==='collision'?`assert.equal(fs.readFileSync(join(factory,'dependency-candidate-'+handle.operationId,'foreign'),'utf8'),'foreign');`:fault==='allocated-partial'?`assert.equal(fs.readFileSync(join(factory,'dependency-candidate-'+handle.operationId,'partial'),'utf8'),'unbound partial');`:fault==='npm-failed'?`assert.equal(fs.readFileSync(join(factory,'dependency-candidate-'+handle.operationId,'toolchain/partial'),'utf8'),'partial');`:''}
      const storeApi=await import(pathToFileURL(join(request.snapshot.bundleRoot,'dist/store.js'))),store=storeApi.openDependencyMaintenanceStore(common);
      try{await assert.rejects(store.clearOwner({claimId:handle.claimId,token:handle.token,inspection:'unknown',operatorConfirmed:true,note:'fixture exact refusal'}),/maintenance|dependencies/);}finally{store.close();}
    `,modulePath,fault!=='offline-missing');
    const after=databaseFacts(c.factory);assert.deepEqual(after.domain,before.domain);assert.equal(after.claims.length,1);
    assert.equal(fingerprint(join(c.factory,'install')),live.install);assert.equal(fingerprint(join(c.factory,'toolchain')),live.toolchain);
    assert.equal((await c.api.inspectDependencyMaintenance(c.root,result.operationId)).candidateBound,false);
  },false));
