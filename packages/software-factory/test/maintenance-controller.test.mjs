import assert from 'node:assert/strict';
import test from 'node:test';
import { spawnSync } from 'node:child_process';
import { join } from 'node:path';
import { mkdirSync, readFileSync, readdirSync, realpathSync, rmdirSync, statSync, symlinkSync, unlinkSync, writeFileSync } from 'node:fs';
import { createRepository } from './fixtures/repository.mjs';

const owner = { host: 'fixture-host', pid: process.pid, start: 'fixture-process-start' };
const selection = { release: '1.0.0', selectionDigest: 'a'.repeat(64), targetReleaseSha256: 'b'.repeat(64),
  artifactDigests: { bundle: 'c'.repeat(64), node: 'd'.repeat(64) }, targetSchema: 7 };

test('two first installers compete for an absent Git-common factory root and leave one incomplete claim', async () => {
  const { beginRepositoryBootstrap, inspectMaintenance } = await import('../dist/maintenance.js');
  const repository = createRepository();
  try {
    const results = await Promise.allSettled([
      beginRepositoryBootstrap(repository.path, selection, owner),
      beginRepositoryBootstrap(repository.path, selection, owner),
    ]);
    assert.equal(results.filter(result => result.status === 'fulfilled').length, 1);
    assert.equal(results.filter(result => result.status === 'rejected').length, 1);
    const inspected = await inspectMaintenance(repository.path);
    assert.equal(inspected.status, 'incomplete');
    assert.equal(inspected.intent.operationId, results.find(result => result.status === 'fulfilled').value.operationId);
    assert.equal(inspected.intent.kind, 'install');
    assert.equal(inspected.intent.phase, 'preparing');
    assert.equal(inspected.claims, 1);
    assert.equal(inspected.marker, 'complete');
    assert.equal(inspected.database, 'current');
    assert.equal(inspected.intent.selectionDigest, selection.selectionDigest);
    assert.equal(inspected.intent.token, undefined);
    assert.equal(inspected.commonDir, realpathSync(join(repository.path, '.git')));
  } finally { repository.dispose(); }
});

test('existing empty, foreign, linked and unmarked factory roots remain untouched', async () => {
  const { beginRepositoryBootstrap, inspectMaintenance } = await import('../dist/maintenance.js');
  for (const shape of ['empty', 'foreign', 'linked', 'unmarked-database']) {
    const repository = createRepository();
    try {
      const factory = join(repository.path, '.git', 'factory');
      if (shape === 'linked') symlinkSync(repository.path, factory);
      else {
        mkdirSync(factory);
        if (shape === 'foreign') writeFileSync(join(factory, 'foreign.txt'), 'owned by somebody else');
        if (shape === 'unmarked-database') writeFileSync(join(factory, 'history.sqlite'), 'partial');
      }
      const before = shape === 'linked' ? readFileSync(join(repository.path, 'tracked.txt')) : readdirSync(factory);
      await assert.rejects(beginRepositoryBootstrap(repository.path, selection, owner));
      assert.deepEqual(shape === 'linked' ? readFileSync(join(repository.path, 'tracked.txt')) : readdirSync(factory), before);
      assert.equal((await inspectMaintenance(repository.path)).status, 'blocked');
    } finally { repository.dispose(); }
  }
});

