import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import { chmodSync, cpSync, existsSync, linkSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, renameSync, rmSync, symlinkSync, unlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
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

test('selected cleanup authenticates a retained backup from genuine public install then upgrade', async t => {
  assert.ok(node, 'supported pinned Darwin arm64 or Linux x64 profile required');
  assert.equal(process.version, node.version);
  const python = process.env.FACTORY_TEST_PYTHON, archive = realpathSync(process.env.FACTORY_TEST_NODE_ARCHIVE);
  const seed = realpathSync(process.env.FACTORY_TEST_NPM_CACHE_SEED);
  assert.ok(python && existsSync(python)); assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-cleanup-backups-')));
  const fixture = createRepository(), root = realpathSync(fixture.path), factory = join(root, '.git/factory');
  try {
    const home = join(container, 'home'), cache = join(container, 'npm-cache');
    mkdirSync(home, { mode: 0o700 }); cpSync(seed, cache, { recursive: true });
    const userConfig = join(container, 'user.npmrc'), globalConfig = join(container, 'global.npmrc');
    writeFileSync(userConfig, '', { mode: 0o600 }); writeFileSync(globalConfig, '', { mode: 0o600 });
    const env = { PATH: process.env.PATH, HOME: home, TMPDIR: container, TMP: container, TEMP: container,
      NPM_CONFIG_USERCONFIG: userConfig, NPM_CONFIG_GLOBALCONFIG: globalConfig };
    const descriptor = join(container, 'selection.json');
    const invoke = (command, version, stop = false) => {
      const bundle = join(container, `bundle-${version}`);
      writeFileSync(descriptor, JSON.stringify({ version, platform, node }));
      const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
        '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
      assert.equal(packaged.status, 0, packaged.stderr);
      const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
      const wrapper = `import os,runpy,sys\nlauncher=sys.argv[1]\nsys.argv=sys.argv[1:]\ndef stop(frame,event,arg):\n if event=='call' and frame.f_code.co_filename==launcher and frame.f_code.co_name=='publish_candidate': os._exit(73)\n return stop\nsys.settrace(stop)\nrunpy.run_path(launcher,run_name='__main__')`;
      const result = spawnSync(python, [...(stop ? ['-c', wrapper] : []), launcher, command, '--repository', root, '--bundle-root', bundle,
        '--manifest-sha256', manifestSha256, '--node-archive', archive, '--offline', '--offline-cache-seed', realpathSync(cache)],
      { env, encoding: 'utf8', timeout: 300_000, maxBuffer: 2 * 1024 * 1024 });
      assert.equal(result.status, stop ? 73 : 0, result.stderr);
      if (stop) return;
      assert.equal(JSON.parse(result.stdout).state, 'ready');
      return JSON.parse(result.stdout);
    };
    const installed = invoke('install', '1.2.3');
    const upgraded = invoke('upgrade', '1.2.4');
    const { resolveOwnedCleanupBackup, inspectCleanupRecoveryDependencies } = await import('../dist/cleanup-backups.js');
    const operationId = upgraded.operationId;
    const intent = JSON.parse(readFileSync(join(factory, `upgrade-${operationId}`, 'intent.json')));
    const original = JSON.parse(readFileSync(join(factory, `upgrade-${operationId}`, 'original.json')));
    // The immutable copied claim, rather than a directory listing, identifies the selected backup.
    const { openCleanupReadStore, openRepositoryStore } = await import('../dist/store.js');
    assert.equal(installed.operationId, original.receipt.operationId);
    const store = openCleanupReadStore(join(root, '.git'));
    let evidence;
    try { evidence = store.readCleanupOperationEvidence({ operationId }); } finally { store.close(); }
    assert.equal(evidence.completion.status, 'known');
    // This committed locator selects a tuple but grants no backup ownership by itself.
    const backupId = evidence.backupBound.data.backupId;
    assert.ok(backupId);
    const result = await resolveOwnedCleanupBackup(root, { operationId, backupId });
    assert.equal(result.status, 'owned');
    assert.equal(result.authority.backupReceiptSha256, intent.backupReceiptSha256);
    assert.equal(result.source.release, '1.2.3');
    assert.equal(result.file.path, join(factory, 'maintenance-backups', operationId, backupId, 'history.sqlite'));
    const key = { operationId, backupId }, target = result.file.path, upgrade = join(factory, `upgrade-${operationId}`);
    const resolveBackup = () => resolveOwnedCleanupBackup(root, key);
    const assertOwned = async () => assert.equal((await resolveBackup()).status, 'owned');
    const assertRefused = async () => assert.equal((await resolveBackup()).status, 'refused');
    const retained = [target, join(upgrade, 'new-receipt.json'), join(upgrade, 'original.json'), join(upgrade, 'intent.json'),
      join(factory, 'maintenance-backups', operationId, backupId, 'backup-receipt.json'),
      join(factory, 'maintenance-backups', operationId, backupId, 'backup-request.json')];
    const baseline = retained.map(path => [path, readFileSync(path), lstatSync(path).ino]);
    await t.test('historical copy counts remain valid after live history grows', async () => {
      const writer = openRepositoryStore(join(root, '.git'));
      try { await writer.createRun(); } finally { writer.close(); }
      await assertOwned();
      assert.equal((await inspectCleanupRecoveryDependencies(root)).status, 'clear');
    });
    await t.test('genuine ended workflow owner requires exact operator clearance before old backups become eligible', async () => {
      const program = `import {openRepositoryStore} from ${JSON.stringify(pathToFileURL(join(packageRoot, 'dist/store.js')).href)};
        import {currentOwner} from ${JSON.stringify(pathToFileURL(join(packageRoot, 'dist/native/process.js')).href)};
        import {randomUUID} from 'node:crypto';
        const store=openRepositoryStore(${JSON.stringify(join(root, '.git'))});
        try {const run=await store.createRun();const worktree=await store.registerWorktree({path:${JSON.stringify(root)},registration:'cleanup-public-activity'});
          const invocation=await store.startInvocation({runId:run.id,worktreeId:worktree.id,owner:currentOwner()});
          await store.activateInvocation(invocation.id);await store.admitAttempt({id:randomUUID(),invocationId:invocation.id,operationKey:'interrupted',kind:'command',intent:'initial'});
          await store.finishInvocation(invocation.id,'interrupted','unknown');process.stdout.write(JSON.stringify({claimId:invocation.claim.id,token:invocation.claim.token}));
        } finally {store.close();}`;
      const child = spawnSync(process.execPath, ['--input-type=module', '-e', program], { encoding: 'utf8', timeout: 30000 });
      assert.equal(child.status, 0, child.stderr);
      const claim = JSON.parse(child.stdout);
      const protectedBackup = await resolveBackup(); assert.equal(protectedBackup.status, 'protected');
      assert.ok(protectedBackup.dependencies.some(row => row.reason === 'activity-unassessed'));
      const writer = openRepositoryStore(join(root, '.git'));
      try {
        const { clearClaim } = await import('../dist/clearance.js');
        await clearClaim(writer, { ...claim, operatorConfirmed: true, note: 'fixture child has ended; confirmed cleanup' });
      } finally { writer.close(); }
      await assertOwned(); assert.equal((await inspectCleanupRecoveryDependencies(root)).status, 'clear');
    });
    await t.test('genuine ordinary finalized invocation proves quiescence without an operator clearance', async () => {
      const { currentOwner } = await import('../dist/native/process.js');
      const writer = openRepositoryStore(join(root, '.git'));
      try {
        const run = await writer.createRun(), worktree = await writer.registerWorktree({ path: root, registration: 'cleanup-public-activity' });
        const invocation = await writer.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: currentOwner() });
        await writer.activateInvocation(invocation.id);
        const attempt = await writer.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'not-launched', kind: 'command', intent: 'initial' });
        await writer.settleAttempt({ id: attempt.id, launch: 'not_started', outcome: 'interrupted', quiescent: true, evidence: 'fixture did not launch a child' });
        await writer.finalizeInvocation({ id: invocation.id, outcome: 'interrupted', cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
      } finally { writer.close(); }
      await assertOwned(); assert.equal((await inspectCleanupRecoveryDependencies(root)).status, 'clear');
    });
    await t.test('retained backup authority does not require the old installed trees to remain live', async () => {
      const old = join(upgrade, 'old'), saved = join(container, 'saved-old'); renameSync(old, saved);
      try { await assertOwned(); } finally { renameSync(saved, old); }
    });
    await t.test('first install and unknown operations supply no backup link', async () => {
      assert.equal((await resolveOwnedCleanupBackup(root, { operationId: installed.operationId, backupId })).reason, 'unsupported-kind');
      assert.equal((await resolveOwnedCleanupBackup(root, { operationId: randomUUID(), backupId })).reason, 'authority-missing');
      assert.equal((await resolveOwnedCleanupBackup(root, { operationId, backupId: randomUUID() })).status, 'refused');
      assert.equal((await resolveOwnedCleanupBackup(root, { operationId: '../escape', backupId })).reason, 'invalid-selection');
    });
    for (const path of retained) {
      await t.test(`missing exact ${path.slice(factory.length + 1)} refuses and preserves authority`, async () => {
        const saved = join(container, 'saved-exact'); renameSync(path, saved);
        try { await assertRefused(); } finally { renameSync(saved, path); }
      });
      await t.test(`changed exact ${path.slice(factory.length + 1)} refuses`, async () => {
        const bytes = readFileSync(path); writeFileSync(path, '{}\n');
        try { await assertRefused(); } finally { writeFileSync(path, bytes); }
      });
    }
    for (const path of [target, join(upgrade, 'new-receipt.json')]) for (const [name, create] of [['symlink', symlinkSync], ['hardlink', linkSync]]) {
      await t.test(`${name} at authenticated ${path.slice(factory.length + 1)} refuses`, async () => {
        const saved = join(container, 'saved-link'); renameSync(path, saved); create(saved, path);
        try { await assertRefused(); } finally { unlinkSync(path); renameSync(saved, path); }
      });
    }
    await t.test('byte-identical replacement of the authenticated file refuses', async () => {
      const saved = join(container, 'saved-backup'); renameSync(target, saved); cpSync(saved, target); chmodSync(target, 0o600);
      try { await assertRefused(); } finally { unlinkSync(target); renameSync(saved, target); }
    });
    await t.test('unexpected SQLite sidecars prevent immutable-copy authority without removing them', async () => {
      for (const suffix of ['-wal', '-shm', '-journal']) {
        const sidecar = `${target}${suffix}`; writeFileSync(sidecar, 'retained uncertain SQLite state', { mode: 0o600 });
        try { await assertRefused(); assert.equal(readFileSync(sidecar, 'utf8'), 'retained uncertain SQLite state'); }
        finally { unlinkSync(sidecar); }
      }
      const outside = join(container, 'foreign-sidecar'); writeFileSync(outside, 'foreign sidecar bytes', { mode: 0o600 });
      const sidecar = `${target}-wal`;
      for (const create of [symlinkSync, linkSync]) {
        create(outside, sidecar);
        try { await assertRefused(); assert.equal(readFileSync(outside, 'utf8'), 'foreign sidecar bytes'); }
        finally { unlinkSync(sidecar); }
      }
    });
    await t.test('nonprivate backup parent refuses without inventing historical directory identity', async () => {
      const parent = join(factory, 'maintenance-backups', operationId, backupId); chmodSync(parent, 0o755);
      try { await assertRefused(); } finally { chmodSync(parent, 0o700); }
      const owned = await resolveBackup(); assert.equal(owned.status, 'owned');
      assert.equal(owned.parents.find(row => row.path === parent).provenance, 'currently-observed');
    });
    // Deliberate test-only authority rebinding starts from this genuine producer output. It is not a repair API.
    // Matching declared hashes must not hide an inconsistent historical SQLite copy from the retained decoder.
    const inconsistentCopy = async mutate => {
      const boundPath = join(factory, 'maintenance-backups', operationId, backupId, 'backup-receipt.json');
      const intentPath = join(upgrade, 'intent.json'), receiptPath = join(upgrade, 'new-receipt.json');
      const saved = [target, boundPath, intentPath, receiptPath].map(path => [path, readFileSync(path)]);
      const db = new DatabaseSync(join(factory, 'history.sqlite'));
      const event = db.prepare("SELECT cursor,data FROM observation_events WHERE kind='upgrade.completed' AND json_extract(data,'$.operationId')=?").get(operationId);
      try {
        const bound = JSON.parse(readFileSync(boundPath));
        const editCopy = change => {
          const copy = new DatabaseSync(target);
          try { copy.exec('PRAGMA journal_mode=DELETE; PRAGMA foreign_keys=OFF'); change(copy); } finally { copy.close(); }
        };
        await mutate({ bound, editCopy });
        const { backupFileDigest } = await import('../dist/maintenance-backup.js');
        Object.assign(bound, backupFileDigest(target));
        writeFileSync(boundPath, `${JSON.stringify(bound)}\n`);
        const nextIntent = JSON.parse(readFileSync(intentPath)); nextIntent.backupReceiptSha256 = hash(readFileSync(boundPath));
        writeFileSync(intentPath, `${JSON.stringify(nextIntent)}\n`);
        const nextReceipt = JSON.parse(readFileSync(receiptPath));
        nextReceipt.backupReceiptSha256 = nextIntent.backupReceiptSha256; nextReceipt.intentSha256 = hash(readFileSync(intentPath));
        writeFileSync(receiptPath, `${JSON.stringify(nextReceipt)}\n`);
        const completion = JSON.parse(event.data); completion.receiptSha256 = hash(readFileSync(receiptPath));
        db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(JSON.stringify(completion), event.cursor);
        await assertRefused();
      } finally {
        for (const [path, bytes] of saved) writeFileSync(path, bytes);
        db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(event.data, event.cursor); db.close();
      }
      await assertOwned();
    };
    await t.test('fault injection: matching file hashes do not replace historical count-digest proof', async () => {
      await inconsistentCopy(({ bound }) => { bound.countDigest = '0'.repeat(64); });
    });
    await t.test('fault injection: unknown historical source schema refuses with rebound outer hashes', async () => {
      await inconsistentCopy(({ editCopy }) => editCopy(copy => copy.exec('PRAGMA user_version=99')));
    });
    await t.test('fault injection: copied repository identity must match the authenticated original', async () => {
      await inconsistentCopy(({ editCopy }) => editCopy(copy => copy.prepare('UPDATE repository SET id=?').run(randomUUID())));
    });
    await t.test('fault injection: sole copied claim must be the originating committed upgrade claim', async () => {
      await inconsistentCopy(({ editCopy }) => editCopy(copy => {
        const claim = JSON.parse(copy.prepare('SELECT data FROM owner_claims').get().data), id = randomUUID(); claim.id = id;
        copy.prepare('UPDATE owner_claims SET id=?,data=?').run(id, JSON.stringify(claim));
      }));
    });
    await t.test('fault injection: copied claim selection and source relationships remain mandatory', async () => {
      await inconsistentCopy(({ editCopy }) => editCopy(copy => {
        const claim = JSON.parse(copy.prepare('SELECT data FROM owner_claims').get().data);
        claim.maintenance.forward.sourceIdentity = '0:1';
        copy.prepare('UPDATE owner_claims SET data=?').run(JSON.stringify(claim));
      }));
    });
    await t.test('fault injection: oversized copied claim body refuses before JavaScript decoding', async () => {
      await inconsistentCopy(({ editCopy }) => editCopy(copy => {
        const claim = JSON.parse(copy.prepare('SELECT data FROM owner_claims').get().data); claim.future = '🌍'.repeat(3000);
        copy.prepare('UPDATE owner_claims SET data=?').run(JSON.stringify(claim));
      }));
    });
    await t.test('fault injection: missing copied claim refuses even when the declared counts match', async () => {
      await inconsistentCopy(async ({ bound, editCopy }) => {
        const { forwardCounts } = await import('../dist/schema-forward.js');
        editCopy(copy => { copy.exec('DELETE FROM owner_claims'); bound.countDigest = forwardCounts(copy).digest; });
      });
    });
    await t.test('fault injection: copied foreign-key failure refuses despite matching file and count digests', async () => {
      await inconsistentCopy(async ({ bound, editCopy }) => {
        const { forwardCounts } = await import('../dist/schema-forward.js');
        editCopy(copy => {
          copy.prepare("INSERT INTO captures(id,invocation_id,attempt_id,channel,state,sequence) VALUES (?,?,NULL,'stdout','complete',0)")
            .run(randomUUID(), randomUUID());
          assert.equal(copy.prepare('PRAGMA integrity_check').get().integrity_check, 'ok');
          assert.ok(copy.prepare('PRAGMA foreign_key_check').get());
          bound.countDigest = forwardCounts(copy).digest;
        });
      });
    });
    for (const marker of ['bootstrap-incomplete', 'upgrade-incomplete']) await t.test(`claimless ready repository with ${marker} protects the selected copy`, async () => {
      const path = join(factory, marker); writeFileSync(path, '{}\n', { mode: 0o600 });
      try {
        const protectedBackup = await resolveBackup();
        assert.equal(protectedBackup.status, 'protected'); assert.equal(protectedBackup.ownership, 'authenticated');
        assert.equal((await inspectCleanupRecoveryDependencies(root)).status, 'blocked');
        assert.ok(protectedBackup.dependencies.some(row => row.reason === (marker === 'bootstrap-incomplete' ? 'bootstrap-marker' : 'upgrade-marker')));
      } finally { unlinkSync(path); }
    });
    const injectedEvent = async (kind, value, action) => {
      const db = new DatabaseSync(join(factory, 'history.sqlite'));
      const cursor = db.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run(kind, value).lastInsertRowid;
      try { await action(); } finally { db.prepare('DELETE FROM observation_events WHERE cursor=?').run(cursor); db.close(); }
    };
    await t.test('duplicate committed operation refuses instead of selecting a newest match', async () => {
      const db = new DatabaseSync(join(factory, 'history.sqlite'), { readOnly: true }); let body;
      try { body = db.prepare("SELECT data FROM observation_events WHERE kind='upgrade.completed' AND json_extract(data,'$.operationId')=?").get(operationId).data; }
      finally { db.close(); }
      await injectedEvent('upgrade.completed', body, async () => {
        assert.equal((await resolveBackup()).reason, 'authority-ambiguous');
      });
    });
    for (const kind of ['dependencies.completed','repair.completed','uninstall.completed','future.completed']) await t.test(`unsupported newest ${kind} blocks ownership clearance`, async () => {
      await injectedEvent(kind, JSON.stringify({ operationId: randomUUID(), at: '2026-11-04T00:00:00Z' }), async () => {
        assert.equal((await resolveBackup()).status, 'protected');
        assert.equal((await inspectCleanupRecoveryDependencies(root)).status, 'blocked');
      });
    });
    await t.test('missing claim never clears a persisted unfinished operation', async () => {
      await injectedEvent('maintenance.started', JSON.stringify({ operationId: randomUUID(), claimId: randomUUID(), kind: 'upgrade', at: '2026-11-04T00:00:00Z' }), async () => {
        assert.equal((await resolveBackup()).status, 'protected');
        assert.equal((await inspectCleanupRecoveryDependencies(root)).status, 'blocked');
      });
    });
    for (const [path, bytes, inode] of baseline) { assert.deepEqual(readFileSync(path), bytes); assert.equal(lstatSync(path).ino, inode); }
    await assertOwned();
    await t.test('genuine interrupted public forward upgrade protects its recovery copy and prior backups', async () => {
      invoke('upgrade', '1.2.5', true);
      const { inspectMaintenance } = await import('../dist/maintenance.js');
      const status = await inspectMaintenance(root); assert.equal(status.status, 'incomplete');
      const selected = status.intent;
      assert.equal(selected.kind, 'upgrade'); assert.ok(selected.backupId);
      const active = await resolveOwnedCleanupBackup(root, { operationId: selected.operationId, backupId: selected.backupId });
      assert.equal(active.status, 'protected'); assert.equal(active.ownership, 'unassessed');
      assert.ok(active.dependencies.some(row => row.claim?.maintenanceKind === 'upgrade' && row.claim.phase === 'handoff-ready'));
      assert.equal((await resolveBackup()).status, 'protected');
      assert.equal((await inspectCleanupRecoveryDependencies(root)).status, 'blocked');
      for (const [path, bytes, inode] of baseline) { assert.deepEqual(readFileSync(path), bytes); assert.equal(lstatSync(path).ino, inode); }
    });
  } finally { fixture.dispose(); rmSync(container, { recursive: true, force: true }); }
});

