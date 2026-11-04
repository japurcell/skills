// Synthetic proposals derived from official 0.65.0 source, not captured native output.
export const sourceCommit = '6006c14a4decfe4b891c6263ad6ad5992e404b5b';
export const sourceRoot = `https://github.com/google-gemini/gemini-cli/blob/${sourceCommit}/`;
export const branches = [
  { name: 'legacy', source: `${sourceRoot}packages/cli/src/nonInteractiveCli.ts#L232-L582` },
  { name: 'agent-session', source: `${sourceRoot}packages/cli/src/nonInteractiveCliAgentSession.ts` },
];
export const timestamp = '2026-10-22T00:00:00.000Z';
export const init = { type: 'init', timestamp, session_id: 'synthetic-session', model: 'synthetic-model' };
export const user = { type: 'message', timestamp, role: 'user', content: 'USER_DECOY' };
export const assistant = content => ({ type: 'message', timestamp, role: 'assistant', content, delta: true });
export const terminal = { type: 'result', timestamp, status: 'success' };
export const toolUse = id => ({ type: 'tool_use', timestamp, tool_name: 'synthetic_read', tool_id: id, parameters: {} });
export const toolResult = id => ({ type: 'tool_result', timestamp, tool_id: id, status: 'success', output: 'TOOL_DECOY' });
export const encode = records => Buffer.from(records.map(record => JSON.stringify(record)).join('\n') + '\n');
export const simple = [init, user, assistant('candidate text'), terminal];
export const afterTools = [
  init, user, assistant('EARLIER_ASSISTANT_DECOY'), toolUse('a'), toolUse('b'),
  assistant('IN_FLIGHT_DECOY'), toolResult('b'), toolResult('a'),
  assistant('final '), assistant('candidate'), terminal,
];

export const toolRejections = [
  { name: 'pending tool cannot reuse earlier assistant text', records: [init, assistant('EARLIER'), toolUse('a'), terminal] },
  { name: 'foreign result cannot satisfy a tool request', records: [init, toolUse('a'), toolResult('b'), assistant('WRONG'), terminal] },
  { name: 'duplicate request ID is ambiguous', records: [init, toolUse('a'), toolUse('a'), toolResult('a'), assistant('WRONG'), terminal] },
  { name: 'duplicate result is ambiguous', records: [init, toolUse('a'), toolResult('a'), toolResult('a'), assistant('WRONG'), terminal] },
  { name: 'tool failure overrides later final text', records: [init, toolUse('a'), { ...toolResult('a'), status: 'error', error: { type: 'permission_denied', message: 'PRIVATE_DENIAL' } }, assistant('WRONG'), terminal] },
  { name: 'STOP_EXECUTION overrides terminal success', records: [init, toolUse('a'), { ...toolResult('a'), status: 'error', error: { type: 'stop_execution', message: 'PRIVATE_HOOK_STOP' } }, terminal] },
  { name: 'error payload contradicts a successful tool status', records: [init, toolUse('a'), { ...toolResult('a'), error: { type: 'stop_execution', message: 'PRIVATE_STOP' } }, assistant('WRONG'), terminal] },
];

const warning = message => ({ type: 'error', timestamp, severity: 'warning', message });
export const transcriptRejections = [
  { name: 'missing terminal', records: [init, assistant('PRIVATE_PARTIAL')], reason: 'terminal' },
  { name: 'duplicate terminal', records: [...simple, terminal], reason: 'terminal' },
  { name: 'post-terminal assistant', records: [...simple, assistant('PRIVATE_LATE')], reason: 'terminal' },
  { name: 'error terminal', records: [init, assistant('PRIVATE_PARTIAL'), { ...terminal, status: 'error' }], reason: 'terminal' },
  { name: 'terminal error contradicts success', records: [init, assistant('PRIVATE_PARTIAL'), { ...terminal, error: { type: 'INVALID_STREAM', message: 'PRIVATE_ERROR' } }], reason: 'terminal' },
  { name: 'error severity event', records: [init, { type: 'error', timestamp, severity: 'error', message: 'PRIVATE_ERROR' }, assistant('WRONG'), terminal], reason: 'native-error' },
  { name: 'warning conservatively unresolved', records: [init, warning('PRIVATE_WARNING'), assistant('WRONG'), terminal], reason: 'warning' },
  { name: 'hook block warning overrides success', records: [init, warning('Agent execution blocked: PRIVATE_HOOK_BLOCK'), assistant('WRONG'), terminal], reason: 'warning' },
  { name: 'empty final cannot reuse user data', records: [init, user, terminal], reason: 'empty-final' },
  { name: 'whitespace final', records: [init, assistant(' \t\n'), terminal], reason: 'empty-final' },
  { name: 'no final after tool phase', records: [init, assistant('EARLIER'), toolUse('a'), toolResult('a'), terminal], reason: 'empty-final' },
  { name: 'missing init', records: [assistant('WRONG'), terminal], reason: 'session' },
  { name: 'mismatched init session', records: [{ ...init, session_id: 'foreign-session' }, assistant('WRONG'), terminal], reason: 'session' },
  { name: 'duplicate init', records: [init, init, assistant('WRONG'), terminal], reason: 'session' },
  { name: 'unknown record type', records: [init, { type: 'unknown', timestamp }, assistant('WRONG'), terminal], reason: 'schema' },
  { name: 'non-delta assistant has no source selection contract', records: [init, { ...assistant('WRONG'), delta: false }, terminal], reason: 'schema' },
  { name: 'injected final response field is unsupported', records: [init, assistant('candidate'), { ...terminal, response: 'PRIVATE_DECOY' }], reason: 'schema' },
  { name: 'foreign per-event session field is unsupported', records: [init, { ...assistant('WRONG'), session_id: 'foreign-session' }, terminal], reason: 'schema' },
  { name: 'missing tool ID', records: [init, { type: 'tool_use', timestamp, tool_name: 'synthetic_read', parameters: {} }, terminal], reason: 'schema' },
  { name: 'non-object record', records: [init, [], terminal], reason: 'schema' },
];

// These source paths can produce the same JSONL: the internal stop reason is not emitted.
// No branch marker or completion-reason field is invented to distinguish them.
export const indistinguishableEndings = [
  { origin: 'ordinary completion', records: [init, user, assistant('candidate text'), terminal] },
  { origin: 'internal stop with no stream-visible marker', records: [init, user, assistant('candidate text'), terminal] },
];
