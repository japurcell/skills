// Qualification only. Native observations never admit a product/helper launch.
import { lstatSync, openSync, fstatSync, readSync, closeSync, mkdirSync, writeFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const cases = Object.freeze(['positive', 'positive-repeat', ...Array.from({ length: 7 }, (_, i) => `positive-repeat-${i + 2}`),
  'wrong-hash', 'different-file-id', 'different-image', 'path-replacement', 'ancestor-replacement', 'alias-replacement',
  'stop-created', 'stop-suspended', 'stop-validated', 'stop-continued', 'stop-detached', 'stop-resume',
  'fail-event', 'fail-image-handle', 'fail-duplicate', 'fail-query', 'fail-suspend', 'fail-continue',
  'fail-detach', 'fail-postcondition', 'fail-resume', 'deadline', 'output-limit', 'crash', 'owner-interruption']);
export const limit = 65536;
const failures = ['none', 'event', 'image-handle', 'duplicate', 'query', 'suspend', 'identity', 'continue', 'detach',
  'postcondition', 'resume', 'stop', 'deadline', 'output-limit', 'crash', 'owner-loss', 'launch', 'marker', 'exit', 'pipe', 'handle', 'host'];
const expectedFailure = (name, mutation) => mutation === 'replaced' || ['wrong-hash', 'different-file-id', 'different-image'].includes(name) ? 'identity'
  : name.startsWith('stop-') ? 'stop' : name.startsWith('fail-') ? name.slice(5)
  : name === 'owner-interruption' ? 'owner-loss' : ['deadline', 'output-limit', 'crash'].includes(name) ? name : 'none';
const base = () => ({ qualified: false, productAdmission: false, helperAdmission: 'refused', rootOfTrust: 'unverified',
  namespaceIdentity: 'unverified', dllIdentity: 'unverified', processClosure: 'unverified', nodeEquivalence: 'unverified',
  failure: 'receipt', cleanup: false });

export function validateNative(text, name) {
  const result = base();
  if (!cases.includes(name) || typeof text !== 'string' || Buffer.byteLength(text) > limit || !text.endsWith('\n')) return result;
  const rows = text.replaceAll('\r\n', '\n').slice(0, -1).split('\n').map(x => x.split('\t'));
  const number = x => /^(?:0|[1-9][0-9]{0,9})$/.test(x) && Number(x) <= 0xffffffff;
  const patterns = {
    OWNED: r => r.length === 3 && r[1] === '1' && r[2] === name,
    MUTATION: r => r.length === 3 && ['file', 'ancestor', 'alias'].includes(r[1]) && ['blocked', 'replaced'].includes(r[2]),
    FIRST: r => r.length === 8 && r.slice(1).every(number),
    SUSPEND: r => r.length === 2 && number(r[1]),
    BARRIER: r => r.length === 3 && ['created', 'suspended', 'validated', 'continued', 'detached'].includes(r[1]) && number(r[2]),
    IDENTITY: r => r.length === 7 && [r[1], r[4]].every(x => /^(?:0|[1-9][0-9]{0,19})$/.test(x) && BigInt(x) <= 18446744073709551615n) &&
      [r[2], r[5]].every(x => /^[a-f0-9]{32}$/.test(x)) && [r[3], r[6]].every(x => /^[a-f0-9]{64}$/.test(x)),
    CONTINUE: r => r.length === 2 && r[1] === '1', DETACH: r => r.length === 2 && r[1] === '1',
    DEBUGGER: r => r.length === 2 && /^[01]$/.test(r[1]), RESUME: r => r.length === 2 && number(r[1]),
    MARKERS: r => r.length === 5 && r.slice(1).every(x => /^[01]$/.test(x)),
    EXIT: r => r.length === 2 && number(r[1]), OUTPUT: r => r.length === 5 && r.slice(1).every(number),
    CONTROL: r => r.length === 3 && r.slice(1).every(x => /^[01]$/.test(x)),
    CLEANUP: r => r.length === 3 && r.slice(1).every(number), HANDLES: r => r.length === 2 && number(r[1]),
    ELAPSED: r => r.length === 2 && number(r[1]), RESULT: r => r.length === 2 && failures.includes(r[1]),
    COMPLETE: r => r.length === 1,
  };
  if (rows.length > 64 || rows.some(r => !Object.hasOwn(patterns, r[0]) || !patterns[r[0]](r))) return result;
  const all = key => rows.filter(r => r[0] === key);
  const one = key => all(key).length === 1 ? all(key)[0] : [];
  const identity = one('IDENTITY');
  const idMatch = identity.length === 7 && identity[1] === identity[4] && identity[2] === identity[5];
  const hashMatch = identity.length === 7 && identity[3] === identity[6];
  const first = one('FIRST');
  if (first.length && (first[1] === '0' || first[2] === '0' || first[1] !== first[3] || first[1] !== first[6] ||
      first[2] !== first[4] || first[2] !== first[7] || first[5] !== '3')) return result;
  for (const key of Object.keys(patterns).filter(x => x !== 'BARRIER')) if (all(key).length > 1) return result;
  const mutation = one('MUTATION');
  const mutationKind = { 'path-replacement': 'file', 'ancestor-replacement': 'ancestor', 'alias-replacement': 'alias' }[name];
  if (mutationKind ? mutation[1] !== mutationKind : mutation.length > 0) return result;
  const barriers = all('BARRIER');
  if (new Set(barriers.map(r => r[1])).size !== barriers.length || barriers.some(r => r[2] !== '0')) return result;
  const canonical = ['OWNED', ...(mutationKind ? ['MUTATION'] : []), 'FIRST', 'BARRIER:created', 'SUSPEND', 'BARRIER:suspended', 'IDENTITY',
    'BARRIER:validated', 'CONTINUE', 'BARRIER:continued', 'DETACH', 'DEBUGGER', 'BARRIER:detached', 'RESUME',
    'MARKERS', 'EXIT', 'OUTPUT', 'CONTROL', 'CLEANUP', 'HANDLES', 'ELAPSED', 'RESULT', 'COMPLETE'];
  const order = rows.map(r => canonical.indexOf(r[0] === 'BARRIER' ? `BARRIER:${r[1]}` : r[0]));
  if (order.some((x, i) => x < 0 || i && x <= order[i - 1])) return result;
  const endpoints = { 'fail-event': 'OWNED', 'fail-suspend': 'BARRIER:created',
    'fail-image-handle': 'BARRIER:suspended', 'fail-duplicate': 'BARRIER:suspended', 'fail-query': 'BARRIER:suspended',
    'wrong-hash': 'IDENTITY', 'different-file-id': 'IDENTITY', 'different-image': 'IDENTITY',
    'fail-continue': 'BARRIER:validated', 'fail-detach': 'BARRIER:continued', 'fail-postcondition': 'DETACH',
    'fail-resume': 'BARRIER:detached', 'owner-interruption': 'BARRIER:created' };
  const endpoint = mutation[2] === 'replaced' ? 'IDENTITY' : endpoints[name] ?? (name.startsWith('stop-') && name !== 'stop-resume' ? `BARRIER:${name.slice(5)}` : 'RESUME');
  const prefix = canonical.slice(0, canonical.indexOf(endpoint) + 1);
  if (prefix.some((key, i) => order[i] !== canonical.indexOf(key))) return result;
  if (order.filter(x => x <= canonical.indexOf('RESUME')).length !== prefix.length) return result;
  if (one('OWNED').length === 0 || one('COMPLETE').length === 0 || rows.at(-1)[0] !== 'COMPLETE' ||
      one('EXIT').length === 0 ||
      one('CLEANUP').slice(1).join(',') !== '1,0' || one('HANDLES')[1] !== '0' ||
      one('CONTROL').slice(1).join(',') !== '1,1' || Number(one('ELAPSED')[1] ?? Infinity) > 10000) return result;
  result.cleanup = true;
  const failure = one('RESULT')[1];
  result.failure = failure ?? 'receipt';
  if (failure !== expectedFailure(name, mutation[2])) return result;
  const exit = one('EXIT')[1];
  if (failure === 'none' ? exit !== '0' : failure === 'crash' ? exit !== '3762438722'
    : failure === 'owner-loss' ? exit === '0' || exit === '259' : exit !== '125') return result;
  if (failure === 'deadline' && Number(one('ELAPSED')[1]) < 500) return result;
  if (one('SUSPEND').length && one('SUSPEND')[1] !== '0' || one('RESUME').length && one('RESUME')[1] !== '1' ||
      one('DEBUGGER').length && one('DEBUGGER')[1] !== '0') return result;
  if (one('RESUME').length && (!one('DETACH').length || !one('DEBUGGER').length || !barriers.some(r => r[1] === 'detached'))) return result;
  if (one('CONTINUE').length && (!idMatch || !hashMatch)) return result;
  if (name === 'wrong-hash' && (!idMatch || hashMatch) ||
      name === 'different-file-id' && (idMatch || !hashMatch) ||
      name === 'different-image' && (idMatch || hashMatch) || mutation[2] === 'replaced' && (idMatch || hashMatch)) return result;
  const output = one('OUTPUT');
  if (output.length !== 5 || output[3] !== '1' || output[4] !== '1' || Number(output[1]) > 1048576 || Number(output[2]) > 1048576) return result;
  if (failure === 'none' || ['deadline', 'output-limit', 'crash'].includes(failure)) {
    for (const key of ['FIRST', 'SUSPEND', 'IDENTITY', 'CONTINUE', 'DETACH', 'DEBUGGER', 'RESUME', 'MARKERS', 'EXIT'])
      if (one(key).length === 0) return result;
    if (barriers.length !== 5 || one('MARKERS').slice(1).join(',') !== '1,1,1,0') return result;
    if (failure === 'none' && (one('EXIT')[1] !== '0' || output[1] !== '3' || output[2] !== '0')) return result;
    if (failure === 'output-limit' && Number(output[1]) <= 262144 ||
        failure !== 'none' && one('EXIT')[1] === '0') return result;
  } else {
    // Refusals before release must not have emitted any native marker or output.
    if (failure !== 'stop' && one('RESUME').length || one('MARKERS').length || output[1] !== '0' || output[2] !== '0') return result;
    const phase = name.startsWith('stop-') ? name.slice(5) : null;
    if (phase === 'resume' && !one('RESUME').length) return result;
    if (phase && phase !== 'resume' && !barriers.some(r => r[1] === phase)) return result;
    if (failure === 'owner-loss' && (!first.length || barriers.length !== 1 || one('RESUME').length)) return result;
  }
  result.qualified = true;
  return result;
}

export function readBounded(path, maximum = limit) {
  const before = lstatSync(path);
  if (!before.isFile() || before.isSymbolicLink() || before.size > maximum) throw new Error('receipt');
  const fd = openSync(path, 'r');
  try {
    const actual = fstatSync(fd);
    if (actual.dev !== before.dev || actual.ino !== before.ino || actual.size > maximum || !actual.isFile()) throw new Error('receipt');
    const bytes = Buffer.alloc(maximum + 1); let size = 0, count;
    do { count = readSync(fd, bytes, size, bytes.length - size, null); size += count; } while (count && size < bytes.length);
    if (size > maximum) throw new Error('receipt');
    const value = bytes.subarray(0, size).toString('utf8');
    if (!Buffer.from(value).equals(bytes.subarray(0, size))) throw new Error('receipt');
    return value;
  } finally { closeSync(fd); }
}

export function prepareUpload(evidence) {
  const root = lstatSync(evidence);
  if (!root.isDirectory() || root.isSymbolicLink()) throw new Error('receipt');
  const source = JSON.parse(readBounded(join(evidence, 'driver.private.json')));
  if (source.protocol !== 1 || source.complete !== true || source.cleanup !== true ||
      source.node !== 'v24.22.1' || source.cases?.length !== cases.length) throw new Error('receipt');
  const results = cases.map((name, i) => {
    const item = source.cases[i];
    if (item.name !== name || item.exitCode !== 0 || item.signal !== null || item.capped !== false || item.timedOut !== false) throw new Error('receipt');
    const checked = validateNative(readBounded(join(evidence, `${name}.private.tsv`)), name);
    if (!checked.qualified || !checked.cleanup) throw new Error('receipt');
    return { name, ...checked };
  });
  const report = { scope: 'T17-Windows-owned-image-canary', protocol: 1, status: 'canary-qualified', productAdmission: false,
    helperAdmission: 'refused', rootOfTrust: 'unverified', namespaceIdentity: 'unverified', dllIdentity: 'unverified',
    processClosure: 'unverified', nodeEquivalence: 'unverified', cases: results };
  const native = results.map(x => `CASE\t${x.name}\t1\t${x.failure}\t1\trefused`).join('\n') + '\n';
  const json = JSON.stringify(report, null, 2) + '\n';
  if (Buffer.byteLength(json) > limit || Buffer.byteLength(native) > limit) throw new Error('receipt');
  const upload = join(evidence, 'upload');
  mkdirSync(upload);
  writeFileSync(join(upload, 'qualification.json'), json, { flag: 'wx' });
  writeFileSync(join(upload, 'native.tsv'), native, { flag: 'wx' });
  if (readdirSync(upload).sort().join(',') !== 'native.tsv,qualification.json') throw new Error('receipt');
  return report;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv[2] !== '--prepare-artifacts' || !process.env.WINDOWS_OWNED_IMAGE_EVIDENCE) throw new Error('protocol');
    prepareUpload(resolve(process.env.WINDOWS_OWNED_IMAGE_EVIDENCE));
  } catch { process.stderr.write('Owned image artifact preparation failed\n'); process.exitCode = 1; }
}
