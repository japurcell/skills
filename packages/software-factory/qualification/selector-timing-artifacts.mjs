import { createHash } from 'node:crypto';
import { closeSync, constants, fstatSync, lstatSync, mkdirSync, openSync, readFileSync, readSync, readdirSync, realpathSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { hasSelectorCoverage, hasFixtureHostCoverage, limits, validateRecord, validateWorkerClosure } from './selector-timing.mjs';

const names = ['selector-timing.json', 'selector-timing.jsonl'];
const metadataKeys = ['schema','status','sourceSha','runtimeSha256','node','platform','arch','availableParallelism','runtimeOsRelease','runnerImage','runnerImageVersion','fixtureExitCode','clock','attemptClock','cpu','records'];
const refuse = () => { throw new Error('invalid selector timing export'); };
function readBounded(root, name, limit) {
  const fd = openSync(join(root, name), constants.O_RDONLY | constants.O_NOFOLLOW);
  try {
    const before = fstatSync(fd);
    if (!before.isFile() || before.nlink !== 1 || before.size > limit || (before.mode & 0o077) !== 0) refuse();
    const bytes = readFileSync(fd), after = fstatSync(fd);
    if (bytes.length !== before.size || after.size !== before.size || after.mtimeMs !== before.mtimeMs || after.ctimeMs !== before.ctimeMs) refuse();
    return bytes;
  } finally { closeSync(fd); }
}
function validateMetadata(value, context) {
  if (!value || typeof value !== 'object' || Object.keys(value).sort().join() !== [...metadataKeys].sort().join()) refuse();
  if (!context || !/^[a-f0-9]{40}$/.test(context.sourceSha) || !/^[a-f0-9]{64}$/.test(context.runtimeSha256)) refuse();
  if (value.schema !== 3 || !['complete','incomplete'].includes(value.status) || value.sourceSha !== context.sourceSha || value.runtimeSha256 !== context.runtimeSha256 || value.node !== 'v24.22.1' || value.platform !== 'darwin' || value.arch !== 'arm64') refuse();
  if (!Number.isSafeInteger(value.availableParallelism) || value.availableParallelism < 1 || value.availableParallelism > 1024 || !Number.isSafeInteger(value.records) || value.records < 0 || value.records > limits.records * limits.files) refuse();
  for (const key of ['runtimeOsRelease','runnerImage','runnerImageVersion']) if (typeof value[key] !== 'string' || !/^[a-zA-Z0-9._-]{1,64}$/.test(value[key])) refuse();
  if (!Number.isInteger(value.fixtureExitCode) || value.fixtureExitCode < 0 || value.fixtureExitCode > 255 || value.clock !== 'host-monotonic-ms' || value.attemptClock !== 'persisted-utc-wall' || value.cpu !== 'emitting-process-only') refuse();
}
function validateTimeline(records, status) {
  const workers = new Map();
  for (const record of records) {
    validateRecord(record);
    let worker = workers.get(record.workerId);
    if (!worker) { worker = { sequence: 0, bytes:0, spans: new Set(), first: record.stage }; workers.set(record.workerId, worker); }
    worker.bytes += Buffer.byteLength(JSON.stringify(record) + '\n');
    if (worker.bytes > limits.processBytes || record.sequence !== ++worker.sequence || workers.size > limits.files || worker.sequence > limits.records) refuse();
    if (record.phase === 'begin') { if (worker.spans.has(record.spanId)) refuse(); worker.spans.add(record.spanId); }
    if (record.phase === 'end' && !worker.spans.delete(record.spanId)) refuse();
    worker.last = record.stage;
  }
  const closed = validateWorkerClosure(records);
  if (status === 'complete' && (!hasSelectorCoverage(records) || !hasFixtureHostCoverage(records) || !closed || records.some(record => record.disposition === 'incomplete'))) refuse();
}
export function stageSelectorTimingExports(source, destination, context) {
  const root = resolve(source), output = resolve(destination);
  if (realpathSync(root) !== root || realpathSync(dirname(output)) !== dirname(output)) refuse();
  const directory = lstatSync(root);
  if (!directory.isDirectory() || directory.isSymbolicLink() || (directory.mode & 0o077) !== 0 || readdirSync(root).sort().join() !== names.join()) refuse();
  const metadataBytes = readBounded(root, names[0], 4096), timelineBytes = readBounded(root, names[1], limits.totalBytes);
  const metadata = JSON.parse(metadataBytes.toString('utf8'));
  if (metadataBytes.toString('utf8') !== JSON.stringify(metadata) + '\n') refuse();
  validateMetadata(metadata, context);
  const raw = timelineBytes.toString('utf8');
  if (raw && !raw.endsWith('\n')) refuse();
  const records = raw ? raw.slice(0, -1).split('\n').map(line => JSON.parse(line)) : [];
  if (raw !== records.map(record => JSON.stringify(record) + '\n').join('')) refuse();
  if (records.length !== metadata.records) refuse();
  validateTimeline(records, metadata.status);
  const after = lstatSync(root);
  if (after.dev !== directory.dev || after.ino !== directory.ino || realpathSync(root) !== root || readdirSync(root).sort().join() !== names.join()) refuse();
  mkdirSync(output, { mode: 0o700 });
  writeFileSync(join(output, names[0]), metadataBytes, { flag: 'wx', mode: 0o600 });
  writeFileSync(join(output, names[1]), timelineBytes, { flag: 'wx', mode: 0o600 });
}
function runtimeHash() {
  const fd = openSync(process.execPath, 'r');
  try {
    if (fstatSync(fd).size > 536870912) refuse();
    const digest = createHash('sha256'), buffer = Buffer.alloc(1048576);
    for (;;) { const count = readSync(fd, buffer); if (!count) break; digest.update(buffer.subarray(0, count)); }
    return digest.digest('hex');
  } finally { closeSync(fd); }
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 4 || process.version !== 'v24.22.1' || process.platform !== 'darwin' || process.arch !== 'arm64') refuse();
    stageSelectorTimingExports(process.argv[2], process.argv[3], { sourceSha: process.env.GITHUB_SHA, runtimeSha256: runtimeHash() });
  } catch { process.stderr.write('factory selector timing staging: refused\n'); process.exitCode = 1; }
}