test('normal open and public work reject incomplete bootstrap while inspection redacts the private token', async () => {
  const { beginRepositoryBootstrap, inspectMaintenance } = await import('../dist/maintenance.js');
  const { openRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  try {
    const saved = await beginRepositoryBootstrap(repository.path, selection, owner);
    assert.throws(() => openRepositoryStore(saved.commonDir), /incomplete bootstrap/);
    const status = await inspectMaintenance(repository.path);
    assert.equal(status.status, 'incomplete');
    assert.equal(status.intent?.token, undefined);
    assert.ok(!JSON.stringify(status).includes(saved.token));
    const marker = join(saved.commonDir, 'factory', 'bootstrap-incomplete');
    assert.equal(statSync(marker).mode & 0o077, 0);
  } finally { repository.dispose(); }
});

test('partial marker and corrupt or unsupported database are preserved and cannot be repaired', async () => {
  const { beginRepositoryBootstrap, inspectMaintenance, reclaimMaintenance } = await import('../dist/maintenance.js');
  for (const damage of ['partial-marker', 'corrupt-database', 'unsupported-schema']) {
    const repository = createRepository();
    try {
      const saved = await beginRepositoryBootstrap(repository.path, selection, owner);
      const marker = join(saved.commonDir, 'factory', 'bootstrap-incomplete');
      const database = join(saved.commonDir, 'factory', 'history.sqlite');
      if (damage === 'partial-marker') writeFileSync(marker, '{"version":1');
      if (damage === 'corrupt-database') writeFileSync(database, 'broken sqlite bytes');
      if (damage === 'unsupported-schema') {
        const { DatabaseSync } = await import('node:sqlite');
        const db = new DatabaseSync(database);
        try { db.exec('PRAGMA user_version=999'); } finally { db.close(); }
      }
      const beforeMarker = readFileSync(marker), beforeDatabase = readFileSync(database);
      assert.equal((await inspectMaintenance(repository.path)).status, 'blocked');
      await assert.rejects(reclaimMaintenance(repository.path, saved.operationId, owner,
        { operatorConfirmed: true, note: 'Inspected disposable fixture owner.' }));
      assert.deepEqual(readFileSync(marker), beforeMarker);
      assert.deepEqual(readFileSync(database), beforeDatabase);
    } finally { repository.dispose(); }
  }
});

test('marker-only recovery refuses unrecorded database sidecars and a partial marker before SQLite', async () => {
  const { beginRepositoryBootstrap, inspectMaintenance, reclaimMaintenance } = await import('../dist/maintenance.js');
  const first = createRepository(), second = createRepository();
  try {
    const saved = await beginRepositoryBootstrap(first.path, selection, owner);
    const database = join(saved.commonDir, 'factory', 'history.sqlite');
    unlinkSync(database);
    const sidecar = database + '-wal';
    writeFileSync(sidecar, 'unrecorded bytes');
    assert.equal((await inspectMaintenance(first.path)).status, 'blocked');
    await assert.rejects(reclaimMaintenance(first.path, saved.operationId, owner,
      { operatorConfirmed: true, note: 'Inspected disposable fixture.' }), /marker-only/);
    assert.equal(readFileSync(sidecar, 'utf8'), 'unrecorded bytes');
    const factory = join(second.path, '.git', 'factory');
    mkdirSync(factory);
    writeFileSync(join(factory, 'bootstrap-incomplete'), '{"version":1', { mode: 0o600 });
    assert.equal((await inspectMaintenance(second.path)).status, 'blocked');
    await assert.rejects(beginRepositoryBootstrap(second.path, selection, owner));
    assert.deepEqual(readdirSync(factory), ['bootstrap-incomplete']);
  } finally { first.dispose(); second.dispose(); }
});

test('marker and typed claim with different selected bytes refuse without changing either record', async () => {
  const { beginRepositoryBootstrap, inspectMaintenance, reclaimMaintenance } = await import('../dist/maintenance.js');
  const { DatabaseSync } = await import('node:sqlite');
  const repository = createRepository();
  try {
    const saved = await beginRepositoryBootstrap(repository.path, selection, owner);
    const database = join(saved.commonDir, 'factory', 'history.sqlite');
    const db = new DatabaseSync(database);
    try {
      const row = db.prepare("SELECT id,data FROM owner_claims WHERE kind='maintenance'").get();
      const altered = JSON.parse(row.data);
      altered.maintenance.artifactDigests.node = 'e'.repeat(64);
      db.prepare('UPDATE owner_claims SET data=? WHERE id=?').run(JSON.stringify(altered), row.id);
    } finally { db.close(); }
    const marker = join(saved.commonDir, 'factory', 'bootstrap-incomplete');
    const beforeMarker = readFileSync(marker), beforeDatabase = readFileSync(database);
    assert.equal((await inspectMaintenance(repository.path)).status, 'blocked');
    await assert.rejects(reclaimMaintenance(repository.path, saved.operationId, owner,
      { operatorConfirmed: true, note: 'Inspected selected bytes mismatch.' }), /identity differ/);
    assert.deepEqual(readFileSync(marker), beforeMarker);
    assert.deepEqual(readFileSync(database), beforeDatabase);
  } finally { repository.dispose(); }
});

test('complete marker with absent database resumes only its recorded operation after owner inspection', async () => {
  const { beginRepositoryBootstrap, inspectMaintenance, reclaimMaintenance } = await import('../dist/maintenance.js');
  const { openRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  try {
    const saved = await beginRepositoryBootstrap(repository.path, selection, owner);
    const database = join(saved.commonDir, 'factory', 'history.sqlite');
    unlinkSync(database); // Disposable crash fixture for marker-flushed-before-SQLite.
    assert.equal((await inspectMaintenance(repository.path)).database, 'absent');
    await assert.rejects(reclaimMaintenance(repository.path, '00000000-0000-4000-8000-000000000001', owner,
      { operatorConfirmed: true, note: 'Inspected disposable fixture owner.' }), /operation differs/);
    const resumed = await reclaimMaintenance(repository.path, saved.operationId, owner,
      { operatorConfirmed: true, note: 'Inspected disposable fixture owner.' });
    assert.equal(resumed.operationId, saved.operationId);
    assert.notEqual(resumed.token, saved.token);
    assert.equal((await inspectMaintenance(repository.path)).claims, 1);
    assert.throws(() => openRepositoryStore(saved.commonDir), /incomplete bootstrap/);
  } finally { repository.dispose(); }
});

test('typed maintenance atomically blocks runners, dashboard, competing maintenance and generic release or clearance', async () => {
  const { beginMaintenance, inspectMaintenance, reclaimMaintenance } = await import('../dist/maintenance.js');
  const { initializeRepositoryStore, openRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const claim = await beginMaintenance(repository.path, 'upgrade', selection, owner);
    const competing = openRepositoryStore(claim.commonDir);
    try {
      assert.equal((await inspectMaintenance(repository.path)).intent?.kind, 'upgrade');
      await assert.rejects(competing.createRun(), /maintenance claimed/);
      await assert.rejects(competing.claimResource({ kind: 'dashboard', owner }), /maintenance claimed/);
      await assert.rejects(beginMaintenance(repository.path, 'cleanup', selection, owner), /maintenance claimed|owner blocks/);
      await assert.rejects(competing.clearOwner({ claimId: claim.claimId, token: claim.token, operatorConfirmed: true,
        inspection: 'unknown', note: 'Test clearance' }), /maintenance claims/);
      await assert.rejects(competing.releaseClaim({ claimId: claim.claimId, token: claim.token, basis: 'quiescent' }),
        /typed maintenance claims/);
      const resumed = await reclaimMaintenance(repository.path, claim.operationId, owner,
        { operatorConfirmed: true, note: 'Inspected disposable fixture owner.' });
      assert.notEqual(resumed.token, claim.token);
      assert.equal(resumed.operationId, claim.operationId);
      assert.equal((await inspectMaintenance(repository.path)).claims, 1);
    } finally { competing.close(); }
  } finally { store?.close(); repository.dispose(); }
});

test('two typed maintenance starts race through one SQLite admission transaction', async () => {
  const { beginMaintenance, inspectMaintenance } = await import('../dist/maintenance.js');
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const results = await Promise.allSettled([
      beginMaintenance(repository.path, 'upgrade', selection, owner),
      beginMaintenance(repository.path, 'cleanup', selection, owner),
    ]);
    assert.equal(results.filter(result => result.status === 'fulfilled').length, 1);
    assert.equal(results.filter(result => result.status === 'rejected').length, 1);
    const saved = results.find(result => result.status === 'fulfilled').value;
    const observed = await inspectMaintenance(repository.path);
    assert.equal(observed.claims, 1);
    assert.equal(observed.intent.operationId, saved.operationId);
  } finally { store?.close(); repository.dispose(); }
});

test('runner and dashboard admissions each serialize against typed maintenance', async () => {
  const { beginMaintenance } = await import('../dist/maintenance.js');
  const { initializeRepositoryStore } = await import('../dist/store.js');
  for (const contender of ['runner', 'dashboard']) {
    const repository = createRepository();
    let store;
    try {
      store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
      let compete;
      if (contender === 'runner') {
        const run = await store.createRun();
        const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
        compete = () => store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
      } else compete = () => store.claimResource({ kind: 'dashboard', owner });
      const results = await Promise.allSettled([compete(), beginMaintenance(repository.path, 'upgrade', selection, owner)]);
      assert.equal(results.filter(result => result.status === 'fulfilled').length, 1, contender);
      assert.equal(results.filter(result => result.status === 'rejected').length, 1, contender);
    } finally { store?.close(); repository.dispose(); }
  }
});

test('known-live owner cannot be reclaimed from a typed maintenance claim', async () => {
  const { beginMaintenance, reclaimMaintenance } = await import('../dist/maintenance.js');
  const { currentOwner } = await import('../dist/native/process.js');
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const claim = await beginMaintenance(repository.path, 'upgrade', selection, currentOwner());
    await assert.rejects(reclaimMaintenance(repository.path, claim.operationId, owner,
      { operatorConfirmed: true, note: 'Fixture operator confirmation.' }), /known-live/);
  } finally { store?.close(); repository.dispose(); }
});

