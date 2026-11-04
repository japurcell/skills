// Qualification only. Never imported by production modules.
import { randomUUID } from 'node:crypto';
import { closeSync, constants, lstatSync, mkdtempSync, openSync, readFileSync, readdirSync, realpathSync, writeFileSync, writeSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, join } from 'node:path';
import { getTestContext } from 'node:test';
import registry from './selector-timing-registry.json' with { type: 'json' };

export const limits = Object.freeze({ records: 4096, processBytes: 2097152, files: 128, totalBytes: 16777216, databaseRows: 4096 });
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const stages = new Set(['worker-open', 'worker-close', 'worker-bind', 'worker-close-observed', 'worker-bind-sync', 'worker-close-returned', 'fixture-host', 'case', 'repository', 'setup', 'commit', 'copy', 'source', 'learn', 'notice', 'interrupt', 'result', 'dispose', 'attempt', 'export', 'dequeue', 'complete', 'summary', 'cancel', 'selector']);
const classes = new Set(['none', 'startup/git', 'startup/build', 'fixture-command', 'fake-agent']);
const phases = new Set(['mark', 'begin', 'end', 'attempt.started', 'attempt.settled']);
const dispositions = new Set(['none', 'ok', 'failed', 'incomplete', 'SIGINT', 'SIGTERM', 'SIGKILL', 'other-signal']);
const keys = ['schema','workerId','subjectWorkerId','sequence','monoMs','epochMs','stage','phase','fileId','caseId','spanId','invocationId','attemptId','operationClass','at','wallMs','cpuUserUs','cpuSystemUs','disposition','exitCode'];
const hostCounts = Object.freeze({ 'learning.test.mjs':[2,4], 'learning-extraction-sources.test.mjs':[2,9,3], 'learning-extraction-paths.test.mjs':[5,2], 'learning-extraction-evidence.test.mjs':[3,1,1,2,1,1] });
const now = () => Number(process.hrtime.bigint()) / 1e6;
const fail = () => { throw new Error('invalid qualification timing evidence'); };

