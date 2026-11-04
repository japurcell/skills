import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore, openCleanupReadStore } from '../dist/store.js';
import { inspectCleanupRecoveryDependencies, resolveOwnedCleanupBackup } from '../dist/cleanup-backups.js';

async function fixture(work) {
  const repository = createRepository(), common = join(repository.path, '.git');
  const store = await initializeRepositoryStore(common, { release: 'fixture' });
  const database = new DatabaseSync(join(common, 'factory/history.sqlite'));
  try { await work({ repository, common, store, database }); }
  finally { database.close(); store.close(); repository.dispose(); }
}
const at = '2026-11-04T00:00:00.000Z';

test('cleanup invalid selection refuses without echoing arbitrary paths or unbounded input fields', async () => {
  const result = await resolveOwnedCleanupBackup('/not-used', { operationId: '../escape', backupId: randomUUID(), secret: 'untrusted'.repeat(10000) });
  assert.deepEqual(result, { status: 'refused', selection: null, reason: 'invalid-selection' });
});

test('cleanup exact operation evidence preserves signed SQLite decimal64 cursors and never discovers backup files', async () => fixture(async c => {
  const operationId = randomUUID(), backupId = randomUUID(), claimId = randomUUID();
  c.database.prepare('INSERT INTO observation_events(cursor,kind,data) VALUES (?,?,?)')
    .run(9007199254740993n, 'maintenance.backup_bound', JSON.stringify({ operationId, claimId, backupId, at }));
  const evidence = c.store.readCleanupOperationEvidence({ operationId });
  assert.equal(evidence.backupBound.status, 'known'); assert.equal(evidence.backupBound.cursor, '9007199254740993');
  assert.equal(evidence.snapshot.highWater.events, '9007199254740993');
  assert.equal(evidence.completion.status, 'missing');
  assert.equal(evidence.snapshot.recovery.authority, 'unassessed');
  const backup = join(c.common, 'factory/maintenance-backups', operationId, backupId);
  mkdirSync(backup, { recursive: true, mode: 0o700 });
  writeFileSync(join(backup, 'history.sqlite'), 'unowned candidate bytes', { mode: 0o600 });
  const before = readFileSync(join(backup, 'history.sqlite'));
  const result = await resolveOwnedCleanupBackup(c.repository.path, { operationId, backupId });
  assert.equal(result.status, 'protected'); assert.equal(result.ownership, 'unassessed'); assert.equal(result.backup, null);
  assert.deepEqual(readFileSync(join(backup, 'history.sqlite')), before);
}));

test('cleanup operation reads apply type and UTF-8 byte limits in SQL before returning any event body', async () => fixture(async c => {
  const operationId = randomUUID(), claimId = randomUUID(), backupId = randomUUID();
  const body = JSON.stringify({ operationId, claimId, backupId, at });
  const insert = c.database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)');
  let cursor = insert.run('maintenance.backup_bound', Buffer.from(body)).lastInsertRowid;
  let event = c.store.readCleanupOperationEvidence({ operationId }).backupBound;
  assert.deepEqual(event, { status: 'opaque', cursor: String(cursor), reason: 'invalid-type' });
  c.database.prepare('DELETE FROM observation_events WHERE cursor=?').run(cursor);
  cursor = insert.run('maintenance.backup_bound', JSON.stringify({ operationId, claimId, backupId, at, privateBody: '🌍'.repeat(2200) })).lastInsertRowid;
  event = c.store.readCleanupOperationEvidence({ operationId }).backupBound;
  assert.deepEqual(event, { status: 'opaque', cursor: String(cursor), reason: 'oversized' });
  assert.doesNotMatch(JSON.stringify(event), /privateBody|🌍/);
  c.database.prepare('DELETE FROM observation_events WHERE cursor=?').run(cursor);
  insert.run('maintenance.backup_bound', JSON.stringify({ operationId, claimId, backupId, at, future: true }));
  assert.equal(c.store.readCleanupOperationEvidence({ operationId }).backupBound.reason, 'unknown-format');
}));

