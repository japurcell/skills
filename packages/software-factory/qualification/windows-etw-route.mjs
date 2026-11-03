// Qualification-only boundary. Private event keys and ambient identities never cross upload.
import { lstatSync, opendirSync, openSync, fstatSync, readSync, closeSync, mkdirSync, writeFileSync, existsSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const routeCases = Object.freeze(['baseline-git', 'baseline-typescript', 'candidate-git',
  'candidate-typescript', 'candidate-nested-cmd', 'candidate-deadline-control', 'candidate-output-control']);
export const receiptLimit = 65536;
const labels = '(?:node|git|typescript|cmd|control|console|other|system|git-dll-[1-5])';
const n = '(?:0|[1-9][0-9]{0,19})';
const patterns = [new RegExp(`^ROUTE\\t1\\t(?:${routeCases.join('|')})$`),
  /^ABI\t120\t280\t112\t448$/, /^OWNED\t1$/, /^SESSION\t37748737\t5\t64$/,
  new RegExp(`^API\\t(?:start|readyQuery|beforeStopQuery|stop|open|process|close)\\t${n}$`),
  /^QUERY\t(?:readyQuery|beforeStopQuery)(?:\t[01]){5}$/,
  /^MODE\t(?:readyQuery|beforeStopQuery)\t[01]\t[01]\t[01]\t(?:none|stop|persist|both)\t[01]$/,
  new RegExp(`^DIRECT\\t${n}$`),
  new RegExp(`^ROOT\\t${n}\\t${n}\\t${n}\\t${n}\\t${n}$`), /^HELD\troot\t1\t1\t1$/,
  new RegExp(`^P\\t[SE]\\t${n}\\t${n}\\t${n}\\t${n}\\t${labels}\\t${n}$`),
  new RegExp(`^I\\t${n}\\t${n}\\t${labels}$`),
  new RegExp(`^COUNTS\\t${n}\\t${n}$`), /^SCHEMA\tverified$/,
  new RegExp(`^STATS\\t${n}\\t${n}\\t${n}$`), new RegExp(`^HEADER\\t${n}\\t${n}\\t${n}$`),
  new RegExp(`^FILE\\t${n}$`), /^CLEANUP\t[01]$/, /^COMPLETE$/,
  /^FAIL\t(?:host|pin|launch|protocol|timeout|schema|callback-cap|graph-cap|decode|stop|loss|header|file-cap|close|cleanup|receipt|operation)$/];
const expectedKind = name => name.endsWith('git') ? 'git' : name.endsWith('typescript') ? 'typescript'
  : name.endsWith('cmd') ? 'cmd' : 'control';
const base = () => ({ observationComplete: false, graphMatched: false, productAdmission: false,
  helperAdmission: 'refused', helperIdentity: 'process-file-identity-unverified',
  namespaceIdentity: 'unverified', imageEvidence: 'expected-pin-path-match-only',
  refusals: ['transient-process-identity-unverified', 'namespace-identity-unverified'],
  outputVerified: false, failures: [], descendants: 0, suspiciousConsoleHosts: 0, diagnostics: emptyDiagnostics() });

// Closed, sparse aggregates only. Ambiguous identities never acquire a graph role.
const diagnosticRoles = ['root', 'direct', 'intended-nested', 'other-descendant', 'unassigned', 'unknown'];
const diagnosticReasons = ['name-mismatch', 'expected-image-zero', 'expected-image-one', 'expected-image-multiple',
  'expected-load-outside-lifetime', 'image-outside-lifetime', 'prohibited-image-class', 'missing-git-import', 'child-start-outside-parent',
  'child-end-at-or-after-root', 'invalid-lifecycle', 'nonroot-outside-bracket', 'direct-exit-mismatch', 'other-nonzero-exit'];
const emptyDiagnostics = () => ({ graph: [], predicates: [], console: [] });
function diagnosticProjection(starts, ends, images, relevant, graph, rootPid, directPid, root, caseName, result, stop) {
  const out = emptyDiagnostics();
  const add = (list, fields) => {
    const key = JSON.stringify(fields);
    const entry = list.find(x => JSON.stringify(Object.fromEntries(Object.entries(x).filter(([k]) => k !== 'count'))) === key);
    if (entry) entry.count++; else list.push({ ...fields, count: 1 });
  };
  const ambiguousCache = new Map();
  const ambiguous = pid => {
    if (ambiguousCache.has(pid)) return ambiguousCache.get(pid);
    const ss = starts.filter(x => x[2] === pid), ee = ends.filter(x => x[2] === pid);
    let invalid = ss.length !== 1 || ee.length !== 1;
    if (!invalid) {
      const [s] = ss, [e] = ee;
      invalid = s[4] === '0' || s[4] !== e[4] || s[3] !== e[3] ||
        starts.some(x => x !== s && x[4] === s[4]) || ends.some(x => x !== e && x[4] === e[4]);
    }
    ambiguousCache.set(pid, invalid);
    return invalid;
  };
  const role = pid => {
    if (ambiguous(pid)) return 'unknown';
    if (!relevant.has(pid)) return 'unassigned';
    const visited = new Set();
    for (let cursor = pid; cursor !== rootPid;) {
      if (visited.has(cursor) || ambiguous(cursor) || !graph.has(cursor)) return 'unknown';
      visited.add(cursor); cursor = graph.get(cursor).s[3];
      if (!relevant.has(cursor)) return 'unknown';
    }
    if (ambiguous(rootPid)) return 'unknown';
    if (pid === rootPid) return 'root';
    if (pid === directPid) return 'direct';
    if (caseName === 'candidate-nested-cmd' && graph.get(pid)?.s[3] === directPid &&
      graph.get(pid).s[6] === 'cmd' && graph.get(pid).e[6] === 'cmd') {
      const candidates = [...relevant].filter(x => x !== rootPid && x !== directPid &&
        graph.get(x)?.s[3] === directPid && graph.get(x).s[6] === 'cmd' && graph.get(x).e[6] === 'cmd');
      return candidates.length === 1 ? 'intended-nested' : 'unknown';
    }
    return 'other-descendant';
  };
  const rootEnd = graph.get(rootPid)?.e[5];
  const release = BigInt(root[4]), observed = BigInt(root[5]);
  for (const s of starts) {
    const pid = s[2], r = role(pid), pair = graph.get(pid), uncertain = r === 'unknown';
    const parent = role(s[3]);
    const parentRole = uncertain ? 'outside-unknown' : parent === 'root' ? 'root' : parent === 'direct' ? 'direct' :
      ['other-descendant', 'intended-nested'].includes(parent) ? 'other-descendant' : 'outside-unknown';
    const expected = pid === rootPid ? 'node' : pid === directPid ? expectedKind(caseName) : 'cmd';
    const processClass = uncertain ? 'other-unknown' : s[6] === 'console' ? 'console' : s[6] === expected ? 'expected' : 'other-unknown';
    const startPhase = uncertain ? 'outside-unknown' : BigInt(s[5]) < release ? 'before-release' :
      BigInt(s[5]) <= observed ? 'release-to-observed' : 'outside-unknown';
    const e = ends.find(x => x[2] === pid);
    const endRelation = uncertain || !e || !rootEnd || ambiguous(rootPid) ? 'missing-unknown' :
      BigInt(e[5]) < BigInt(rootEnd) ? 'before' : 'at-or-after';
    add(out.graph, { role: r, processClass, parentRole, startPhase, endRelation });
    if (s[6] === 'console') add(out.console, { membership: r === 'unknown' ? 'unknown' : r === 'unassigned' ? 'unassigned' : 'graph-member', evidence: 'start' });
    if (!pair || uncertain || r === 'unassigned') continue;
    const end = pair.e, pin = expected;
    const mark = reason => add(out.predicates, { role: r, reason });
    if (s[6] !== pin || end[6] !== pin) mark('name-mismatch');
    const loaded = images.filter(x => x[1] === pid && x[3] === pin);
    mark(loaded.length === 0 ? 'expected-image-zero' : loaded.length === 1 ? 'expected-image-one' : 'expected-image-multiple');
    const outside = x => BigInt(x[2]) < BigInt(s[5]) || BigInt(x[2]) > BigInt(end[5]) ||
      pid === rootPid && (BigInt(x[2]) < BigInt(root[2]) || BigInt(x[2]) > BigInt(root[3]));
    if (loaded.some(outside)) mark('expected-load-outside-lifetime');
    if (images.some(x => x[1] === pid && !(x[3] === pin || x[3] === 'system' || pin === 'git' && /^git-dll-[1-5]$/.test(x[3])))) mark('prohibited-image-class');
    if (pid === directPid && caseName.endsWith('git')) for (let i = 1; i <= 5; i++)
      if (!images.some(x => x[1] === pid && x[3] === `git-dll-${i}`)) mark('missing-git-import');
    if (BigInt(s[5]) >= BigInt(end[5])) mark('invalid-lifecycle');
    if (images.some(x => x[1] === pid && outside(x))) mark('image-outside-lifetime');
    if (pid !== rootPid) {
      const parentPair = graph.get(s[3]);
      if (!parentPair || ambiguous(s[3]) || BigInt(s[5]) <= BigInt(parentPair.s[5]) || BigInt(s[5]) >= BigInt(parentPair.e[5])) mark('child-start-outside-parent');
      if (!rootEnd || ambiguous(rootPid) || BigInt(end[5]) >= BigInt(rootEnd)) mark('child-end-at-or-after-root');
      if (BigInt(s[5]) < release || BigInt(end[5]) > observed) mark('nonroot-outside-bracket');
      if (pid === directPid && (stop ? end[7] === '0' || result?.exitCode !== null && Number(end[7]) !== result?.exitCode : Number(end[7]) !== result?.exitCode)) mark('direct-exit-mismatch');
      if (pid !== directPid && end[7] !== '0') mark('other-nonzero-exit');
    }
  }
  for (const image of images.filter(x => x[3] === 'console')) {
    const r = role(image[1]);
    add(out.console, { membership: r === 'unknown' ? 'unknown' : r === 'unassigned' ? 'unassigned' : 'graph-member', evidence: 'image' });
  }
  return out;
}

export function validateObservation(text, result, caseName) {
  const answer = base();
  const fail = code => { if (!answer.failures.includes(code)) answer.failures.push(code); };
  if (typeof text !== 'string' || Buffer.byteLength(text) > receiptLimit || !routeCases.includes(caseName)) {
    fail('receipt-invalid'); return answer;
  }
  const lines = text.trimEnd().split('\n').map(line => line.replace(/\r$/, ''));
  if (lines.some(line => !patterns.some(pattern => pattern.test(line)))) { fail('receipt-invalid'); return answer; }
  const rows = lines.map(line => line.split('\t'));
  const all = kind => rows.filter(row => row[0] === kind);
  const one = kind => { const list = all(kind); if (list.length !== 1) fail('receipt-incomplete'); return list[0] ?? []; };
  if (one('ROUTE').join('\t') !== `ROUTE\t1\t${caseName}`) fail('case-mismatch');
  const unsigned = (value, max) => BigInt(value) <= max;
  for (const row of rows) {
    if (row[0] === 'P' && (!unsigned(row[2], 4294967295n) || !unsigned(row[3], 4294967295n) ||
      !unsigned(row[4], 18446744073709551615n) || !unsigned(row[5], 9223372036854775807n) || !unsigned(row[7], 4294967295n)) ||
      row[0] === 'I' && (!unsigned(row[1], 4294967295n) || !unsigned(row[2], 9223372036854775807n)) ||
      ['ROOT', 'DIRECT'].includes(row[0]) && (!unsigned(row[1], 4294967295n) || row[1] === '0')) {
      fail('receipt-invalid'); return answer;
    }
  }
  if (all('FAIL').length) {
    if (all('FAIL').length !== 1 || rows.at(-1)[0] !== 'FAIL' || all('COMPLETE').length) fail('receipt-invalid');
    else fail(all('FAIL')[0][1]);
    return answer;
  }
  for (const kind of ['ABI', 'SESSION', 'OWNED', 'HELD', 'SCHEMA', 'COMPLETE']) one(kind);
  if (one('CLEANUP')[1] !== '1') fail('cleanup');
  const apis = all('API');
  for (const name of ['start', 'readyQuery', 'beforeStopQuery', 'stop', 'open', 'process', 'close']) {
    const hits = apis.filter(row => row[1] === name);
    if (hits.length !== 1 || hits[0][2] !== '0') fail(name === 'close' ? 'close' : 'native-api');
  }
  if (apis.length !== 7) fail('native-api');
  for (const name of ['readyQuery', 'beforeStopQuery']) {
    const q = all('QUERY').filter(row => row[1] === name);
    const m = all('MODE').filter(row => row[1] === name);
    if (q.length !== 1 || q[0].slice(2).join('') !== '11111' || m.length !== 1 ||
      m[0].slice(2).join(',') !== '1,1,0,stop,0') fail('session');
  }
  if (all('QUERY').length !== 2 || all('MODE').length !== 2) fail('session');
  const stats = one('STATS'), header = one('HEADER'), file = one('FILE'), counts = one('COUNTS');
  if (stats.slice(1).some(x => x !== '0') || header.slice(2).some(x => x !== '0')) fail('loss');
  if (!header[1] || BigInt(header[1]) <= 0n) fail('header');
  if (!file[1] || BigInt(file[1]) <= 0n || BigInt(file[1]) >= 67108864n) fail('file-cap');
  const starts = all('P').filter(row => row[1] === 'S');
  const ends = all('P').filter(row => row[1] === 'E');
  const images = all('I');
  if (all('P').length > 4096 || images.length > 4096 || !counts[1] || BigInt(counts[1]) > 100000n ||
    Number(counts[2]) !== all('P').length + images.length || Number(counts[1]) < Number(counts[2])) fail('graph-cap');
  const root = one('ROOT');
  if (root.length !== 6) { fail('root-identity'); return answer; }
  const rootPid = root[1], creation = BigInt(root[2]), exit = BigInt(root[3]);
  const release = BigInt(root[4]), observed = BigInt(root[5]);
  if (!(creation > 0n && exit > creation && release >= creation && release <= exit && observed >= exit &&
    BigInt(header[1] ?? 0) >= observed)) fail('root-identity');
  const candidate = !caseName.startsWith('baseline');
  if (!result || result.protocol !== 1 || result.case !== caseName || result.rootPid !== Number(rootPid) ||
    !Number.isSafeInteger(result.childPid) || result.childPid <= 0 || result.childPid > 0xffffffff ||
    result.childPid === Number(rootPid) || result.error !== null ||
    ['spawnObserved', 'exitObserved', 'closeObserved', 'stdoutClosed', 'stderrClosed'].some(key => result[key] !== true) ||
    result.exitCode !== result.closeCode || result.exitSignal !== result.closeSignal ||
    JSON.stringify(result.spawnOptions) !== JSON.stringify({ detached: candidate, windowsHide: candidate,
      shell: false, stdio: ['ignore', 'pipe', 'pipe'] })) fail('launcher-incomplete');
  for (const stream of ['stdout', 'stderr']) {
    const bytes = result?.[`${stream}Bytes`], kept = result?.[`${stream}CapturedBytes`];
    if (!Number.isSafeInteger(bytes) || bytes < 0 || !Number.isSafeInteger(kept) || kept !== Math.min(bytes, 262144))
      fail('output-bound');
  }
  const stop = caseName.includes('deadline') ? 'deadline' : caseName.includes('output') ? 'output-limit' : null;
  const definiteStop = result && (Number.isSafeInteger(result.exitCode) && result.exitCode > 0 &&
    result.exitCode <= 0xffffffff && result.exitSignal === null || result.exitCode === null && result.exitSignal === 'SIGTERM');
  if (stop ? !definiteStop || result?.stop?.reason !== stop || result.stop.killReturned !== true ||
    !Number.isFinite(result.stop.requestedAtMs) || result.stop.requestedAtMs >= 10000 ||
    stop === 'deadline' && (result.stop.requestedAtMs < 500 || result.stdoutBytes !== 15) ||
    stop === 'output-limit' && result.stdoutBytes + result.stderrBytes <= 262144 ||
    result.exitCode === 0 && result.exitSignal === null :
    result?.stop !== null || result.exitCode !== 0 || result.exitSignal !== null) fail('stop-outcome');
  const relevant = new Set([rootPid]);
  for (let changed = true; changed;) {
    changed = false;
    for (const item of starts) if (relevant.has(item[3]) && !relevant.has(item[2])) {
      relevant.add(item[2]); changed = true;
    }
  }
  const directPid = String(result?.childPid);
  if (one('DIRECT')[1] !== directPid) fail('direct-pid');
  if (!relevant.has(directPid)) fail('direct-pid');
  const graph = new Map();
  for (const pid of relevant) {
    const ss = starts.filter(row => row[2] === pid), ee = ends.filter(row => row[2] === pid);
    if (ss.length !== 1 || ee.length !== 1) { fail('lifecycle-ambiguous'); continue; }
    const s = ss[0], e = ee[0];
    if (s[4] === '0' || s[4] !== e[4] || s[3] !== e[3] ||
      starts.some(row => row !== s && row[4] === s[4]) ||
      ends.some(row => row !== e && row[4] === e[4])) fail('identity-key');
    if (BigInt(s[5]) >= BigInt(e[5])) fail('lifetime');
    graph.set(pid, { s, e });
    const pin = pid === rootPid ? 'node' : pid === directPid ? expectedKind(caseName) : 'cmd';
    if (s[6] !== pin || e[6] !== pin) fail('image-name');
    const loaded = images.filter(row => row[1] === pid && row[3] === pin);
    if (loaded.length !== 1 || loaded.some(row => BigInt(row[2]) < BigInt(s[5]) ||
      BigInt(row[2]) > BigInt(e[5]) || pid === rootPid && (BigInt(row[2]) < creation || BigInt(row[2]) > exit)))
      fail('image-unknown');
    for (const image of images.filter(row => row[1] === pid)) {
      if (!(image[3] === pin || image[3] === 'system' || pin === 'git' && /^git-dll-[1-5]$/.test(image[3]))) fail('image-unknown');
      if (BigInt(image[2]) < BigInt(s[5]) || BigInt(image[2]) > BigInt(e[5]) ||
        pid === rootPid && (BigInt(image[2]) < creation || BigInt(image[2]) > exit)) fail('lifetime');
    }
    if (pid === rootPid) {
      if (BigInt(s[5]) < creation || BigInt(s[5]) > exit || BigInt(e[5]) < release || BigInt(e[5]) > observed || e[7] !== '0')
        fail('root-identity');
    } else {
      if (pid === directPid && s[3] !== rootPid) fail('direct-parent');
      if (BigInt(s[5]) < release || BigInt(e[5]) > observed) fail('lifetime');
      if (pid === directPid && (stop ? e[7] === '0' || result?.exitCode !== null && Number(e[7]) !== result?.exitCode : Number(e[7]) !== result?.exitCode)) fail('exit-status');
      if (pid !== directPid && e[7] !== '0') fail('exit-status');
    }
  }
  for (const [pid, { s, e }] of graph) if (pid !== rootPid) {
    const parent = graph.get(s[3]);
    if (!parent || BigInt(s[5]) <= BigInt(parent.s[5]) || BigInt(s[5]) >= BigInt(parent.e[5]) ||
      BigInt(e[5]) >= BigInt(graph.get(rootPid)?.e[5] ?? 0)) fail('parent-lifetime');
  }
  if (caseName.endsWith('git')) for (let index = 1; index <= 5; index++)
    if (!images.some(row => row[1] === directPid && row[3] === `git-dll-${index}`)) fail('image-unknown');
  const nested = [...relevant].filter(pid => pid !== rootPid && pid !== directPid);
  if (caseName === 'candidate-nested-cmd' ? nested.length !== 1 || graph.get(nested[0])?.s[3] !== directPid : nested.length !== 0)
    fail('unexpected-descendant');
  answer.descendants = relevant.size - 1;
  answer.suspiciousConsoleHosts = starts.filter(row => row[6] === 'console').length +
    images.filter(row => row[3] === 'console' && !starts.some(s => s[2] === row[1] && s[6] === 'console')).length;
  if (answer.suspiciousConsoleHosts) fail('console-host-ambiguous');
  answer.diagnostics = diagnosticProjection(starts, ends, images, relevant, graph, rootPid, directPid, root, caseName, result, stop);
  // These conditions diagnose the route. They never certify a held helper or namespace.
  const infrastructure = ['receipt-invalid', 'receipt-incomplete', 'case-mismatch', 'cleanup', 'native-api',
    'close', 'session', 'loss', 'header', 'file-cap', 'graph-cap', 'root-identity', 'launcher-incomplete', 'output-bound'];
  answer.observationComplete = !answer.failures.some(code => infrastructure.includes(code));
  answer.graphMatched = answer.observationComplete && answer.failures.length === 0;
  return answer;
}

export function readBounded(path, maximum = receiptLimit) {
  const before = lstatSync(path);
  if (!before.isFile() || before.isSymbolicLink() || before.size > maximum) throw new Error('bounded-file');
  const fd = openSync(path, 'r');
  try {
    const actual = fstatSync(fd);
    if (!actual.isFile() || actual.size > maximum || actual.dev !== before.dev || actual.ino !== before.ino)
      throw new Error('bounded-file');
    const bytes = Buffer.alloc(maximum + 1);
    let offset = 0, count;
    do { count = readSync(fd, bytes, offset, bytes.length - offset, null); offset += count; }
    while (count && offset < bytes.length);
    if (offset > maximum) throw new Error('bounded-file');
    return bytes.subarray(0, offset).toString('utf8');
  } finally { closeSync(fd); }
}

export function verifyOutput(result, name, cwd, emitted) {
  try {
    const outputs = {};
    for (const stream of ['stdout', 'stderr']) {
      const encoded = result[`${stream}Base64`];
      if (typeof encoded !== 'string' || encoded.length > 349528) return false;
      const bytes = Buffer.from(encoded, 'base64');
      if (bytes.toString('base64') !== encoded || bytes.length !== result[`${stream}CapturedBytes`] || bytes.length > 262144)
        return false;
      outputs[stream] = bytes;
    }
    if (name.endsWith('git')) return result.stdoutBytes === outputs.stdout.length && outputs.stderr.length === 0 &&
      outputs.stdout.equals(Buffer.from(cwd.replaceAll('\\', '/') + '\n'));
    if (name.endsWith('typescript')) return outputs.stdout.length === 0 && outputs.stderr.length === 0 &&
      Buffer.isBuffer(emitted) && emitted.equals(Buffer.from('const result = 42;\nexport { result };\n'));
    if (name.endsWith('cmd')) return outputs.stdout.length === 0 && outputs.stderr.length === 0;
    if (name.includes('deadline')) return outputs.stdout.equals(Buffer.from('deadline-ready\n')) && outputs.stderr.length === 0;
    return outputs.stdout.length === 262144 && outputs.stdout.every(byte => byte === 120) && outputs.stderr.length === 0;
  } catch { return false; }
}

const safeFailure = new Set(['receipt-invalid', 'receipt-incomplete', 'case-mismatch', 'cleanup', 'native-api',
 'close', 'session', 'loss', 'header', 'file-cap', 'graph-cap', 'root-identity', 'launcher-incomplete',
 'output-bound', 'stop-outcome', 'direct-pid', 'lifecycle-ambiguous', 'identity-key', 'lifetime', 'image-name',
 'image-unknown', 'direct-parent', 'exit-status', 'parent-lifetime', 'unexpected-descendant', 'console-host-ambiguous',
 'host', 'pin', 'launch', 'protocol', 'timeout', 'schema', 'callback-cap', 'decode', 'stop', 'file-cap', 'receipt', 'operation']);
function safeDiagnostics(value) {
  const schema = {
    graph: { role: diagnosticRoles, processClass: ['expected', 'console', 'other-unknown'],
      parentRole: ['root', 'direct', 'other-descendant', 'outside-unknown'],
      startPhase: ['before-release', 'release-to-observed', 'outside-unknown'], endRelation: ['before', 'at-or-after', 'missing-unknown'] },
    predicates: { role: diagnosticRoles, reason: diagnosticReasons },
    console: { membership: ['graph-member', 'unassigned', 'unknown'], evidence: ['start', 'image'] }
  };
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join() !== 'console,graph,predicates') throw new Error('receipt-invalid');
  const output = emptyDiagnostics();
  for (const [group, fields] of Object.entries(schema)) {
    const rows = value[group];
    if (!Array.isArray(rows) || rows.length > 4096) throw new Error('receipt-invalid');
    const seen = new Set();
    for (const row of rows) {
      if (!row || typeof row !== 'object' || Array.isArray(row) ||
        Object.keys(row).sort().join() !== [...Object.keys(fields), 'count'].sort().join() ||
        !Number.isSafeInteger(row.count) || row.count < 1 || row.count > 4096 ||
        Object.entries(fields).some(([key, choices]) => !choices.includes(row[key]))) throw new Error('receipt-invalid');
      const normalized = Object.fromEntries(Object.keys(fields).map(key => [key, row[key]]));
      const key = JSON.stringify(normalized);
      if (seen.has(key)) throw new Error('receipt-invalid');
      seen.add(key); output[group].push({ ...normalized, count: row.count });
    }
  }
  return output;
}
export function safeObservation(value) {
  if (!value || value.productAdmission !== false || value.helperAdmission !== 'refused' ||
    value.helperIdentity !== 'process-file-identity-unverified' || value.namespaceIdentity !== 'unverified' ||
    value.imageEvidence !== 'expected-pin-path-match-only' || !Array.isArray(value.failures) ||
    value.failures.some(code => !safeFailure.has(code)) ||
    !Number.isSafeInteger(value.descendants) || value.descendants < 0 || value.descendants > 4096 ||
    !Number.isSafeInteger(value.suspiciousConsoleHosts) || value.suspiciousConsoleHosts < 0 || value.suspiciousConsoleHosts > 8192 ||
    typeof value.observationComplete !== 'boolean' || typeof value.graphMatched !== 'boolean' ||
    value.graphMatched && (!value.observationComplete || value.failures.length)) throw new Error('receipt-invalid');
  return { ...base(), observationComplete: value.observationComplete, graphMatched: value.graphMatched,
    outputVerified: value.outputVerified === true, failures: [...new Set(value.failures)], descendants: value.descendants,
    suspiciousConsoleHosts: value.suspiciousConsoleHosts, diagnostics: safeDiagnostics(value.diagnostics) };
}

