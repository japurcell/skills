import assert from 'node:assert/strict';
import test from 'node:test';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore } from '../dist/store.js';

const owner = { host: 'fixture', pid: process.pid, start: 'cleanup-readers' };
async function fixture(action) {
  const repository = createRepository();
  const common = join(repository.path, '.git');
  let store;
  try {
    store = await initializeRepositoryStore(common, { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const input = await store.createCapture({ invocationId: invocation.id, channel: 'context' });
    await store.appendCapture({ id: input.id, chunks: [{ sequence: 1, text: 'saved input 🌍' }], state: 'complete' });
    await store.saveInvocationMetadata(invocation.id, { settings: {}, workflow: 'workflow.ts', selectedCommit: null,
      inputCaptureId: input.id, question: null, contexts: [] });
    const attempt = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'check', kind: 'command', intent: 'initial' });
    await action({ repository, common, store, run, invocation, input, attempt });
  } finally { store?.close(); repository.dispose(); }
}

test('cleanup reads retained input and attempt facts without loading capture previews', async () => fixture(async ({ store, invocation, input, attempt }) => {
  const snapshot = store.readCleanupSnapshot();
  assert.equal(snapshot.schema, 7);
  assert.equal(snapshot.recovery.authority, 'unassessed');
  const invocations = store.pageCleanupInvocationFacts({ through: snapshot.highWater.invocations });
  assert.equal(invocations.records.length, 1);
  assert.equal(invocations.records[0].status, 'known');
  assert.equal(invocations.records[0].inputCaptureId, input.id);
  const attempts = store.pageCleanupAttemptFacts({ through: snapshot.highWater.attempts });
  assert.equal(attempts.records[0].id, attempt.id);
  assert.equal(attempts.records[0].invocationId, invocation.id);
  const headers = store.pageCleanupCaptureHeaders({ through: snapshot.highWater.captures });
  assert.equal(headers.records[0].logicalPayloadBytes, '16');
  assert.equal(headers.records[0].id, input.id);
  assert.equal(Object.hasOwn(headers.records[0], 'text'), false);
}));

test('cleanup exact payload pages preserve partial state and distinguish empty, missing, foreign and pruned', async () => fixture(async ({ store, invocation, input }) => {
  const partial = await store.createCapture({ invocationId: invocation.id, channel: 'stderr' });
  await store.appendCapture({ id: partial.id, chunks: [{ sequence: 1, text: 'α' }, { sequence: 2, text: '🌍' }], state: 'partial' });
  const empty = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
  await store.appendCapture({ id: empty.id, chunks: [], state: 'complete' });
  const pruned = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
  await store.appendCapture({ id: pruned.id, chunks: [], state: 'pruned' });
  const first = store.readCleanupCapture({ invocationId: invocation.id, captureId: partial.id, limit: 1 });
  assert.equal(first.header.state, 'partial');
  assert.deepEqual(first.chunks, [{ sequence: '1', text: 'α' }]);
  assert.equal(first.hasMore, true);
  const second = store.readCleanupCapture({ invocationId: invocation.id, captureId: partial.id, after: first.nextSequence });
  assert.deepEqual(second.chunks, [{ sequence: '2', text: '🌍' }]);
  assert.equal(second.hasMore, false);
  const measurements = store.measureCleanupCaptures([
    { invocationId: invocation.id, captureId: partial.id }, { invocationId: invocation.id, captureId: empty.id },
    { invocationId: invocation.id, captureId: pruned.id }, { invocationId: invocation.id, captureId: 'absent' },
    { invocationId: 'foreign', captureId: input.id },
  ]);
  assert.deepEqual(measurements.map(item => [item.status, item.logicalPayloadBytes]),
    [['present', '6'], ['empty', '0'], ['pruned', '0'], ['missing', null], ['foreign', null]]);
  assert.equal(store.readCleanupCapture({ invocationId: 'foreign', captureId: input.id }).status, 'foreign');
  assert.equal(store.readCleanupCapture({ invocationId: invocation.id, captureId: 'absent' }).status, 'missing');
  assert.equal(store.readCleanupCapture({ invocationId: invocation.id, captureId: pruned.id }).status, 'pruned');
}));

