import assert from 'node:assert/strict';
import test from 'node:test';
import cases from './fixtures/opencode-2.1.3-contract-cases.json' with { type: 'json' };
import { inspectSyntheticOpenCodeTranscript, inspectSyntheticOpenCodePromptData } from './fixtures/opencode-contract.mjs';

const encode = records => Buffer.from(records.map(record => JSON.stringify(record)).join('\n') + '\n');
const attempt = { id: 'fixture-attempt', sessionId: 'ses_fixture' };
const text = (value, messageID = 'msg_final', id = 'prt_text') => ({
  type: 'text', timestamp: 1000, sessionID: 'ses_fixture',
  part: { id, sessionID: 'ses_fixture', messageID, type: 'text', text: value, time: { start: 1000, end: 1000 } },
});
const inspect = (records, overrides = {}) => inspectSyntheticOpenCodeTranscript({ chunks: [encode(records)], exitCode: 0, attempt, ...overrides });
const candidate = (value = 'candidate 🙂', identity = attempt) => ({
  state: 'candidate', text: value, terminal: 'unknown',
  identity: { attemptId: identity.id, sessionId: identity.sessionId, messageId: 'msg_final' },
});

test('synthetic OpenCode text without a terminal is only a candidate with unknown terminal evidence', () => {
  assert.deepEqual(inspect([text('candidate 🙂')]), candidate());
});

const recordsFor = names => structuredClone(names.map(name => cases.records[name]));
for (const scenario of cases.scenarios) test(`synthetic OpenCode: ${scenario.name}`, () => {
  assert.deepEqual(inspect(recordsFor(scenario.records)), scenario.reason
    ? { state: 'rejected', reason: scenario.reason } : candidate(scenario.text));
});
test('source success and external user interruption can have indistinguishable JSONL and exit fixtures', () => {
  const [completed, interrupted] = cases.indistinguishableEndings;
  assert.deepEqual(encode(recordsFor(completed.records)), encode(recordsFor(interrupted.records)));
  for (const ending of cases.indistinguishableEndings) {
    assert.deepEqual(inspect(recordsFor(ending.records), { exitCode: ending.exitCode }), candidate());
  }
});
test('a repeated step finish is never a terminal success marker', () => {
  const finish = structuredClone(cases.records.finalFinish);
  finish.part.id = 'prt_another_finish';
  assert.deepEqual(inspect([cases.records.final, cases.records.finalFinish, finish]), candidate());
});
test('new assistant message discards an earlier plausible final', () => {
  assert.deepEqual(inspect([text('PRIVATE_EARLIER', 'msg_old', 'prt_old'), text('candidate 🙂')]), candidate());
});
test('revisiting an earlier assistant message refuses ambiguous final selection', () => {
  assert.deepEqual(inspect([text('PRIVATE_OLD', 'msg_old', 'prt_old'), text('candidate 🙂'), text('PRIVATE_TAIL', 'msg_old', 'prt_tail')]), { state: 'rejected', reason: 'message-order' });
});