export function prepareUpload(evidence) {
  const upload = join(evidence, 'upload');
  rmSync(upload, { recursive: true, force: true });
  const source = JSON.parse(readBounded(join(evidence, 'qualification.json')));
  if (source.rawEtl !== 'removed-after-offline-parse' || source.cleanupUncertain !== false ||
    !Array.isArray(source.cases) || source.cases.length > 7) throw new Error('cleanup');
  for (const name of routeCases) if (existsSync(join(evidence, 'cases', name, 'trace.etl'))) throw new Error('cleanup');
  const report = { scope: 'T17-Windows-ETW-representative-observation', productAdmission: false,
    status: 'inconclusive', comparison: 'refused', failure: null, rawEtl: 'removed-after-offline-parse', cases: [] };
  if (['host','pin','fixture','bridge','receipt','output','cleanup'].includes(source.failure?.stage) &&
    ['operation-failed','inconclusive'].includes(source.failure?.code))
    report.failure = { stage: source.failure.stage, code: source.failure.code };
  for (const item of source.cases) {
    if (!routeCases.includes(item.name) || report.cases.some(x => x.name === item.name) ||
      existsSync(join(evidence, 'cases', item.name, 'trace.etl'))) throw new Error('receipt-invalid');
    // Revalidate private native and launcher inputs. A forged public summary is never authority.
    const text = readBounded(join(evidence, 'cases', item.name, 'observation.private.tsv'));
    const launcher = join(evidence, 'cases', item.name, 'launcher.private.json');
    const result = existsSync(launcher) ? JSON.parse(readBounded(launcher, 800000)) : null;
    const checked = validateObservation(text, result, item.name);
    if (checked.failures.includes('receipt-invalid') || !text.includes('CLEANUP\t1\n') ||
      text.includes('FAIL\ttimeout\n') || result?.stop?.reason === 'guard' || result?.error === 'output-timeout')
      throw new Error('receipt-invalid');
    if (result) {
      const spec = JSON.parse(readBounded(join(evidence, 'cases', item.name, 'spec.private.json')));
      const emittedPath = join(evidence, 'cases', item.name, 'work', 'out', 'input.js');
      const emitted = item.name.endsWith('typescript') && existsSync(emittedPath) ? Buffer.from(readBounded(emittedPath, 262144)) : undefined;
      checked.outputVerified = spec.case === item.name && verifyOutput(result, item.name, spec.cwd, emitted);
      if (item.name.endsWith('typescript') && existsSync(emittedPath)) {
        const directory = opendirSync(join(evidence, 'cases', item.name, 'work', 'out'));
        try { const first = directory.readSync(); if (first?.name !== 'input.js' || !first.isFile() || directory.readSync()) checked.outputVerified = false; }
        finally { directory.closeSync(); }
      }
      if (!checked.outputVerified) checked.graphMatched = false;
    }
    report.cases.push({ name: item.name, ...safeObservation(checked) });
  }
  if (report.cases.length === 7 && report.cases.every(item => item.observationComplete)) report.status = 'observation-complete';
  else if (report.cases.some(item => item.observationComplete)) report.status = 'route-refused';
  if (report.cases.length === 7 && report.cases.every(item => item.graphMatched && item.outputVerified)) report.comparison = 'matched';
  const native = report.cases.map(item => ['CASE', item.name, item.observationComplete ? '1' : '0',
    item.graphMatched ? '1' : '0', item.descendants, item.suspiciousConsoleHosts,
    'event-only', 'process-file-identity-unverified', 'namespace-unverified', 'refused'].join('\t')).join('\n') + '\n';
  const encoded = JSON.stringify(report, null, 2) + '\n';
  if (Buffer.byteLength(native) > receiptLimit || Buffer.byteLength(encoded) > receiptLimit) throw new Error('receipt-invalid');
  mkdirSync(upload, { recursive: false });
  writeFileSync(join(upload, 'qualification.json'), encoded, { flag: 'wx' });
  writeFileSync(join(upload, 'native.tsv'), native, { flag: 'wx' });
  return report;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv[2] !== '--prepare-artifacts') throw new Error('protocol');
    prepareUpload(resolve(process.env.WINDOWS_ETW_ROUTE_EVIDENCE ?? 'windows-etw-route-evidence'));
  } catch { process.stderr.write('ETW route artifact preparation failed\n'); process.exitCode = 1; }
}