test('cleanup refuses nonadvancing payload pages, gaps and invalid cursor or UTF-8 bounds', async () => fixture(async ({ store, invocation, common }) => {
  const capture = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
  await store.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: '🌍'.repeat(1000) }], state: 'unknown' });
  const page = store.readCleanupCapture({ invocationId: invocation.id, captureId: capture.id, byteBudget: 1024 });
  assert.deepEqual(page.chunks, []);
  assert.equal(page.nextSequence, '0');
  assert.equal(page.hasMore, true);
  assert.equal(page.blocked, 'byte-budget');
  for (const after of ['-1','1.5','01','9223372036854775808', 0])
    assert.throws(() => store.pageCleanupCaptureHeaders({ after }), /cleanup/);
  assert.throws(() => store.readCleanupCapture({ invocationId: invocation.id, captureId: '🌍'.repeat(65) }), /identity/);
  assert.throws(() => store.readCleanupCapture({ invocationId: invocation.id, captureId: capture.id, limit: 21 }), /page/);
  const db = new DatabaseSync(join(common, 'factory/history.sqlite'));
  try { db.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(capture.id); } finally { db.close(); }
  const gap = store.readCleanupCapture({ invocationId: invocation.id, captureId: capture.id });
  assert.equal(gap.blocked, 'sequence-gap');
  assert.equal(gap.hasMore, true);
}));

test('cleanup read-only view holds a consistent snapshot across concurrent updates and does not change history bytes', async () => fixture(async ({ store, common, invocation, input }) => {
  const { openCleanupReadStore } = await import('../dist/store.js');
  const path = join(common, 'factory/history.sqlite');
  const before = [readFileSync(path), readFileSync(`${path}-wal`)];
  const reader = openCleanupReadStore(common);
  try {
    assert.equal(Object.hasOwn(reader, 'appendCapture'), false);
    const snapshot = reader.readCleanupSnapshot();
    assert.equal(snapshot.recovery.authority, 'unassessed');
    assert.equal(reader.pageCleanupInvocationFacts().records[0].inputCaptureId, input.id);
    assert.deepEqual([readFileSync(path), readFileSync(`${path}-wal`)], before);
    const later = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
    await store.saveInvocationMetadata(invocation.id, { futureReference: later.id });
    const committed = [readFileSync(path), readFileSync(`${path}-wal`)];
    assert.deepEqual(reader.readCleanupSnapshot(), snapshot);
    assert.equal(reader.pageCleanupCaptureHeaders().records.length, 1);
    assert.equal(reader.pageCleanupInvocationFacts().records[0].inputCaptureId, input.id);
    assert.deepEqual([readFileSync(path), readFileSync(`${path}-wal`)], committed);
  } finally { reader.close(); }
  const fresh = openCleanupReadStore(common);
  try {
    assert.equal(fresh.pageCleanupCaptureHeaders().records.length, 2);
    assert.equal(fresh.pageCleanupInvocationFacts().records[0].status, 'opaque');
  } finally { fresh.close(); }
}));