test('cleanup completion uniqueness includes oversized and unknown exact operation matches', async () => fixture(async c => {
  const operationId = randomUUID();
  c.database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)')
    .run('future.completed', JSON.stringify({ operationId, at, privateBody: 'x'.repeat(9000) }));
  assert.equal(c.store.readCleanupOperationEvidence({ operationId }).completion.reason, 'oversized');
  c.database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run('upgrade.completed', JSON.stringify({ operationId, at }));
  const read = openCleanupReadStore(c.common);
  try {
    const evidence = read.readCleanupOperationEvidence({ operationId });
    assert.equal(evidence.completion.status, 'ambiguous');
    assert.equal(evidence.newestCompletion.reason, 'unknown-format');
    assert.ok(Buffer.byteLength(JSON.stringify(evidence)) < 16384);
    assert.doesNotMatch(JSON.stringify(evidence), /privateBody/);
    assert.throws(() => read.readCleanupOperationEvidence({ operationId: '../escape' }), /identity/);
  } finally { read.close(); }
}));

test('cleanup sanitizes current forward and dependency claims and keeps missing-claim recovery unassessed', async () => fixture(async c => {
  const repositoryId = c.store.repositoryId(), operationId = randomUUID(), backupId = randomUUID();
  for (const kind of ['upgrade', 'dependencies']) {
    const id = randomUUID(), token = randomUUID();
    const claim = { id, token, kind: 'maintenance', resourceKey: repositoryId, invocationId: null,
      owner: { host: 'fixture', pid: process.pid, start: 'fixture' }, maintenance: {
        operationId, repositoryId, kind, phase: 'preparing', backupId, stagePath: join(c.common, 'factory/controller-staging', operationId) } };
    c.database.prepare('INSERT INTO owner_claims(id,token,kind,resource_key,invocation_id,data) VALUES (?,?,?,?,?,?)')
      .run(id, token, 'maintenance', repositoryId, null, JSON.stringify(claim));
    const evidence = c.store.readCleanupOperationEvidence({ operationId });
    assert.equal(evidence.claims[0].maintenanceKind, kind); assert.equal(evidence.claims[0].backupId, backupId);
    assert.doesNotMatch(JSON.stringify(evidence), new RegExp(token));
    assert.equal((await inspectCleanupRecoveryDependencies(c.repository.path)).status, 'blocked');
    c.database.prepare('DELETE FROM owner_claims WHERE id=?').run(id);
  }
  assert.equal(c.store.readCleanupSnapshot().recovery.authority, 'unassessed');
  const result = await inspectCleanupRecoveryDependencies(c.repository.path);
  assert.equal(result.status, 'blocked'); assert.equal(result.authority, 'unassessed');
  assert.ok(result.dependencies.some(row => row.reason === 'operation-unassessed'));
}));

async function invocationFixture(c) {
  const run = await c.store.createRun();
  const worktree = await c.store.registerWorktree({ path: c.repository.path, registration: 'fixture' });
  const invocation = await c.store.startInvocation({ runId: run.id, worktreeId: worktree.id,
    owner: { host: 'fixture', pid: process.pid, start: 'fixture' } });
  await c.store.activateInvocation(invocation.id);
  const attempt = await c.store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'check', kind: 'command', intent: 'initial' });
  return { invocation, attempt, read: () => c.store.readCleanupOperationEvidence({ operationId: randomUUID() }).activity };
}

test('cleanup activity evidence blocks occupied work and unfinished invocation whose claim disappeared', async () => fixture(async c => {
  const { invocation, attempt, read } = await invocationFixture(c);
  assert.equal(read().status, 'blocked'); assert.equal(read().source, 'attempt');
  await c.store.settleAttempt({ id: attempt.id, launch: 'not_started', outcome: 'interrupted', quiescent: true, evidence: 'fixture' });
  c.database.prepare('DELETE FROM owner_claims WHERE id=?').run(invocation.claim.id);
  assert.equal(read().status, 'blocked'); assert.equal(read().source, 'invocation');
}));

