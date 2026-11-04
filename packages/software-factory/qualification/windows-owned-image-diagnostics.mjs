// Public diagnostic wire boundary. Raw native/build output never passes through.
import { cases, limit } from './windows-owned-image.mjs';

export const buildCategories = Object.freeze(['host', 'path', 'existing-build', 'missing-msvc', 'tool-signature',
  'compiler-version', 'source', 'compile', 'build-cap', 'source-changed', 'binary', 'report', 'unexpected']);
const empty = () => ({ category: 'unexpected', code: 'none', source: 'none', line: 0, tool: 'none', condition: 'none' });
const validTool = (category, tool) => category === 'tool-signature'
  ? ['vswhere', 'compiler', 'linker'].includes(tool) : tool === 'none';
const validCondition = (category, condition) => category === 'tool-signature'
  ? ['status-not-valid', 'signer-absent', 'subject-mismatch', 'api-failure', 'command-unavailable',
    'parameter-binding', 'invocation-failure', 'classification-failure', 'nested-command-unavailable',
    'unresolved-command-unavailable', 'command-probe-failure'].includes(condition) : condition === 'none';
const moduleConditions = ['nested-command-unavailable', 'unresolved-command-unavailable', 'command-probe-failure'];
function validModule(value, condition) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== 4 ||
      Object.keys(value).some(key => !['inbox', 'core', 'autoload', 'direct'].includes(key)) ||
      !['present', 'absent', 'unknown'].includes(value.inbox) || !['present', 'absent', 'unknown'].includes(value.core) ||
      !['all', 'qualified', 'none', 'unknown'].includes(value.autoload) ||
      !['imported', 'not-imported', 'unknown'].includes(value.direct)) return false;
  return condition === 'nested-command-unavailable' ? value.direct === 'imported'
    : condition === 'unresolved-command-unavailable' ? value.direct === 'not-imported'
    : condition === 'command-probe-failure' ? value.direct === 'unknown' : true;
}
const validCompiler = (category, code, source, line) => {
  if (code === 'none') return source === 'none' && line === 0;
  if (category !== 'compile' || typeof code !== 'string') return false;
  if (code.length === 7 && /^LNK[1-9][0-9]{3}$/.test(code)) return source === 'none' && line === 0;
  if (code.length !== 5 || !/^C[1-9][0-9]{3}$/.test(code)) return false;
  return source === 'none' ? line === 0 : ['probe', 'shared', 'fixture', 'fixture-dll'].includes(source) &&
    Number.isInteger(line) && line >= 1 && line <= 4096;
};

function validNative(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== 3 ||
      Object.keys(value).some(key => !['exit', 'status', 'stderr'].includes(key)) ||
      !['present', 'absent', 'null'].includes(value.exit) || !['empty', 'nonempty'].includes(value.stderr)) return false;
  if (value.exit !== 'present') return value.status === 'none';
  return Number.isInteger(value.status) && value.status >= -2147483648 && value.status <= 4294967295 &&
    (value.status !== 0 || value.stderr === 'nonempty');
}

function copyNative(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== 3) return null;
  const copy = {};
  for (const key of ['exit', 'status', 'stderr']) {
    const field = Object.getOwnPropertyDescriptor(value, key);
    if (!field || !Object.hasOwn(field, 'value')) return null;
    copy[key] = field.value;
  }
  return validNative(copy) ? copy : null;
}

export function nativeOutcome(result) {
  try {
    if (!result || typeof result !== 'object' || Array.isArray(result)) return null;
    const error = Object.getOwnPropertyDescriptor(result, 'stderr');
    if (!error || !Object.hasOwn(error, 'value') || typeof error.value !== 'string' || Buffer.byteLength(error.value) > limit) return null;
    const stderr = error.value.length ? 'nonempty' : 'empty';
    const exit = Object.getOwnPropertyDescriptor(result, 'exitCode');
    if (!exit) return { exit: 'absent', status: 'none', stderr };
    if (!Object.hasOwn(exit, 'value')) return null;
    if (exit.value === null) return { exit: 'null', status: 'none', stderr };
    const value = { exit: 'present', status: exit.value, stderr };
    return validNative(value) ? value : null;
  } catch { return null; }
}