test('cleanup keyed attempt and event reads enforce ownership and keep unknown or oversized evidence opaque', async () => fixture(async ({ store, common, invocation, input, attempt }) => {
  assert.equal(store.readCleanupAttempt({ invocationId: invocation.id, attemptId: attempt.id }).fact.operationKey, 'check');
  assert.equal(store.readCleanupAttempt({ invocationId: 'foreign', attemptId: attempt.id }).status, 'foreign');
  assert.equal(store.readCleanupAttempt({ invocationId: invocation.id, attemptId: 'missing' }).status, 'missing');
  const db = new DatabaseSync(join(common, 'factory/history.sqlite'));
  try {
    const add = (kind, data) => String(db.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run(kind, JSON.stringify(data)).lastInsertRowid);
    const indirect = add('attempt.started', { attemptId: attempt.id, at: '2026-11-04T00:00:00.000Z' });
    const capture = add('capture.appended', { captureId: input.id, sequence: 1, state: 'complete', bytes: 16 });
    const explicit = add('attempt.started', { invocationId: 'foreign', attemptId: attempt.id });
    const future = add('future.references', { invocationId: invocation.id, secretDiagnostic: 'must not echo' });
    const oversized = add('attempt.started', { invocationId: invocation.id, padding: 'x'.repeat(9000) });
    const wide = db.prepare('INSERT INTO observation_events(cursor,kind,data) VALUES (?,?,?)'); wide.setReadBigInts(true);
    wide.run(9007199254740993n, 'attempt.started', JSON.stringify({ attemptId: attempt.id }));
    assert.equal(store.readCleanupEvent({ invocationId: invocation.id, cursor: indirect }).status, 'known');
    assert.equal(store.readCleanupEvent({ invocationId: invocation.id, cursor: capture }).status, 'known');
    assert.equal(store.readCleanupEvent({ invocationId: invocation.id, cursor: explicit }).status, 'foreign');
    const opaque = store.readCleanupEvent({ invocationId: invocation.id, cursor: future });
    assert.equal(opaque.status, 'opaque');
    assert.equal(opaque.reason, 'unknown-format');
    assert.doesNotMatch(JSON.stringify(opaque), /must not echo|secretDiagnostic/);
    const large = store.readCleanupEvent({ invocationId: invocation.id, cursor: oversized });
    assert.equal(large.reason, 'oversized');
    assert.equal(large.sha256, null);
    assert.equal(store.readCleanupEvent({ invocationId: invocation.id, cursor: '9007199254740993' }).status, 'known');
    assert.equal(store.readCleanupSnapshot().highWater.events, '9007199254740993');
    assert.equal(store.readCleanupEvent({ invocationId: invocation.id, cursor: '9223372036854775807' }).status, 'missing');
  } finally { db.close(); }
}));

test('cleanup pages enumerate sparse headers with exact 64-bit cursors and stop at the captured high water', async () => fixture(async ({ store, common, invocation, input, attempt }) => {
  const report = await store.createCapture({ invocationId: invocation.id, channel: 'report' });
  const stdout = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
  const db = new DatabaseSync(join(common, 'factory/history.sqlite'));
  try {
    db.prepare('UPDATE captures SET rowid=? WHERE id=?').run(9007199254740993n, report.id);
    db.prepare('UPDATE captures SET rowid=? WHERE id=?').run(9223372036854775806n, stdout.id);
    db.prepare('UPDATE invocations SET rowid=? WHERE id=?').run(9007199254740994n, invocation.id);
    db.prepare('UPDATE attempts SET rowid=? WHERE id=?').run(9007199254740995n, attempt.id);
  } finally { db.close(); }
  const through = store.readCleanupSnapshot().highWater.captures;
  assert.equal(through, '9223372036854775806');
  assert.equal(store.pageCleanupInvocationFacts().nextCursor, '9007199254740994');
  assert.equal(store.pageCleanupAttemptFacts().nextCursor, '9007199254740995');
  const first = store.pageCleanupCaptureHeaders({ limit: 1, through });
  assert.equal(first.records[0].id, input.id);
  const second = store.pageCleanupCaptureHeaders({ after: first.nextCursor, through, limit: 1 });
  assert.equal(second.nextCursor, '9007199254740993');
  assert.equal(second.records[0].id, report.id);
  const third = store.pageCleanupCaptureHeaders({ after: second.nextCursor, through, limit: 1 });
  assert.equal(third.nextCursor, '9223372036854775806');
  assert.equal(third.records[0].id, stdout.id);
  assert.equal(third.hasMore, false);
  const ended = store.pageCleanupCaptureHeaders({ after: through, through });
  assert.deepEqual(ended.records, []);
  assert.equal(ended.hasMore, false);
}));

