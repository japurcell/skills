import assert from 'node:assert/strict';
import test from 'node:test';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { DatabaseSync } from 'node:sqlite';
import { setTimeout as delay } from 'node:timers/promises';
import { Readable } from 'node:stream';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore } from '../dist/store.js';

const owner = { host: 'fixture', pid: process.pid, start: 'capture-test' };
async function fixture(action) {
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    await action({ store, invocation, repository });
  } finally { store?.close(); repository.dispose(); }
}

function captureText(store, id) {
  let after = 0, text = '', page;
  do {
    page = store.readCapture({ id, after });
    text += page.chunks.map(c => c.text).join('');
    after = page.nextSequence;
  } while (page.hasMore);
  return text;
}

test('saved text and its completeness event are atomic, sequenced and bounded', async () => fixture(async ({ store, invocation }) => {
  const capture = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
  const cursor = store.readEvents({ after: '0' }).nextCursor;
  await store.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: 'hello 🌍' }], state: 'complete' });
  const page = store.readCapture({ id: capture.id });
  assert.equal(page.state, 'complete');
  assert.equal(captureText(store, capture.id), 'hello 🌍');
  assert.equal(store.readEvents({ after: cursor }).events.at(-1).data.state, 'complete');
  await assert.rejects(store.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: 'duplicate' }] }), /complete|sequence/);
  assert.equal(captureText(store, capture.id), 'hello 🌍');
  assert.equal(store.readCapture({ id: 'absent' }).state, 'missing');
}));


test('recorder reconstructs split UTF-8 and filters split secrets and sensitive structured values before save', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, secrets: ['fixture-sensitive-value'], requestShutdown() {} });
  const output = await recorder.openCapture({ channel: 'stdout' });
  const bytes = Buffer.from('hello 🌍 fixture-sensitive-value!');
  for (const byte of bytes) await output.write(Uint8Array.of(byte));
  await output.finish();
  assert.equal(captureText(store, output.id), 'hello 🌍 [REDACTED]!');
  const result = await recorder.openCapture({ channel: 'result' });
  for (const piece of ['{"pass', 'word": "unknown-private-value", "payload":{"api_', 'key":{"nested":"private"},"summary":"safe"}}']) await result.write(piece);
  await result.finish();
  assert.deepEqual(await result.readResult(), { password: '[REDACTED]', payload: { api_key: '[REDACTED]', summary: 'safe' } });
  assert.doesNotMatch(captureText(store, result.id), /unknown-private-value|nested|private/);
}));

test('shared environment policy filters lowercase credential names across saved capture chunks', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const { environmentRedactionPolicy } = await import('../dist/redaction.js');
  const key = 'factory_password';
  const before = process.env[key];
  process.env[key] = 'fixture-lowercase-password';
  try {
    const recorder = new InvocationRecorder({ store, invocationId: invocation.id,
      secrets: environmentRedactionPolicy().secrets, requestShutdown() {} });
    const output = await recorder.openCapture({ channel: 'stdout' });
    await output.write('Value: fixture-lowercase-');
    await output.write('password; safe');
    await output.finish();
    assert.equal(captureText(store, output.id), 'Value: [REDACTED]; safe');
  } finally {
    if (before === undefined) delete process.env[key];
    else process.env[key] = before;
  }
}));


