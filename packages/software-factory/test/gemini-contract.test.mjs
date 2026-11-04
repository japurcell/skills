import assert from 'node:assert/strict';
import test from 'node:test';
import { inspectSyntheticGeminiTranscript } from './fixtures/gemini-contract.mjs';

const encode = records => Buffer.from(records.map(record => JSON.stringify(record)).join('\n') + '\n');
const init = { type: 'init', timestamp: '2026-10-22T00:00:00.000Z', session_id: 'synthetic-session', model: 'synthetic-model' };
const message = content => ({ type: 'message', timestamp: init.timestamp, role: 'assistant', content, delta: true });
const result = { type: 'result', timestamp: init.timestamp, status: 'success' };

test('synthetic Gemini text is a proposed candidate rather than provider success', () => {
  assert.deepEqual(inspectSyntheticGeminiTranscript({
    stdout: encode([init, message('candidate text'), result]),
    exitCode: 0,
    expectedSessionId: 'synthetic-session',
  }), { state: 'candidate', text: 'candidate text', sessionId: 'synthetic-session' });
});

const cases = await import('./fixtures/gemini-0.65.0-contract-cases.mjs');
for (const branch of cases.branches) test(`synthetic ${branch.name} selects only assistant deltas after the completed tool phase`, () => {
  assert.deepEqual(inspectSyntheticGeminiTranscript({
    stdout: cases.encode(cases.afterTools), exitCode: 0, expectedSessionId: 'synthetic-session',
  }), { state: 'candidate', text: 'final candidate', sessionId: 'synthetic-session' });
});

for (const branch of cases.branches) {
  for (const scenario of cases.toolRejections) test(`synthetic ${branch.name}: ${scenario.name}`, () => {
    assert.deepEqual(inspectSyntheticGeminiTranscript({
      stdout: cases.encode(scenario.records), exitCode: 0, expectedSessionId: 'synthetic-session',
    }), { state: 'rejected', reason: 'tool-protocol' });
  });
}

for (const branch of cases.branches) {
  for (const scenario of cases.transcriptRejections) test(`synthetic ${branch.name}: ${scenario.name}`, () => {
    const actual = inspectSyntheticGeminiTranscript({ stdout: cases.encode(scenario.records), exitCode: 0, expectedSessionId: 'synthetic-session' });
    assert.deepEqual(actual, { state: 'rejected', reason: scenario.reason });
    assert.doesNotMatch(JSON.stringify(actual), /PRIVATE_|WRONG|EARLIER/);
  });
  test(`synthetic ${branch.name} cannot distinguish unmarked internal stop from ordinary completion`, () => {
    const [ordinary, stopped] = cases.indistinguishableEndings.map(value => cases.encode(value.records));
    assert.deepEqual(ordinary, stopped, 'source-derived limitation: stream bytes contain no stop discriminator');
    for (const stdout of [ordinary, stopped]) assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout, exitCode: 0, expectedSessionId: 'synthetic-session' }), {
      state: 'candidate', text: 'candidate text', sessionId: 'synthetic-session',
    });
  });
}
for (const exit of [{ exitCode: 1 }, { exitCode: 42 }, { exitCode: 53 }, { exitCode: null }, { exitCode: 0, signal: 'SIGTERM' }]) {
  test(`synthetic native exit ${exit.exitCode}/${exit.signal ?? 'none'} rejects a valid-looking final`, () => {
    assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout: cases.encode(cases.simple), expectedSessionId: 'synthetic-session', ...exit }), { state: 'rejected', reason: 'exit' });
  });
}
for (const [name, stdout] of [
  ['malformed JSON', Buffer.from('PRIVATE_BAD_JSON\n')],
  ['truncated record', Buffer.concat([cases.encode([cases.init]), Buffer.from('{"type":')])],
  ['missing final line delimiter', cases.encode(cases.simple).subarray(0, -1)],
  ['blank record', Buffer.concat([cases.encode(cases.simple), Buffer.from('\n')])],
]) test(`synthetic JSONL rejects ${name}`, () => {
  assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout, exitCode: 0, expectedSessionId: 'synthetic-session' }), { state: 'rejected', reason: 'jsonl' });
});