test('cleanup metadata returns only opaque facts for future, malformed or oversized records', async () => fixture(async ({ store, common, invocation, attempt }) => {
  await store.saveInvocationMetadata(invocation.id, { futureCaptureReference: 'private-reference' });
  let fact = store.pageCleanupInvocationFacts().records[0];
  assert.equal(fact.status, 'opaque');
  assert.equal(fact.reason, 'unknown-format');
  assert.match(fact.sha256, /^[a-f0-9]{64}$/);
  assert.doesNotMatch(JSON.stringify(fact), /private-reference|futureCapture/);
  await store.saveInvocationMetadata(invocation.id, { payload: '🌍'.repeat(20000) });
  fact = store.pageCleanupInvocationFacts().records[0];
  assert.equal(fact.reason, 'oversized');
  assert.equal(fact.sha256, null);
  const db = new DatabaseSync(join(common, 'factory/history.sqlite'));
  try {
    db.exec('PRAGMA ignore_check_constraints=ON');
    db.prepare('UPDATE attempts SET data=? WHERE id=?').run('{malformed fixture', attempt.id);
    assert.equal(store.readCleanupAttempt({ invocationId: invocation.id, attemptId: attempt.id }).fact.reason, 'malformed');
    db.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify({ id: attempt.id, payload: 'x'.repeat(70000) }), attempt.id);
    const oversized = store.readCleanupAttempt({ invocationId: invocation.id, attemptId: attempt.id });
    assert.equal(oversized.fact.reason, 'oversized');
    assert.equal(oversized.fact.sha256, null);
  } finally { db.close(); }
}));

test('cleanup rejects unknown header formats and future nested metadata without echoing text', async () => fixture(async ({ store, common, input, invocation }) => {
  await store.saveInvocationMetadata(invocation.id, { settings: { futureReference: input.id }, workflow: 'workflow.ts',
    selectedCommit: null, inputCaptureId: input.id, question: null, contexts: [] });
  assert.equal(store.pageCleanupInvocationFacts().records[0].status, 'opaque');
  const db = new DatabaseSync(join(common, 'factory/history.sqlite'));
  try {
    db.prepare('UPDATE captures SET channel=? WHERE id=?').run('untrusted-channel'.repeat(10000), input.id);
    const page = store.pageCleanupCaptureHeaders();
    assert.equal(page.records[0].status, 'opaque');
    assert.equal(store.readCleanupCapture({ invocationId: invocation.id, captureId: input.id }).blocked, 'unknown-header');
    assert.doesNotMatch(JSON.stringify(page), /untrusted-channel/);
    db.exec('PRAGMA ignore_check_constraints=ON');
    db.prepare('UPDATE captures SET channel=?,sequence=? WHERE id=?').run('stdout', 'untrusted-sequence'.repeat(10000), input.id);
    assert.equal(store.pageCleanupCaptureHeaders().records[0].status, 'opaque');
  } finally { db.close(); }
}));

test('cleanup pages respect the serialized UTF-8 budget and expose every chunk through continuation', async () => fixture(async ({ store, invocation }) => {
  const capture = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
  await store.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: '\u0000'.repeat(32768) }, { sequence: 2, text: '🌍'.repeat(16384) }], state: 'complete' });
  const first = store.readCleanupCapture({ invocationId: invocation.id, captureId: capture.id });
  assert.ok(Buffer.byteLength(JSON.stringify(first)) <= 262144);
  assert.equal(first.chunks.length, 1);
  assert.equal(first.hasMore, true);
  const second = store.readCleanupCapture({ invocationId: invocation.id, captureId: capture.id, after: first.nextSequence });
  assert.equal(second.chunks[0].sequence, '2');
  assert.equal(second.hasMore, false);
  assert.ok(Buffer.byteLength(JSON.stringify(second)) <= 262144);
  const tiny = store.pageCleanupCaptureHeaders({ byteBudget: 1 });
  assert.equal(tiny.nextCursor, '0');
  assert.equal(tiny.hasMore, true);
  assert.equal(tiny.blocked, 'byte-budget');
}));

