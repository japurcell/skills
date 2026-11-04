import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, readlinkSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const launcher = resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py');
const hash = value => createHash('sha256').update(value).digest('hex');
const platform = `${process.platform}-${process.arch}`;
const node = {
  'darwin-arm64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz', sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' },
  'linux-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz', sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' },
}[platform];
function rows(common) {
  const database = new DatabaseSync(join(common, 'factory/history.sqlite'), { readOnly: true });
  try {
    const result = {};
    for (const { name } of database.prepare("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all()) {
      const statement = database.prepare(`SELECT * FROM "${name.replaceAll('"', '""')}" ORDER BY rowid`);
      statement.setReadBigInts(true); result[name] = statement.all();
    }
    return result;
  } finally { database.close(); }
}
function authoring(root) {
  const result = {};
  const visit = (path, relative) => {
    const info = lstatSync(path);
    if (info.isSymbolicLink()) result[relative] = ['link', readlinkSync(path)];
    else if (info.isDirectory()) for (const name of readdirSync(path).sort()) visit(join(path, name), `${relative}/${name}`);
    else result[relative] = ['file', info.mode, readFileSync(path)];
  };
  visit(join(root, '.factory'), '.factory');
  for (const name of ['.gitignore','tracked.txt','untracked.txt','ignored.txt']) visit(join(root, name), name);
  return result;
}

test('installed change and audit reports preserve their evidence while unrelated setup output stays eligible', async () => {
  assert.ok(node); assert.equal(process.version, node.version);
  const python = process.env.FACTORY_TEST_PYTHON; assert.ok(python && existsSync(python));
  const archive = realpathSync(process.env.FACTORY_TEST_NODE_ARCHIVE), seed = realpathSync(process.env.FACTORY_TEST_NPM_CACHE_SEED);
  assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-ordinary-public-'))), fixture = createRepository();
  const root = realpathSync(fixture.path), common = join(root, '.git');
  try {
    const home = join(container, 'home'), cache = join(container, 'npm-cache');
    mkdirSync(home, { mode: 0o700 }); cpSync(seed, cache, { recursive: true });
    const userConfig = join(container, 'user.npmrc'), globalConfig = join(container, 'global.npmrc');
    writeFileSync(userConfig, '', { mode: 0o600 }); writeFileSync(globalConfig, '', { mode: 0o600 });
    const env = { PATH: process.env.PATH, HOME: home, TMPDIR: container, TMP: container, TEMP: container,
      NPM_CONFIG_USERCONFIG: userConfig, NPM_CONFIG_GLOBALCONFIG: globalConfig };
    const descriptor = join(container, 'selection.json'); let upgraded;
    for (const [command, version] of [['install','1.2.3'],['upgrade','1.2.4']]) {
      const bundle = join(container, `bundle-${version}`);
      writeFileSync(descriptor, JSON.stringify({version,platform,node}));
      const packaged = spawnSync(process.execPath, [join(packageRoot,'scripts/package-release.mjs'),'--descriptor',descriptor,
        '--source-root',packageRoot,'--destination',bundle], {encoding:'utf8'});
      assert.equal(packaged.status,0,packaged.stderr);
      const installed = spawnSync(python,[launcher,command,'--repository',root,'--bundle-root',bundle,
        '--manifest-sha256',JSON.parse(packaged.stdout).manifestSha256,'--node-archive',archive,'--offline','--offline-cache-seed',realpathSync(cache)],
      {env,encoding:'utf8',timeout:300_000,maxBuffer:2*1024*1024});
      assert.equal(installed.status,0,installed.stderr); assert.equal(JSON.parse(installed.stdout).state,'ready');
      if(command==='upgrade') upgraded=JSON.parse(installed.stdout);
    }
    writeFileSync(join(root,'.factory/agents.json'), JSON.stringify({defaults:{harness:'fake',permissions:'read-only',skillDelivery:'instructions',prompt:'default',skills:[]}}));
    for(const name of ['change','audit']) {
      const path=join(root,`.factory/workflows/${name}.ts`), source=readFileSync(path,'utf8');
      const setup=`await context.command('startup/ordinary-public/' + raw.prompt, {argv:[${JSON.stringify(process.execPath)},'-e',${JSON.stringify("process.stdout.write('unreferenced setup 🌍\\n')")} ]});`;
      writeFileSync(path,source.replace('export async function run(context: WorkflowContext, raw: Record<string, unknown>) {',
        `export async function run(context: WorkflowContext, raw: Record<string, unknown>) { ${setup}`));
    }
    const harness=join(container,'fake.mjs'), input=join(container,'input.json');
    writeFileSync(harness, `import { randomUUID } from 'node:crypto';
process.stderr.write(JSON.stringify({kind:'session',nativeId:randomUUID(),parentNativeId:null,lifecycle:'succeeded'})+'\\n');
process.stdout.write(JSON.stringify({kind:'result',payload:{summary:'Public result',findings:[],extra:'retained raw'}}));
`);
    const { invoke } = await import('../dist/lifecycle.js');
    const { createFakeAdapter } = await import('../dist/adapters/fake.js');
    const { openCleanupReadStore } = await import('../dist/store.js');
    const { inspectCleanupSelection } = await import('../dist/cleanup.js');
    const launch=async (workflow,payload,extra={})=>{
      writeFileSync(input,JSON.stringify(payload));
      const result=await invoke({repository:root,workflow:`.factory/workflows/${workflow}.ts`,input,newWorktree:false,worktreeId:root,
        shutdownGraceMs:100,adapters:{fake:createFakeAdapter({executable:process.execPath,script:harness})},...extra});
      assert.equal(result.outcome,'succeeded',JSON.stringify(result));assert.equal(result.cleanup,'complete');return result;
    };
    function facts() {
      const reader=openCleanupReadStore(common);
      try {
        const snapshot=reader.readCleanupSnapshot();
        const pages=(method,domain)=>{const values=[];let after='0';for(;;){const page=reader[method]({after,through:snapshot.highWater[domain]});
          assert.equal(page.blocked,null);values.push(...page.records);if(!page.hasMore)break;assert.ok(BigInt(page.nextCursor)>BigInt(after));after=page.nextCursor;}
          assert.ok(values.every(row=>row.status==='known'));return values;};
        const headers=pages('pageCleanupCaptureHeaders','captures'),attempts=pages('pageCleanupAttemptFacts','attempts'),invocations=pages('pageCleanupInvocationFacts','invocations');
        const content=header=>{let after='0',text='';for(;;){const page=reader.readCleanupCapture({invocationId:header.invocationId,captureId:header.id,after});
          assert.equal(page.status,'present');assert.equal(page.blocked,null);text+=page.chunks.map(item=>item.text).join('');if(!page.hasMore)return text;
          assert.ok(BigInt(page.nextSequence)>BigInt(after));after=page.nextSequence;}};
        const bound=reader.readCleanupOperationEvidence({operationId:upgraded.operationId}).backupBound;assert.equal(bound.status,'known');
        return {headers,attempts,invocations,content:new Map(headers.map(header=>[header.id,content(header)])),backupId:bound.data.backupId};
      } finally {reader.close();}
    }
    const check={name:'verify',argv:[process.execPath,'-e',"process.stdout.write('public check')"]};
    const first=await launch('change',{prompt:'first',checks:[check]}); let saved=facts();
    const reportFor=id=>{const header=saved.headers.find(row=>row.invocationId===id&&row.channel==='report');assert.ok(header);return JSON.parse(saved.content.get(header.id));};
    const firstReport=reportFor(first.invocationId);
    const replay=await launch('change',{prompt:'replay',implement:false,review:false,checks:[check],priorAttempts:firstReport.priorAttempts},
      {worktreeId:first.worktreeId,runId:first.runId});
    const audit=await launch('audit',{prompt:'audit',scopes:[{name:'scope',target:'tracked.txt'}],checks:[check]});
    writeFileSync(join(root,'.factory/workflows/ordinary-request.ts'), `export async function run(context) { await context.needsInput('Choose a target', 'A target is required.'); }\n`);
    writeFileSync(input,'{}');
    const request=await invoke({repository:root,workflow:'.factory/workflows/ordinary-request.ts',input,newWorktree:false,worktreeId:root,shutdownGraceMs:100});
    assert.equal(request.outcome,'needs_input',JSON.stringify(request));assert.equal(request.cleanup,'complete');
    saved=facts();const replayReport=reportFor(replay.invocationId),auditReport=reportFor(audit.invocationId);
    assert.deepEqual(firstReport.candidate,{summary:'Public result'});assert.deepEqual(auditReport.investigations[0].result,{summary:'Public result'});
    const setup=saved.attempts.find(row=>row.invocationId===first.invocationId&&row.operationKey==='startup/ordinary-public/first');
    const output=saved.headers.find(row=>row.attemptId===setup?.id&&row.channel==='stdout');assert.ok(output);
    assert.equal(saved.content.get(output.id),'unreferenced setup 🌍\n');
    const selected={invocationId:output.invocationId,captureId:output.id};
    const upgrade=join(common,'factory',`upgrade-${upgraded.operationId}`),backup=join(common,'factory/maintenance-backups',upgraded.operationId,saved.backupId);
    const fixed=[join(common,'index'),...['new-receipt.json','intent.json','original.json'].map(name=>join(upgrade,name)),
      ...['backup-receipt.json','backup-request.json','history.sqlite'].map(name=>join(backup,name))];
    const inspect=async selection=>{const before=rows(common),files=authoring(root),bytes=fixed.map(path=>[path,readFileSync(path)]);
      const result=await inspectCleanupSelection(root,selection);assert.deepEqual(rows(common),before);assert.deepEqual(authoring(root),files);
      for(const [path,value] of bytes)assert.deepEqual(readFileSync(path),value);return result;};
    const impact=await inspect({kind:'captures',captures:[selected],exceptional:[],reviewNonOutput:[]});
    assert.equal(impact.status,'inspectable',JSON.stringify(impact.blockers));assert.equal(impact.captures[0].disposition,'eligible');
    assert.equal(impact.captures[0].payloadSha256,hash('unreferenced setup 🌍\n'));
    const ids=new Set([firstReport,replayReport,auditReport].flatMap(report=>Object.values(report.priorAttempts))),pending=[...ids];
    while(pending.length){const id=pending.pop(),fact=saved.attempts.find(row=>row.id===id);assert.ok(fact);
      for(const prior of [fact.priorAttemptId,fact.agent?.reusedAttemptId])if(prior&&!ids.has(prior)){ids.add(prior);pending.push(prior);}}
    const protectedIds=new Set(saved.headers.filter(row=>row.channel==='report'||row.channel==='request'||ids.has(row.attemptId)||row.channel==='context'
      &&saved.attempts.some(fact=>fact.id===row.attemptId&&fact.kind==='command')).map(row=>row.id));
    for(const owner of saved.invocations) {assert.ok(owner.inputCaptureId);protectedIds.add(owner.inputCaptureId);}
    for(const fact of saved.attempts.filter(row=>ids.has(row.id)&&row.agent)) protectedIds.add(JSON.parse(saved.content.get(fact.agent.inputsCaptureId)).sourceCaptureId);
    const protectedKeys=[...protectedIds].map(id=>{const header=saved.headers.find(row=>row.id===id);assert.ok(header);return {invocationId:header.invocationId,captureId:id};})
      .sort((a,b)=>{const left=JSON.stringify(['capture',a.invocationId,a.captureId]),right=JSON.stringify(['capture',b.invocationId,b.captureId]);return left<right?-1:left>right?1:0;});
    for(let index=0;index<protectedKeys.length;index+=50){const captures=protectedKeys.slice(index,index+50);
      const result=await inspect({kind:'captures',captures,exceptional:[],reviewNonOutput:[]});
      assert.equal(result.status,'inspectable',JSON.stringify(result.blockers));
      assert.equal(result.captures.length,captures.length);for(const item of result.captures)assert.equal(item.disposition,'protected');}
  } finally {fixture.dispose();rmSync(container,{recursive:true,force:true});}
});