test('large lines and oversized control JSON stay complete, paged and filtered across emitted boundaries', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, secrets: ['abcdef', 'abcdefgh'], requestShutdown() {} });
  const output = await recorder.openCapture({ channel: 'stdout' });
  const prefix = 'x'.repeat(65532);
  await output.write(prefix + 'abc');
  await output.write('defgh' + 'z'.repeat(2200000));
  await output.finish();
  assert.equal(captureText(store, output.id), prefix + '[REDACTED]' + 'z'.repeat(2200000));
  let after = 0, pages = 0;
  do {
    const page = store.readCapture({ id: output.id, after });
    assert.ok(Buffer.byteLength(JSON.stringify(page)) <= 1048576);
    assert.ok(page.chunks.every(chunk => Buffer.byteLength(chunk.text) <= 65536));
    after = page.nextSequence; pages++;
    if (!page.hasMore) break;
  } while (true);
  assert.ok(pages > 1);
  assert.ok(recorder.peakBufferedBytes <= 4194304);
  const result = await recorder.openCapture({ channel: 'result' });
  const raw = JSON.stringify({ payload: 'r'.repeat(1200000) });
  await result.write(raw); await result.finish();
  await assert.rejects(result.readResult(), /size limit/);
  assert.equal(captureText(store, result.id), raw);
}));

test('streaming sensitive JSON values handle escapes, nesting, primitive values and arbitrary whitespace', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, requestShutdown() {} });
  const result = await recorder.openCapture({ channel: 'result' });
  const raw = '{"pass\\u0077ord"' + ' '.repeat(3000) + ':"fixture-quote-\\"-secret", "apiKey":[{"secret":"nested"}],"token":123,"payload":{"summary":"safe \\"text\\""}}';
  for (let offset = 0; offset < raw.length; offset += 3) await result.write(raw.slice(offset, offset + 3));
  await result.finish();
  assert.doesNotMatch(captureText(store, result.id), /fixture-quote|nested|123/);
  assert.deepEqual(await result.readResult(), { password: '[REDACTED]', apiKey: '[REDACTED]', token: '[REDACTED]', payload: { summary: 'safe "text"' } });
}));


test('control limit counts original bytes even when sensitive values shrink during filtering', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, requestShutdown() {} });
  const result = await recorder.openCapture({ channel: 'result' });
  await result.write('{"password":"' + 's'.repeat(1100000) + '","payload":"safe"}');
  await result.finish();
  assert.equal(captureText(store, result.id), '{"password":"[REDACTED]","payload":"safe"}');
  await assert.rejects(result.readResult(), /size limit/);
}));

test('unsupported bytes stop admission, preserve committed text and expose partial capture with safe fallback', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const fallbacks = [], shutdown = [];
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, requestShutdown: reason => shutdown.push(reason), fallback: text => fallbacks.push(text) });
  const output = await recorder.openCapture({ channel: 'stdout' });
  await output.write('saved text'); await recorder.barrier();
  await assert.rejects(output.write(Uint8Array.of(255)), /capture recording failed/);
  assert.equal(store.readInvocation(invocation.id).stage, 'shutting_down');
  assert.equal(store.readCapture({ id: output.id }).state, 'partial');
  assert.equal(captureText(store, output.id), 'saved text');
  assert.equal(shutdown.length, 1); assert.equal(fallbacks.length, 1);
  await assert.rejects(store.admitAttempt({ id: 'never-launched', invocationId: invocation.id, operationKey: 'late', kind: 'command', intent: 'initial' }), /admission|eligible/);
}));


test('real SQLite write failure under a native OS constraint stops admission and preserves committed evidence', () => {
  const script = fileURLToPath(new URL('./fixtures/capture-storage-failure.mjs', import.meta.url));
  // Retain POSIX RLIMIT_FSIZE. Windows gets real OS WAL write denial, not a simulated store error.
  const result = process.platform === 'win32'
    ? spawnSync(process.execPath, [script], { encoding: 'utf8', timeout: 30000 })
    : spawnSync('/usr/bin/python3', ['-c',
      'import resource,os,sys; resource.setrlimit(resource.RLIMIT_FSIZE,(524288,524288)); os.execv(sys.argv[1],sys.argv[1:])', process.execPath, script],
      { encoding: 'utf8', timeout: 15000 });
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout), { failed: true, admissionBlocked: true, shutdown: 1, notices: 1,
    savedPrefix: 'committed-before-failure', eventsReadable: true });
});

