import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const launcher = resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py');
const platform = `${process.platform}-${process.arch}`;
const node = {
  'darwin-arm64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
    sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' },
  'linux-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz',
    sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' },
}[platform];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

test('public inspection selects intact recorded upgrade resume after a previous completed upgrade', () => {
  assert.ok(node); assert.equal(process.version, node.version);
  const python = process.env.FACTORY_TEST_PYTHON, archive = realpathSync(process.env.FACTORY_TEST_NODE_ARCHIVE);
  const seed = realpathSync(process.env.FACTORY_TEST_NPM_CACHE_SEED);
  assert.ok(python && existsSync(python)); assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-repair-resume-'))), fixture = createRepository();
  const root = realpathSync(fixture.path), factory = join(root, '.git/factory');
  try {
    const home = join(container, 'home'), cache = join(container, 'npm-cache');
    mkdirSync(home, { mode: 0o700 }); cpSync(seed, cache, { recursive: true });
    const userConfig = join(container, 'user.npmrc'), globalConfig = join(container, 'global.npmrc');
    writeFileSync(userConfig, '', { mode: 0o600 }); writeFileSync(globalConfig, '', { mode: 0o600 });
    const env = { PATH: process.env.PATH, HOME: home, TMPDIR: container, TMP: container, TEMP: container,
      NPM_CONFIG_USERCONFIG: userConfig, NPM_CONFIG_GLOBALCONFIG: globalConfig };
    let bundle, manifestSha256;
    const select = version => {
      const descriptor = join(container, `selection-${version}.json`); bundle = join(container, `bundle-${version}`);
      writeFileSync(descriptor, JSON.stringify({ version, platform, node }));
      const result = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
        '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
      assert.equal(result.status, 0, result.stderr); manifestSha256 = JSON.parse(result.stdout).manifestSha256;
    };
    const invoke = (command, extra = [], prefix = [launcher]) => spawnSync(python, [...prefix, command, '--repository', root,
      '--bundle-root', bundle, '--manifest-sha256', manifestSha256, '--node-archive', archive, ...extra],
    { env, encoding: 'utf8', timeout: 300_000, maxBuffer: 2 * 1024 * 1024 });
    select('1.2.3');
    let result = invoke('install', ['--offline', '--offline-cache-seed', realpathSync(cache)]);
    assert.equal(result.status, 0, result.stderr);
    select('1.2.4'); result = invoke('upgrade', ['--offline', '--offline-cache-seed', realpathSync(cache)]);
    assert.equal(result.status, 0, result.stderr);
    const prior = JSON.parse(result.stdout), priorReceipt = readFileSync(join(factory, `upgrade-${prior.operationId}/new-receipt.json`));
    select('1.2.5');
    // No production hook: this launcher wrapper observes only its own freshly created staged child and group.
    const wrapper = `import os,runpy,signal,subprocess,sys,threading,time\nfrom pathlib import Path\nlauncher=sys.argv[1]\nsys.argv=sys.argv[1:]\noriginal=subprocess.Popen\ndef start(argv,*args,**kwargs):\n child=original(argv,*args,**kwargs)\n if '--ticket' in argv and len(argv)>1 and str(argv[1]).endswith('/payload/dist/maintenance-entry.js'):\n  ticket=Path(argv[argv.index('--ticket')+1]); operation=ticket.parent.name\n  expected=Path(${JSON.stringify(factory)})/'controller-staging'/operation/'payload'\n  if Path(argv[0])!=expected/'node' or Path(argv[1])!=expected/'dist/maintenance-entry.js' or not kwargs.get('start_new_session'): raise RuntimeError('fixture staged child differs')\n  receipt=Path(${JSON.stringify(factory)})/('upgrade-'+operation)/'01-old-install.json'\n  def interrupt():\n   deadline=time.monotonic()+60\n   while child.poll() is None and time.monotonic()<deadline:\n    if receipt.exists():\n     if os.getpgid(child.pid)!=child.pid: raise RuntimeError('fixture child group differs')\n     os.killpg(child.pid,signal.SIGSTOP)\n     os.killpg(child.pid,signal.SIGKILL)\n     return\n    time.sleep(0.001)\n  threading.Thread(target=interrupt,daemon=True).start()\n return child\nsubprocess.Popen=start\nrunpy.run_path(launcher,run_name='__main__')`;
    result = invoke('upgrade', ['--offline', '--offline-cache-seed', realpathSync(cache)], ['-c', wrapper, launcher]);
    assert.notEqual(result.status, 0, 'owned staged controller must be interrupted');
    const marker = readFileSync(join(factory, 'upgrade-incomplete'));
    const operationId = JSON.parse(marker).operationId;
    const stepPath = join(factory, `upgrade-${operationId}/01-old-install.json`), step = readFileSync(stepPath);
    assert.ok(step.length > 0, 'genuine recorded move required before inspection');
    const database = hash(readFileSync(join(factory, 'history.sqlite')));
    const inspected = invoke('inspect-repair', ['--operation', operationId]);
    assert.equal(inspected.status, 0, inspected.stderr);
    const inspection = JSON.parse(inspected.stdout);
    assert.equal(inspection.action, 'resume-upgrade', inspected.stdout);
    assert.equal(inspection.resume.operationId, operationId); assert.ok(inspection.resume.recorded >= 1);
    assert.equal(inspection.selection.intendedRelease, '1.2.5'); assert.equal(inspection.resume.clearanceRequired, true);
    assert.equal(hash(readFileSync(join(factory, 'history.sqlite'))), database);
    assert.deepEqual(readFileSync(join(factory, 'upgrade-incomplete')), marker);
    assert.deepEqual(readFileSync(stepPath), step);
    assert.deepEqual(readFileSync(join(factory, `upgrade-${prior.operationId}/new-receipt.json`)), priorReceipt);
  } finally { fixture.dispose(); rmSync(container, { recursive: true, force: true }); }
});