const refusalReasons = {
  none: ['clear'],
  'survival-create': ['launch-check', 'pipe-check', 'host-check'],
  'survival-ready': ['host-check'],
  probe: ['event-check', 'image-handle-check', 'duplicate-check', 'query-check', 'suspend-check', 'identity-check',
    'continue-check', 'detach-check', 'debugger-check', 'resume-check', 'requested-stop', 'deadline-reached',
    'output-cap', 'child-crash', 'launch-check', 'marker-check', 'exit-check', 'pipe-check', 'handle-check', 'host-check'],
  'owner-interruption': ['owner-interrupted', 'host-check'],
  'output-check': ['pipe-check'],
};
const refusalFields = ['phase', 'reason', 'cleanup', 'survival', 'flush', 'close'];
function copyRefusal(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Reflect.ownKeys(value).length !== refusalFields.length) return null;
  const copy = {};
  for (const key of refusalFields) {
    const field = Object.getOwnPropertyDescriptor(value, key);
    if (!field || !Object.hasOwn(field, 'value')) return null;
    copy[key] = field.value;
  }
  if (typeof copy.phase !== 'string' || !Object.hasOwn(refusalReasons, copy.phase) ||
      !refusalReasons[copy.phase].includes(copy.reason) ||
      ['cleanup', 'survival', 'flush', 'close'].some(key => typeof copy[key] !== 'boolean') ||
      copy.cleanup && copy.survival && copy.flush && copy.close) return null;
  return copy;
}
const validRefusalCase = (value, name) => value.phase === 'owner-interruption' ? name === 'owner-interruption'
  : name !== 'owner-interruption' || ['survival-create', 'survival-ready'].includes(value.phase);

const stopFields = ['Process', 'Stop', 'InitialWait', 'Termination', 'DebugWait', 'EventOwner', 'EventClose', 'Continue',
  'DebugExit', 'FinalWait', 'OutputEof', 'ErrorEof', 'OutputValid', 'ErrorValid'];
const cleanupFields = [...['child', 'control'].flatMap(prefix => stopFields.map(key => prefix + key)),
  'exitQuery', 'exitInactive', 'earlyClear', 'rejectedClear', 'ownedZero', 'countQuery', 'countNonincrease', 'leakedZero',
  'closeCalls', 'closeIdentity', 'closeQuery', 'closed', 'ownedClose', 'mappingClose', 'debugClose', 'hashClose', 'algorithmClose', 'ownerFileClose'];
const closeFields = ['ownedClose', 'mappingClose', 'debugClose', 'hashClose', 'algorithmClose', 'ownerFileClose'];
const notReached = 'not-reached';
function coherentStop(value, prefix) {
  const field = key => value[prefix + key];
  if (typeof field('Process') !== 'boolean' || typeof field('Stop') !== 'boolean') return false;
  if (!field('Process')) return field('Stop') && stopFields.slice(2).every(key => field(key) === notReached);
  if (['InitialWait', 'FinalWait', 'OutputEof', 'ErrorEof', 'OutputValid', 'ErrorValid'].some(key => typeof field(key) !== 'boolean') ||
      field('InitialWait') === false && field('Termination') !== notReached ||
      field('DebugExit') === notReached && ['DebugWait', 'EventOwner', 'EventClose', 'Continue'].some(key => field(key) !== notReached)) return false;
  return field('Stop') === stopFields.slice(2).every(key => field(key) !== false);
}
function copyCleanup(value, refusal, name) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Reflect.ownKeys(value).length !== cleanupFields.length ||
      !refusal || refusal.cleanup !== false) return null;
  const copy = {};
  for (const key of cleanupFields) {
    const field = Object.getOwnPropertyDescriptor(value, key);
    if (!field || !Object.hasOwn(field, 'value') || ![true, false, notReached].includes(field.value)) return null;
    copy[key] = field.value;
  }
  if (!coherentStop(copy, 'child') || !coherentStop(copy, 'control') ||
      ['ownedZero', 'countQuery', 'closeCalls', 'closed'].some(key => typeof copy[key] !== 'boolean') ||
      (copy.childProcess ? typeof copy.exitQuery !== 'boolean' || (copy.exitQuery ? typeof copy.exitInactive !== 'boolean' : copy.exitInactive !== notReached)
        : copy.exitQuery !== notReached || copy.exitInactive !== notReached) ||
      (copy.countQuery ? typeof copy.countNonincrease !== 'boolean'
        : copy.countNonincrease !== notReached) ||
      copy.closeQuery === notReached && copy.closeIdentity !== notReached ||
      copy.closeCalls !== closeFields.every(key => copy[key] !== false) ||
      copy.closed !== (copy.closeCalls && copy.closeIdentity !== false && copy.closeQuery !== false && copy.countQuery)) return null;
  const rejectedCheck = name !== 'stop-resume' && !['clear', 'deadline-reached', 'output-cap', 'child-crash'].includes(refusal.reason) &&
    refusal.phase !== 'output-check' && copy.earlyClear !== notReached;
  if (rejectedCheck ? typeof copy.rejectedClear !== 'boolean' : copy.rejectedClear !== notReached) return null;
  if (refusal.survival && !copy.controlProcess) return null;
  if (name !== 'owner-interruption' && copy.ownerFileClose !== notReached ||
      copy.debugClose !== notReached && (copy.closeIdentity === notReached || copy.closeQuery === notReached)) return null;
  if (['none', 'output-check'].includes(refusal.phase) && (!copy.childProcess || copy.earlyClear === notReached) ||
      ['survival-create', 'survival-ready'].includes(refusal.phase) && (copy.childProcess || copy.earlyClear !== notReached) ||
      refusal.phase !== 'survival-create' && !copy.controlProcess) return null;
  const beforeHandles = copy.childStop && copy.exitQuery !== false && copy.exitInactive !== false && copy.controlStop &&
    copy.earlyClear !== false && copy.rejectedClear !== false && copy.closed;
  if (beforeHandles ? typeof copy.leakedZero !== 'boolean' || copy.leakedZero !== (copy.ownedZero && copy.countNonincrease)
    : copy.leakedZero !== notReached) return null;
  const cleanup = beforeHandles && copy.leakedZero;
  return cleanup === refusal.cleanup ? copy : null;
}