test('cleanup activity evidence accepts ordinary finalized quiescence but rejects bounded inconsistent metadata', async () => fixture(async c => {
  const { invocation, attempt, read } = await invocationFixture(c);
  await c.store.settleAttempt({ id: attempt.id, launch: 'not_started', outcome: 'interrupted', quiescent: true, evidence: 'fixture' });
  await c.store.finalizeInvocation({ id: invocation.id, outcome: 'interrupted', cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
  assert.equal(read().status, 'clear');
  const body = c.database.prepare('SELECT data FROM attempts WHERE id=?').get(attempt.id).data;
  const altered = JSON.parse(body); altered.quiescent = false;
  c.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify(altered), attempt.id);
  assert.equal(read().status, 'blocked');
  for (const value of [Buffer.from(body), JSON.stringify({ ...JSON.parse(body), evidence: '🌍'.repeat(18000) })]) {
    c.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(value, attempt.id);
    const activity = read(); assert.equal(activity.status, 'blocked');
    assert.ok(Buffer.byteLength(JSON.stringify(activity)) < 1024); assert.doesNotMatch(JSON.stringify(activity), /🌍/);
  }
  c.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(body, attempt.id);
  assert.equal(read().status, 'clear');
}));

test('cleanup activity evidence authenticates explicit clearance instead of treating historical uncertainty as current work', async () => fixture(async c => {
  const { invocation, attempt, read } = await invocationFixture(c);
  const clearance = await c.store.clearOwner({ claimId: invocation.claim.id, token: invocation.claim.token,
    operatorConfirmed: true, inspection: 'unknown', note: 'confirmed bounded fixture child closure' });
  assert.equal(c.store.readInvocation(invocation.id).stage, 'running');
  assert.equal(c.store.readAttempt(attempt.id).cleanupBasis, 'operator_confirmed');
  assert.equal(read().status, 'clear');
  const clearedBody = c.database.prepare('SELECT data FROM attempts WHERE id=?').get(attempt.id).data;
  for (const altered of [{ ...JSON.parse(clearedBody), outcome: 'failed', evidence: 'impossible admitted terminal' },
    { ...JSON.parse(clearedBody), evidence: { unknown: true } }]) {
    c.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify(altered), attempt.id);
    assert.equal(read().status, 'blocked');
  }
  c.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(clearedBody, attempt.id);
  // The accepted producer sets true during clearance; an old clearance cannot bless a later inconsistent false.
  const attemptBody = JSON.parse(c.database.prepare('SELECT data FROM attempts WHERE id=?').get(attempt.id).data);
  attemptBody.quiescent = false;
  c.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify(attemptBody), attempt.id);
  assert.equal(read().status, 'blocked');
  attemptBody.quiescent = true;
  c.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify(attemptBody), attempt.id);
  assert.equal(read().status, 'clear');
  const row = c.database.prepare('SELECT data FROM clearances WHERE id=?').get(clearance.id);
  for (const value of [Buffer.from(row.data), JSON.stringify({ ...clearance, invocationId: randomUUID() }),
    JSON.stringify({ ...clearance, details: { untrusted: '🌍'.repeat(5000) } }), JSON.stringify({ ...clearance, future: true })]) {
    c.database.prepare('UPDATE clearances SET data=? WHERE id=?').run(value, clearance.id);
    assert.equal(read().status, 'blocked');
  }
  c.database.prepare('UPDATE clearances SET data=? WHERE id=?').run(row.data, clearance.id);
  const event = c.database.prepare("SELECT cursor,data FROM observation_events WHERE kind='owner.cleared' AND json_extract(data,'$.clearanceId')=?").get(clearance.id);
  const duplicate = c.database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run('owner.cleared', event.data).lastInsertRowid;
  assert.equal(read().status, 'blocked');
  c.database.prepare('DELETE FROM observation_events WHERE cursor=?').run(duplicate);
  assert.equal(read().status, 'clear');
  c.database.prepare('DELETE FROM observation_events WHERE cursor=?').run(event.cursor);
  assert.equal(read().status, 'blocked');
}));
