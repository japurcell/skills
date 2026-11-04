import assert from 'node:assert/strict';
import { join } from 'node:path';
import { realpathSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore, openCleanupReadStore } from '../dist/store.js';
import { InvocationRecorder } from '../dist/capture.js';
import { CommandRunner } from '../dist/workflow.js';
import { currentOwner } from '../dist/native/process.js';
import { analyzeCleanupReferences } from '../dist/cleanup-references.js';
import { readCleanupSnapshotAuthority } from '../dist/cleanup-backups.js';
import { inspectCleanupSelection } from '../dist/cleanup.js';

async function endedCommand(work) {
  const repository = createRepository(), common = join(repository.path, '.git');
  const store = await initializeRepositoryStore(common, { release: 'graph-fixture' });
  let runner;
  try {
    const run = await store.createRun(), worktree = await store.registerWorktree({ path: repository.path, registration: 'graph-fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: currentOwner() });
    const recorder = new InvocationRecorder({ store, invocationId: invocation.id, secrets: [], requestShutdown: reason => runner?.requestShutdown('recording', reason) });
    const input = await recorder.openCapture({ channel: 'context' });
    await input.write('{"inputs":{},"question":null,"contexts":[]}'); await input.finish();
    await store.saveInvocationMetadata(invocation.id, { settings: {}, workflow: '.factory/workflows/graph.ts', selectedCommit: null,
      inputCaptureId: input.id, question: null, contexts: [] });
    await store.activateInvocation(invocation.id);
    runner = new CommandRunner(store, recorder, invocation.id, repository.path, { commandTimeoutMs: 10000, agentTimeoutMs: 10000, shutdownGraceMs: 1000 });
    await runner.execute('ordinary', { argv: [process.execPath, '-e', "process.stdout.write('retained\\n')"] });
    await runner.drain(); await recorder.barrier(); runner.close();
    await store.stopAdmissions(invocation.id);
    await store.finalizeInvocation({ id: invocation.id, outcome: 'succeeded', cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
    await work({ repository, common, store, run, invocation, input });
  } finally { runner?.close(); store.close(); repository.dispose(); }
}
function graph(c, limits, adapt = reader => reader) {
  const reader = openCleanupReadStore(c.common);
  try { return analyzeCleanupReferences(adapt(reader), limits); } finally { reader.close(); }
}
function database(c) { return new DatabaseSync(join(c.common, 'factory/history.sqlite')); }
function setData(db, table, id, transform) {
  const original = db.prepare(`SELECT data FROM ${table} WHERE id=?`).get(id).data;
  db.prepare(`UPDATE ${table} SET data=? WHERE id=?`).run(JSON.stringify(transform(JSON.parse(original))), id);
  return () => db.prepare(`UPDATE ${table} SET data=? WHERE id=?`).run(original, id);
}
async function recordInvocation(c, emit, contexts = []) {
  const invocation = await c.store.startInvocation({ runId: c.run.id, worktreeId: c.invocation.worktreeId, owner: currentOwner() });
  const input = await c.store.createCapture({ invocationId: invocation.id, channel: 'context' });
  await c.store.appendCapture({ id: input.id, chunks: [{ sequence: 1, text: JSON.stringify({ inputs: {}, question: null, contexts }) }], state: 'complete' });
  await c.store.saveInvocationMetadata(invocation.id, { settings: {}, workflow: '.factory/workflows/recorded.ts', selectedCommit: null,
    inputCaptureId: input.id, question: null, contexts });
  await c.store.activateInvocation(invocation.id);
  const result = await emit(invocation);
  await c.store.stopAdmissions(invocation.id);
  await c.store.finalizeInvocation({ id: invocation.id, outcome: 'succeeded', cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
  return result;
}

test('public reference analysis refuses a prematurely completed sparse header page', async () => endedCommand(async c => {
  const reader = openCleanupReadStore(c.common);
  try {
    assert.equal(analyzeCleanupReferences(reader).status, 'complete');
    const partial = { ...reader, pageCleanupCaptureHeaders(input) {
      const page = reader.pageCleanupCaptureHeaders({ ...input, limit: 1 });
      return { ...page, hasMore: false };
    } };
    const graph = analyzeCleanupReferences(partial);
    assert.equal(graph.status, 'blocked');
    assert.ok(graph.blockers.some(row => row.code === 'unstable'));
    assert.ok(graph.protected.some(node => node.kind === 'capture' && node.captureId === c.input.id));
  } finally { reader.close(); }
}));

test('snapshot authority refuses copied and fabricated read views before assessing them', async () => endedCommand(async c => {
  const root = realpathSync(c.repository.path), common = realpathSync(c.common), reader = openCleanupReadStore(common);
  try {
    assert.match(readCleanupSnapshotAuthority(root, common, reader).sha256, /^[a-f0-9]{64}$/);
    const copied = readCleanupSnapshotAuthority(root, common, { ...reader });
    assert.equal(copied.sha256, null);
    assert.equal(copied.recovery.status, 'blocked');
    assert.deepEqual(copied.recovery.dependencies, [{ reason: 'repository-unavailable' }]);
    let assessed = false;
    const fake = readCleanupSnapshotAuthority(root, common, { readCleanupOperationEvidence() { assessed = true; throw new Error('must never be called'); } });
    assert.equal(fake.sha256, null); assert.equal(assessed, false);
  } finally { reader.close(); }
}));

test('every exposed analysis budget refuses without presenting a truncated graph as complete', async t => endedCommand(async c => {
  for (const [field, maximum, reason] of [
    ['sourceRows', 1, 'sourceRows'], ['nodes', 1, 'nodes'], ['edges', 1, 'edges'], ['pages', 1, 'pages'],
    ['stateBytes', 1024, 'stateBytes'], ['payloadBytes', 1, 'payloadBytes'], ['metadataPageBytes', 1, 'metadataPageBytes'],
  ]) await t.test(field, () => {
    const result = graph(c, { [field]: maximum });
    assert.equal(result.status, 'blocked'); assert.equal(result.snapshotSha256, null);
    assert.ok(result.blockers.some(row => row.code === 'limit' && row.limit === reason), JSON.stringify(result.blockers));
  });
  await t.test('cooperative elapsed deadline', () => {
    const result = graph(c, { elapsedMs: 1 }, reader => ({ ...reader, pageCleanupInvocationFacts(input) {
      const page = reader.pageCleanupInvocationFacts(input), until = performance.now() + 3;
      while (performance.now() < until) { /* A deliberately slow public read adapter. */ }
      return page;
    } }));
    assert.ok(result.blockers.some(row => row.code === 'limit' && row.limit === 'elapsedMs'));
  });
  await t.test('row-page tightening preserves complete sparse facts', () => {
    assert.equal(graph(c, { rowsPerPage: 1 }).status, 'complete');
    assert.throws(() => graph(c, { rowsPerPage: 101 }), /bounds/);
  });
  await recordInvocation(c, async invocation => {
    for (let index = 0; index < 2; index++) {
      const report = await c.store.createCapture({ invocationId: invocation.id, channel: 'report' });
      await c.store.appendCapture({ id: report.id, chunks: [{ sequence: 1, text: '{}' }], state: 'complete' });
    }
  });
  await t.test('report count', () => {
    const result = graph(c, { reports: 1 });
    assert.ok(result.blockers.some(row => row.code === 'limit' && row.limit === 'reports'));
  });
}));

test('request selection caps are typed limits before repository or authority discovery', async () => {
  const captures = Array.from({ length: 101 }, (_, index) => ({ invocationId: 'owned', captureId: String(index).padStart(3, '0') }));
  const result = await inspectCleanupSelection('/must-not-be-resolved', { kind: 'captures', captures, exceptional: [], reviewNonOutput: [] });
  assert.deepEqual(result.blockers, [{ code: 'limit', node: null, limit: 'selectionCaptures' }]);
  const backups = Array.from({ length: 21 }, (_, index) => ({ operationId: '00000000-0000-4000-8000-000000000001',
    backupId: `00000000-0000-4000-8000-${String(index).padStart(12, '0')}` }));
  const backupResult = await inspectCleanupSelection('/must-not-be-resolved', { kind: 'backups', backups });
  assert.deepEqual(backupResult.blockers, [{ code: 'limit', node: null, limit: 'selectionBackups' }]);
});

test('in-place metadata and operation content changes alter a fresh snapshot while a held view stays coherent', async () => endedCommand(async c => {
  const reader = openCleanupReadStore(c.common), db = database(c);
  try {
    const before = analyzeCleanupReferences(reader), highWater = before.snapshot.highWater;
    const reverse = value => Object.fromEntries(Object.entries(value).reverse());
    const restoreInvocation = setData(db, 'invocations', c.invocation.id, reverse);
    try {
      assert.equal(analyzeCleanupReferences(reader).snapshotSha256, before.snapshotSha256);
      const changed = graph(c);
      assert.equal(changed.status, 'complete'); assert.deepEqual(changed.snapshot.highWater, highWater);
      assert.notEqual(changed.snapshotSha256, before.snapshotSha256); assert.equal(changed.graphSha256, before.graphSha256);
    } finally { restoreInvocation(); }
    const attempt = c.store.pageCleanupAttemptFacts().records[0];
    const restoreOperation = setData(db, 'operations', attempt.operationId, reverse);
    try { assert.notEqual(graph(c).snapshotSha256, before.snapshotSha256); } finally { restoreOperation(); }
  } finally { db.close(); reader.close(); }
}));

test('whole-domain paging retains sparse headers beyond one page and recognizes the distant opaque report', async () => endedCommand(async c => {
  await recordInvocation(c, async invocation => {
    for (let index = 0; index < 105; index++) {
      const capture = await c.store.createCapture({ invocationId: invocation.id, channel: 'event' });
      await c.store.appendCapture({ id: capture.id, chunks: [], state: 'complete' });
    }
  });
  assert.equal(graph(c).status, 'complete');
  const report = await recordInvocation(c, async invocation => {
    const report = await c.store.createCapture({ invocationId: invocation.id, channel: 'report' });
    await c.store.appendCapture({ id: report.id, chunks: [{ sequence: 1, text: '{}' }], state: 'complete' });
    return report;
  });
  const db = database(c);
  try { db.prepare('UPDATE captures SET rowid=? WHERE id=?').run(9007199254740993n, report.id); } finally { db.close(); }
  const result = graph(c, { rowsPerPage: 20 });
  assert.equal(result.snapshot.highWater.captures, '9007199254740993');
  assert.equal(result.status, 'blocked'); assert.ok(result.blockers.some(row => row.code === 'opaque' && row.node?.captureId === report.id));
  assert.ok(result.protected.some(node => node.kind === 'capture' && node.captureId === report.id));
}));

test('missing or foreign exact operations and inconsistent operation content retain exact blockers', async t => endedCommand(async c => {
  const attempt = c.store.pageCleanupAttemptFacts().records[0], db = database(c);
  for (const status of ['missing', 'foreign']) await t.test(status, () => {
    const result = graph(c, undefined, reader => ({ ...reader, readCleanupOperation() { return { status }; } }));
    assert.ok(result.blockers.some(row => row.code === status && row.node?.operationId === attempt.operationId));
  });
  try {
    const restore = setData(db, 'operations', attempt.operationId, value => ({ ...value, kind: 'agent' }));
    try { assert.ok(graph(c).blockers.some(row => row.code === 'ownership' && row.node?.operationId === attempt.operationId)); } finally { restore(); }
    const oversized = setData(db, 'operations', attempt.operationId, value => ({ ...value, loopKey: '🌍'.repeat(2100) }));
    try { const result = graph(c); assert.equal(result.status, 'blocked'); assert.ok(result.blockers.some(row => row.code === 'opaque'));
      assert.doesNotMatch(JSON.stringify(result), /🌍/); } finally { oversized(); }
  } finally { db.close(); }
}));

test('missing input and incomplete capture chunks block without dropping the known protected input', async t => endedCommand(async c => {
  const db = database(c);
  try {
    await t.test('missing root input', () => {
      const restore = setData(db, 'invocations', c.invocation.id, value => ({ ...value, metadata: { ...value.metadata, inputCaptureId: 'missing-root' } }));
      try { assert.ok(graph(c).blockers.some(row => row.code === 'missing' && row.node?.captureId === 'missing-root')); } finally { restore(); }
    });
    await t.test('missing chunk', () => {
      const text = db.prepare('SELECT text FROM capture_chunks WHERE capture_id=? AND sequence=1').get(c.input.id).text;
      db.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(c.input.id);
      try { const result = graph(c); assert.ok(result.blockers.some(row => row.code === 'partial' && row.node?.captureId === c.input.id));
        assert.ok(result.protected.some(node => node.kind === 'capture' && node.captureId === c.input.id));
      } finally { db.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,1,?)').run(c.input.id, text); }
    });
    await t.test('nonadvancing chunk page', () => {
      const result = graph(c, undefined, reader => ({ ...reader, readCleanupCapture(input) {
        const page = reader.readCleanupCapture(input); return { ...page, chunks: [], nextSequence: input.after ?? '0', hasMore: true };
      } }));
      assert.ok(result.blockers.some(row => row.code === 'partial'));
    });
  } finally { db.close(); }
}));

test('cycles and missing attempt lineage block and keep the real attempt and owned capture edges', async () => endedCommand(async c => {
  const attempt = c.store.pageCleanupAttemptFacts().records[0], db = database(c);
  try {
    const missing = setData(db, 'attempts', attempt.id, value => ({ ...value, priorAttemptId: 'absent-prior' }));
    try { assert.ok(graph(c).blockers.some(row => row.code === 'missing' && row.id === 'absent-prior' && row.node === null)); } finally { missing(); }
    const cycle = setData(db, 'attempts', attempt.id, value => ({ ...value, priorAttemptId: attempt.id }));
    try { const result = graph(c); assert.ok(result.blockers.some(row => row.code === 'cycle' && row.node?.attemptId === attempt.id));
      assert.ok(result.edges.some(edge => edge.kind === 'owned-capture' && edge.from.attemptId === attempt.id));
    } finally { cycle(); }
  } finally { db.close(); }
}));

test('lineage depth is independently bounded even when every prior attempt is real settled public history', async () => endedCommand(async c => {
  let prior = c.store.pageCleanupAttemptFacts().records[0];
  const later = await c.store.startInvocation({ runId: c.run.id, worktreeId: c.invocation.worktreeId, owner: currentOwner() });
  const input = await c.store.createCapture({ invocationId: later.id, channel: 'context' });
  await c.store.appendCapture({ id: input.id, chunks: [{ sequence: 1, text: '{"inputs":{},"question":null,"contexts":[]}' }], state: 'complete' });
  await c.store.saveInvocationMetadata(later.id, { settings: {}, workflow: '.factory/workflows/graph.ts', selectedCommit: null,
    inputCaptureId: input.id, question: null, contexts: [] });
  await c.store.activateInvocation(later.id);
  for (let index = 0; index < 130; index++) {
    const attempt = await c.store.admitAttempt({ id: randomUUID(), invocationId: later.id, operationKey: 'ordinary', kind: 'command', intent: 'followup', priorAttemptId: prior.id });
    await c.store.settleAttempt({ id: attempt.id, launch: 'not_started', outcome: 'interrupted', quiescent: true, evidence: 'fixture child was not started' });
    prior = attempt;
  }
  await c.store.stopAdmissions(later.id);
  await c.store.finalizeInvocation({ id: later.id, outcome: 'interrupted', cleanup: 'complete', claimId: later.claim.id, token: later.claim.token });
  const result = graph(c);
  assert.equal(result.status, 'blocked'); assert.ok(result.blockers.some(row => row.code === 'limit' && row.limit === 'dependencyDepth'));
  assert.ok(result.protected.some(node => node.kind === 'capture' && node.captureId === c.input.id));
}));

test('full selected-context hashes include chunks beyond the first payload page', async () => endedCommand(async c => {
  const capture = await recordInvocation(c, async invocation => {
    const value = await c.store.createCapture({ invocationId: invocation.id, channel: 'event' });
    await c.store.appendCapture({ id: value.id, chunks: Array.from({ length: 21 }, (_, index) => ({ sequence: index + 1, text: `chunk-${index + 1}\n` })), state: 'complete' });
    return value;
  });
  await recordInvocation(c, async () => {}, [capture.id]);
  const before = graph(c), db = database(c);
  assert.equal(before.status, 'complete');
  try {
    db.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=21').run('other-21\n', capture.id);
    const after = graph(c);
    assert.equal(after.status, 'complete'); assert.deepEqual(after.snapshot.highWater, before.snapshot.highWater);
    assert.equal(after.graphSha256, before.graphSha256); assert.notEqual(after.snapshotSha256, before.snapshotSha256);
    assert.ok(after.protected.some(node => node.kind === 'capture' && node.captureId === capture.id));
  } finally { db.close(); }
}));

test('report UTF-8 byte and JSON depth caps refuse while retaining each opaque report root', async t => endedCommand(async c => {
  for (const [name, chunks, limit] of [
    ['UTF-8 bytes', Array.from({ length: 3 }, (_, index) => ({ sequence: index + 1, text: '🌍'.repeat(16384) })), 'reportBytes'],
    ['JSON depth', [{ sequence: 1, text: '['.repeat(13) + '0' + ']'.repeat(13) }], 'jsonDepth'],
  ]) await t.test(name, async () => {
    const report = await recordInvocation(c, async invocation => {
      const value = await c.store.createCapture({ invocationId: invocation.id, channel: 'report' });
      await c.store.appendCapture({ id: value.id, chunks, state: 'complete' }); return value;
    });
    const result = graph(c);
    assert.equal(result.status, 'blocked'); assert.ok(result.blockers.some(row => row.code === 'limit' && row.limit === limit));
    assert.ok(result.protected.some(node => node.kind === 'capture' && node.captureId === report.id));
  });
}));

test('oversized root input is measured in UTF-8 bytes before decoding or concatenation', async () => endedCommand(async c => {
  const db = database(c);
  try {
    db.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(c.input.id);
    const insert = db.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)');
    for (let index = 1; index <= 7; index++) insert.run(c.input.id, index, '🌍'.repeat(16384));
    db.prepare('UPDATE captures SET sequence=7 WHERE id=?').run(c.input.id);
    const result = graph(c);
    assert.ok(result.blockers.some(row => row.code === 'limit' && row.limit === 'inputBytes' && row.node?.captureId === c.input.id));
    assert.ok(result.protected.some(node => node.kind === 'capture' && node.captureId === c.input.id));
    assert.doesNotMatch(JSON.stringify(result), /🌍/);
  } finally { db.close(); }
}));

test('missing and empty owned command input cannot be treated as reference-free', async t => {
  for (const mode of ['missing', 'empty']) await t.test(mode, async () => endedCommand(async c => {
    const attempt = c.store.pageCleanupAttemptFacts().records[0];
    const header = c.store.pageCleanupCaptureHeaders().records.find(row => row.attemptId === attempt.id && row.channel === 'context');
    const db = database(c);
    try {
      db.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(header.id);
      if (mode === 'missing') db.prepare('DELETE FROM captures WHERE id=?').run(header.id);
      else db.prepare('UPDATE captures SET sequence=0 WHERE id=?').run(header.id);
      const result = graph(c);
      assert.equal(result.status, 'blocked');
      assert.ok(result.blockers.some(row => row.code === (mode === 'missing' ? 'missing' : 'malformed') && row.node?.attemptId === attempt.id));
    } finally { db.close(); }
  }));
});

test('opaque facts retain stable IDs and missing selected context never invents an owner', async () => endedCommand(async c => {
  const db = database(c);
  try {
    const opaque = setData(db, 'invocations', c.invocation.id, value => ({ ...value, metadata: { ...value.metadata, unknown: 'must-not-echo' } }));
    try {
      const result = graph(c);
      assert.ok(result.blockers.some(row => row.code === 'opaque' && row.source === 'invocation' && row.id === c.invocation.id && row.cursor === '1'));
      assert.doesNotMatch(JSON.stringify(result), /must-not-echo/);
    } finally { opaque(); }
    const restore = setData(db, 'invocations', c.invocation.id, value => ({ ...value, metadata: { ...value.metadata, contexts: ['missing-older-context'] } }));
    db.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1')
      .run('{"inputs":{},"question":null,"contexts":["missing-older-context"]}', c.input.id);
    try {
      const result = graph(c);
      assert.ok(result.blockers.some(row => row.code === 'missing' && row.source === 'capture' && row.id === 'missing-older-context' && row.node === null));
      assert.equal(result.edges.some(edge => edge.to.captureId === 'missing-older-context'), false);
    } finally { restore(); }
  } finally { db.close(); }
}));
