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

async function scenario(baseline, work) {
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
      const owner = currentOwner(), handle = await api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner);
      assert.ok(lstatSync(join(factory, 'history.sqlite-wal')).size > 0);
      await work({ api, maintenance, handle, root, common, factory, container, writer, run, openDependencyMaintenanceStore });
    } finally { writer.close(); }
  } finally { repository.dispose(); rmSync(container, { recursive: true, force: true }); }
}

for (const baseline of ['installed', 'upgraded']) test(`genuine ${baseline} claim gets exactly one verified WAL-consistent backup`, async t => scenario(baseline, async c => {
  const { api, handle, root, factory, writer, openDependencyMaintenanceStore } = c;
  const before = databaseFacts(factory), live = { install: fingerprint(join(factory, 'install')),
    toolchain: fingerprint(join(factory, 'toolchain')), authoring: fingerprint(join(root, '.factory')),
    source: readFileSync(join(root, 'tracked.txt')), index: readFileSync(join(c.common, 'index')) };
  await t.test('stale token and foreign live caller refuse before attempt allocation', async () => {
    await assert.rejects(api.prepareDependencyBackup(root, { ...handle, token: 'stale' }), /claim|token/);
    const script = `import {readFileSync} from 'node:fs'; const h=JSON.parse(readFileSync(0,'utf8'));
      const api=await import(${JSON.stringify(pathToFileURL(join(packageRoot, 'dist/dependency-maintenance.js')).href)});
      try { await api.prepareDependencyBackup(${JSON.stringify(root)}, h); process.exitCode=2; }
      catch(e) { if(!String(e.message).includes('exact live claim owner')) throw e; process.stdout.write('refused'); }`;
    const other = spawnSync(process.execPath, ['--input-type=module', '-e', script], { input: JSON.stringify(handle), encoding: 'utf8' });
    assert.equal(other.status, 0, other.stderr); assert.equal(other.stdout, 'refused');
    const db = new DatabaseSync(join(factory, 'history.sqlite'));
    const originalClaim = db.prepare('SELECT data FROM owner_claims WHERE id=?').get(handle.claimId).data;
    const event = db.prepare("SELECT cursor,data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed') ORDER BY cursor DESC LIMIT 1").get();
    try {
      const altered = JSON.parse(originalClaim); altered.maintenance.selectionDigest = 'a'.repeat(64);
      db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(JSON.stringify(altered), handle.claimId);
      await assert.rejects(api.prepareDependencyBackup(root, handle), /claimed original|selection changed/);
      db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(originalClaim, handle.claimId);
      const changed = JSON.parse(event.data); changed.at = '2000-01-01T00:00:00.000Z';
      db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(JSON.stringify(changed), event.cursor);
      await assert.rejects(api.prepareDependencyBackup(root, handle), /completion changed/);
    } finally {
      db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(originalClaim, handle.claimId);
      db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(event.data, event.cursor); db.close();
    }
    assert.equal((await api.inspectDependencyMaintenance(root, handle.operationId)).backupAttempted, false);
  });
  const raced = await Promise.allSettled([api.prepareDependencyBackup(root, handle), api.prepareDependencyBackup(root, handle)]);
  assert.equal(raced.filter(row => row.status === 'fulfilled').length, 1);
  assert.equal(raced.filter(row => row.status === 'rejected').length, 1);
  const result = raced.find(row => row.status === 'fulfilled').value;
  assert.equal(result.backupBound, true); assert.equal(result.operationId, handle.operationId);
  const target = join(factory, 'maintenance-backups', handle.operationId, result.backupId, 'history.sqlite');
  const copiedUrl = pathToFileURL(target); copiedUrl.searchParams.set('mode', 'ro'); copiedUrl.searchParams.set('immutable', '1');
  const copied = new DatabaseSync(copiedUrl, { readOnly: true });
  try {
    assert.deepEqual(copied.prepare('SELECT id,data FROM runs ORDER BY rowid').all(), before.domain.runs);
    assert.equal(copied.prepare('PRAGMA integrity_check').get().integrity_check, 'ok');
    assert.equal(copied.prepare('PRAGMA foreign_key_check').all().length, 0);
    assert.equal(copied.prepare('SELECT state FROM repository').get().state, 'ready');
  } finally { copied.close(); }
  await t.test('bound backup, attempt and receipt tampering block without adoption', async () => {
    for (const name of ['backup-attempt.json', 'backup-request.json', 'backup-receipt.json']) {
      const path = join(dirname(target), name), bytes = readFileSync(path);
      try { writeFileSync(path, `${bytes}\n`); await assert.rejects(api.inspectDependencyMaintenance(root, handle.operationId), /backup/); }
      finally { writeFileSync(path, bytes); }
    }
    const original = join(c.container, 'original-backup'); renameSync(target, original);
    try {
      copyFileSync(original, target);
      await assert.rejects(api.inspectDependencyMaintenance(root, handle.operationId), /backup/);
      unlinkSync(target); symlinkSync(original, target);
      await assert.rejects(api.inspectDependencyMaintenance(root, handle.operationId), /backup/);
    } finally { if (existsSync(target)) unlinkSync(target); renameSync(original, target); }
    const bytes = readFileSync(target);
    try { writeFileSync(target, Buffer.from('corrupt backup')); await assert.rejects(api.inspectDependencyMaintenance(root, handle.operationId), /backup/); }
    finally { writeFileSync(target, bytes); }
  });
  const receipt = readFileSync(join(dirname(target), 'backup-receipt.json'));
  await assert.rejects(api.prepareDependencyBackup(root, handle), /already allocated/);
  assert.deepEqual(readFileSync(join(dirname(target), 'backup-receipt.json')), receipt);
  assert.equal((await api.inspectDependencyMaintenance(root, handle.operationId)).backupBound, true);
  assert.equal((await c.maintenance.inspectMaintenance(root)).intent.dependencies.backupBound, true);
  await assert.rejects(writer.createRun(), /maintenance claimed/);
  const after = databaseFacts(factory);
  assert.deepEqual(after.domain, before.domain);
  assert.deepEqual(after.events.slice(0, before.events.length), before.events);
  assert.deepEqual(after.events.slice(before.events.length).map(row => row.kind),
    ['maintenance.backup_attempted', 'maintenance.backup_attempt_bound', 'maintenance.backup_bound']);
  assert.equal(after.claims.length, 1);
  assert.equal(fingerprint(join(factory, 'install')), live.install);
  assert.equal(fingerprint(join(factory, 'toolchain')), live.toolchain);
  assert.equal(fingerprint(join(root, '.factory')), live.authoring);
  assert.deepEqual(readFileSync(join(root, 'tracked.txt')), live.source);
  assert.deepEqual(readFileSync(join(c.common, 'index')), live.index);
  assert.equal(existsSync(join(factory, 'controller-staging', handle.operationId)), false);
  const store = openDependencyMaintenanceStore(c.common);
  try { assert.equal(store.readDependencyMaintenance(handle).claim.maintenance.phase, 'preparing'); }
  finally { store.close(); }
}));