export function labels(file, name) {
  const fileId = basename(file ?? '');
  if (!Object.hasOwn(registry, fileId)) return { fileId: '', caseId: '' };
  const index = registry[fileId].indexOf(name);
  return { fileId, caseId: index < 0 ? '' : String(index + 1) };
}
function currentLabels() { const context = getTestContext(); return labels(context?.filePath, context?.name); }
export function validateRecord(record) {
  if (!record || typeof record !== 'object' || Object.keys(record).sort().join() !== [...keys].sort().join()) fail();
  for (const key of ['workerId','subjectWorkerId','fileId','caseId','spanId','invocationId','attemptId','at']) if (typeof record[key] !== 'string') fail();
  if (record.schema !== 3 || !uuid.test(record.workerId) || !Number.isSafeInteger(record.sequence) || record.sequence < 1 || !stages.has(record.stage) || !phases.has(record.phase) || !classes.has(record.operationClass) || !dispositions.has(record.disposition)) fail();
  const binding = record.stage === 'worker-bind' || record.stage === 'worker-bind-sync';
  const closure = record.stage === 'worker-close-observed' || record.stage === 'worker-close-returned';
  const observation = binding || closure;
  if (observation ? (!uuid.test(record.subjectWorkerId) || record.subjectWorkerId === record.workerId || record.phase !== 'mark') : record.subjectWorkerId !== '') fail();
  if (binding && (record.exitCode !== null || record.disposition !== 'none')) fail();
  if (closure) {
    const signaled = ['SIGINT','SIGTERM','SIGKILL','other-signal'].includes(record.disposition);
    if (record.exitCode === null ? !signaled : (record.exitCode < 0 || record.disposition !== (record.exitCode === 0 ? 'ok' : 'failed'))) fail();
  }
  for (const key of ['monoMs','epochMs','wallMs','cpuUserUs','cpuSystemUs']) if (!Number.isFinite(record[key]) || record[key] < 0) fail();
  for (const key of ['spanId','invocationId','attemptId']) if (record[key] !== '' && !uuid.test(record[key])) fail();
  if (record.fileId !== '' && !Object.hasOwn(registry, record.fileId)) fail();
  if (record.caseId !== '' && (!record.fileId || !/^[1-9]\d*$/.test(record.caseId) || Number(record.caseId) > registry[record.fileId].length)) fail();
  if (record.at !== '' && (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(record.at) || !Number.isFinite(Date.parse(record.at)))) fail();
  const attempt = record.phase === 'attempt.started' || record.phase === 'attempt.settled';
  if (attempt !== (record.stage === 'attempt') || (attempt && (!record.at || !record.invocationId || !record.attemptId || record.operationClass === 'none'))) fail();
  if (record.phase === 'begin' || record.phase === 'end') { if (!record.spanId) fail(); }
  if (record.exitCode !== null && (!Number.isInteger(record.exitCode) || record.exitCode < -1 || record.exitCode > 255)) fail();
  if (observation || record.stage === 'fixture-host') {
    if (record.phase !== 'mark' || record.wallMs !== 0 || record.cpuUserUs !== 0 || record.cpuSystemUs !== 0 || record.spanId !== '' || record.invocationId !== '' || record.attemptId !== '' || record.operationClass !== 'none' || record.at !== '') fail();
  }
  if (record.stage === 'fixture-host' || record.stage === 'worker-bind-sync' || record.stage === 'worker-close-returned') {
    if (!Object.hasOwn(hostCounts, record.fileId) || !record.caseId) fail();
  }
  if (record.stage === 'fixture-host' && (record.exitCode !== null || record.disposition !== 'none')) fail();
  return record;
}
export function createEvidenceRoot() {
  const path = realpathSync(mkdtempSync(join(tmpdir(), 'factory-selector-timing-')));
  const token = randomUUID();
  writeFileSync(join(path, 'owner.json'), JSON.stringify({ schema: 1, token }), { flag: 'wx', mode: 0o600 });
  return { path, token };
}
function owned(root) {
  if (!root || !uuid.test(root.token) || realpathSync(root.path) !== root.path) fail();
  const stat = lstatSync(root.path), owner = lstatSync(join(root.path, 'owner.json'));
  if (!stat.isDirectory() || stat.isSymbolicLink() || !owner.isFile() || owner.isSymbolicLink() || owner.nlink !== 1 || owner.size > 100 || (stat.mode & 0o077) !== 0 || (owner.mode & 0o077) !== 0) fail();
  const data = JSON.parse(readFileSync(join(root.path, 'owner.json'), 'utf8'));
  if (Object.keys(data).sort().join() !== 'schema,token' || data.schema !== 1 || data.token !== root.token) fail();
}
export function createCollector(root, workerId = randomUUID()) {
  owned(root);
  if (!uuid.test(workerId)) fail();
  let fd;
  for (let slot = 0; slot < limits.files; slot++) {
    try { fd = openSync(join(root.path, `${String(slot).padStart(3, '0')}.jsonl`), constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW, 0o600); break; }
    catch (error) { if (error.code !== 'EEXIST') throw error; }
  }
  if (fd === undefined) {
    try { writeFileSync(join(root.path, 'incomplete.json'), '{"status":"incomplete"}\n', { flag: 'wx', mode: 0o600 }); }
    catch (error) { if (error.code !== 'EEXIST') throw error; }
    fail();
  }
  const opened = now(), openedCpu = process.cpuUsage();
  let sequence = 0, bytes = 0, closed = false, incomplete = false;
  const emit = (stage, data = {}) => {
    if (!stages.has(stage) || Object.keys(data).some(key => !keys.includes(key) || ['schema','workerId','sequence','monoMs','stage'].includes(key))) fail();
    if (closed || incomplete) return;
    const record = validateRecord({ schema: 3, workerId, subjectWorkerId: '', sequence: ++sequence, monoMs: now(), epochMs: Date.now(), stage, phase: 'mark', ...currentLabels(), spanId: '', invocationId: '', attemptId: '', operationClass: 'none', at: '', wallMs: 0, cpuUserUs: 0, cpuSystemUs: 0, disposition: 'none', exitCode: null, ...data });
    const line = JSON.stringify(record) + '\n';
    if (sequence >= limits.records || bytes + Buffer.byteLength(line) > limits.processBytes - 1024) {
      incomplete = true;
      const marker = JSON.stringify({ ...record, stage: 'export', phase: 'mark', disposition: 'incomplete' }) + '\n';
      try { writeSync(fd, marker); } catch { /* Missing closure remains visibly incomplete. */ }
      return;
    }
    bytes += Buffer.byteLength(line);
    try { if (writeSync(fd, line) !== Buffer.byteLength(line)) incomplete = true; }
    catch { incomplete = true; }
  };
  return {
    mark: emit,
    begin(stage, data = {}) {
      const start = now(), cpu = process.cpuUsage(), spanId = randomUUID(), context = currentLabels();
      emit(stage, { ...context, ...data, spanId, phase: 'begin' });
      return (disposition = 'ok', extra = {}) => { const delta = process.cpuUsage(cpu); emit(stage, { ...context, ...data, ...extra, spanId, phase: 'end', disposition, wallMs: now() - start, cpuUserUs: delta.user, cpuSystemUs: delta.system }); };
    },
    close() { if (closed) return; const cpu = process.cpuUsage(openedCpu); emit('worker-close', { wallMs: now() - opened, cpuUserUs: cpu.user, cpuSystemUs: cpu.system }); closed = true; closeSync(fd); },
  };
}
export function collectEvidence(root) {
  owned(root);
  const entries = readdirSync(root.path);
  if (entries.length < 2 || entries.length > limits.files + 2) fail();
  const records = []; let total = 0, incomplete = false;
  const workers = new Set();
  for (const name of entries) {
    if (name === 'owner.json') continue;
    if (name === 'incomplete.json') {
      const marker = lstatSync(join(root.path, name));
      if (!marker.isFile() || marker.isSymbolicLink() || marker.nlink !== 1 || marker.size !== 24 || readFileSync(join(root.path, name), 'utf8') !== '{"status":"incomplete"}\n') fail();
      incomplete = true; continue;
    }
    if (!/^\d{3}\.jsonl$/.test(name) || Number(name.slice(0, 3)) >= limits.files) fail();
    const path = join(root.path, name), stat = lstatSync(path);
    if (!stat.isFile() || stat.isSymbolicLink() || stat.nlink !== 1 || stat.size > limits.processBytes || (total += stat.size) > limits.totalBytes) fail();
    const raw = readFileSync(path, 'utf8'); if (!raw.endsWith('\n')) fail();
    const lines = raw.slice(0, -1).split('\n'); if (lines.length > limits.records) fail();
    let sequence = 0, workerId;
    const spans = new Set();
    let firstStage;
    for (const line of lines) {
      const record = validateRecord(JSON.parse(line));
      firstStage ??= record.stage;
      workerId ??= record.workerId;
      if (record.workerId !== workerId || record.sequence !== ++sequence) fail();
      if (record.phase === 'begin') { if (spans.has(record.spanId)) fail(); spans.add(record.spanId); }
      if (record.phase === 'end' && !spans.delete(record.spanId)) fail();
      if (record.disposition === 'incomplete') incomplete = true;
      records.push(record);
    }
    if (workers.has(workerId)) fail();
    workers.add(workerId);
    if (spans.size > 0 || firstStage !== 'worker-open') incomplete = true;
  }
  records.sort((a, b) => a.monoMs - b.monoMs || a.workerId.localeCompare(b.workerId) || a.sequence - b.sequence);
  if (!validateWorkerClosure(records)) incomplete = true;
  return { status: incomplete ? 'incomplete' : 'complete', records };
}