for (const exit of [{ exitCode: 1 }, { exitCode: 130 }, { exitCode: null }, { exitCode: 0, signal: 'SIGINT' }]) {
  test(`native exit ${exit.exitCode}/${exit.signal ?? 'none'} refuses plausible text`, () => {
    assert.deepEqual(inspect([cases.records.final], exit), { state: 'rejected', reason: 'exit' });
  });
}
for (const [name, change, reason] of [
  ['outer session mismatch', r => { r.sessionID = 'ses_PRIVATE'; }, 'session'],
  ['part session mismatch', r => { r.part.sessionID = 'ses_PRIVATE'; }, 'session'],
  ['missing session', r => { delete r.sessionID; }, 'schema'],
  ['missing message', r => { delete r.part.messageID; }, 'schema'],
  ['empty part identity', r => { r.part.id = ''; }, 'schema'],
  ['nonstring record type', r => { r.type = {}; }, 'schema'],
  ['unknown record type', r => { r.type = 'session.execution.succeeded'; }, 'schema'],
  ['invented success field', r => { r.success = true; }, 'schema'],
  ['wrong native timestamp shape', r => { r.timestamp = '2026-10-22T00:00:00Z'; }, 'schema'],
  ['wrong text part type', r => { r.part.type = 'reasoning'; }, 'schema'],
  ['escaped lone surrogate', r => { r.part.text = '\ud800'; }, 'schema'],
  ['invented final flag', r => { r.part.final = true; }, 'schema'],
  ['invalid part timing', r => { r.part.time.end = -1; }, 'schema'],
]) test(`synthetic source shape refuses ${name}`, () => {
  const record = structuredClone(cases.records.final); change(record);
  const actual = inspect([record]);
  assert.deepEqual(actual, { state: 'rejected', reason });
  assert.doesNotMatch(JSON.stringify(actual), /PRIVATE|candidate/);
});
for (const badAttempt of [undefined, {}, { id: '', sessionId: 'ses_fixture' }, { id: 'attempt', sessionId: 'ses_OTHER' }]) {
  test(`capture requires an explicit matching attempt envelope ${JSON.stringify(badAttempt)}`, () => {
    assert.deepEqual(inspect([cases.records.final], { attempt: badAttempt }), { state: 'rejected', reason: 'session' });
  });
}
test('same native session and message IDs remain scoped to independent attempt envelopes', () => {
  for (const id of ['attempt-a', 'attempt-b', 'attempt-a']) {
    const current = { ...attempt, id };
    assert.deepEqual(inspect([cases.records.final], { attempt: current }), candidate('candidate 🙂', current));
  }
});
test('a repeated part identity is ambiguous, even if its text looks valid', () => {
  assert.deepEqual(inspect([cases.records.final, cases.records.final]), { state: 'rejected', reason: 'identity' });
});
test('tool identity is message-scoped and duplicate tool outcomes refuse', () => {
  const one = structuredClone(cases.records.tool), two = structuredClone(one);
  two.part.partID = 'prt_second_tool';
  assert.deepEqual(inspect([one, two, cases.records.final]), { state: 'rejected', reason: 'identity' });
  two.part.messageID = 'msg_second_tool';
  assert.deepEqual(inspect([one, two, cases.records.final]), candidate());
});
for (const [name, change] of [
  ['unknown tool status', r => { r.part.state.status = 'running'; }],
  ['error payload on completed tool', r => { r.part.state.error = 'PRIVATE_ERROR'; }],
  ['missing completed output', r => { delete r.part.state.output; }],
  ['wrong tool input shape', r => { r.part.state.input = []; }],
]) test(`tool source shape refuses ${name}`, () => {
  const tool = structuredClone(cases.records.tool); change(tool);
  assert.deepEqual(inspect([tool, cases.records.final]), { state: 'rejected', reason: 'schema' });
});
test('failed tool output is never rescued by later text or by a completed tool record', () => {
  assert.deepEqual(inspect(recordsFor(['deniedTool', 'tool', 'final'])), { state: 'rejected', reason: 'tool-failure' });
});
for (const records of [[], recordsFor(['reasoning']), recordsFor(['tool']), [text('  ')]]) {
  test(`no assistant segment refuses ${JSON.stringify(records.map(r => r.type))}`, () => {
    assert.deepEqual(inspect(records), { state: 'rejected', reason: records.length ? 'empty-final' : 'jsonl' });
  });
}