test('a slow real SQLite writer backpressures concurrent managed streams and commits no early events', async () => fixture(async ({ store, invocation, repository }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, requestShutdown() {} });
  const left = await recorder.openCapture({ channel: 'stdout' });
  const right = await recorder.openCapture({ channel: 'stderr' });
  const cursor = store.readEvents({ after: '0' }).nextCursor;
  // A genuine competing connection holds the writer lock. All observations use the public store API.
  const competing = new DatabaseSync(join(repository.path, '.git', 'factory', 'history.sqlite'));
  competing.exec('BEGIN IMMEDIATE');
  let produced = 0, completed = false;
  async function* source(letter) { for (let index = 0; index < 100; index++) { produced++; yield Buffer.alloc(65536, letter); } }
  const streams = Promise.all([left.consume(Readable.from(source(65))), right.consume(Readable.from(source(66)))]).then(() => { completed = true; });
  try {
    await delay(350);
    assert.equal(completed, false); assert.ok(produced < 20, `produced ${produced}`);
    assert.ok(recorder.peakBufferedBytes <= 4194304);
    assert.equal(store.readEvents({ after: cursor }).events.length, 0);
  } finally { competing.exec('ROLLBACK'); competing.close(); }
  await streams;
  assert.equal(captureText(store, left.id).length, 6553600);
  assert.equal(captureText(store, right.id).length, 6553600);
  assert.equal(store.readCapture({ id: left.id }).state, 'complete');
}));

test('pending output flushes within the timer and terminal barriers order text before state events', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, requestShutdown() {} });
  const output = await recorder.openCapture({ channel: 'stdout' });
  await output.write('timer text');
  assert.equal(captureText(store, output.id), '');
  await delay(150);
  assert.equal(captureText(store, output.id), 'timer text');
  await output.write(' barrier text'); await output.finish();
  const events = store.readEvents({ after: '0' }).events.filter(event => event.data.captureId === output.id);
  assert.equal(events.at(-1).data.state, 'complete');
  assert.equal(captureText(store, output.id), 'timer text barrier text');
}));

test('configuration bounds reject upfront without storing or echoing filter values', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const cursor = store.readEvents({ after: '0' }).nextCursor;
  for (const secrets of [[''], ['s'.repeat(4097)], Array(129).fill('fake'), Array(17).fill('v'.repeat(4096))]) {
    assert.throws(() => new InvocationRecorder({ store, invocationId: invocation.id, secrets, requestShutdown() {} }), /configuration/);
  }
  assert.equal(store.readEvents({ after: cursor }).events.length, 0);
}));

test('bad sequences and oversized batches roll back all state and events, while detail states remain explicit', async () => fixture(async ({ store, invocation }) => {
  const capture = await store.createCapture({ invocationId: invocation.id, channel: 'report' });
  const cursor = store.readEvents({ after: '0' }).nextCursor;
  await assert.rejects(store.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: 'not committed' }, { sequence: 1, text: 'duplicate' }] }), /sequence/);
  await assert.rejects(store.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: 'x'.repeat(65537) }] }), /64 KiB/);
  await assert.rejects(store.appendCapture({ id: capture.id, chunks: Array.from({ length: 5 }, (_, i) => ({ sequence: i + 1, text: 'x'.repeat(65536) })) }), /256 KiB/);
  assert.equal(store.readEvents({ after: cursor }).events.length, 0);
  assert.equal(captureText(store, capture.id), '');
  for (const state of ['partial','unknown','pruned']) {
    const item = await store.createCapture({ invocationId: invocation.id, channel: 'report' });
    await store.appendCapture({ id: item.id, chunks: [], state });
    assert.equal(store.readCapture({ id: item.id }).state, state);
  }
  assert.equal(store.readCapture({ id: 'absent' }).state, 'missing');
  assert.equal(store.readEvents({ after: '9223372036854775807' }).gap, true);
  assert.ok(Buffer.byteLength(JSON.stringify(store.readEvents({ after: '0' }))) <= 1048576);
}));