// Parent receipts are valid only for one fresh spawn, with its real exit followed
// by close. They prove this child process closed, not that a descendant tree did.
export function ownedWorkerTiming() {
  const collector = telemetry();
  if (!collector) return undefined;
  const workerId = randomUUID();
  collector.mark('worker-bind', { subjectWorkerId: workerId });
  return {
    workerId,
    observe(child) {
      let spawned = false, exited;
      child.once('spawn', () => { spawned = true; });
      child.once('exit', (code, signal) => { exited = { code, signal }; });
      child.once('close', (code, signal) => {
        const outcomeValid = code === null ? typeof signal === 'string' && signal.length > 0 : Number.isInteger(code) && code >= 0 && code <= 255 && signal === null;
        if (!spawned || !exited || exited.code !== code || exited.signal !== signal || !outcomeValid) {
          collector.mark('export', { disposition: 'incomplete' }); return;
        }
        const disposition = signal === 'SIGINT' || signal === 'SIGTERM' || signal === 'SIGKILL' ? signal : signal ? 'other-signal' : code === 0 ? 'ok' : 'failed';
        collector.mark('worker-close-observed', { subjectWorkerId: workerId, exitCode: code, disposition });
      });
    },
  };
}

export function validateWorkerClosure(records) {
  const workers = new Map(), bindings = new Map();
  for (const record of records) {
    const prior = workers.get(record.workerId);
    if (!prior && record.sequence !== 1) fail();
    if (prior && (record.sequence !== prior.last.sequence + 1 || record.monoMs < prior.last.monoMs)) fail();
    const worker = prior ?? { first: record, last: record, spans: new Set() };
    worker.last = record;
    if (record.phase === 'begin') worker.spans.add(record.spanId);
    if (record.phase === 'end') worker.spans.delete(record.spanId);
    workers.set(record.workerId, worker);
    if (record.stage === 'worker-bind' || record.stage === 'worker-bind-sync') {
      if (bindings.has(record.subjectWorkerId)) fail();
      bindings.set(record.subjectWorkerId, { bind: record });
    }
    if (record.stage === 'worker-close-observed' || record.stage === 'worker-close-returned') {
      const binding = bindings.get(record.subjectWorkerId);
      if (!binding || binding.close || binding.bind.workerId !== record.workerId || binding.bind.sequence >= record.sequence) fail();
      if ((binding.bind.stage === 'worker-bind-sync') !== (record.stage === 'worker-close-returned') || binding.bind.fileId !== record.fileId || binding.bind.caseId !== record.caseId) fail();
      binding.close = record;
    }
  }
  for (const [subject, binding] of bindings) {
    const worker = workers.get(subject);
    if (worker && (worker.first.stage !== 'worker-open' || binding.bind.monoMs > worker.first.monoMs)) fail();
    if (binding.close && (!worker || binding.close.monoMs < worker.last.monoMs)) fail();
    const hosts = records.filter(record => record.workerId === subject && record.stage === 'fixture-host');
    if (hosts.length > 1 || hosts.some(record => record.fileId !== binding.bind.fileId || record.caseId !== binding.bind.caseId)) fail();
    const ancestors = new Set([subject]);
    let parent = binding.bind.workerId;
    while (bindings.has(parent)) {
      if (ancestors.has(parent)) fail();
      ancestors.add(parent); parent = bindings.get(parent).bind.workerId;
    }
  }
  for (const record of records) if (record.stage === 'fixture-host' && !bindings.has(record.workerId)) fail();
  return workers.size > 0 && [...bindings.values()].every(binding => binding.close && (binding.bind.stage !== 'worker-bind-sync' || records.some(record => record.workerId === binding.bind.subjectWorkerId && record.stage === 'fixture-host'))) && [...workers].every(([id, worker]) => worker.first.stage === 'worker-open' && !worker.spans.size &&
    (worker.last.stage === 'worker-close' || bindings.get(id)?.close !== undefined));
}
let singleton;
const fixturePaths = new Map();
export function rememberFixturePath(path) {
  if (telemetry()) fixturePaths.set(realpathSync(path), lstatSync(path));
}
export function fixtureIdentity(path) {
  const identity = fixturePaths.get(path);
  if (!identity) fail();
  return identity;
}
export function telemetry(workerId) {
  if (!process.env.FACTORY_SELECTOR_TIMING_ROOT) return undefined;
  if (!singleton) {
    singleton = createCollector({ path: process.env.FACTORY_SELECTOR_TIMING_ROOT, token: process.env.FACTORY_SELECTOR_TIMING_TOKEN }, workerId);
    singleton.mark('worker-open', labels(process.argv[1]));
    process.once('exit', () => singleton.close());
  }
  return singleton;
}
export function timingSync(stage, callback) {
  const end = telemetry()?.begin(stage);
  try { const value = callback(); end?.(); return value; } catch (error) { end?.('failed'); throw error; }
}
export function hasSelectorCoverage(records) {
  const selected = Object.entries(registry).filter(([file]) => file.startsWith('learning') || (file.startsWith('notification-') && file !== 'notification-selector-order.test.mjs'));
  const ended = new Set(records.filter(record => record.stage === 'case' && record.phase === 'end').map(record => record.fileId + '/' + record.caseId));
  return selected.every(([file, cases]) => cases.every((_, index) => ended.has(file + '/' + String(index + 1)))) &&
    ['startup/git','startup/build','fake-agent'].every(operationClass => records.some(record => record.stage === 'attempt' && record.operationClass === operationClass));
}
export function timingNodeArgs() {
  return process.env.FACTORY_SELECTOR_TIMING_ROOT ? ['--import', new URL('./selector-timing-preload.mjs', import.meta.url).href] : [];
}

