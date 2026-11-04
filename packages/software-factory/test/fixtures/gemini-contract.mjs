// TEST ONLY: synthetic source-contract proposal, never a runtime provider adapter.
// Candidate text cannot prove normal completion: both 0.65.0 branches can hide a stop.
// Conservative fixture budgets, not Gemini limits or measured delivery allowances.
const maxBytes = 1_048_576, maxRecordBytes = 65_536, maxRecords = 4096, maxFinalBytes = 65_536;
const utf8 = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
const reject = reason => ({ state: 'rejected', reason });
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const nonempty = value => typeof value === 'string' && value.isWellFormed() && value.trim().length > 0;
const errorShape = value => object(value) && typeof value.type === 'string' && typeof value.message === 'string';
const fields = {
  init: ['session_id', 'model'], message: ['role', 'content', 'delta'],
  tool_use: ['tool_name', 'tool_id', 'parameters'], tool_result: ['tool_id', 'status', 'output', 'error'],
  error: ['severity', 'message'], result: ['status', 'error', 'stats'],
};
function validRecord(record) {
  if (!object(record) || typeof record.type !== 'string' || !Object.hasOwn(fields, record.type)) return false;
  if (typeof record.timestamp !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(record.timestamp)) return false;
  if (Object.keys(record).some(key => !['type', 'timestamp', ...fields[record.type]].includes(key))) return false;
  switch (record.type) {
    case 'init': return nonempty(record.session_id) && nonempty(record.model);
    case 'message': return ['user', 'assistant'].includes(record.role) && typeof record.content === 'string' && record.content.isWellFormed() &&
      (record.role === 'assistant' ? record.delta === true : record.delta === undefined);
    case 'tool_use': return nonempty(record.tool_id) && nonempty(record.tool_name) && object(record.parameters);
    case 'tool_result': return nonempty(record.tool_id) && ['success', 'error'].includes(record.status) &&
      (record.output === undefined || typeof record.output === 'string') && (record.error === undefined || errorShape(record.error));
    case 'error': return ['warning', 'error'].includes(record.severity) && typeof record.message === 'string';
    case 'result': return ['success', 'error'].includes(record.status) &&
      (record.error === undefined || errorShape(record.error)) && (record.stats === undefined || object(record.stats));
  }
}

export function inspectSyntheticGeminiTranscript({ stdout, exitCode, signal = null, expectedSessionId }) {
  if (exitCode !== 0 || signal !== null) return reject('exit');
  if (!Buffer.isBuffer(stdout)) return reject('jsonl');
  if (stdout.length > maxBytes) return reject('bounds');
  if (stdout.length === 0 || stdout.at(-1) !== 10) return reject('jsonl');
  let decoded;
  try { decoded = utf8.decode(stdout); } catch { return reject('utf8'); }
  const lines = decoded.slice(0, -1).split('\n');
  if (lines.length > maxRecords || lines.some(line => Buffer.byteLength(line) > maxRecordBytes)) return reject('bounds');
  let records;
  try { records = lines.map(line => JSON.parse(line)); } catch { return reject('jsonl'); }
  const pending = new Set();
  const seen = new Set();
  let text = '', textBytes = 0, sessionId, ended = false;
  for (const record of records) {
    if (ended) return reject('terminal');
    if (!validRecord(record)) return reject('schema');
    if (record.type === 'init') {
      if (sessionId !== undefined || !nonempty(expectedSessionId) || record.session_id !== expectedSessionId) return reject('session');
      sessionId = record.session_id;
      continue;
    }
    if (sessionId === undefined) return reject('session');
    switch (record.type) {
      case 'tool_use':
        if (seen.has(record.tool_id)) return reject('tool-protocol');
        pending.add(record.tool_id); seen.add(record.tool_id); text = ''; textBytes = 0;
        break;
      case 'tool_result':
        if (!pending.has(record.tool_id) || record.status !== 'success' || record.error !== undefined) return reject('tool-protocol');
        pending.delete(record.tool_id); text = ''; textBytes = 0;
        break;
      case 'message':
        if (record.role === 'assistant' && pending.size === 0) {
          textBytes += Buffer.byteLength(record.content);
          if (textBytes > maxFinalBytes) return reject('bounds');
          text += record.content;
        }
        break;
      case 'error': return reject(record.severity === 'warning' ? 'warning' : 'native-error');
      case 'result':
        if (record.status !== 'success' || record.error !== undefined) return reject('terminal');
        if (pending.size > 0) return reject('tool-protocol');
        ended = true;
        break;
    }
  }
  if (sessionId === undefined) return reject('session');
  if (!ended) return reject('terminal');
  if (!text.trim()) return reject('empty-final');
  return { state: 'candidate', text, sessionId };
}

// Validates only in-memory data. It never creates a Gemini prompt, file, argv or stdin.
export function inspectSyntheticPromptData(bytes) {
  if (!Buffer.isBuffer(bytes)) return reject('utf8');
  if (bytes.length > maxBytes) return reject('bounds');
  try { return { state: 'data', text: utf8.decode(bytes) }; } catch { return reject('utf8'); }
}