test('handoff ticket binds exact stage, nonce and claim, then consumes once after a simulated launcher receipt', async () => {
  const { beginMaintenance, consumeMaintenanceHandoff, inspectMaintenance, prepareMaintenanceHandoff,
    recordMaintenanceStage } = await import('../dist/maintenance.js');
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const claim = await beginMaintenance(repository.path, 'upgrade', selection, owner);
    const stagePath = (await inspectMaintenance(repository.path)).intent.stagePath;
    mkdirSync(join(stagePath, 'payload', 'dist'), { recursive: true, mode: 0o700 });
    writeFileSync(join(stagePath, 'payload', 'node'), 'controlled test payload');
    writeFileSync(join(stagePath, 'payload', 'dist', 'maintenance-entry.js'), 'controlled test entry');
    const publicTicket = await prepareMaintenanceHandoff(repository.path, claim);
    assert.equal(publicTicket.stagePath, stagePath);
    assert.ok(!JSON.stringify(publicTicket).includes(claim.token));
    assert.equal(statSync(publicTicket.ticketPath).mode & 0o077, 0);
    await assert.rejects(consumeMaintenanceHandoff(publicTicket.ticketPath), /ENOENT|receipt/);
    const privateTicket = JSON.parse(readFileSync(publicTicket.ticketPath, 'utf8'));
    assert.equal(privateTicket.selectionDigest, selection.selectionDigest);
    assert.deepEqual(privateTicket.artifactDigests, selection.artifactDigests);
    const receiptPath = privateTicket.exitReceiptPath;
    writeFileSync(receiptPath, JSON.stringify({ version: 1, operationId: claim.operationId, claimId: claim.claimId,
      stageDigest: publicTicket.stageDigest, nonce: 'changed-nonce' }), { flag: 'wx', mode: 0o600 });
    await assert.rejects(consumeMaintenanceHandoff(publicTicket.ticketPath), /receipt/);
    writeFileSync(receiptPath, JSON.stringify({ version: 1, operationId: claim.operationId, claimId: claim.claimId,
      stageDigest: publicTicket.stageDigest, nonce: privateTicket.nonce }), { mode: 0o600 });
    writeFileSync(publicTicket.ticketPath, JSON.stringify({ ...privateTicket, selectionDigest: 'f'.repeat(64) }), { mode: 0o600 });
    await assert.rejects(consumeMaintenanceHandoff(publicTicket.ticketPath), /selection|ticket/);
    writeFileSync(publicTicket.ticketPath, JSON.stringify(privateTicket), { mode: 0o600 });
    writeFileSync(join(stagePath, 'payload', 'node'), 'altered test payload');
    await assert.rejects(consumeMaintenanceHandoff(publicTicket.ticketPath), /stage changed/);
    writeFileSync(join(stagePath, 'payload', 'node'), 'controlled test payload');
    mkdirSync(join(stagePath, 'payload', 'empty-added-directory'));
    await assert.rejects(consumeMaintenanceHandoff(publicTicket.ticketPath), /stage changed/);
    rmdirSync(join(stagePath, 'payload', 'empty-added-directory'));
    const modifying = await consumeMaintenanceHandoff(publicTicket.ticketPath);
    assert.equal(modifying.phase, 'modifying');
    await assert.rejects(consumeMaintenanceHandoff(publicTicket.ticketPath), /handoff claim\/token\/stage\/nonce/);
    await assert.rejects(recordMaintenanceStage(claim, 'handoff-ready', 'validating'), /phase/);
    const validating = await recordMaintenanceStage(claim, 'modifying', 'validating');
    assert.equal(validating.phase, 'validating');
    assert.equal((await inspectMaintenance(repository.path)).claims, 1);
  } finally { store?.close(); repository.dispose(); }
});

