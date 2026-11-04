// TEST ONLY: synthetic pinned-source contracts, never a production provider adapter.
// No JSONL execution-success record exists. Candidate text always has unknown terminal evidence.
// Local fixture budgets, not measured OpenCode limits or native delivery allowances.
const maxBytes = 1_048_576, maxRecordBytes = 65_536, maxRecords = 4096, maxCandidateBytes = 65_536;
const utf8 = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
const reject = reason => ({ state: 'rejected', reason });
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const string = value => typeof value === 'string' && value.isWellFormed();
const identity = value => string(value) && value.trim().length > 0;
const number = value => typeof value === 'number' && Number.isFinite(value) && value >= 0;
const fields = (value, required, optional = []) => object(value) && required.every(key => Object.hasOwn(value, key)) &&
  Object.keys(value).every(key => required.includes(key) || optional.includes(key));
const time = value => fields(value, ['start', 'end']) && number(value.start) && number(value.end) && value.end >= value.start;
const tokens = value => fields(value, ['input', 'output', 'reasoning', 'cache']) &&
  ['input', 'output', 'reasoning'].every(key => number(value[key])) && fields(value.cache, ['read', 'write']) &&
  number(value.cache.read) && number(value.cache.write);
function validRecord(record) {
  if (!object(record) || !identity(record.sessionID) || !number(record.timestamp)) return false;
  if (record.type === 'error') {
    const error = record.error;
    return fields(record, ['type', 'timestamp', 'sessionID', 'error']) &&
      fields(error, ['type', 'message'], ['status', 'response', 'retryAfterMs']) && string(error.type) && string(error.message) &&
      (error.status === undefined || (Number.isInteger(error.status) && error.status >= 100 && error.status <= 599)) &&
      (error.retryAfterMs === undefined || (Number.isInteger(error.retryAfterMs) && error.retryAfterMs >= 0)) &&
      (error.response === undefined || (fields(error.response, ['body']) && string(error.response.body)));
  }
  if (!fields(record, ['type', 'timestamp', 'sessionID', 'part'])) return false;
  const part = record.part;
  if (!object(part) || !identity(part.sessionID) || !identity(part.messageID)) return false;
  const base = ['id', 'sessionID', 'messageID', 'type'];
  if (record.type === 'tool_use') {
    if (!fields(part, ['partID', 'sessionID', 'messageID', 'type', 'id', 'tool', 'state']) ||
      !identity(part.partID) || !identity(part.id) || !identity(part.tool) || part.type !== 'tool') return false;
    const state = part.state;
    if (!object(state) || !object(state.input) || !object(state.metadata) || !time(state.time)) return false;
    return state.status === 'completed'
      ? fields(state, ['status', 'input', 'output', 'title', 'metadata', 'time']) && string(state.output) && string(state.title)
      : state.status === 'error' && fields(state, ['status', 'input', 'error', 'metadata', 'time']) && string(state.error);
  }
  if (!identity(part.id)) return false;
  switch (record.type) {
    case 'text': case 'reasoning':
      return fields(part, [...base, 'text', 'time'], record.type === 'reasoning' ? ['metadata'] : []) &&
        part.type === record.type && string(part.text) && time(part.time) &&
        (part.metadata === undefined || object(part.metadata));
    case 'step_start':
      return fields(part, base, ['snapshot']) && part.type === 'step-start' && (part.snapshot === undefined || string(part.snapshot));
    case 'step_finish':
      return fields(part, [...base, 'reason', 'cost', 'tokens'], ['snapshot']) && part.type === 'step-finish' &&
        ['stop', 'length', 'tool-calls', 'content-filter', 'error', 'unknown'].includes(part.reason) &&
        number(part.cost) && tokens(part.tokens) && (part.snapshot === undefined || string(part.snapshot));
    default: return false;
  }
}

export function inspectSyntheticOpenCodeTranscript({ chunks, attempt, exitCode, signal = null }) {
  if (exitCode !== 0 || signal !== null) return reject('exit');
  if (!object(attempt) || !identity(attempt.id) || !identity(attempt.sessionId)) return reject('session');
  if (!Array.isArray(chunks) || chunks.some(chunk => !Buffer.isBuffer(chunk))) return reject('jsonl');
  let total = 0;
  for (const chunk of chunks) {
    total += chunk.length;
    if (total > maxBytes) return reject('bounds');
  }
  const bytes = Buffer.concat(chunks, total);
  if (bytes.length === 0 || bytes.at(-1) !== 10) return reject('jsonl');
  let decoded;
  try { decoded = utf8.decode(bytes); } catch { return reject('utf8'); }
  const lines = decoded.slice(0, -1).split('\n').map(line => line.endsWith('\r') ? line.slice(0, -1) : line);
  if (lines.length > maxRecords || lines.some(line => Buffer.byteLength(line) > maxRecordBytes)) return reject('bounds');
  let records;
  try { records = lines.map(line => JSON.parse(line)); }
  catch { return reject('jsonl'); }
  let text = '', textBytes = 0, messageId;
  const messages = new Set(), parts = new Set(), tools = new Set();
  for (const record of records) {
    if (!validRecord(record)) return reject('schema');
    if (record.sessionID !== attempt.sessionId) return reject('session');
    if (record.type === 'error') return reject('native-error');
    const part = record.part;
    if (part.sessionID !== attempt.sessionId) return reject('session');
    const partId = record.type === 'tool_use' ? part.partID : part.id;
    if (parts.has(partId)) return reject('identity');
    parts.add(partId);
    if (record.type === 'tool_use') {
      const key = JSON.stringify([part.messageID, part.id]);
      if (tools.has(key)) return reject('identity');
      tools.add(key);
      if (part.state.status !== 'completed') return reject('tool-failure');
    }
    if (['step_start', 'text', 'tool_use'].includes(record.type)) {
      if (part.messageID !== messageId) {
        if (messages.has(part.messageID)) return reject('message-order');
        messages.add(part.messageID); messageId = part.messageID; text = ''; textBytes = 0;
      }
      if (record.type === 'text') {
        textBytes += Buffer.byteLength(part.text);
        if (textBytes > maxCandidateBytes) return reject('bounds');
        text += part.text;
      } else { text = ''; textBytes = 0; }
    }
  }
  if (!text.trim()) return reject('empty-final');
  return { state: 'candidate', text, terminal: 'unknown',
    identity: { attemptId: attempt.id, sessionId: attempt.sessionId, messageId } };
}

// In-memory data seam only: no prompt construction, file reads, argv, stdin or native delivery.
export function inspectSyntheticOpenCodePromptData(bytes) {
  if (!Buffer.isBuffer(bytes)) return reject('utf8');
  if (bytes.length > maxBytes) return reject('bounds');
  try { return { state: 'data', text: utf8.decode(bytes) }; } catch { return reject('utf8'); }
}
