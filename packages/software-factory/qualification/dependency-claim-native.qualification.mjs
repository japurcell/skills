import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, readdirSync, rmSync, unlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
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

const scenarios = [['installed', 'dependencies'], ['upgraded', 'dependencies'], ['installed', 'dashboard'],
  ['installed', 'runner'], ['installed', 'maintenance']];
for (const [baseline, opponent] of scenarios) test(`genuine ${baseline} dependency admission races ${opponent} with no backup or live mutation`, async t => {
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
    const plan = await api.inspectDependencyMaintenanceSelection(root, source);
    assert.deepEqual(plan.toolchain.missing, ['node_modules/typescript/bin/tsc']);
    const owner = currentOwner(), fixtureStore = openRepositoryStore(common);
    let run, worktree;
    try {
      run = await fixtureStore.createRun();
      worktree = await fixtureStore.registerWorktree({ path: root, registration: 'claim admission fixture' });
      await t.test('dashboard, runner and other maintenance claims exclude dependency admission', async () => {
        for (const kind of ['dashboard', 'maintenance']) {
          const claim = await fixtureStore.claimResource({ kind, owner });
          await assert.rejects(api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner), /claimed|owner|binding refused|idle/);
          await fixtureStore.releaseClaim({ claimId: claim.id, token: claim.token, basis: 'quiescent' });
        }
        const invocation = await fixtureStore.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
        await assert.rejects(api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner), /owner|idle/);
        await fixtureStore.finalizeInvocation({ id: invocation.id, outcome: 'succeeded', cleanup: 'complete',
          claimId: invocation.claim.id, token: invocation.claim.token });
      });
      await t.test('wrong manifest and stale selection refuse before creating a claim', async () => {
        await assert.rejects(api.admitDependencyMaintenance(root, source, plan.selectionDigest,
          { ...owner, start: 'wrong fixture process identity' }), /owner identity unavailable/);
        await assert.rejects(api.admitDependencyMaintenance(root, { ...source, manifestSha256: 'a'.repeat(64) }, plan.selectionDigest, owner));
        await assert.rejects(api.admitDependencyMaintenance(root, source, 'a'.repeat(64), owner), /selection changed/);
        const file = join(factory, 'toolchain/node_modules/@types/node/index.d.ts'), bytes = readFileSync(file);
        try {
          writeFileSync(file, 'changed known selected bytes');
          await assert.rejects(api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner), /selection changed/);
        } finally { writeFileSync(file, bytes); }
        const db = new DatabaseSync(join(factory, 'history.sqlite'));
        const completion = db.prepare("SELECT cursor,data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed') ORDER BY cursor DESC LIMIT 1").get();
        try {
          const changed = JSON.parse(completion.data); changed.at = '2000-01-01T00:00:00.000Z';
          db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(JSON.stringify(changed), completion.cursor);
          await assert.rejects(api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner), /selection changed/);
        } finally {
          db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(completion.data, completion.cursor); db.close();
        }
        assert.equal(databaseFacts(factory).claims.length, 0);
      });
    } finally { fixtureStore.close(); }
    let before = databaseFacts(factory);
    const liveBefore = { install: fingerprint(join(factory, 'install')),
      toolchain: fingerprint(join(factory, 'toolchain')), authoring: fingerprint(join(root, '.factory')),
      source: readFileSync(join(root, 'tracked.txt')), index: readFileSync(join(common, 'index')),
      backups: existsSync(join(factory, 'maintenance-backups')) ? fingerprint(join(factory, 'maintenance-backups')) : null };
    let races;
    if (opponent !== 'dependencies') {
      const raceStore = openRepositoryStore(common);
      try {
        const contender = () => opponent === 'runner'
          ? raceStore.startInvocation({ runId: run.id, worktreeId: worktree.id, owner })
          : opponent === 'maintenance'
            ? maintenance.beginMaintenance(root, 'cleanup', { release: plan.release, selectionDigest: 'd'.repeat(64),
              targetReleaseSha256: manifestSha256, artifactDigests: { bundle: manifestSha256 }, targetSchema: 7 }, owner)
            : raceStore.claimResource({ kind: 'dashboard', owner });
        const competed = await Promise.allSettled([api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner), Promise.resolve().then(contender)]);
        assert.equal(competed.filter(result => result.status === 'fulfilled').length, 1, 'dependency and competing admission cannot both win');
        assert.equal(databaseFacts(factory).claims.length, 1);
        if (competed[0].status === 'fulfilled') races = competed;
        else {
          assert.equal(competed[1].status, 'fulfilled');
          const winner = competed[1].value;
          if (opponent === 'maintenance') {
            const competing = databaseFacts(factory);
            assert.equal(JSON.parse(competing.claims[0].data).maintenance.kind, 'cleanup');
            assert.deepEqual(competing.domain, before.domain);
            assert.deepEqual(competing.events.slice(0, before.events.length), before.events);
            assert.deepEqual(competing.events.slice(before.events.length).map(event => event.kind), ['maintenance.started']);
            assert.equal(fingerprint(join(factory, 'install')), liveBefore.install);
            assert.equal(fingerprint(join(factory, 'toolchain')), liveBefore.toolchain);
            assert.equal(fingerprint(join(root, '.factory')), liveBefore.authoring);
            assert.equal(existsSync(join(factory, 'maintenance-backups', winner.operationId)), false);
            return;
          }
          if (opponent === 'runner') await raceStore.finalizeInvocation({ id: winner.id, outcome: 'succeeded', cleanup: 'complete',
            claimId: winner.claim.id, token: winner.claim.token });
          else await raceStore.releaseClaim({ claimId: winner.id, token: winner.token, basis: 'quiescent' });
          before = databaseFacts(factory);
        }
      } finally { raceStore.close(); }
    }
    races ??= await Promise.allSettled([api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner),
      api.admitDependencyMaintenance(root, source, plan.selectionDigest, owner)]);
    assert.equal(races.filter(result => result.status === 'fulfilled').length, 1, 'one exact dependency caller wins');
    assert.equal(races.filter(result => result.status === 'rejected').length, 1);
    const handle = races[0].status === 'fulfilled' ? races[0].value : races[1].value;
    const inspected = await api.inspectDependencyMaintenance(root, handle.operationId);
    assert.equal(inspected.status, 'preparing');
    assert.equal(inspected.backupBound, false);
    assert.equal(inspected.selectionDigest, plan.selectionDigest);
    assert.doesNotMatch(JSON.stringify(inspected), /token|bundleRoot|providers|controller-staging/);
    assert.equal(existsSync(join(factory, 'controller-staging', handle.operationId)), false);
    assert.equal(existsSync(join(factory, `dependencies-${handle.operationId}`)), false);
    assert.equal(existsSync(join(factory, 'maintenance-backups', handle.operationId)), false);
    assert.equal(existsSync(compiler), false, 'admission must not repair the selected file');
    const database = new DatabaseSync(join(factory, 'history.sqlite'), { readOnly: true });
    try {
      assert.equal(database.prepare('SELECT state FROM repository').get().state, 'ready');
      assert.equal(database.prepare('SELECT count(*) AS n FROM owner_claims').get().n, 1);
      assert.equal(database.prepare("SELECT count(*) AS n FROM attempts WHERE kind='agent'").get().n, 0);
      assert.equal(database.prepare('SELECT count(*) AS n FROM sessions').get().n, 0);
    } finally { database.close(); }
    await t.test('exact claim excludes ordinary admission, generic clearing, handoff and stale handles', async () => {
      const store = openDependencyMaintenanceStore(common);
      try {
        assert.throws(() => store.readDependencyMaintenance({ ...handle, token: 'stale' }), /claim|token/);
        await assert.rejects(api.assertDependencyMaintenance(root, { ...handle, token: 'stale' }), /claim|token/);
        await assert.rejects(store.claimResource({ kind: 'dashboard', owner }), /maintenance claimed/);
        await assert.rejects(store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner }), /maintenance claimed/);
        await assert.rejects(store.clearOwner({ claimId: handle.claimId, token: handle.token, operatorConfirmed: true,
          note: 'Fixture verifies generic clearance refusal.', inspection: 'unknown' }), /operation-preserving recovery/);
        await assert.rejects(store.releaseClaim({ claimId: handle.claimId, token: handle.token, basis: 'quiescent' }), /validated completion/);
        await assert.rejects(store.advanceMaintenance({ handle, expected: 'preparing', next: 'handoff-ready',
          stageDigest: 'a'.repeat(64), stageIdentity: '1:1', ticketNonceHash: 'b'.repeat(64) }), /no handoff/);
        await assert.rejects(maintenance.prepareMaintenanceHandoff(root, handle), /no backup, stage or handoff/);
        await assert.rejects(maintenance.reclaimMaintenance(root, handle.operationId, owner,
          { operatorConfirmed: true, note: 'Fixture verifies explicit dependency recovery boundary.' }), /later operation-specific/);
      } finally { store.close(); }
    });
    await t.test('claimed expected and observed facts reject later file or selection changes without adoption', async () => {
      const file = join(factory, 'toolchain/node_modules/@types/node/index.d.ts'), bytes = readFileSync(file);
      try {
        writeFileSync(file, 'new selected damage after admission');
        await assert.rejects(api.assertDependencyMaintenance(root, handle), /claimed original|selection changed/);
        assert.equal((await maintenance.inspectMaintenance(root)).status, 'blocked');
      } finally { writeFileSync(file, bytes); }
      const runtimeFile = join(factory, 'install/runtime/dist/accounting.js'), runtimeBytes = readFileSync(runtimeFile);
      try {
        writeFileSync(runtimeFile, 'unrelated runtime damage');
        await assert.rejects(api.assertDependencyMaintenance(root, handle), /installed binding refused/);
      } finally { writeFileSync(runtimeFile, runtimeBytes); }
      const db = new DatabaseSync(join(factory, 'history.sqlite'));
      const originalClaim = db.prepare('SELECT data FROM owner_claims WHERE id=?').get(handle.claimId).data;
      const event = db.prepare("SELECT cursor,data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed') ORDER BY cursor DESC LIMIT 1").get();
      try {
        const altered = JSON.parse(originalClaim); altered.maintenance.selectionDigest = 'b'.repeat(64);
        db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(JSON.stringify(altered), handle.claimId);
        await assert.rejects(api.assertDependencyMaintenance(root, handle), /claimed original|selection changed/);
        db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(originalClaim, handle.claimId);
        const completion = JSON.parse(event.data); completion.selectionDigest = 'c'.repeat(64);
        db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(JSON.stringify(completion), event.cursor);
        await assert.rejects(api.assertDependencyMaintenance(root, handle), /completion changed/);
      } finally {
        db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(originalClaim, handle.claimId);
        db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(event.data, event.cursor); db.close();
      }
    });
    const after = databaseFacts(factory);
    assert.deepEqual(after.domain, before.domain, 'admission preserves every domain row and schema');
    assert.deepEqual(after.events.slice(0, before.events.length), before.events);
    assert.deepEqual(after.events.slice(before.events.length).map(event => event.kind), ['maintenance.started']);
    assert.equal(after.claims.length, 1);
    assert.equal(fingerprint(join(factory, 'install')), liveBefore.install);
    assert.equal(fingerprint(join(factory, 'toolchain')), liveBefore.toolchain);
    assert.equal(fingerprint(join(root, '.factory')), liveBefore.authoring);
    assert.deepEqual(readFileSync(join(root, 'tracked.txt')), liveBefore.source);
    assert.deepEqual(readFileSync(join(common, 'index')), liveBefore.index);
    assert.equal(existsSync(join(factory, 'maintenance-backups')) ? fingerprint(join(factory, 'maintenance-backups')) : null, liveBefore.backups);
    assert.equal((await api.inspectDependencyMaintenance(root, handle.operationId)).status, 'preparing');
    assert.equal((await maintenance.inspectMaintenance(root)).status, 'incomplete');
  } finally { repository.dispose(); rmSync(container, { recursive: true, force: true }); }
});
