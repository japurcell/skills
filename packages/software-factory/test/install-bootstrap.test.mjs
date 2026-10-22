import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdtempSync, mkdirSync, readFileSync, readdirSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const script = resolve(fileURLToPath(new URL('../../../skills/software-factory/scripts/install.py', import.meta.url)));
const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const packageCommand = join(packageRoot, 'scripts/package-release.mjs');
const nativeQualification = join(packageRoot, 'qualification/install-bootstrap-native.qualification.mjs');
const python = process.env.FACTORY_TEST_PYTHON ?? 'python3';
const prerequisite = spawnSync(python, ['-c', 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'], { encoding: 'utf8' });
assert.equal(prerequisite.status, 0, `Python 3.11+ prerequisite failed: ${prerequisite.error?.message ?? prerequisite.stderr}`);
const nodeAsset = { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz', sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' };
const sha = data => createHash('sha256').update(data).digest('hex');
const run = args => spawnSync(python, [script, ...args], { encoding: 'utf8' });

test('default Node discovery excludes explicit native bootstrap qualification', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-discovery-')));
  try {
    mkdirSync(join(root, 'qualification'));
    copyFileSync(nativeQualification, join(root, 'qualification/install-bootstrap-native.qualification.mjs'));
    const environment = { ...process.env };
    delete environment.FACTORY_TEST_NODE_ARCHIVE;
    delete environment.NODE_TEST_CONTEXT;
    const result = spawnSync(process.execPath, ['--test'], { cwd: root, env: environment, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.match(result.stdout, /tests 0/);
    assert.doesNotMatch(result.stdout + result.stderr, /FACTORY_TEST_NODE_ARCHIVE is required/);
    const explicit = spawnSync(process.execPath, ['--test', 'qualification/install-bootstrap-native.qualification.mjs'], { cwd: root, env: environment, encoding: 'utf8' });
    assert.equal(explicit.status, 1);
    assert.match(explicit.stdout + explicit.stderr, /FACTORY_TEST_NODE_ARCHIVE is required/);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

function fixture() {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-test-')));
  const bundle = join(root, 'bundle');
  const archive = join(root, 'node.tar.xz');
  mkdirSync(bundle);
  writeFileSync(archive, 'unqualified archive');
  const entry = { path: 'dist/cli.js', bytes: 8, sha256: sha('old code') };
  mkdirSync(join(bundle, 'dist'));
  writeFileSync(join(bundle, entry.path), 'old code');
  const manifest = { schema: 2, version: '1.2.3', platform: 'darwin-arm64', node: nodeAsset, files: [entry] };
  const save = () => {
    const bytes = `${JSON.stringify(manifest)}\n`;
    writeFileSync(join(bundle, 'release-manifest.json'), bytes);
    return sha(bytes);
  };
  const verify = digest => run(['verify', '--bundle-root', bundle, '--manifest-sha256', digest, '--node-archive', archive]);
  return { root, bundle, archive, manifest, save, verify, dispose: () => rmSync(root, { recursive: true, force: true }) };
}

function completeFixture() {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-complete-')));
  const bundle = join(root, 'bundle');
  const selection = join(root, 'selection.json');
  writeFileSync(selection, JSON.stringify({ version: '1.2.3', platform: 'darwin-arm64', node: nodeAsset }));
  const packaged = spawnSync(process.execPath, [packageCommand, '--descriptor', selection, '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
  assert.equal(packaged.status, 0, packaged.stderr);
  const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
  const archive = join(root, 'unqualified-node.tar.xz');
  writeFileSync(archive, 'unqualified archive');
  return { root, bundle, archive, manifestSha256, verify: () => run(['verify', '--bundle-root', bundle, '--manifest-sha256', manifestSha256, '--node-archive', archive]), dispose: () => rmSync(root, { recursive: true, force: true }) };
}

test('public verifier refuses a changed imported module before any selected JavaScript runs', () => {
  const f = completeFixture();
  try {
    const importPath = join(f.bundle, 'dist/release.js');
    writeFileSync(importPath, `process.stderr.write('EXECUTED');\n${readFileSync(importPath, 'utf8')}`);
    const result = f.verify();
    assert.equal(result.status, 1);
    assert.match(result.stderr, /changed file|size mismatch/i);
    assert.doesNotMatch(result.stderr + result.stdout, /EXECUTED/);
    assert.equal(result.stdout, '');
  } finally { f.dispose(); }
});

test('source mutation while the bundle is copied is refused before execution', async () => {
  const f = completeFixture();
  const marker = join(f.root, 'unverified-module-ran');
  const original = readFileSync(join(f.bundle, 'dist/accounting.js'));
  const manifestPath = join(f.bundle, 'release-manifest.json');
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
  const largeMap = Buffer.alloc(30 * 1024 * 1024, 'x');
  for (const stem of ['accounting', 'agents', 'build', 'capture', 'clearance', 'cli', 'dashboard']) {
    const name = `dist/${stem}.js.map`;
    writeFileSync(join(f.bundle, name), largeMap);
    const entry = manifest.files.find(item => item.path === name);
    entry.bytes = largeMap.length;
    entry.sha256 = sha(largeMap);
  }
  const selectedManifest = `${JSON.stringify(manifest)}\n`;
  writeFileSync(manifestPath, selectedManifest);
  f.manifestSha256 = sha(selectedManifest);
  const knownStages = new Set(readdirSync(tmpdir()).filter(name => name.startsWith('factory-install-verify-')));
  const child = spawn(python, [script, 'verify', '--bundle-root', f.bundle, '--manifest-sha256', f.manifestSha256, '--node-archive', f.archive], { stdio: ['ignore', 'pipe', 'pipe'] });
  const completed = new Promise(resolve => child.on('close', resolve));
  let output = '', errors = '';
  child.stdout.setEncoding('utf8').on('data', data => { output += data; });
  child.stderr.setEncoding('utf8').on('data', data => { errors += data; });
  try {
    let copied = false;
    const deadline = Date.now() + 5000;
    while (!copied && Date.now() < deadline) {
      for (const name of readdirSync(tmpdir()).filter(item => item.startsWith('factory-install-verify-') && !knownStages.has(item))) {
        const path = join(tmpdir(), name, 'bundle/dist/accounting.js');
        if (existsSync(path) && readFileSync(path).equals(original)) copied = true;
      }
      if (!copied) await new Promise(resolve => setTimeout(resolve, 5));
    }
    assert.equal(copied, true, 'private copy was never observed');
    writeFileSync(join(f.bundle, 'dist/accounting.js'), `import {writeFileSync} from 'node:fs'; writeFileSync(${JSON.stringify(marker)}, 'executed');\n`);
    const code = await completed;
    assert.equal(code, 1);
    assert.match(errors, /source changed|changed file|size mismatch/i);
    assert.equal(output, '');
    assert.equal(existsSync(marker), false);
  } finally { child.kill(); await completed; f.dispose(); }
});

test('public verifier refuses malformed selected inventories before archive or JS use', () => {
  const cases = [
    ['unknown manifest field', f => { f.manifest.surprise = true; }, /field/i],
    ['duplicate JSON key', f => { const bytes = '{"schema":2,"schema":2}\n'; writeFileSync(join(f.bundle, 'release-manifest.json'), bytes); return sha(bytes); }, /duplicate/i],
    ['duplicate file', f => { f.manifest.files.push({ ...f.manifest.files[0] }); }, /duplicate/i],
    ['case-colliding file', f => { f.manifest.files.push({ ...f.manifest.files[0], path: 'dist/CLI.js' }); }, /case-colliding/i],
    ['oversize file', f => { f.manifest.files[0].bytes = 32 * 1024 * 1024 + 1; }, /size|limit/i],
    ['unsafe path', f => { f.manifest.files[0].path = '../outside.js'; }, /unsafe/i],
    ['unbounded release version', f => { f.manifest.version = `1.2.${'3'.repeat(10_000)}`; }, /version/i],
    ['missing required files', () => {}, /incomplete/i],
  ];
  for (const [name, mutate, pattern] of cases) {
    const f = fixture();
    try {
      const directDigest = mutate(f);
      const result = f.verify(directDigest ?? f.save());
      assert.equal(result.status, 1, `${name}: ${result.stderr}`);
      assert.match(result.stderr, pattern, name);
      assert.equal(result.stdout, '', name);
    } finally { f.dispose(); }
  }
});

test('public verifier bounds a hostile source-path diagnostic', () => {
  const result = run(['verify', '--bundle-root', `/private/tmp/${'x'.repeat(10_000)}`, '--manifest-sha256', 'a'.repeat(64), '--node-archive', '/private/tmp/node.tar.xz']);
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.ok(Buffer.byteLength(result.stderr) <= 512, `stderr was ${Buffer.byteLength(result.stderr)} bytes`);
});

test('public verifier refuses unowned files, directories and links in a complete bundle', () => {
  const cases = [
    ['extra file', f => writeFileSync(join(f.bundle, 'dist/unowned.js'), 'x'), /unowned/i],
    ['extra empty directory', f => mkdirSync(join(f.bundle, 'dist/unowned')), /unowned/i],
    ['linked file', f => { rmSync(join(f.bundle, 'dist/release.js')); symlinkSync(join(f.bundle, 'dist/cli.js'), join(f.bundle, 'dist/release.js')); }, /linked/i],
  ];
  for (const [name, mutate, diagnostic] of cases) {
    const f = completeFixture();
    try {
      mutate(f);
      const result = f.verify();
      assert.equal(result.status, 1, `${name}: ${result.stderr}`);
      assert.match(result.stderr, diagnostic, name);
      assert.equal(result.stdout, '');
    } finally { f.dispose(); }
  }
});

test('public extraction API accepts only safe regular payload and exact convenience omissions', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-archive-test-')));
  try {
    const driver = `import importlib.util,io,json,tarfile,sys\n` +
      `spec=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)\n` +
      `root=sys.argv[2]; top='node-v24.22.1-darwin-arm64/'\n` +
      `def archive(name,typ=tarfile.REGTYPE,target=''):\n` +
      ` p=root+'/case-'+str(len(results))+'.tar.xz'\n` +
      ` with tarfile.open(p,'w:xz') as tf:\n` +
      `  d=tarfile.TarInfo(top); d.type=tarfile.DIRTYPE; tf.addfile(d)\n` +
      `  m=tarfile.TarInfo(top+name); m.type=typ; m.linkname=target; m.size=1 if typ==tarfile.REGTYPE else 0; tf.addfile(m,io.BytesIO(b'x') if typ==tarfile.REGTYPE else None)\n` +
      ` return p\n` +
      `results=[]\n` +
      `for name,typ,target,ok in [('bin/node',tarfile.REGTYPE,'',True),('bin/npm',tarfile.SYMTYPE,'../lib/node_modules/npm/bin/npm-cli.js',True),('bin/other',tarfile.SYMTYPE,'../lib/node_modules/npm/bin/npm-cli.js',False),('../escape',tarfile.REGTYPE,'',False)]:\n` +
      ` try:\n` +
      `  with module.private_stage() as stage: module.extract_node_archive(archive(name,typ,target),'darwin-arm64',stage)\n` +
      `  accepted=True\n` +
      ` except (ValueError,RuntimeError): accepted=False\n` +
      ` results.append(accepted==ok)\n` +
      `print(json.dumps(results))\n`;
    const driverPath = join(root, 'driver.py');
    writeFileSync(driverPath, driver);
    const result = spawnSync(python, [driverPath, script, root], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout), [true, true, true, true]);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('public extraction API refuses hostile TAR and ZIP entries before writing them', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-hostile-')));
  try {
    const driver = `import importlib.util,io,json,lzma,stat,sys,tarfile,zipfile\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `root=sys.argv[2]; top='node-v24.22.1-darwin-arm64/'; checks=[]\n` +
      `def check(label,entries):\n` +
      ` p=root+'/'+label+'.tar.xz'\n` +
      ` with tarfile.open(p,'w:xz') as tar:\n` +
      `  directory=tarfile.TarInfo(top); directory.type=tarfile.DIRTYPE; tar.addfile(directory)\n` +
      `  for name,kind,target in entries:\n` +
      `   item=tarfile.TarInfo(name); item.type=kind; item.linkname=target; item.size=1 if kind==tarfile.REGTYPE else 0\n` +
      `   tar.addfile(item,io.BytesIO(b'x') if kind==tarfile.REGTYPE else None)\n` +
      ` try:\n` +
      `  with m.private_stage() as stage: m.extract_node_archive(p,'darwin-arm64',stage)\n` +
      `  checks.append(False)\n` +
      ` except ValueError: checks.append(True)\n` +
      `base=lambda name,kind=tarfile.REGTYPE,target='':(top+name,kind,target)\n` +
      `check('duplicate',[base('bin/node'),base('bin/node')])\n` +
      `check('case-parent',[base('Bin/node'),base('bin/npm-cli')])\n` +
      `check('wrong-omission',[base('bin/npm',tarfile.SYMTYPE,'../wrong')])\n` +
      `check('hard-link',[base('bin/other',tarfile.LNKTYPE,'bin/node')])\n` +
      `check('fifo',[base('bin/fifo',tarfile.FIFOTYPE)])\n` +
      `check('traversal',[base('../escape')])\n` +
      `check('file-parent',[base('bin'),base('bin/node')])\n` +
      `p=root+'/oversize.tar.xz'; directory=tarfile.TarInfo(top); directory.type=tarfile.DIRTYPE; big=tarfile.TarInfo(top+'bin/node'); big.size=128*1024*1024+1\n` +
      `open(p,'wb').write(lzma.compress(directory.tobuf()+big.tobuf()+b'\\0'*1024))\n` +
      `try:\n` +
      ` with m.private_stage() as stage: m.extract_node_archive(p,'darwin-arm64',stage)\n` +
      ` checks.append(False)\n` +
      `except ValueError: checks.append(True)\n` +
      `check('too-many',[(top+'d'+str(i)+'/',tarfile.DIRTYPE,'') for i in range(8192)])\n` +
      `p=root+'/reparse.zip'; info=zipfile.ZipInfo('node-v24.22.1-win-x64/node.exe'); info.create_system=3; info.external_attr=(stat.S_IFLNK|0o777)<<16\n` +
      `with zipfile.ZipFile(p,'w') as z: z.writestr('node-v24.22.1-win-x64/',''); z.writestr(info,b'x')\n` +
      `try:\n` +
      ` with m.private_stage() as stage: m.extract_node_archive(p,'win32-x64',stage)\n` +
      ` checks.append(False)\n` +
      `except ValueError: checks.append(True)\n` +
      `p=root+'/long-name.tar.xz'\n` +
      `with tarfile.open(p,'w:xz') as tar:\n` +
      ` directory=tarfile.TarInfo(top); directory.type=tarfile.DIRTYPE; tar.addfile(directory)\n` +
      ` item=tarfile.TarInfo(top+'x'*100000); item.size=1; tar.addfile(item,io.BytesIO(b'x'))\n` +
      `try:\n` +
      ` with m.private_stage() as stage: m.extract_node_archive(p,'darwin-arm64',stage)\n` +
      ` checks.append(False)\n` +
      `except ValueError as error: checks.append(len(str(error))<512)\n` +
      `p=root+'/pax-chain.tar.xz'\n` +
      `with tarfile.open(p,'w:xz') as tar:\n` +
      ` for i in range(8200):\n` +
      `  item=tarfile.TarInfo('g'); item.type=tarfile.XGLTYPE; tar.addfile(item)\n` +
      ` directory=tarfile.TarInfo(top); directory.type=tarfile.DIRTYPE; tar.addfile(directory)\n` +
      `try:\n` +
      ` with m.private_stage() as stage: m.extract_node_archive(p,'darwin-arm64',stage)\n` +
      ` checks.append(False)\n` +
      `except ValueError as error: checks.append(len(str(error))<512)\n` +
      `print(json.dumps(checks))\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script, root], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout), Array(12).fill(true));
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('private stage cleanup preserves an unexpected foreign file', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-ownership-')));
  try {
    const driver = `import importlib.util,os,sys\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `stage=m.PrivateStage(); stage.mkdir('node'); owned=stage.root/'node'/'owned'; foreign=stage.root/'foreign'; stage.create('node/owned').close(); foreign.write_text('keep')\n` +
      `try: stage.cleanup()\n` +
      `except ValueError: pass\n` +
      `else: raise AssertionError('foreign file was silently removed')\n` +
      `assert foreign.read_text()=='keep' and not owned.exists()\n` +
      `foreign.unlink(); stage.root.rmdir(); print('preserved')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'preserved');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('validator refuses inherited descendant pipes and preserves uncertain stages', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-process-')));
  try {
    const driver = `import importlib.util,os,subprocess,sys,threading,time\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `for escaped in (False,True):\n` +
      ` stage=m.PrivateStage()\n` +
      ` child='import time; time.sleep(2)'\n` +
      ` program='import subprocess,sys; subprocess.Popen([sys.executable,"-c",'+repr(child)+'],stdout=subprocess.DEVNULL,start_new_session='+repr(escaped)+'); print("{}")'\n` +
      ` begin=time.monotonic()\n` +
      ` try: m.bounded_child([sys.executable,'-c',program],stage,1)\n` +
      ` except ValueError: pass\n` +
      ` else: raise AssertionError('receipt returned with inherited pipe open')\n` +
      ` assert time.monotonic()-begin<2 and stage.preserved and stage.root.exists()\n` +
      ` if escaped:\n` +
      `  assert any(t.name.startswith('factory-install-drain') for t in threading.enumerate())\n` +
      ` if any(t.name.startswith('factory-install-drain') for t in threading.enumerate()): time.sleep(2.2)\n` +
      ` assert not any(t.name.startswith('factory-install-drain') for t in threading.enumerate())\n` +
      ` stage.cleanup()\n` +
      `with m.private_stage() as managed: managed.preserved=True\n` +
      `assert managed.root.exists()\n` +
      `managed.cleanup()\n` +
      `print('refused and owned cleanup completed')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'refused and owned cleanup completed');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('validator preserves its stage if either drain thread fails to start', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-thread-fault-')));
  try {
    const driver = `import importlib.util,subprocess,sys,threading\n` +
      `from unittest.mock import patch\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `for fault_at in (1,2):\n` +
      ` owned=[]; real_popen=subprocess.Popen; real_start=threading.Thread.start; starts=[0]; stage=None\n` +
      ` def capture(*args,**kwargs):\n` +
      `  process=real_popen(*args,**kwargs); owned.append(process); return process\n` +
      ` def fault(self):\n` +
      `  if self.name.startswith('factory-install-drain'):\n` +
      `   starts[0]+=1\n` +
      `   if starts[0]==fault_at: raise RuntimeError('controlled thread start failure')\n` +
      `  return real_start(self)\n` +
      ` try:\n` +
      `  with m.private_stage() as stage:\n` +
      `   with patch.object(m.subprocess,'Popen',capture),patch.object(threading.Thread,'start',fault):\n` +
      `    try: m.bounded_child([sys.executable,'-c','import time; time.sleep(5)'],stage,1)\n` +
      `    except RuntimeError: pass\n` +
      `    else: raise AssertionError('thread fault produced a receipt')\n` +
      `  assert stage.preserved and stage.root.exists() and owned[0].poll() is not None\n` +
      ` finally:\n` +
      `  for process in owned:\n` +
      `   if process.poll() is None: process.kill()\n` +
      `   process.wait(timeout=5); process.stdout.close(); process.stderr.close()\n` +
      `  if stage is not None and stage.root.exists(): stage.cleanup()\n` +
      `print('both startup faults refused without a surviving child')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'both startup faults refused without a surviving child');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('validator preserves its stage if waiting or joining raises unexpectedly', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-wait-fault-')));
  try {
    const driver = `import importlib.util,subprocess,sys,threading\n` +
      `from unittest.mock import patch\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `for mode in ('wait','join'):\n` +
      ` owned=[]; real_popen=subprocess.Popen; real_wait=subprocess.Popen.wait; real_join=threading.Thread.join; calls=[0]; stage=None\n` +
      ` def capture(*args,**kwargs):\n` +
      `  process=real_popen(*args,**kwargs); owned.append(process); return process\n` +
      ` def fault_wait(self,*args,**kwargs):\n` +
      `  if self in owned and calls[0]==0:\n` +
      `   calls[0]+=1; raise RuntimeError('controlled wait failure')\n` +
      `  return real_wait(self,*args,**kwargs)\n` +
      ` def fault_join(self,*args,**kwargs):\n` +
      `  if self.name.startswith('factory-install-drain'): raise ValueError('controlled join failure')\n` +
      `  return real_join(self,*args,**kwargs)\n` +
      ` try:\n` +
      `  with m.private_stage() as stage:\n` +
      `   with patch.object(m.subprocess,'Popen',capture):\n` +
      `    target=real_popen if mode=='wait' else threading.Thread\n` +
      `    attribute='wait' if mode=='wait' else 'join'\n` +
      `    replacement=fault_wait if mode=='wait' else fault_join\n` +
      `    with patch.object(target,attribute,replacement):\n` +
      `     try: m.bounded_child([sys.executable,'-c','print("{}")'],stage,1)\n` +
      `     except RuntimeError: pass\n` +
      `     else: raise AssertionError('unexpected lifecycle fault produced a receipt')\n` +
      `  assert stage.preserved and stage.root.exists() and owned[0].poll() is not None\n` +
      ` finally:\n` +
      `  for process in owned:\n` +
      `   if process.poll() is None: process.kill()\n` +
      `   process.wait(timeout=5); process.stdout.close(); process.stderr.close()\n` +
      `  if stage is not None and stage.root.exists(): stage.cleanup()\n` +
      `print('wait and join faults preserved owned stages')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'wait and join faults preserved owned stages');
  } finally { rmSync(root, { recursive: true, force: true }); }
});
