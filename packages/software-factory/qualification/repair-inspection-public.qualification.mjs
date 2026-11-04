import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { chmodSync, cpSync, existsSync, linkSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, renameSync, rmSync, symlinkSync, unlinkSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const launcher = resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const platform = `${process.platform}-${process.arch}`;
const node = {
  'darwin-arm64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
    sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' },
  'linux-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz',
    sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' },
}[platform];

// Read-only SQLite can create an empty WAL and update SHM. Existing WAL frames remain authoritative.
function fingerprint(root) {
  const rows = [];
  const visit = (path, prefix) => {
    for (const name of readdirSync(path).sort()) {
      const relative = prefix ? `${prefix}/${name}` : name;
      const file = join(path, name), info = lstatSync(file);
      if (relative === 'history.sqlite-shm' || relative === 'history.sqlite-wal') {
        assert.ok(info.isFile() && !info.isSymbolicLink() && info.nlink === 1 && (info.mode & 0o077) === 0);
        assert.equal(info.uid, process.getuid());
        if (relative.endsWith('-shm')) continue;
      }
      rows.push([relative, info.dev, info.ino, info.mode, info.nlink, info.size,
        info.isFile() ? hash(readFileSync(file)) : info.isSymbolicLink() ? 'link' : 'other']);
      if (info.isDirectory()) visit(file, relative);
    }
  };
  visit(root, ''); return rows;
}
function assertPreserved(before, after) {
  const priorWal = before.find(row => row[0] === 'history.sqlite-wal');
  if (!priorWal) {
    const newWal = after.find(row => row[0] === 'history.sqlite-wal');
    if (newWal) {
      assert.equal(newWal[5], 0, 'a newly created SQLite WAL must contain no frames');
      assert.equal(newWal[6], hash(Buffer.alloc(0)), 'new WAL must be exactly empty');
      after = after.filter(row => row[0] !== 'history.sqlite-wal');
    }
  }
  assert.equal(hash(JSON.stringify(after)), hash(JSON.stringify(before)),
    'inspection must preserve DB, preexisting WAL, claims, receipts and all other managed paths');
}

test('public external inspection authenticates retained installation without executing damaged runtime', async t => {
  assert.ok(node, 'supported pinned Darwin arm64 or Linux x64 profile required');
  assert.equal(process.version, node.version);
  const python = process.env.FACTORY_TEST_PYTHON, archive = realpathSync(process.env.FACTORY_TEST_NODE_ARCHIVE);
  const seed = realpathSync(process.env.FACTORY_TEST_NPM_CACHE_SEED);
  assert.ok(python && existsSync(python)); assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-repair-inspection-')));
  const fixture = createRepository(), root = realpathSync(fixture.path), factory = join(root, '.git/factory');
  try {
    const home = join(container, 'home'), cache = join(container, 'npm-cache');
    mkdirSync(home, { mode: 0o700 }); cpSync(seed, cache, { recursive: true });
    const userConfig = join(container, 'user.npmrc'), globalConfig = join(container, 'global.npmrc');
    writeFileSync(userConfig, '', { mode: 0o600 }); writeFileSync(globalConfig, '', { mode: 0o600 });
    const env = { PATH: process.env.PATH, HOME: home, TMPDIR: container, TMP: container, TEMP: container,
      NPM_CONFIG_USERCONFIG: userConfig, NPM_CONFIG_GLOBALCONFIG: globalConfig };
    const descriptor = join(container, 'selection.json'), bundle = join(container, 'bundle');
    writeFileSync(descriptor, JSON.stringify({ version: '1.2.3', platform, node }));
    const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
      '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
    assert.equal(packaged.status, 0, packaged.stderr);
    const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
    let activeBundle = bundle, activeSha = manifestSha256;
    const invoke = (command, extra = [], script = [launcher]) => spawnSync(python, [...script, command, '--repository', root,
      '--bundle-root', activeBundle, '--manifest-sha256', activeSha, '--node-archive', archive, ...extra],
    { env, encoding: 'utf8', timeout: 300_000, maxBuffer: 2 * 1024 * 1024 });
    const installed = invoke('install', ['--offline', '--offline-cache-seed', realpathSync(cache)]);
    assert.equal(installed.status, 0, installed.stderr); assert.equal(JSON.parse(installed.stdout).state, 'ready');
    const retained = Object.fromEntries(['tracked.txt', '.git/index', '.factory/package.json', '.factory/agents.json']
      .map(path => [path, readFileSync(join(root, path))]));
    mkdirSync(join(root, 'application'), { mode: 0o700 });
    writeFileSync(join(root, 'application/package.json'), '{"dependencies":{"untouched":"1.0.0"}}\n');
    retained['application/package.json'] = readFileSync(join(root, 'application/package.json'));
    const firstReceipt = readFileSync(join(factory, 'installed-receipt.json'));
    const inspect = (expectedAction, extra = []) => {
      const before = fingerprint(factory), result = invoke('inspect-repair', extra);
      assert.equal(result.status, 0, result.stderr); assert.ok(Buffer.byteLength(result.stdout) <= 8192);
      const response = JSON.parse(result.stdout); assert.equal(response.action, expectedAction, result.stdout);
      assertPreserved(before, fingerprint(factory));
      return response;
    };
    const runtimeFile = join(factory, 'install/runtime/dist/accounting.js');
    const bytes = readFileSync(runtimeFile); unlinkSync(runtimeFile);
    try {
      const result = inspect('repair');
      assert.equal(result.action, 'repair');
      assert.equal(result.damage.missingFiles, 1);
      assert.deepEqual(result.impact.replace, ['install', 'toolchain']);
    } finally { writeFileSync(runtimeFile, bytes, { mode: 0o600 }); }
    await t.test('healthy inspection is deterministic and grants no repair effect', () => {
      const healthy = inspect('healthy');
      assert.equal(inspect('healthy').selectionSha256, healthy.selectionSha256);
      assert.deepEqual(healthy.impact.replace, []); assert.equal(healthy.nativeSupport.repairImplemented, false);
    });
    const damageFile = async (name, change, expected = {}) => {
      const path = join(factory, name), original = readFileSync(path), mode = lstatSync(path).mode & 0o777;
      try {
        change(path); const result = inspect('repair');
        for (const [key, value] of Object.entries(expected)) assert.equal(result.damage[key], value);
        assert.equal(result.selection.intendedRelease, '1.2.3');
      } finally { rmSync(path, { force: true }); writeFileSync(path, original, { mode }); }
    };
    await t.test('missing manifest uses the independently authenticated same intended bundle', () =>
      damageFile('install/runtime/release-manifest.json', unlinkSync, { missingFiles: 1 }));
    await t.test('missing installed Node never invokes a global or damaged runtime', () =>
      damageFile('install/node/bin/node', unlinkSync, { missingFiles: 1 }));
    await t.test('changed Node is observed without execution', () =>
      damageFile('install/node/bin/node', path => writeFileSync(path, '#!/bin/sh\nexit 99\n'), { changedFiles: 1 }));
    await t.test('changed compiler is observed without npm or compiler effects', () =>
      damageFile('toolchain/node_modules/typescript/bin/tsc', path => writeFileSync(path, 'process.exit(99);\n'), { changedFiles: 1 }));
    await t.test('allowed regular file mode changes are damage at the same known path', () =>
      damageFile('install/runtime/dist/accounting.js', path => chmodSync(path, 0o700), { changedFiles: 1 }));
    for (const names of [['install'], ['toolchain'], ['install', 'toolchain']]) await t.test(`absent ${names.join('+')} is explicit and retained ownership remains required`, () => {
      for (const name of names) renameSync(join(factory, name), join(container, `saved-${name}`));
      try {
        const result = inspect('repair'); assert.equal(result.damage.absentRoots, names.length);
        for (const name of names) assert.deepEqual(result.selection.roots.find(root => root.name === name), { name, state: 'absent' });
      } finally { for (const name of names) renameSync(join(container, `saved-${name}`), join(factory, name)); }
    });
    await t.test('missing known subtree counts its descendants without inventing identities', () => {
      const path = join(factory, 'install/runtime/dist/web'), saved = join(container, 'saved-web'); renameSync(path, saved);
      try { const result = inspect('repair'); assert.equal(result.damage.missingFiles, 3); assert.equal(result.damage.missingDirectories, 1); }
      finally { renameSync(saved, path); }
    });
    for (const artifact of ['installed-receipt.json', `install-candidate-${JSON.parse(installed.stdout).operationId}/candidate-receipt.json`]) {
      await t.test(`missing ${artifact} refuses instead of authenticating external bytes as ownership`, () => {
        const path = join(factory, artifact), saved = join(container, 'saved-authority'); renameSync(path, saved);
        try { inspect('refused'); } finally { renameSync(saved, path); }
      });
    }
    await t.test('missing database refuses without creating a new history or repository identity', () => {
      const path = join(factory, 'history.sqlite'), saved = join(container, 'saved-history'); renameSync(path, saved);
      try { inspect('refused'); assert.equal(existsSync(path), false); } finally { renameSync(saved, path); }
    });
    await t.test('malformed latest installed receipt refuses', () => {
      const path = join(factory, 'installed-receipt.json'); writeFileSync(path, '{}\n');
      try { inspect('refused'); } finally { writeFileSync(path, firstReceipt); }
    });
    for (const name of ['install', 'toolchain']) await t.test(`replacement ${name} root refuses even with byte-identical content`, () => {
      const path = join(factory, name), saved = join(container, `saved-root-${name}`); renameSync(path, saved);
      cpSync(saved, path, { recursive: true }); chmodSync(path, 0o700);
      try { inspect('refused'); } finally { rmSync(path, { recursive: true }); renameSync(saved, path); }
    });
    await t.test('extra unknown runtime entry refuses', () => {
      const path = join(factory, 'install/runtime/unknown'); writeFileSync(path, 'unowned', { mode: 0o600 });
      try { inspect('refused'); } finally { unlinkSync(path); }
    });
    await t.test('unsafe runtime path refuses without expanding managed ownership', () => {
      const path = join(factory, 'install/runtime/bad:name'); writeFileSync(path, 'unowned', { mode: 0o600 });
      try { inspect('refused'); } finally { unlinkSync(path); }
    });
    for (const [name, make] of [['symlink', symlinkSync], ['hardlink', linkSync]]) await t.test(`${name} at known regular path refuses`, () => {
      const outside = join(container, `${name}-target`); writeFileSync(outside, bytes, { mode: 0o600 });
      unlinkSync(runtimeFile); make(outside, runtimeFile);
      try { inspect('refused'); } finally { unlinkSync(runtimeFile); writeFileSync(runtimeFile, bytes, { mode: 0o600 }); }
    });
    await t.test('special runtime entry refuses', async () => {
      const server = createServer(), cwd = process.cwd(); process.chdir(join(factory, 'install'));
      try {
        await new Promise((resolve, reject) => { server.once('error', reject); server.listen('socket', resolve); });
        inspect('refused');
      } finally { await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve())); process.chdir(cwd); }
    });
    for (const kind of ['dependencies.completed', 'repair.completed', 'uninstall.completed']) await t.test(`newest unsupported ${kind} never falls back`, () => {
      const database = new DatabaseSync(join(factory, 'history.sqlite'));
      try {
        database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run(kind, JSON.stringify(JSON.parse(firstReceipt)));
        inspect('refused');
      } finally { database.prepare('DELETE FROM observation_events WHERE kind=?').run(kind); database.close(); }
    });
    await t.test('unknown schema refuses without schema mutation', () => {
      const database = new DatabaseSync(join(factory, 'history.sqlite'));
      try { database.exec('PRAGMA user_version=99'); inspect('refused'); }
      finally { database.exec('PRAGMA user_version=7'); database.close(); }
    });
    await t.test('wrong requested source operation refuses', () => inspect('refused', ['--operation', '12345678-1234-4123-8123-123456789abc']));
    await t.test('genuine upgraded installation can inspect missing selected roots and refuses the older external bundle', () => {
      const upgradedBundle = join(container, 'upgrade-bundle');
      writeFileSync(descriptor, JSON.stringify({ version: '1.2.4', platform, node }));
      const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
        '--source-root', packageRoot, '--destination', upgradedBundle], { encoding: 'utf8' });
      assert.equal(packaged.status, 0, packaged.stderr);
      activeBundle = upgradedBundle; activeSha = JSON.parse(packaged.stdout).manifestSha256;
      const upgraded = invoke('upgrade', ['--offline', '--offline-cache-seed', realpathSync(cache)]);
      assert.equal(upgraded.status, 0, upgraded.stderr); assert.equal(JSON.parse(upgraded.stdout).state, 'ready');
      assert.equal(inspect('healthy').selection.intendedRelease, '1.2.4');
      const currentBundle = activeBundle, currentSha = activeSha;
      activeBundle = bundle; activeSha = manifestSha256;
      try { inspect('refused'); } finally { activeBundle = currentBundle; activeSha = currentSha; }
      for (const name of ['install', 'toolchain']) renameSync(join(factory, name), join(container, `upgraded-${name}`));
      try { const result = inspect('repair'); assert.equal(result.damage.absentRoots, 2); assert.equal(result.selection.intendedRelease, '1.2.4'); }
      finally { for (const name of ['install', 'toolchain']) renameSync(join(container, `upgraded-${name}`), join(factory, name)); }
    });
    await t.test('genuine intact interrupted public upgrade selects exact existing resume with explicit clearance', () => {
      const nextBundle = join(container, 'next-bundle');
      writeFileSync(descriptor, JSON.stringify({ version: '1.2.5', platform, node }));
      const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
        '--source-root', packageRoot, '--destination', nextBundle], { encoding: 'utf8' });
      assert.equal(packaged.status, 0, packaged.stderr);
      activeBundle = nextBundle; activeSha = JSON.parse(packaged.stdout).manifestSha256;
      // Fixture-only stop at the actual public launcher's first publication call, after genuine preparation.
      const wrapper = `import os,runpy,sys\nlauncher=sys.argv[1]\nsys.argv=sys.argv[1:]\ndef stop(frame,event,arg):\n if event=='call' and frame.f_code.co_filename==launcher and frame.f_code.co_name=='publish_candidate': os._exit(73)\n return stop\nsys.settrace(stop)\nrunpy.run_path(launcher,run_name='__main__')`;
      const stopped = invoke('upgrade', ['--offline', '--offline-cache-seed', realpathSync(cache)], ['-c', wrapper, launcher]);
      assert.equal(stopped.status, 73, stopped.stderr);
      const resumed = inspect('resume-upgrade');
      assert.equal(resumed.selection.intendedRelease, '1.2.5'); assert.equal(resumed.resume.clearanceRequired, true);
      assert.ok(['not_live', 'unknown'].includes(resumed.resume.owner));
      inspect('resume-upgrade', ['--operation', resumed.source.operationId]);
      const path = join(factory, 'controller-staging', resumed.source.operationId, 'payload/dist/accounting.js');
      const saved = readFileSync(path); unlinkSync(path);
      try { inspect('refused'); } finally { writeFileSync(path, saved, { mode: 0o600 }); }
    });
    for (const [path, bytes] of Object.entries(retained)) assert.deepEqual(readFileSync(join(root, path)), bytes);
    assert.deepEqual(readFileSync(join(factory, 'installed-receipt.json')), firstReceipt);
  } finally { fixture.dispose(); rmSync(container, { recursive: true, force: true }); }
});