for (const fault of ['collision', 'allocated-partial', 'helper-failed', 'helper-closure', 'helper-stale-completion'])
  test(`dependency backup ${fault} retains one attempt and never retries or adopts evidence`, async () => scenario('installed', async c => {
    const { api, handle, factory, root, openDependencyMaintenanceStore } = c;
    const before = databaseFacts(factory), live = fingerprint(join(factory, 'install'));
    let expectedPath, expectedBytes, selected = api, completion;
    if (fault === 'collision') {
      const operation = join(factory, 'maintenance-backups', handle.operationId);
      mkdirSync(operation, { recursive: true, mode: 0o700 });
      expectedPath = join(operation, 'foreign'); expectedBytes = Buffer.from('foreign evidence');
      writeFileSync(expectedPath, expectedBytes, { mode: 0o600 });
    } else if (fault === 'allocated-partial') {
      const id = randomUUID(), store = openDependencyMaintenanceStore(c.common);
      try { await store.reserveDependencyBackupAttempt(handle, id, () => {}); } finally { store.close(); }
      expectedPath = join(factory, 'maintenance-backups', handle.operationId, id, 'history.sqlite');
      mkdirSync(dirname(expectedPath), { recursive: true, mode: 0o700 }); expectedBytes = Buffer.from('partial evidence');
      writeFileSync(expectedPath, expectedBytes, { mode: 0o600 });
    } else {
      // Trusted-helper fault seam only: genuine installed/runtime/source ownership is unchanged.
      const copied = join(c.container, 'fault-package'); mkdirSync(copied, { mode: 0o700 });
      cpSync(join(packageRoot, 'dist'), join(copied, 'dist'), { recursive: true });
      writeFileSync(join(copied, 'package.json'), '{"type":"module"}');
      let code = fault === 'helper-failed'
        ? `import fs from 'node:fs'; const r=JSON.parse(fs.readFileSync(process.argv[3])); fs.writeFileSync(r.target,'partial helper output',{flag:'wx',mode:0o600}); process.exitCode=17;`
        : `import {spawn} from 'node:child_process'; spawn(process.execPath,['-e','setTimeout(()=>{},15000)'],{stdio:'ignore'}).unref(); process.stdout.write(${JSON.stringify('{"completed":true}\n')});`;
      if (fault === 'helper-stale-completion') {
        const db = new DatabaseSync(join(factory, 'history.sqlite'));
        try { completion = db.prepare("SELECT cursor,data FROM observation_events WHERE kind='install.completed' ORDER BY cursor DESC LIMIT 1").get(); }
        finally { db.close(); }
        const original = readFileSync(join(packageRoot, 'dist/forward-backup-entry.js'), 'utf8');
        code = original.replace('process.stdout.write(', `const drift = new DatabaseSync(source);
          try { const row=drift.prepare("SELECT cursor,data FROM observation_events WHERE kind='install.completed' ORDER BY cursor DESC LIMIT 1").get();
            const data=JSON.parse(row.data); data.at='2000-01-01T00:00:00.000Z';
            drift.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(JSON.stringify(data),row.cursor); }
          finally { drift.close(); } process.stdout.write(`);
        assert.notEqual(code, original, 'fixed trusted-helper fixture must reach the post-copy drift boundary');
      }
      writeFileSync(join(copied, 'dist/forward-backup-entry.js'), code);
      selected = await import(pathToFileURL(join(copied, 'dist/dependency-maintenance.js')).href);
    }
    try {
      await assert.rejects(selected.prepareDependencyBackup(root, handle), fault === 'helper-stale-completion'
        ? /completion changed/ : /already allocated|EEXIST|helper failed|closure uncertain/);
    } finally {
      if (completion) {
        const db = new DatabaseSync(join(factory, 'history.sqlite'));
        try { db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(completion.data, completion.cursor); }
        finally { db.close(); }
      }
    }
    const store = openDependencyMaintenanceStore(c.common); let claim;
    try { claim = store.readDependencyMaintenance(handle).claim; } finally { store.close(); }
    assert.ok(claim.maintenance.backupId); assert.equal(claim.maintenance.dependencies.backup, null);
    if (fault === 'helper-failed') {
      expectedPath = join(factory, 'maintenance-backups', handle.operationId, claim.maintenance.backupId, 'history.sqlite');
      expectedBytes = Buffer.from('partial helper output');
    }
    if (expectedPath) assert.deepEqual(readFileSync(expectedPath), expectedBytes);
    const claimBytes = databaseFacts(factory).claims[0].data;
    await assert.rejects(api.prepareDependencyBackup(root, handle), /already allocated/);
    assert.equal(databaseFacts(factory).claims[0].data, claimBytes);
    if (expectedPath) assert.deepEqual(readFileSync(expectedPath), expectedBytes);
    assert.equal((await api.inspectDependencyMaintenance(root, handle.operationId)).backupBound, false);
    assert.deepEqual(databaseFacts(factory).domain, before.domain);
    assert.equal(fingerprint(join(factory, 'install')), live);
    assert.equal(existsSync(join(factory, 'controller-staging', handle.operationId)), false);
  }));