test('an exact capture append retry reconciles its committed identity without another event', async () => fixture(async ({ store, invocation }) => {
  const capture = await store.createCapture({ invocationId: invocation.id, channel: 'report' });
  const input = { id: capture.id, chunks: [{ sequence: 1, text: 'saved once' }], state: 'complete' };
  await store.appendCapture(input);
  const cursor = store.readEvents({ after: '0' }).nextCursor;
  await store.appendCapture(input);
  assert.equal(store.readEvents({ after: cursor }).events.length, 0);
  assert.equal(captureText(store, capture.id), 'saved once');
  await assert.rejects(store.appendCapture({ ...input, chunks: [{ sequence: 1, text: 'changed' }] }), /sequence/);
}));


test('JSON escapes and ordinary multiline serialization cannot bypass configured secrets', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, secrets: ['abcdef', 'abcdefgh', 'fixture\ncredential', '🌍-private'], requestShutdown() {} });
  const result = await recorder.openCapture({ channel: 'result' });
  const raw = String.raw`{"summary":"abc\u0064efgh","multiline":"fixture\ncredential","unicode":"\ud83c\udf0d-private","safe":"leave\u0020this"}`;
  for (let offset = 0; offset < raw.length; offset += 2) await result.write(raw.slice(offset, offset + 2));
  await result.finish();
  assert.equal(captureText(store, result.id), String.raw`{"summary":"[REDACTED]","multiline":"[REDACTED]","unicode":"[REDACTED]","safe":"leave\u0020this"}`);
  assert.deepEqual(await result.readResult(), { summary: '[REDACTED]', multiline: '[REDACTED]', unicode: '[REDACTED]', safe: 'leave this' });
}));


test('independent invocation recorders persist concurrent text and preserve their shared admission accounting', async () => fixture(async ({ store, invocation, repository }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const { mkdtempSync } = await import('node:fs');
  const worktree = await store.registerWorktree({ path: mkdtempSync(join(repository.path, 'capture-other-')), registration: 'capture-other' });
  const other = await store.startInvocation({ runId: invocation.runId, worktreeId: worktree.id, owner });
  await store.activateInvocation(other.id);
  const recorders = [invocation, other].map(value => new InvocationRecorder({ store, invocationId: value.id, secrets: ['fixture-secret'], requestShutdown() {} }));
  const outputs = await Promise.all(recorders.map(recorder => recorder.openCapture({ channel: 'stdout' })));
  await Promise.all(outputs.map(async (output, index) => {
    await output.write('stream-' + index + '-fixture-'); await output.write('secret-' + 'w'.repeat(600000)); await output.finish();
  }));
  for (let i = 0; i < outputs.length; i++) {
    assert.equal(captureText(store, outputs[i].id), 'stream-' + i + '-[REDACTED]-' + 'w'.repeat(600000));
    assert.ok(recorders[i].peakBufferedBytes <= 4194304);
  }
  assert.equal(store.readAccounting(invocation.runId).additionalUsed, 0);
}));


test('supported UTF-8 BOM text is retained and incomplete terminal bytes remain an explicit failure', async () => fixture(async ({ store, invocation }) => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, requestShutdown() {}, fallback() {} });
  const output = await recorder.openCapture({ channel: 'stdout' });
  await output.write(Buffer.from('\uFEFFtext')); await output.finish();
  assert.equal(captureText(store, output.id), '\uFEFFtext');
  const incomplete = await recorder.openCapture({ channel: 'stderr' });
  await incomplete.write(Buffer.from('prefix')); await recorder.barrier();
  await incomplete.write(Uint8Array.of(0xF0, 0x9F));
  await assert.rejects(incomplete.finish(), /capture recording failed/);
  assert.equal(store.readCapture({ id: incomplete.id }).state, 'partial');
  assert.equal(captureText(store, incomplete.id), 'prefix');
}));