test('reclamation rotates the token while retaining operation, selection and phase', async () => {
  const { beginMaintenance, inspectMaintenance, reclaimMaintenance, recordMaintenanceStage } = await import('../dist/maintenance.js');
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const old = await beginMaintenance(repository.path, 'repair', selection, owner);
    const before = (await inspectMaintenance(repository.path)).intent;
    const current = await reclaimMaintenance(repository.path, old.operationId, owner,
      { operatorConfirmed: true, note: 'Inspected controlled fixture owner.' });
    assert.notEqual(current.token, old.token);
    assert.equal(current.operationId, old.operationId);
    assert.deepEqual((await inspectMaintenance(repository.path)).intent, before);
    await assert.rejects(recordMaintenanceStage(old, 'preparing', 'handoff-ready'), /token/);
    await assert.rejects(recordMaintenanceStage(current, 'preparing', 'modifying'), /phase/);
    await assert.rejects(reclaimMaintenance(repository.path, '00000000-0000-4000-8000-000000000001', owner,
      { operatorConfirmed: true, note: 'Inspected controlled fixture owner.' }), /operation/);
  } finally { store?.close(); repository.dispose(); }
});

test('reclaimed handoff keeps its operation and phase but invalidates the old ticket and nonce', async () => {
  const { beginMaintenance, consumeMaintenanceHandoff, inspectMaintenance, prepareMaintenanceHandoff,
    reclaimMaintenance } = await import('../dist/maintenance.js');
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const original = await beginMaintenance(repository.path, 'dependencies', selection, owner);
    const stage = (await inspectMaintenance(repository.path)).intent.stagePath;
    mkdirSync(join(stage, 'payload'), { recursive: true });
    writeFileSync(join(stage, 'payload', 'node'), 'controlled staged node');
    const first = await prepareMaintenanceHandoff(repository.path, original);
    const oldTicket = JSON.parse(readFileSync(first.ticketPath, 'utf8'));
    const recovered = await reclaimMaintenance(repository.path, original.operationId, owner,
      { operatorConfirmed: true, note: 'Inspected original fixture owner and stage.' });
    assert.equal((await inspectMaintenance(repository.path)).intent.phase, 'handoff-ready');
    assert.notEqual(recovered.token, original.token);
    const second = await prepareMaintenanceHandoff(repository.path, recovered);
    const freshTicket = JSON.parse(readFileSync(second.ticketPath, 'utf8'));
    assert.notEqual(freshTicket.nonce, oldTicket.nonce);
    assert.equal(freshTicket.token, recovered.token);
    writeFileSync(oldTicket.exitReceiptPath, JSON.stringify({ version: 1, operationId: original.operationId,
      claimId: original.claimId, stageDigest: first.stageDigest, nonce: oldTicket.nonce }), { flag: 'wx', mode: 0o600 });
    await assert.rejects(consumeMaintenanceHandoff(second.ticketPath), /ENOENT|receipt/);
    writeFileSync(freshTicket.exitReceiptPath, JSON.stringify({ version: 1, operationId: recovered.operationId,
      claimId: recovered.claimId, stageDigest: second.stageDigest, nonce: freshTicket.nonce }), { flag: 'wx', mode: 0o600 });
    assert.equal((await consumeMaintenanceHandoff(second.ticketPath)).phase, 'modifying');
  } finally { store?.close(); repository.dispose(); }
});