test('cleanup reads empty retained history without treating absent claims as recovery clearance', async () => {
  const repository = createRepository(); let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const snapshot = store.readCleanupSnapshot();
    assert.deepEqual(snapshot.highWater, { invocations: '0', attempts: '0', captures: '0', events: '0' });
    assert.equal(snapshot.recovery.claimCount, '0');
    assert.equal(snapshot.recovery.authority, 'unassessed');
    assert.deepEqual(store.pageCleanupCaptureHeaders().records, []);
    assert.deepEqual(store.pageCleanupInvocationFacts().records, []);
    assert.deepEqual(store.pageCleanupAttemptFacts().records, []);
    assert.deepEqual(store.measureCleanupCaptures([]), []);
  } finally { store?.close(); repository.dispose(); }
});

test('cleanup agent facts retain every saved evidence capture and prior attempt reference', async () => fixture(async ({ store, invocation }) => {
  const agent = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'review', kind: 'agent', intent: 'initial' });
  const captures = [];
  for (const channel of ['context','result','stdout','validated-result']) {
    const capture = await store.createCapture({ invocationId: invocation.id, attemptId: agent.id, channel });
    await store.appendCapture({ id: capture.id, chunks: [], state: 'complete' }); captures.push(capture.id);
  }
  await store.saveAgentMetadata(agent.id, { inputsCaptureId: captures[0], resultCaptureId: captures[1], outputCaptureId: captures[2],
    adapter: 'fixture', sessionMode: 'fresh', context: '{}', validator: 'learn/extract/v1' });
  await store.markStarted({ id: agent.id, owner });
  await store.settleAttempt({ id: agent.id, launch: 'started', outcome: 'succeeded', quiescent: true, evidence: 'fixture complete', validatedResultCaptureId: captures[3] });
  const fact = store.readCleanupAttempt({ invocationId: invocation.id, attemptId: agent.id }).fact;
  assert.equal(fact.status, 'known');
  assert.deepEqual(fact.agent, { inputsCaptureId: captures[0], resultCaptureId: captures[1], outputCaptureId: captures[2],
    validatedResultCaptureId: captures[3], reusedAttemptId: null, validator: 'learn/extract/v1' });
  const repeated = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'review', kind: 'agent', intent: 'repeat', priorAttemptId: agent.id });
  assert.equal(store.readCleanupAttempt({ invocationId: invocation.id, attemptId: repeated.id }).fact.priorAttemptId, agent.id);
  assert.equal(store.pageCleanupAttemptFacts().records.every(item => item.status === 'known'), true);
}));

test('cleanup captures through-bound excludes later committed headers and chunks page at twenty rows', async () => fixture(async ({ store, invocation }) => {
  const through = store.readCleanupSnapshot().highWater.captures;
  const capture = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
  await store.appendCapture({ id: capture.id, chunks: Array.from({ length: 25 }, (_, index) => ({ sequence: index + 1, text: 'x' })), state: 'complete' });
  assert.equal(store.pageCleanupCaptureHeaders({ through }).records.length, 1);
  const first = store.readCleanupCapture({ invocationId: invocation.id, captureId: capture.id });
  assert.equal(first.chunks.length, 20);
  assert.equal(first.nextSequence, '20');
  const last = store.readCleanupCapture({ invocationId: invocation.id, captureId: capture.id, after: first.nextSequence });
  assert.equal(last.chunks.length, 5);
  assert.equal(last.nextSequence, '25');
  assert.equal(last.hasMore, false);
  assert.throws(() => store.readCleanupCapture({ invocationId: invocation.id, captureId: capture.id, after: '26' }), /continuation/);
}));
