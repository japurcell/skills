import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
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
async function deadline(promise, milliseconds) {
  let timer;
  try { return await Promise.race([promise, new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error('owned launcher fixture deadline exceeded')), milliseconds);
  })]); } finally { clearTimeout(timer); }
}

test('public inspection blocks the authenticated live original launcher, then offers the same selection after closure', async () => {
  assert.ok(node); assert.equal(process.version, node.version);
  const python = process.env.FACTORY_TEST_PYTHON, archive = realpathSync(process.env.FACTORY_TEST_NODE_ARCHIVE);
  const seed = realpathSync(process.env.FACTORY_TEST_NPM_CACHE_SEED);
  assert.ok(python && existsSync(python)); assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-repair-live-launcher-'))), fixture = createRepository();
  const root = realpathSync(fixture.path), factory = join(root, '.git/factory'), release = join(container, 'release-launcher');
  let child, closed;
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
    const args = (command, extra = []) => [command, '--repository', root, '--bundle-root', bundle,
      '--manifest-sha256', manifestSha256, '--node-archive', archive, ...extra];
    const invoke = (command, extra = []) => spawnSync(python, [launcher, ...args(command, extra)],
      { env, encoding: 'utf8', timeout: 300_000, maxBuffer: 2 * 1024 * 1024 });
    select('1.2.3');
    const installed = invoke('install', ['--offline', '--offline-cache-seed', realpathSync(cache)]);
    assert.equal(installed.status, 0, installed.stderr);
    const source = readFileSync(join(root, 'tracked.txt')), index = readFileSync(join(root, '.git/index'));
    select('1.2.4');
    // Only this freshly owned public launcher waits. Its real preparer has already exited and closed its streams.
    const wrapper = `import os,runpy,signal,sys,time\nfrom pathlib import Path\nlauncher=sys.argv[1]\nsys.argv=sys.argv[1:]\ndef stop(signum,frame): raise KeyboardInterrupt\nsignal.signal(signal.SIGTERM,stop)\ndef barrier(frame,event,arg):\n if event=='call' and frame.f_code.co_filename==launcher and frame.f_code.co_name=='publish_candidate':\n  print('fixture-handoff-ready',flush=True)\n  while not Path(${JSON.stringify(release)}).exists(): time.sleep(0.01)\n  os._exit(73)\n return barrier\nsys.settrace(barrier)\nrunpy.run_path(launcher,run_name='__main__')`;
    child = spawn(python, ['-c', wrapper, launcher, ...args('upgrade', ['--offline', '--offline-cache-seed', realpathSync(cache)])],
      { env, stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '', errors = '';
    closed = new Promise(resolve => child.once('close', (code, signal) => resolve({ code, signal })));
    const ready = new Promise((resolve, reject) => {
      child.once('error', reject);
      child.stdout.on('data', bytes => { output = (output + String(bytes)).slice(-8192); if (output.includes('fixture-handoff-ready')) resolve(); });
      child.stderr.on('data', bytes => { errors = (errors + String(bytes)).slice(-8192); });
    });
    await deadline(Promise.race([ready, closed.then(result => { throw new Error(`launcher closed before handoff: ${JSON.stringify(result)} ${errors}`); })]), 120_000);
    const operations = readdirSync(join(factory, 'controller-staging')); assert.equal(operations.length, 1);
    const operationId = operations[0], originalPath = join(factory, `upgrade-${operationId}/original.json`);
    const original = readFileSync(originalPath), database = hash(readFileSync(join(factory, 'history.sqlite')));
    const walPath = join(factory, 'history.sqlite-wal'), wal = existsSync(walPath) ? readFileSync(walPath) : null;
    const liveResult = invoke('inspect-repair', ['--operation', operationId]);
    assert.equal(liveResult.status, 0, liveResult.stderr);
    const live = JSON.parse(liveResult.stdout);
    writeFileSync(release, 'release only this fixture launcher\n', { mode: 0o600 });
    assert.deepEqual(await deadline(closed, 15_000), { code: 73, signal: null });
    const endedResult = invoke('inspect-repair', ['--operation', operationId]);
    assert.equal(endedResult.status, 0, endedResult.stderr);
    const ended = JSON.parse(endedResult.stdout);
    assert.equal(ended.action, 'resume-upgrade', endedResult.stdout);
    assert.equal(live.selectionSha256, ended.selectionSha256, 'launcher lifetime does not change authenticated selection');
    assert.equal(hash(readFileSync(join(factory, 'history.sqlite'))), database);
    if (wal) assert.deepEqual(readFileSync(walPath), wal);
    else if (existsSync(walPath)) assert.equal(readFileSync(walPath).length, 0, 'only empty WAL bookkeeping may appear');
    if (existsSync(walPath)) {
      const info = lstatSync(walPath); assert.ok(info.isFile() && !info.isSymbolicLink() && info.nlink === 1 && (info.mode & 0o077) === 0);
      assert.equal(info.uid, process.getuid());
    }
    assert.deepEqual(readFileSync(originalPath), original);
    assert.deepEqual(readFileSync(join(root, 'tracked.txt')), source); assert.deepEqual(readFileSync(join(root, '.git/index')), index);
    assert.equal(live.action, 'refused', liveResult.stdout);
    assert.equal(live.reason, 'known-live-original-launcher');
    assert.equal(live.resume.originalLauncher, 'known_live');
    assert.equal(Object.hasOwn(live.resume, 'command'), false, 'blocked inspection must not offer a usable resume command');
  } finally {
    if (child && child.exitCode === null && child.signalCode === null) {
      writeFileSync(release, 'release only this fixture launcher\n', { mode: 0o600 });
      try { await deadline(closed, 15_000); } catch { child.kill('SIGTERM'); await deadline(closed, 5000); }
    }
    fixture.dispose(); rmSync(container, { recursive: true, force: true });
  }
});