test('a live staged consumer cannot be reclaimed after its preparer exits', async () => {
  const { consumeMaintenanceHandoff, inspectMaintenance, prepareMaintenanceHandoff, reclaimMaintenance } = await import('../dist/maintenance.js');
  const { initializeRepositoryStore, openMaintenanceStore } = await import('../dist/store.js');
  const { currentOwner, inspectOwner } = await import('../dist/native/process.js');
  const repository = createRepository();
  try {
    const store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    store.close();
    const childScript = `import {beginMaintenance} from ${JSON.stringify(new URL('../dist/maintenance.js', import.meta.url).href)};
import {currentOwner} from ${JSON.stringify(new URL('../dist/native/process.js', import.meta.url).href)};
const selection=${JSON.stringify(selection)};
const claim=await beginMaintenance(process.argv[1], 'upgrade', selection, currentOwner());
console.log(JSON.stringify(claim));`;
    const child = spawnSync(process.execPath, ['--input-type=module', '-e', childScript, repository.path],
      { encoding: 'utf8', timeout: 10000 });
    assert.equal(child.status, 0, child.stderr);
    const claim = JSON.parse(child.stdout.trim());
    const recorded = (await inspectMaintenance(repository.path)).intent;
    mkdirSync(join(recorded.stagePath, 'payload'), { recursive: true, mode: 0o700 });
    writeFileSync(join(recorded.stagePath, 'payload', 'node'), 'controlled staged runtime');
    const prepared = await prepareMaintenanceHandoff(repository.path, claim);
    const beforeHandoff = openMaintenanceStore(claim.commonDir);
    const inspectedPreparer = beforeHandoff.readMaintenanceClaim(claim.operationId);
    beforeHandoff.close();
    const ticket = JSON.parse(readFileSync(prepared.ticketPath, 'utf8'));
    writeFileSync(ticket.exitReceiptPath, JSON.stringify({ version: 1, operationId: claim.operationId,
      claimId: claim.claimId, stageDigest: prepared.stageDigest, nonce: ticket.nonce }), { flag: 'wx', mode: 0o600 });
    assert.equal(inspectOwner(currentOwner()).state, 'known_live');
    assert.equal((await consumeMaintenanceHandoff(prepared.ticketPath)).phase, 'modifying');
    const staleRecovery = openMaintenanceStore(claim.commonDir);
    try {
      await assert.rejects(staleRecovery.reclaimMaintenance({ operationId: claim.operationId,
        expectedToken: claim.token, expectedOwner: inspectedPreparer.owner, expectedPhase: 'handoff-ready',
        owner: currentOwner(), inspection: 'not_live', note: 'Inspection preceded the owner transfer.' }),
      /owner or phase changed/);
    } finally { staleRecovery.close(); }
    await assert.rejects(reclaimMaintenance(repository.path, claim.operationId, currentOwner(),
      { operatorConfirmed: true, note: 'Preparer exited; staged consumer is live.' }), /known-live/);
  } finally { repository.dispose(); }
});