export function hasFixtureHostCoverage(records) {
  const hosts = records.filter(record => record.stage === 'fixture-host');
  if (hosts.length !== 36 || new Set(hosts.map(record => record.workerId)).size !== 36) return false;
  let synchronous = 0, asynchronous = 0;
  for (const host of hosts) {
    const binds = records.filter(record => record.subjectWorkerId === host.workerId && ['worker-bind','worker-bind-sync'].includes(record.stage));
    if (binds.length !== 1 || binds[0].fileId !== host.fileId || binds[0].caseId !== host.caseId) return false;
    const bind = binds[0], closeStage = bind.stage === 'worker-bind-sync' ? 'worker-close-returned' : 'worker-close-observed';
    const closes = records.filter(record => record.subjectWorkerId === host.workerId && record.stage === closeStage && record.workerId === bind.workerId);
    if (closes.length !== 1) return false;
    if (bind.stage === 'worker-bind-sync') synchronous++; else {
      asynchronous++; if (host.fileId !== 'learning.test.mjs' || host.caseId !== '2') return false;
    }
  }
  return synchronous === 35 && asynchronous === 1 && Object.entries(hostCounts).every(([file, counts]) => counts.every((count, index) => hosts.filter(host => host.fileId === file && host.caseId === String(index + 1)).length === count));
}