export function parseNativeDiagnostic(result, name) {
  try {
    if (!cases.includes(name) || !result || typeof result !== 'object' || Array.isArray(result)) return null;
    const fields = {};
    for (const key of ['exitCode', 'signal', 'capped', 'timedOut', 'stderr']) {
      const field = Object.getOwnPropertyDescriptor(result, key);
      if (!field || !Object.hasOwn(field, 'value')) return null;
      fields[key] = field.value;
    }
    if (fields.exitCode !== 1 || fields.signal !== null || fields.capped !== false || fields.timedOut !== false ||
        typeof fields.stderr !== 'string' || Buffer.byteLength(fields.stderr) > 512) return null;
    const rows = fields.stderr.replaceAll('\r\n', '\n').split('\n');
    if (![2, 3].includes(rows.length) || rows.at(-1) !== '') return null;
    const match = /^OWNED_IMAGE_REFUSAL\t1\t([a-z0-9-]+)\t([a-z-]+)\t([a-z-]+)\t([01])\t([01])\t([01])\t([01])$/.exec(rows[0]);
    if (!match || match[0] !== rows[0] || match[1] !== name) return null;
    const [, , phase, reason, cleanup, survival, flush, close] = match;
    const value = copyRefusal({ phase, reason, cleanup: cleanup === '1', survival: survival === '1', flush: flush === '1', close: close === '1' });
    if (!value || !validRefusalCase(value, name)) return null;
    if (rows.length === 2) return { refusal: value, cleanup: null };
    const row = rows[1].split('\t');
    if (row.length !== cleanupFields.length + 3 || row[0] !== 'OWNED_IMAGE_CLEANUP' || row[1] !== '1' || row[2] !== name ||
        row.slice(3).some(field => !['0', '1', 'n'].includes(field))) return null;
    const cleanupValue = Object.fromEntries(cleanupFields.map((key, i) => [key, row[i + 3] === 'n' ? notReached : row[i + 3] === '1']));
    const cleanupValueCopy = copyCleanup(cleanupValue, value, name);
    return cleanupValueCopy ? { refusal: value, cleanup: cleanupValueCopy } : null;
  } catch { return null; }
}
export const parseNativeRefusal = (result, name) => parseNativeDiagnostic(result, name)?.refusal ?? null;
export const parseNativeCleanup = (result, name) => parseNativeDiagnostic(result, name)?.cleanup ?? null;

export function parseBuildDiagnostic(text) {
  if (typeof text !== 'string' || Buffer.byteLength(text) > 512) return empty();
  const match = /^OWNED_IMAGE_BUILD\t3\t([a-z-]+)\t(none|C[1-9][0-9]{3}|LNK[1-9][0-9]{3})\t(none|probe|shared|fixture|fixture-dll)\t(0|[1-9][0-9]{0,3})\t(none|vswhere|compiler|linker)\t(none|status-not-valid|signer-absent|subject-mismatch|api-failure|command-unavailable|parameter-binding|invocation-failure|classification-failure|nested-command-unavailable|unresolved-command-unavailable|command-probe-failure)\r?\n$/.exec(text);
  if (!match || match[0] !== text || !buildCategories.includes(match[1])) return empty();
  const [, category, code, source, number, tool, condition] = match;
  const line = Number(number);
  return validCompiler(category, code, source, line) && validTool(category, tool) && validCondition(category, condition)
    ? { category, code, source, line, tool, condition } : empty();
}

export function parseBuildObservation(text) {
  if (typeof text !== 'string' || Buffer.byteLength(text) > 512) return empty();
  const lines = text.replaceAll('\r\n', '\n').split('\n');
  if (lines.at(-1) !== '' || ![2, 3].includes(lines.length)) return empty();
  const result = parseBuildDiagnostic(lines[0] + '\n');
  if (lines.length === 2) return moduleConditions.includes(result.condition) ? empty() : result;
  const match = /^OWNED_IMAGE_MODULE\t1\t(present|absent|unknown)\t(present|absent|unknown)\t(all|qualified|none|unknown)\t(imported|not-imported|unknown)$/.exec(lines[1]);
  if (!match || match[0] !== lines[1] || result.category !== 'tool-signature') return empty();
  const [, inbox, core, autoload, direct] = match;
  const module = { inbox, core, autoload, direct };
  return validModule(module, result.condition) ? { ...result, module } : empty();
}