const helper = await import('./fixtures/gemini-contract.mjs');
for (const literal of [
  '/help\nKeep this slash command literal.',
  '@file ./DO_NOT_READ\n@agent:DO_NOT_INVOKE',
  '@mcp:server/resource mcp://DO_NOT_CONNECT/resource',
  '`$(DO_NOT_EXECUTE)` \"quotes\" \r\nUnicode 🙂 \uFFFD',
]) test(`synthetic prompt data preserves literal ${JSON.stringify(literal.slice(0, 24))}`, () => {
  assert.deepEqual(helper.inspectSyntheticPromptData(Buffer.from(literal)), { state: 'data', text: literal });
});
test('synthetic prompt cap counts UTF-8 bytes with an inclusive 1 MiB bound', () => {
  const exact = '🙂'.repeat(262_144);
  assert.deepEqual(helper.inspectSyntheticPromptData(Buffer.from(exact)), { state: 'data', text: exact });
  assert.deepEqual(helper.inspectSyntheticPromptData(Buffer.from(exact + 'a')), { state: 'rejected', reason: 'bounds' });
});
for (const bytes of [Buffer.from([0xc3, 0x28]), Buffer.from([0xf0, 0x9f, 0x99]), Buffer.from([0xed, 0xa0, 0x80])]) {
  test(`synthetic prompt data refuses invalid UTF-8 ${bytes.toString('hex')}`, () => {
    assert.deepEqual(helper.inspectSyntheticPromptData(bytes), { state: 'rejected', reason: 'utf8' });
  });
}
test('synthetic transcript refuses malformed UTF-8 instead of substituting candidate text', () => {
  const invalid = Buffer.concat([
    cases.encode([cases.init]),
    Buffer.from('{"type":"message","timestamp":"2026-10-22T00:00:00.000Z","role":"assistant","delta":true,"content":"'),
    Buffer.from([0xc3, 0x28]), Buffer.from('"}\n'), cases.encode([cases.terminal]),
  ]);
  assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout: invalid, exitCode: 0, expectedSessionId: 'synthetic-session' }), { state: 'rejected', reason: 'utf8' });
});
test('synthetic escaped lone surrogate is not well-formed assistant text', () => {
  assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout: cases.encode([cases.init, cases.assistant('\ud800'), cases.terminal]), exitCode: 0, expectedSessionId: 'synthetic-session' }), { state: 'rejected', reason: 'schema' });
});
test('synthetic record type objects are rejected without coercion or exceptions', () => {
  assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout: cases.encode([cases.init, { type: { toString: 1 }, timestamp: cases.timestamp }, cases.terminal]), exitCode: 0, expectedSessionId: 'synthetic-session' }), { state: 'rejected', reason: 'schema' });
});
test('synthetic JSONL record byte cap is inclusive and enforced before decoding content', () => {
  const overhead = Buffer.byteLength(JSON.stringify(cases.user));
  const exactUser = { ...cases.user, content: cases.user.content + 'x'.repeat(65_536 - overhead) };
  assert.equal(Buffer.byteLength(JSON.stringify(exactUser)), 65_536);
  const inspect = record => inspectSyntheticGeminiTranscript({ stdout: cases.encode([cases.init, record, cases.assistant('candidate'), cases.terminal]), exitCode: 0, expectedSessionId: 'synthetic-session' });
  assert.equal(inspect(exactUser).state, 'candidate');
  assert.deepEqual(inspect({ ...exactUser, content: exactUser.content + 'x' }), { state: 'rejected', reason: 'bounds' });
});
test('synthetic total JSONL bytes are capped at 1 MiB before parse', () => {
  assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout: Buffer.alloc(1_048_577, 32), exitCode: 0, expectedSessionId: 'synthetic-session' }), { state: 'rejected', reason: 'bounds' });
});
test('synthetic record count is capped at 4096', () => {
  const records = [cases.init, cases.assistant('candidate'), ...Array.from({ length: 4093 }, () => cases.assistant('')), cases.terminal];
  assert.equal(inspectSyntheticGeminiTranscript({ stdout: cases.encode(records), exitCode: 0, expectedSessionId: 'synthetic-session' }).state, 'candidate');
  records.splice(2, 0, cases.assistant(''));
  assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout: cases.encode(records), exitCode: 0, expectedSessionId: 'synthetic-session' }), { state: 'rejected', reason: 'bounds' });
});
test('synthetic final segment has an inclusive 64 KiB UTF-8 cap across chunks', () => {
  const chunk = '🙂'.repeat(8192);
  const records = [cases.init, cases.assistant(chunk), cases.assistant(chunk), cases.terminal];
  assert.equal(inspectSyntheticGeminiTranscript({ stdout: cases.encode(records), exitCode: 0, expectedSessionId: 'synthetic-session' }).text, chunk + chunk);
  records.splice(-1, 0, cases.assistant('a'));
  assert.deepEqual(inspectSyntheticGeminiTranscript({ stdout: cases.encode(records), exitCode: 0, expectedSessionId: 'synthetic-session' }), { state: 'rejected', reason: 'bounds' });
});