test('genuine dependency preparing backup remains protected under its original owner', async () => {
  assert.ok(node); assert.equal(process.version, node.version);
  const python = process.env.FACTORY_TEST_PYTHON, archive = realpathSync(process.env.FACTORY_TEST_NODE_ARCHIVE);
  assert.ok(python && existsSync(python)); assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-cleanup-dependency-')));
  const fixture = createRepository(), root = realpathSync(fixture.path), common = join(root, '.git'), factory = join(common, 'factory');
  try {
    const home = join(container, 'home'), cache = join(container, 'npm-cache');
    mkdirSync(home, { mode: 0o700 }); cpSync(realpathSync(process.env.FACTORY_TEST_NPM_CACHE_SEED), cache, { recursive: true });
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
    const installed = spawnSync(python, [launcher, 'install', '--repository', root, '--bundle-root', bundle,
      '--manifest-sha256', manifestSha256, '--node-archive', archive, '--offline', '--offline-cache-seed', realpathSync(cache)],
    { env, encoding: 'utf8', timeout: 300_000, maxBuffer: 2 * 1024 * 1024 });
    assert.equal(installed.status, 0, installed.stderr);
    // Existing accepted dependency producer, with a real damaged compiler and no provider/candidate preparation.
    unlinkSync(join(factory, 'toolchain/node_modules/typescript/bin/tsc'));
    const api = await import('../dist/dependency-maintenance.js');
    const { currentOwner } = await import('../dist/native/process.js');
    const { resolveOwnedCleanupBackup, inspectCleanupRecoveryDependencies } = await import('../dist/cleanup-backups.js');
    const source = { mode: 'repair', bundleRoot: bundle, manifestSha256 };
    const plan = await api.inspectDependencyMaintenanceSelection(root, source);
    const handle = await api.admitDependencyMaintenance(root, source, plan.selectionDigest, currentOwner());
    const prepared = await api.prepareDependencyBackup(root, handle);
    assert.equal(prepared.backupBound, true);
    const backup = join(factory, 'maintenance-backups', handle.operationId, prepared.backupId);
    const retained = ['history.sqlite', 'backup-attempt.json', 'backup-request.json', 'backup-receipt.json']
      .map(name => [join(backup, name), readFileSync(join(backup, name))]);
    const selected = await resolveOwnedCleanupBackup(root, { operationId: handle.operationId, backupId: prepared.backupId });
    assert.equal(selected.status, 'protected'); assert.equal(selected.ownership, 'unassessed');
    assert.ok(selected.dependencies.some(row => row.claim?.maintenanceKind === 'dependencies'
      && row.claim.phase === 'preparing' && row.claim.backupId === prepared.backupId));
    assert.doesNotMatch(JSON.stringify(selected), new RegExp(handle.token));
    assert.equal((await inspectCleanupRecoveryDependencies(root)).status, 'blocked');
    for (const [path, bytes] of retained) assert.deepEqual(readFileSync(path), bytes);
    assert.equal((await api.inspectDependencyMaintenance(root, handle.operationId)).backupBound, true);
  } finally { fixture.dispose(); rmSync(container, { recursive: true, force: true }); }
});