const unexpected = 'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0 tool=none condition=none\n';
const phaseCategories = {
  host: ['host', 'unexpected'],
  build: [...buildCategories, 'launch', 'timeout', 'cap', 'interrupted'],
  pin: ['pin', 'interrupted', 'unexpected'],
  case: ['native', 'receipt', 'cleanup', 'timeout', 'cap', 'signal', 'interrupted', 'unexpected'],
};
export function formatFailure(value) {
  try {
    if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).some(key => !['phase', 'name', 'category', 'code', 'source', 'line', 'tool', 'condition', 'module', 'native', 'refusal', 'cleanupEvidence'].includes(key))) return unexpected;
    const refusalField = Object.getOwnPropertyDescriptor(value, 'refusal');
    if (refusalField ? !Object.hasOwn(refusalField, 'value') : 'refusal' in value) return unexpected;
    const cleanupField = Object.getOwnPropertyDescriptor(value, 'cleanupEvidence');
    if (cleanupField ? !Object.hasOwn(cleanupField, 'value') : 'cleanupEvidence' in value) return unexpected;
    const { phase, category, name = 'none', code = 'none', source = 'none', line = 0, tool = 'none', condition = 'none', module, native, refusal, cleanupEvidence } = value;
    if (typeof phase !== 'string' || typeof category !== 'string' || typeof name !== 'string' ||
      !Object.hasOwn(phaseCategories, phase) || !phaseCategories[phase].includes(category) ||
      (phase === 'case' ? !cases.includes(name) : phase === 'pin' ? name !== 'none' && !cases.includes(name) : name !== 'none') ||
      !validCompiler(category, code, source, line) || code !== 'none' && phase !== 'build' ||
      !validTool(category, tool) || tool !== 'none' && phase !== 'build' ||
      !validCondition(category, condition) || condition !== 'none' && phase !== 'build') return unexpected;
    if (module === undefined ? moduleConditions.includes(condition) :
      phase !== 'build' || category !== 'tool-signature' || !validModule(module, condition)) return unexpected;
    const nativeCopy = native === undefined ? undefined : copyNative(native);
    if (native !== undefined && (phase !== 'case' || category !== 'native' || nativeCopy === null)) return unexpected;
    const refusalCopy = refusal === undefined || refusal === null ? refusal : copyRefusal(refusal);
    if (refusal !== undefined && (phase !== 'case' || category !== 'native' || nativeCopy?.exit !== 'present' ||
        nativeCopy.status !== 1 || refusal !== null && (refusalCopy === null || nativeCopy.stderr !== 'nonempty' ||
        !validRefusalCase(refusalCopy, name)))) return unexpected;
    const cleanupCopy = cleanupEvidence === undefined || cleanupEvidence === null ? cleanupEvidence : copyCleanup(cleanupEvidence, refusalCopy, name);
    if (cleanupEvidence !== undefined && (phase !== 'case' || category !== 'native' || nativeCopy?.exit !== 'present' || nativeCopy.status !== 1 ||
        cleanupEvidence !== null && (cleanupCopy === null || nativeCopy.stderr !== 'nonempty' || !refusalCopy || refusalCopy.cleanup !== false))) return unexpected;
    const extra = module === undefined ? '' : ` inbox=${module.inbox} core=${module.core} autoload=${module.autoload} direct=${module.direct}`;
    const outcome = nativeCopy === undefined ? '' : ` exit=${nativeCopy.exit} status=${nativeCopy.status} stderr=${nativeCopy.stderr}`;
    const refusalText = refusalCopy === undefined ? '' : refusalCopy === null
      ? ' nativePhase=unknown nativeReason=unknown cleanup=unknown survival=unknown flush=unknown close=unknown'
      : ` nativePhase=${refusalCopy.phase} nativeReason=${refusalCopy.reason} cleanup=${refusalCopy.cleanup} survival=${refusalCopy.survival} flush=${refusalCopy.flush} close=${refusalCopy.close}`;
    const cleanupText = cleanupCopy === undefined ? '' : cleanupCopy === null ? ' cleanupEvidence=unknown'
      : cleanupFields.map(key => ` ${key}=${cleanupCopy[key]}`).join('');
    return `Owned image native qualification failed phase=${phase} case=${name} category=${category} code=${code} source=${source} line=${line} tool=${tool} condition=${condition}${extra}${outcome}${refusalText}${cleanupText}\n`;
  } catch { return unexpected; }
}