test('all byte split positions, including inside UTF-8, preserve one complete capture', () => {
  const bytes = encode(recordsFor(['final', 'finalFinish', 'projectedTail']));
  for (let split = 0; split <= bytes.length; split++) {
    assert.deepEqual(inspect([], { chunks: [bytes.subarray(0, split), bytes.subarray(split)] }), candidate('candidate 🙂 plus tail'));
  }
  assert.deepEqual(inspect([], { chunks: [...bytes].map(value => Buffer.from([value])) }), candidate('candidate 🙂 plus tail'));
});
test('source platform CRLF is accepted without changing assistant text', () => {
  const bytes = Buffer.from(encode(recordsFor(['final'])).toString().replaceAll('\n', '\r\n'));
  assert.deepEqual(inspect([], { chunks: [bytes] }), candidate());
});
for (const [name, chunks] of [
  ['malformed JSON', [Buffer.from('PRIVATE_BAD_JSON\n')]],
  ['truncated JSON', [Buffer.concat([encode(recordsFor(['final'])), Buffer.from('{"type":')])]],
  ['missing final LF', [encode(recordsFor(['final'])).subarray(0, -1)]],
  ['blank line', [Buffer.concat([encode(recordsFor(['final'])), Buffer.from('\n')])]],
  ['nonbuffer chunk', ['PRIVATE_STRING']],
  ['nonarray chunks', null],
]) test(`capture refuses ${name} without echoing bytes`, () => {
  const actual = inspect([], { chunks });
  assert.deepEqual(actual, { state: 'rejected', reason: 'jsonl' });
  assert.doesNotMatch(JSON.stringify(actual), /PRIVATE/);
});
for (const invalid of [Buffer.from([0xc3, 0x28]), Buffer.from([0xf0, 0x9f, 0x99]), Buffer.from([0xed, 0xa0, 0x80])]) {
  test(`fatal transcript UTF-8 refuses ${invalid.toString('hex')}`, () => {
    assert.deepEqual(inspect([], { chunks: [invalid, Buffer.from('\n')] }), { state: 'rejected', reason: 'utf8' });
  });
  test(`fatal prompt UTF-8 refuses ${invalid.toString('hex')}`, () => {
    assert.deepEqual(inspectSyntheticOpenCodePromptData(invalid), { state: 'rejected', reason: 'utf8' });
  });
}
for (const literal of cases.literalPromptData) test(`prompt bytes preserve literal ${JSON.stringify(literal.slice(0, 24))}`, () => {
  assert.deepEqual(inspectSyntheticOpenCodePromptData(Buffer.from(literal)), { state: 'data', text: literal });
  assert.deepEqual(inspect([text(literal)]), candidate(literal));
});
test('prompt data has an inclusive 1 MiB byte cap, including multibyte characters', () => {
  const exact = '🙂'.repeat(262_144);
  assert.deepEqual(inspectSyntheticOpenCodePromptData(Buffer.from(exact)), { state: 'data', text: exact });
  assert.deepEqual(inspectSyntheticOpenCodePromptData(Buffer.from(exact + 'x')), { state: 'rejected', reason: 'bounds' });
  assert.deepEqual(inspectSyntheticOpenCodePromptData('PRIVATE_NOT_BUFFER'), { state: 'rejected', reason: 'utf8' });
});
const sizedReasoning = (size, id) => {
  const record = structuredClone(cases.records.reasoning);
  record.part.id = id; record.part.text = '';
  record.part.text = 'x'.repeat(size - Buffer.byteLength(JSON.stringify(record)));
  assert.equal(Buffer.byteLength(JSON.stringify(record)), size);
  return record;
};
test('JSONL record byte cap is inclusive at 64 KiB, excluding the platform line ending', () => {
  assert.deepEqual(inspect([sizedReasoning(65_536, 'prt_sized'), cases.records.final]), candidate());
  assert.deepEqual(inspect([sizedReasoning(65_537, 'prt_sized'), cases.records.final]), { state: 'rejected', reason: 'bounds' });
});
test('complete capture byte cap is inclusive at 1 MiB across input chunks', () => {
  const records = Array.from({ length: 15 }, (_, index) => sizedReasoning(65_535, `prt_large_${index}`));
  const finalBytes = encode(recordsFor(['final'])).length;
  records.push(sizedReasoning(65_535 - finalBytes, 'prt_last_large'), cases.records.final);
  const bytes = encode(records);
  assert.equal(bytes.length, 1_048_576);
  assert.deepEqual(inspect([], { chunks: [bytes] }), candidate());
  assert.deepEqual(inspect([], { chunks: [bytes, Buffer.from('\n')] }), { state: 'rejected', reason: 'bounds' });
});
test('capture record count is inclusive at 4096', () => {
  const records = Array.from({ length: 4095 }, (_, index) => {
    const record = structuredClone(cases.records.reasoning); record.part.id = `prt_count_${index}`; record.part.text = ''; return record;
  });
  records.push(cases.records.final);
  assert.deepEqual(inspect(records), candidate());
  records.unshift({ ...cases.records.reasoning, part: { ...cases.records.reasoning.part, id: 'prt_extra' } });
  assert.deepEqual(inspect(records), { state: 'rejected', reason: 'bounds' });
});
test('candidate segment has an inclusive 64 KiB UTF-8 bound across text records', () => {
  const value = '🙂'.repeat(8192);
  const records = [text(value, 'msg_final', 'prt_a'), text(value, 'msg_final', 'prt_b')];
  assert.deepEqual(inspect(records), candidate(value + value));
  assert.deepEqual(inspect([...records, text('x', 'msg_final', 'prt_c')]), { state: 'rejected', reason: 'bounds' });
});
