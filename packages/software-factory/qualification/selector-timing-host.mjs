// Test-only observation for the fixed disposable learning lifecycle host.
import { randomUUID } from 'node:crypto';
import { closeSync, constants, fstatSync, lstatSync, openSync, readSync, realpathSync, writeFileSync } from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { constants as osConstants } from 'node:os';
import { getTestContext } from 'node:test';
import { fixtureIdentity, labels, ownedWorkerTiming, telemetry } from './selector-timing.mjs';

const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const counts = { 'learning.test.mjs':2, 'learning-extraction-sources.test.mjs':3, 'learning-extraction-paths.test.mjs':2, 'learning-extraction-evidence.test.mjs':6 };
const nodeArgs = Object.freeze(['--import', new URL('./selector-timing-host-preload.mjs', import.meta.url).href]);
const launches = new Map(); let total = 0;
const refuse = () => { throw new Error('invalid qualification host evidence'); };
const same = (a, b) => a.dev === b.dev && a.ino === b.ino;
const unchanged = (a, b) => same(a, b) && a.size === b.size && a.mtimeMs === b.mtimeMs && a.ctimeMs === b.ctimeMs && a.mode === b.mode && a.nlink === b.nlink;
function repositoryIdentity(repository, expected) {
  if (typeof repository !== 'string' || realpathSync(repository) !== repository || basename(repository) !== 'repository' || !basename(dirname(repository)).startsWith('factory-repository-')) refuse();
  const identity = lstatSync(repository), common = join(repository, '.git'), git = lstatSync(common);
  if (!identity.isDirectory() || identity.isSymbolicLink() || !git.isDirectory() || git.isSymbolicLink() || realpathSync(common) !== common || (expected && (!same(identity, expected.repository) || !same(git, expected.git)))) refuse();
  return { repository:identity, git };
}
function validContext(context) {
  if (!context || Object.keys(context).sort().join() !== 'caseId,fileId,schema,workerId' || context.schema !== 1 || typeof context.workerId !== 'string' || typeof context.fileId !== 'string' || typeof context.caseId !== 'string' || !uuid.test(context.workerId) || !Object.hasOwn(counts, context.fileId) || !/^[1-9]\d*$/.test(context.caseId) || Number(context.caseId) > counts[context.fileId]) refuse();
  return context;
}
const receiptPath = (repository, workerId) => join(repository, '.git', 'selector-host-' + workerId + '.identity.json');
function readReceipt(repository, context, identity) {
  repositoryIdentity(repository, identity);
  const path = receiptPath(repository, context.workerId), fd = openSync(path, constants.O_RDONLY | constants.O_NOFOLLOW);
  try {
    const before = fstatSync(fd);
    if (!before.isFile() || before.nlink !== 1 || before.size < 1 || before.size > 256 || (before.mode & 0o777) !== 0o600) refuse();
    const buffer = Buffer.alloc(257), count = readSync(fd, buffer, 0, buffer.length, 0);
    const bytes = buffer.subarray(0, count), after = fstatSync(fd), named = lstatSync(path);
    if (!unchanged(before, after) || !unchanged(after, named) || !named.isFile() || named.isSymbolicLink() || bytes.length !== before.size || realpathSync(path) !== path) refuse();
    const value = JSON.parse(bytes.toString('utf8'));
    if (Object.keys(value).join() !== 'schema,workerId,pid' || value.schema !== 1 || value.workerId !== context.workerId || !Number.isSafeInteger(value.pid) || value.pid < 1 || !bytes.equals(Buffer.from(JSON.stringify(value) + '\n'))) refuse();
    repositoryIdentity(repository, identity);
    return value.pid;
  } finally { closeSync(fd); }
}
function incomplete(collector) { try { collector?.mark('export', { disposition:'incomplete' }); } catch { /* Missing closure remains incomplete. */ } }

export function fixtureHostTiming(repository, kind) {
  // Do no fixture filesystem work, including identity lookups, in the default mode.
  if (!process.env.FACTORY_SELECTOR_TIMING_ROOT) return undefined;
  let collector;
  try {
    collector = telemetry();
    if (!['sync','async'].includes(kind)) refuse();
    const path = realpathSync(repository), identity = repositoryIdentity(path), remembered = fixtureIdentity(path);
    if (lstatSync(repository).isSymbolicLink()) refuse();
    if (!same(identity.repository, remembered)) refuse();
    const current = getTestContext(), contextLabels = labels(current?.filePath, current?.name);
    validContext({ schema:1, workerId:randomUUID(), ...contextLabels });
    if (total >= 36 || (launches.get(path) ?? 0) >= 9) refuse();
    const binding = kind === 'async' ? ownedWorkerTiming() : { workerId:randomUUID() };
    const context = Object.freeze({ schema:1, workerId:binding.workerId, ...contextLabels });
    // Exclusive creation in the preload must be fresh for this launch.
    try { lstatSync(receiptPath(path, context.workerId)); refuse(); } catch (error) { if (error.code !== 'ENOENT') throw error; }
    total++; launches.set(path, (launches.get(path) ?? 0) + 1);
    if (kind === 'sync') collector.mark('worker-bind-sync', { ...contextLabels, subjectWorkerId:context.workerId });
    let used = false;
    if (kind === 'async') return Object.freeze({ kind, nodeArgs, context, observe(child) {
      try { if (used) refuse(); used = true; if (realpathSync(repository) !== path || lstatSync(repository).isSymbolicLink()) refuse(); repositoryIdentity(path, identity); binding.observe(child); }
      catch { incomplete(collector); }
    } });
    return Object.freeze({ kind, nodeArgs, context, returned(outcome) {
      try {
        if (used) refuse(); used = true;
        if (!outcome || Object.keys(outcome).sort().join() !== 'apiError,pid,signal,status' || outcome.apiError !== false || !Number.isSafeInteger(outcome.pid) || outcome.pid < 1) refuse();
        if (realpathSync(repository) !== path || lstatSync(repository).isSymbolicLink()) refuse();
        const { status, signal } = outcome;
        if (status === null ? typeof signal !== 'string' || !Object.hasOwn(osConstants.signals, signal) : !Number.isInteger(status) || status < 0 || status > 255 || signal !== null) refuse();
        if (readReceipt(path, context, identity) !== outcome.pid) refuse();
        const disposition = ['SIGINT','SIGTERM','SIGKILL'].includes(signal) ? signal : signal ? 'other-signal' : status === 0 ? 'ok' : 'failed';
        collector.mark('worker-close-returned', { ...contextLabels, subjectWorkerId:context.workerId, exitCode:status, disposition });
      } catch { incomplete(collector); }
    } });
  } catch { incomplete(collector); return undefined; }
}

// Called only by the fixed --import module. Never forwards descriptor data to invoke.
export function preloadFixtureHostTiming() {
  if (!process.env.FACTORY_SELECTOR_TIMING_ROOT) return;
  let collector;
  try {
    const input = JSON.parse(process.argv[2]), context = validContext(input?.qualificationTiming), repository = realpathSync(input.repository);
    repositoryIdentity(repository);
    if (lstatSync(input.repository).isSymbolicLink() || process.argv[1] !== join(input.repository, '.git', 'host.mjs') || lstatSync(process.argv[1]).isSymbolicLink() || realpathSync(process.argv[1]) !== join(repository, '.git', 'host.mjs')) refuse();
    collector = telemetry(context.workerId);
    collector.mark('fixture-host', { fileId:context.fileId, caseId:context.caseId });
    const bytes = JSON.stringify({ schema:1, workerId:context.workerId, pid:process.pid }) + '\n';
    if (Buffer.byteLength(bytes) > 256) refuse();
    writeFileSync(receiptPath(repository, context.workerId), bytes, { flag:'wx', mode:0o600 });
  } catch { try { collector ??= telemetry(); } catch { /* Parent binding remains unclosed. */ } incomplete(collector); }
}
