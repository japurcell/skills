import { preparationIdentity, assertPreparationIdentity } from './workspace.js';
import type { PreparationIdentity } from './workspace.js';
import { redactText } from './redaction.js';
import type { SessionEvent } from './adapters/types.js';
import { createHash, randomUUID } from 'node:crypto';
import { closeSync, existsSync, lstatSync, mkdirSync, openSync, realpathSync, unlinkSync } from 'node:fs';
import { basename, dirname, isAbsolute, join, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { pathToFileURL } from 'node:url';
import { currentOwner, inspectOwner } from './native/process.js';
import { setTimeout as delay } from 'node:timers/promises';
import { initializeSchema, schemaVersion } from './schema.js';
import { validateAdmission } from './accounting.js';
import { assertLocalPlacement } from './placement.js';
import { applyForwardStep, assertForwardIntegrity, assertForwardRuntime, forwardCounts, knownForwardShape } from './schema-forward.js';
import type { ForwardShape } from './schema-forward.js';
import type { Admission } from './accounting.js';
import { assertCleanupId, cleanupBounds, cleanupCursor, cleanupHash, cleanupId, cleanupIdentity, cleanupObject, cleanupOpaque,
  decodeCleanupAttempt, decodeCleanupEvent, decodeCleanupHeader, decodeCleanupInvocation } from './cleanup-read.js';
import type { CleanupAttemptFact, CleanupAttemptRead, CleanupEventRead, CleanupCaptureHeader, CleanupCaptureKey, CleanupCaptureMeasurement, CleanupCapturePage, CleanupInvocationFact, CleanupOpaque, CleanupPage,
  CleanupPageInput, CleanupSnapshot } from './cleanup-read.js';
export type { CleanupAttemptFact, CleanupAttemptRead, CleanupEventRead, CleanupCaptureHeader, CleanupCaptureKey, CleanupCaptureMeasurement, CleanupCapturePage, CleanupInvocationFact, CleanupOpaque, CleanupPage,
  CleanupPageInput, CleanupSnapshot } from './cleanup-read.js';

export interface Owner { host: string; pid: number; start: string | null }
export interface InstalledCompletion {
  version: number; operationId: string; repositoryId: string; claimId: string; selectionDigest: string;
  manifestSha256: string; receiptId: string; receiptSha256: string; receiptIdentity?: string;
  controllerOwner?: Owner; launcherOwner?: Owner; stageIdentity?: string;
  originalInstalledSha256?: string; originalCompletionSha256?: string;
}
export interface ActiveInstalledCompletion {
  kind: 'install.completed' | 'upgrade.completed'; completion: InstalledCompletion;
  repositoryId: string; release: string;
}
export type CleanupOperationEvent = { status: 'missing' | 'ambiguous' }
  | { status: 'opaque'; cursor: string; reason: 'invalid-type' | 'oversized' | 'malformed' | 'unknown-format' }
  | { status: 'known'; cursor: string; kind: string; sha256: string; data: Record<string, unknown> };
export type CleanupRecoveryClaim = { status: 'opaque'; id: string | null }
  | { status: 'known'; id: string; kind: Claim['kind']; operationId: string | null;
      maintenanceKind: MaintenanceKind | null; phase: MaintenancePhase | null; backupId: string | null; stagePath: string | null };
export type CleanupActivityEvidence = { status: 'clear' }
  | { status: 'blocked'; source: 'attempt' | 'invocation'; id: string | null; cursor: string };
export interface CleanupOperationEvidence {
  snapshot: CleanupSnapshot; completion: CleanupOperationEvent; backupBound: CleanupOperationEvent;
  newestOperation: CleanupOperationEvent; newestCompletion: CleanupOperationEvent;
  claims: CleanupRecoveryClaim[]; occupiedAttempts: boolean; activity: CleanupActivityEvidence;
}
export interface DependencyMaintenanceBinding {
  version: 1; bundleRoot: string; originalSha256: string; originalCompletionSha256: string;
  expectedToolchainSha256: string; observedToolchainSha256: string;
  sourceIdentity: string; factoryIdentity: string; toolchainIdentity: string;
  declarationSha256: string; lockSha256: string;
  backupAttempt?: DependencyBackupAttemptBinding | null;
  backup?: VerifiedMaintenanceBackup | null;
  candidateAttempt?: { id: string; binding: DependencyCandidateAttemptBinding | null; events: { cursor: string; sha256: string }[] };
}
export interface DependencyCandidateAttemptBinding {
  identity: string; sha256: string; rootIdentity: string; requestSha256: string;
}
export interface VerifiedMaintenanceBackup {
  id: string; identity: string; sha256: string; bytes: number; countDigest: string; receiptId: string; receiptSha256: string;
}
export interface DependencyBackupAttemptBinding {
  identity: string; sha256: string; rootIdentity: string; operationIdentity: string; directoryIdentity: string; requestSha256: string;
}
export interface Claim {
  id: string; token: string; kind: 'worktree' | 'dashboard' | 'maintenance'; resourceKey: string;
  invocationId: string | null; owner: Owner; endpoint?: { url: string; instanceId: string };
  maintenance?: MaintenanceIntent;
}
export type MaintenanceKind = 'install' | 'upgrade' | 'dependencies' | 'repair' | 'uninstall' | 'cleanup';
export type MaintenancePhase = 'preparing' | 'handoff-ready' | 'modifying' | 'validating';
export interface CandidateBinding { path: string; identity: string; treeDigest: string; receiptId: string; receiptSha256: string }
export interface MaintenanceIntent {
  operationId: string; repositoryId: string; kind: MaintenanceKind; release: string;
  targetReleaseSha256: string | null; selectionDigest: string; artifactDigests: Record<string, string>;
  targetSchema: number; stagePath: string; stageDigest: string | null; stageIdentity: string | null;
  phase: MaintenancePhase; ownedReceiptId: string | null; backupId: string | null;
  ticketNonceHash: string | null; ticketConsumed: boolean;
  candidate: CandidateBinding | null;
  upgradeIntentSha256?: string;
  upgradeReceipt?: { id: string; sha256: string; identity: string };
  activeLauncher?: Owner;
  dependencies?: DependencyMaintenanceBinding;
  forward?: { sourceShape: ForwardShape; currentShape: ForwardShape; sourceRelease: string; sourceIdentity: string; backup: VerifiedMaintenanceBackup | null };
}
export interface MaintenanceHandle { operationId: string; claimId: string; token: string; repositoryId: string; commonDir: string }
interface Run { id: string; additionalLimit: number; codeLimit: number; formatLimit: number }
interface Worktree { id: string; path: string; registration: string; preparation?: { identity: PreparationIdentity; invocationId: string; claimId: string } }
export interface Invocation { id: string; runId: string; worktreeId: string; stage: 'starting' | 'running' | 'shutting_down' | 'finalized'; outcome: string | null; cleanup?: 'complete' | 'unknown'; metadata?: object; successNoticePlanned?: boolean }
export interface Attempt extends Admission {
  runId: string; operationId: string; fingerprint: string;
  launch: 'admitted' | 'started' | 'not_started' | 'unknown'; outcome: 'succeeded' | 'failed' | 'needs_input' | 'interrupted' | null;
  quiescent: boolean; owner: Owner | null; evidence: string | null;
  cleanupBasis?: 'operator_confirmed';
  agent?: { inputsCaptureId:string; resultCaptureId:string; outputCaptureId:string; adapter:string; sessionMode:'fresh'|'reuse'; context:string; reusedAttemptId?:string; validator:string|null; validatedResultCaptureId?:string };
}
/** Optional observations remain unknown until the adapter reports actual evidence. */
export interface NativeSession {
  id: string; attemptId: string; invocationId: string; nativeId: string; parentNativeId: string | null;
  lifecycle: SessionEvent['lifecycle'];
  usage: NonNullable<SessionEvent['usage']> | { state: 'unknown' };
  loadedSkills: string[] | { state: 'unknown' };
  inputsCaptureId: string | null; outputCaptureId: string | null; resultCaptureId: string | null;
}
export type CaptureState = 'open' | 'complete' | 'partial' | 'unknown' | 'pruned';
export interface CaptureChunk { sequence: number; text: string }
export interface Clearance { id: string; claimId: string; invocationId?: string; note: string; basis: 'operator_confirmed'; inspection: 'not_live' | 'unknown'; details?: object }
export interface NotificationDelivery {
  id: string; invocationId: string; kind: 'initial'; state: 'submitted' | 'failed' | 'timed_out' | 'unknown';
  reason?: string; cleanup: 'complete' | 'unknown'; visibleDelivery: false;
  issues: { outcome: string; cleanup: 'complete' | 'unknown'; questions: number };
  createdAt: string; updatedAt: string;
}
export interface NotificationPreferences { successNotices: boolean; reminders: boolean; updatedAt: string | null }
export interface NotificationAcknowledgment { id: string; invocationId: string; acknowledgedAt: string }
export interface ReminderGroup {
  id: string; kind: 'reminder'; claimId: string; invocationIds: string[]; count: number; hasMore: boolean;
  state: 'reserved' | NotificationDelivery['state']; reason?: string; cleanup: 'complete' | 'unknown';
  visibleDelivery: false; createdAt: string; updatedAt: string;
}
export class NotificationMetadataError extends Error { constructor(readonly status: 400 | 404, message: string) { super(message); } }
function exactObject(value: unknown, keys: string[]): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value) &&
    Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
}

/** These event projections never forward an unknown body, owner token or operator note. */
function cleanupOperationEvent(rows: Record<string, unknown>[]): CleanupOperationEvent {
  if (!rows.length) return { status: 'missing' };
  if (rows.length !== 1) return { status: 'ambiguous' };
  const row = rows[0]!, cursor = String(row['cursor']); cleanupCursor(cursor);
  const opaque = (reason: 'invalid-type' | 'oversized' | 'malformed' | 'unknown-format'): CleanupOperationEvent => ({ status: 'opaque', cursor, reason });
  if (row['body_type'] !== 'text' || typeof row['kind'] !== 'string') return opaque('invalid-type');
  if (BigInt(String(row['bytes'])) > 8192n) return opaque('oversized');
  if (typeof row['data'] !== 'string') return opaque('invalid-type');
  let data: unknown;
  try { data = JSON.parse(row['data']); } catch { return opaque('malformed'); }
  if (!cleanupObject(data) || !cleanupId(data.at)) return opaque('unknown-format');
  const uuid = (value: unknown) => typeof value === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
  const sha = (value: unknown) => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
  const owner = (value: unknown) => cleanupObject(value) && exactObject(value, ['host','pid','start'])
    && cleanupId(value.host) && Number.isSafeInteger(value.pid) && Number(value.pid) > 0 && cleanupId(value.start);
  const kind = row['kind'];
  let allowed: string[];
  if (kind === 'install.completed' || kind === 'upgrade.completed') {
    allowed = ['version','operationId','repositoryId','claimId','selectionDigest','manifestSha256','receiptId','receiptSha256','controllerOwner','at',
      ...(kind === 'install.completed' ? ['stageIdentity'] : ['receiptIdentity','launcherOwner','originalCompletionSha256','originalInstalledSha256'])];
    if (!exactObject(data, allowed) || data.version !== 1 || ![data.operationId,data.repositoryId,data.claimId,data.receiptId].every(uuid)
      || ![data.selectionDigest,data.manifestSha256,data.receiptSha256].every(sha) || !owner(data.controllerOwner)
      || kind === 'install.completed' && (typeof data.stageIdentity !== 'string' || !/^\d+:\d+$/.test(data.stageIdentity))
      || kind === 'upgrade.completed' && (!owner(data.launcherOwner) || !sha(data.originalCompletionSha256)
        || !sha(data.originalInstalledSha256) || typeof data.receiptIdentity !== 'string' || !/^\d+:\d+$/.test(data.receiptIdentity))) return opaque('unknown-format');
  } else if (kind === 'maintenance.backup_bound') {
    if (!exactObject(data, ['operationId','claimId','backupId','at']) || ![data.operationId,data.claimId,data.backupId].every(uuid)) return opaque('unknown-format');
  } else if (kind === 'maintenance.completed_recovery_inspected') {
    allowed = ['operationId','receiptId','receiptSha256','note','controllerState','controllerLimitation','launcherState','launcherLimitation',
      'originalLauncherState','originalLauncherLimitation','childClosure','operatorConfirmed','at'];
    if (!exactObject(data, allowed) || !uuid(data.operationId) || !uuid(data.receiptId) || !sha(data.receiptSha256)
      || data.childClosure !== 'operator-confirmed-unknown' || data.operatorConfirmed !== true
      || ['controllerState','launcherState','originalLauncherState'].some(key => !['not_live','unknown'].includes(String((data as Record<string, unknown>)[key])))
      || ['note','controllerLimitation','launcherLimitation','originalLauncherLimitation'].some(key => !cleanupId((data as Record<string, unknown>)[key]))) return opaque('unknown-format');
    data = { operationId: data.operationId, receiptId: data.receiptId, receiptSha256: data.receiptSha256, at: data.at };
  } else return opaque('unknown-format');
  return { status: 'known', cursor, kind, sha256: cleanupHash(row['data']), data: data as Record<string, unknown> };
}

function text(value: string, label: string) {
  if (typeof value !== 'string' || Buffer.byteLength(value) < 1 || Buffer.byteLength(value) > 256 || value.includes('\0')) {
    throw new Error(`invalid ${label}: expected 1-256 UTF-8 bytes without NUL`);
  }
  return value;
}

function validateOwner(owner: Owner) {
  text(owner.host, 'owner host');
  if (!Number.isSafeInteger(owner.pid) || owner.pid < 1) throw new Error('invalid owner PID');
  if (owner.start !== null) text(owner.start, 'owner start identity');
}

function increase(current: number, requested: number | undefined) {
  if (requested === undefined) return current;
  if (!Number.isSafeInteger(requested) || requested <= current) throw new Error('explicit limit must increase the current allowance');
  return requested;
}

function paths(commonDir: string, create: boolean) {
  const common = realpathSync(commonDir);
  const directory = join(common, 'factory');
  if (create && !existsSync(directory)) mkdirSync(directory, { mode: 0o700 });
  if (lstatSync(directory).isSymbolicLink() || !lstatSync(directory).isDirectory()) throw new Error('factory storage must be an owned directory, not a symlink');
  // Native qualification records support; placement checks reject unsupported storage before opening it.
  assertLocalPlacement(directory);
  return { directory, database: join(directory, 'history.sqlite'), marker: join(directory, 'bootstrap-incomplete') };
}

function pathAbsent(path: string) {
  try { lstatSync(path); return false; }
  catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return true; throw error; }
}
function assertForwardSidecars(path: string) {
  for (const suffix of ['-wal', '-shm', '-journal']) {
    const sidecar = `${path}${suffix}`;
    if (pathAbsent(sidecar)) continue;
    const file = lstatSync(sidecar, { bigint: true });
    if (!file.isFile() || file.isSymbolicLink() || file.nlink !== 1n || (file.mode & 0o077n) !== 0n)
      throw new Error('forward store sidecar is not private regular storage');
  }
}

function configure(database: DatabaseSync) {
  database.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON');
  if (database.prepare('PRAGMA journal_mode').get()?.['journal_mode'] !== 'wal'
    || database.prepare('PRAGMA synchronous').get()?.['synchronous'] !== 2
    || database.prepare('PRAGMA foreign_keys').get()?.['foreign_keys'] !== 1) throw new Error('required SQLite durability settings unavailable');
}

/** Explicit bootstrap only. Normal open never treats missing/unreadable storage as a new repository. */
export async function initializeRepositoryStore(commonDir: string, options: { release: string }) {
  text(options.release, 'release');
  const location = paths(commonDir, true);
  if (existsSync(location.database)) throw new Error('store already exists; explicit repair required');
  closeSync(openSync(location.marker, 'wx', 0o600));
  closeSync(openSync(location.database, 'wx', 0o600));
  const database = new DatabaseSync(location.database, { timeout: 100 });
  try {
    configure(database);
    initializeSchema(database);
    database.prepare('INSERT INTO repository(id,release,state) VALUES (?,?,?)').run(randomUUID(), options.release, 'ready');
    unlinkSync(location.marker);
    return new RepositoryStore(database);
  } catch (error) {
    database.close();
    throw error; // Preserve incomplete bootstrap and data for explicit recovery.
  }
}

export function openRepositoryStore(commonDir: string) {
  return openStore(commonDir, false);
}

/** Trusted controller path. Ordinary callers still refuse a bootstrap marker. */
export function openMaintenanceStore(commonDir: string) {
  return openStore(commonDir, true);
}

export type CleanupReadStore = Pick<RepositoryStore, 'close' | 'readCleanupSnapshot' | 'pageCleanupInvocationFacts'
  | 'pageCleanupAttemptFacts' | 'pageCleanupCaptureHeaders' | 'measureCleanupCaptures' | 'readCleanupCapture' | 'readCleanupAttempt' | 'readCleanupEvent' | 'readCleanupOperation' | 'readCleanupOperationEvidence'>;

// Only the existing-only opener can establish this identity. Structural copies
// and ordinary writer stores cannot supply authority to the snapshot adapter.
const cleanupSnapshotViews = new WeakMap<object, { common: string; assertIdentity: () => void }>();
export function assertCleanupSnapshotView(store: CleanupReadStore, common: string): void {
  const binding = cleanupSnapshotViews.get(store);
  if (!binding || binding.common !== common) throw new Error('cleanup requires its original existing-only snapshot view');
  binding.assertIdentity();
}

/** Existing-only view. All pages share one read-only SQLite transaction until close(). */
export function openCleanupReadStore(commonDir: string): CleanupReadStore {
  const location = paths(commonDir, false), before = lstatSync(location.database, { bigint: true });
  if (!before.isFile() || before.isSymbolicLink() || before.nlink !== 1n || before.ino === 0n
    || process.platform !== 'win32' && ((before.mode & 0o077n) !== 0n || before.uid !== BigInt(process.getuid!())))
    throw new Error('invalid cleanup store file');
  const assertIdentity = () => {
    const file = lstatSync(location.database, { bigint: true });
    if (!file.isFile() || file.isSymbolicLink() || file.nlink !== 1n || file.dev !== before.dev || file.ino !== before.ino)
      throw new Error('cleanup store identity changed');
    assertForwardSidecars(location.database);
    for (const suffix of ['-wal','-shm','-journal']) {
      const path = `${location.database}${suffix}`;
      if (!pathAbsent(path) && process.platform !== 'win32' && lstatSync(path).uid !== process.getuid!())
        throw new Error('cleanup sidecar owner differs');
    }
  };
  assertIdentity();
  const database = new DatabaseSync(location.database, { readOnly: true, timeout: 100 });
  try {
    database.exec('BEGIN');
    if (knownForwardShape(database) !== 'v7') throw new Error('cleanup requires current schema');
    assertForwardIntegrity(database);
    const store = new RepositoryStore(database);
    const read = <T>(action: () => T) => { assertIdentity(); const result = action(); assertIdentity(); return result; };
    read(() => store.readCleanupSnapshot()); // Establish and validate the WAL endmark before returning the view.
    const view: CleanupReadStore = Object.freeze({
      close: () => { cleanupSnapshotViews.delete(view); database.close(); }, readCleanupSnapshot: () => read(() => store.readCleanupSnapshot()),
      pageCleanupInvocationFacts: (input: CleanupPageInput = {}) => read(() => store.pageCleanupInvocationFacts(input)),
      pageCleanupAttemptFacts: (input: CleanupPageInput = {}) => read(() => store.pageCleanupAttemptFacts(input)),
      pageCleanupCaptureHeaders: (input: CleanupPageInput = {}) => read(() => store.pageCleanupCaptureHeaders(input)),
      measureCleanupCaptures: (keys: CleanupCaptureKey[]) => read(() => store.measureCleanupCaptures(keys)),
      readCleanupCapture: (input: Parameters<RepositoryStore['readCleanupCapture']>[0]) => read(() => store.readCleanupCapture(input)),
      readCleanupAttempt: (input: Parameters<RepositoryStore['readCleanupAttempt']>[0]) => read(() => store.readCleanupAttempt(input)),
      readCleanupEvent: (input: Parameters<RepositoryStore['readCleanupEvent']>[0]) => read(() => store.readCleanupEvent(input)),
      readCleanupOperation: (input: Parameters<RepositoryStore['readCleanupOperation']>[0]) => read(() => store.readCleanupOperation(input)),
      readCleanupOperationEvidence: (input: Parameters<RepositoryStore['readCleanupOperationEvidence']>[0]) => read(() => store.readCleanupOperationEvidence(input)),
    });
    cleanupSnapshotViews.set(view, { common: realpathSync(commonDir), assertIdentity });
    return view;
  } catch (error) { database.close(); throw error; }
}

/** Existing-only historical opener. Never creates, configures, or migrates storage. */
function openExistingMaintenanceStore(commonDir: string, scope: 'forward' | 'current') {
  assertForwardRuntime();
  if (process.platform === 'win32') throw new Error('forward maintenance private ownership is unqualified on Windows');
  const location = paths(commonDir, false);
  if (!pathAbsent(location.marker)) throw new Error('bootstrap marker blocks forward maintenance');
  if (scope === 'current' && !pathAbsent(join(commonDir, 'factory', 'upgrade-incomplete')))
    throw new Error('upgrade marker blocks dependency maintenance');
  const before = lstatSync(location.database, { bigint: true });
  if (!before.isFile() || before.isSymbolicLink() || before.nlink !== 1n || before.ino === 0n
    || (before.mode & 0o077n) !== 0n) throw new Error('invalid forward store file');
  assertForwardSidecars(location.database);
  const url = pathToFileURL(location.database); url.searchParams.set('mode', 'rw');
  const database = new DatabaseSync(url, { timeout: 100 });
  try {
    const after = lstatSync(location.database, { bigint: true });
    if (after.dev !== before.dev || after.ino !== before.ino || after.nlink !== 1n) throw new Error('forward store identity changed');
    assertForwardSidecars(location.database);
    const shape = knownForwardShape(database);
    if (scope === 'current' && shape !== 'v7') throw new Error('dependency maintenance requires existing current schema');
    assertForwardIntegrity(database);
    database.exec('PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL');
    if (database.prepare('PRAGMA foreign_keys').get()?.['foreign_keys'] !== 1
      || database.prepare('PRAGMA synchronous').get()?.['synchronous'] !== 2)
      throw new Error('forward durability settings unavailable');
    return new RepositoryStore(database, { path: location.database, marker: location.marker,
      identity: `${before.dev}:${before.ino}` });
  } catch (error) { database.close(); throw error; }
}

export function openForwardMaintenanceStore(commonDir: string) { return openExistingMaintenanceStore(commonDir, 'forward'); }
/** Existing-only and current-schema-only, with the same storage identity and durability checks. */
export function openDependencyMaintenanceStore(commonDir: string) { return openExistingMaintenanceStore(commonDir, 'current'); }

export function validateDependencyMaintenanceBinding(value: unknown): asserts value is DependencyMaintenanceBinding {
  const extra = value && typeof value === 'object' && !Array.isArray(value)
    ? ['backupAttempt', 'backup'].filter(key => Object.hasOwn(value, key)) : [];
  if (extra.length !== 0 && extra.length !== 2) throw new Error('incomplete dependency backup fields');
  if (!exactObject(value, ['version', 'bundleRoot', 'originalSha256', 'originalCompletionSha256',
    'expectedToolchainSha256', 'observedToolchainSha256', 'sourceIdentity', 'factoryIdentity', 'toolchainIdentity',
    'declarationSha256', 'lockSha256', ...extra, ...(value && typeof value === 'object' && Object.hasOwn(value, 'candidateAttempt') ? ['candidateAttempt'] : [])]) || value['version'] !== 1 || typeof value['bundleRoot'] !== 'string'
    || Buffer.byteLength(value['bundleRoot']) < 1 || Buffer.byteLength(value['bundleRoot']) > 4096
    || value['bundleRoot'].includes('\0')
    || !isAbsolute(value['bundleRoot']) || resolve(value['bundleRoot']) !== value['bundleRoot']
    || ['originalSha256', 'originalCompletionSha256', 'expectedToolchainSha256', 'observedToolchainSha256', 'declarationSha256', 'lockSha256']
      .some(key => typeof value[key] !== 'string' || !/^[a-f0-9]{64}$/.test(value[key]))
    || ['sourceIdentity', 'factoryIdentity', 'toolchainIdentity'].some(key => typeof value[key] !== 'string' || !/^\d+:\d+$/.test(value[key])))
    throw new Error('invalid dependency maintenance binding');
  if (Object.hasOwn(value, 'backupAttempt') && value['backupAttempt'] !== null) validateDependencyBackupAttempt(value['backupAttempt']);
  if (Object.hasOwn(value, 'backup') && value['backup'] !== null) validateMaintenanceBackup(value['backup']);
  if (Object.hasOwn(value, 'candidateAttempt')) {
    const attempt = value['candidateAttempt'];
    if (!exactObject(attempt, ['id', 'binding', 'events']) || typeof attempt['id'] !== 'string' || !/^[0-9a-f]{8}-[0-9a-f-]{27}$/i.test(attempt['id'])
      || !Array.isArray(attempt['events']) || attempt['events'].length < 2 || attempt['events'].length > 4
      || attempt['events'].some(event => !exactObject(event, ['cursor', 'sha256']) || typeof event['cursor'] !== 'string'
        || !/^[1-9][0-9]{0,18}$/.test(event['cursor']) || typeof event['sha256'] !== 'string' || !/^[a-f0-9]{64}$/.test(event['sha256'])))
      throw new Error('invalid dependency candidate attempt');
    if (attempt['binding'] !== null) validateDependencyCandidateAttempt(attempt['binding']);
  }
}
export function validateDependencyCandidateAttempt(value: unknown): asserts value is DependencyCandidateAttemptBinding {
  if (!exactObject(value, ['identity', 'sha256', 'rootIdentity', 'requestSha256'])
    || ['identity', 'rootIdentity'].some(key => typeof value[key] !== 'string' || !/^\d+:\d+$/.test(value[key]))
    || ['sha256', 'requestSha256'].some(key => typeof value[key] !== 'string' || !/^[a-f0-9]{64}$/.test(value[key])))
    throw new Error('invalid dependency candidate attempt binding');
}

export function validateDependencyBackupAttempt(value: unknown): asserts value is DependencyBackupAttemptBinding {
  if (!exactObject(value, ['identity', 'sha256', 'rootIdentity', 'operationIdentity', 'directoryIdentity', 'requestSha256'])
    || ['identity', 'rootIdentity', 'operationIdentity', 'directoryIdentity'].some(key => typeof value[key] !== 'string' || !/^\d+:\d+$/.test(value[key]))
    || ['sha256', 'requestSha256'].some(key => typeof value[key] !== 'string' || !/^[a-f0-9]{64}$/.test(value[key])))
    throw new Error('invalid dependency backup attempt binding');
}
export function validateMaintenanceBackup(value: unknown): asserts value is VerifiedMaintenanceBackup {
  if (!exactObject(value, ['id', 'identity', 'sha256', 'bytes', 'countDigest', 'receiptId', 'receiptSha256'])
    || ['id', 'receiptId'].some(key => typeof value[key] !== 'string' || !/^[0-9a-f-]{36}$/i.test(value[key]))
    || ['sha256', 'countDigest', 'receiptSha256'].some(key => typeof value[key] !== 'string' || !/^[a-f0-9]{64}$/.test(value[key]))
    || typeof value['identity'] !== 'string' || !/^\d+:\d+$/.test(value['identity'])
    || !Number.isSafeInteger(value['bytes']) || Number(value['bytes']) < 1 || Number(value['bytes']) > 512 * 1024 * 1024)
    throw new Error('invalid maintenance backup binding');
}

/** Existing-only, read-only installed ownership proof. Ordinary runner/dashboard claims remain valid. */
export function readInstalledCompletion(commonDir: string, operationId: string) {
  if (!/^[0-9a-f-]{36}$/i.test(operationId)) throw new Error('invalid installed operation identity');
  const location = paths(commonDir, false);
  if (!pathAbsent(location.marker)) throw new Error('incomplete bootstrap; explicit repair required');
  if (!pathAbsent(join(commonDir, 'factory', 'upgrade-incomplete'))) throw new Error('incomplete upgrade; explicit recovery required');
  const file = lstatSync(location.database);
  if (!file.isFile() || file.isSymbolicLink() || file.nlink !== 1
    || (process.platform !== 'win32' && (file.mode & 0o077) !== 0)) throw new Error('invalid store file');
  const database = new DatabaseSync(location.database, { readOnly: true, timeout: 100 });
  try {
    if (database.prepare('PRAGMA user_version').get()?.['user_version'] !== schemaVersion
      || database.prepare('PRAGMA quick_check').get()?.['quick_check'] !== 'ok')
      throw new Error('installed store schema or integrity differs');
    const repositories = database.prepare('SELECT id,release,state FROM repository LIMIT 2').all();
    const repository = repositories[0];
    if (repositories.length !== 1 || repository?.['state'] !== 'ready'
      || database.prepare("SELECT id FROM owner_claims WHERE kind='maintenance' LIMIT 1").get())
      throw new Error('installed repository is not ready');
    const rows = database.prepare("SELECT data FROM observation_events WHERE kind='install.completed' AND json_extract(data,'$.operationId')=? LIMIT 2")
      .all(operationId);
    if (rows.length !== 1) throw new Error('unique installed completion unavailable');
    return { completion: JSON.parse(String(rows[0]!['data'])) as { version: number; operationId: string;
      repositoryId: string; claimId: string; selectionDigest: string; manifestSha256: string;
      receiptId: string; receiptSha256: string }, repositoryId: String(repository['id']), release: String(repository['release']) };
  } finally { database.close(); }
}

function activeInstalledEvidence(database: DatabaseSync, repositoryId: string, release: string): ActiveInstalledCompletion {
  const row = database.prepare("SELECT kind,data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed','dependencies.completed','repair.completed','uninstall.completed','cleanup.completed') ORDER BY cursor DESC LIMIT 1").get();
  if (!row) throw new Error('active installed completion unavailable');
  const kind = row['kind'];
  if (kind !== 'install.completed' && kind !== 'upgrade.completed') throw new Error('unsupported installed completion kind');
  if (Buffer.byteLength(String(row['data'])) > 8192) throw new Error('installed completion exceeds bound');
  const completion = JSON.parse(String(row['data'])) as InstalledCompletion;
  if (completion.version !== 1 || completion.repositoryId !== repositoryId
    || !/^[0-9a-f-]{36}$/i.test(completion.operationId)) throw new Error('active installed completion invalid');
  if (kind === 'install.completed' && database.prepare("SELECT count(*) AS count FROM observation_events WHERE kind='install.completed' AND json_extract(data,'$.operationId')=?")
    .get(completion.operationId)?.['count'] !== 1) throw new Error('unique installed completion unavailable');
  return { kind, completion, repositoryId, release };
}

/** One snapshot selects the latest installed completion. Invalid newest evidence never falls back. */
function selectActiveInstalledCompletion(commonDir: string, allowUpgradeMarker: boolean): ActiveInstalledCompletion {
  const location = paths(commonDir, false);
  if (!pathAbsent(location.marker) || (!allowUpgradeMarker && !pathAbsent(join(commonDir, 'factory', 'upgrade-incomplete'))))
    throw new Error('incomplete installation; explicit recovery required');
  const file = lstatSync(location.database);
  if (!file.isFile() || file.isSymbolicLink() || file.nlink !== 1
    || (process.platform !== 'win32' && (file.mode & 0o077) !== 0)) throw new Error('invalid store file');
  const database = new DatabaseSync(location.database, { readOnly: true, timeout: 100 });
  try {
    database.exec('BEGIN');
    if (database.prepare('PRAGMA user_version').get()?.['user_version'] !== schemaVersion
      || database.prepare('PRAGMA quick_check').get()?.['quick_check'] !== 'ok')
      throw new Error('installed store schema or integrity differs');
    const repositories = database.prepare('SELECT id,release,state FROM repository LIMIT 2').all();
    const repository = repositories[0];
    if (repositories.length !== 1 || repository?.['state'] !== 'ready'
      || database.prepare("SELECT id FROM owner_claims WHERE kind='maintenance' LIMIT 1").get())
      throw new Error('installed repository is not ready');
    const active = activeInstalledEvidence(database, String(repository['id']), String(repository['release']));
    database.exec('COMMIT');
    return active;
  } finally { database.close(); }
}

export function readActiveInstalledCompletion(commonDir: string) {
  return selectActiveInstalledCompletion(commonDir, false);
}

/** Controller-only read snapshot. Never opens writable storage or changes claims, schema or readiness. */
export function readRepairStoreSnapshot(commonDir: string) {
  const location = paths(commonDir, false);
  if (!pathAbsent(location.marker)) throw new Error('bootstrap authority is incomplete');
  const before = lstatSync(location.database);
  if (!before.isFile() || before.isSymbolicLink() || before.nlink !== 1 || before.ino === 0
    || (process.platform !== 'win32' && ((before.mode & 0o077) !== 0 || before.uid !== process.getuid!())))
    throw new Error('invalid repair store file');
  assertForwardSidecars(location.database);
  const sidecarOwners = () => {
    for (const suffix of ['-wal', '-shm', '-journal']) {
      const path = `${location.database}${suffix}`;
      if (!pathAbsent(path) && process.platform !== 'win32' && lstatSync(path).uid !== process.getuid!())
        throw new Error('repair sidecar owner differs');
    }
  };
  sidecarOwners();
  const database = new DatabaseSync(location.database, { readOnly: true, timeout: 100 });
  try {
    database.exec('BEGIN');
    const shape = knownForwardShape(database);
    assertForwardIntegrity(database);
    const repositories = database.prepare('SELECT id,release,state FROM repository LIMIT 2').all(), repository = repositories[0];
    if (repositories.length !== 1 || !repository || !['ready', 'incomplete'].includes(String(repository['state'])))
      throw new Error('unsupported repair repository state');
    const repositoryId = String(repository['id']), release = String(repository['release']);
    const active = activeInstalledEvidence(database, repositoryId, release);
    const rows = database.prepare('SELECT id,token,kind,resource_key,data FROM owner_claims LIMIT 2').all();
    const claims = rows.map(row => {
      const text = String(row['data']);
      if (Buffer.byteLength(text) > 8192) throw new Error('repair claim exceeds bound');
      const claim = JSON.parse(text) as Claim;
      if (!claim || claim.id !== row['id'] || claim.token !== row['token'] || claim.kind !== row['kind']
        || claim.resourceKey !== row['resource_key']) throw new Error('repair claim columns differ');
      return claim;
    });
    const marker = !pathAbsent(join(commonDir, 'factory', 'upgrade-incomplete'));
    if (repository['state'] === 'ready' && claims.length === 0) {
      if (shape !== 'v7' || marker) throw new Error('ready repair snapshot is not idle');
    } else {
      const claim = claims[0], selected = claim?.maintenance;
      if (claims.length !== 1 || claim?.kind !== 'maintenance' || claim.resourceKey !== repositoryId
        || !selected || selected.kind !== 'upgrade' || selected.repositoryId !== repositoryId
        || !/^[a-f0-9-]{36}$/i.test(selected.operationId) || selected.forward?.currentShape !== shape
        || !['handoff-ready', 'modifying', 'validating'].includes(selected.phase)
        || repository['state'] === 'ready' && (selected.phase !== 'handoff-ready' || selected.ticketConsumed || marker)
        || repository['state'] === 'incomplete' && !selected.ticketConsumed)
        throw new Error('unsupported incomplete repair authority');
    }
    const after = lstatSync(location.database);
    if (before.dev !== after.dev || before.ino !== after.ino || after.nlink !== 1)
      throw new Error('repair store identity changed');
    assertForwardSidecars(location.database);
    sidecarOwners();
    database.exec('COMMIT');
    return { repositoryId, release, state: String(repository['state']) as 'ready' | 'incomplete', shape, active,
      claim: claims[0] ?? null, databaseIdentity: `${before.dev}:${before.ino}` };
  } finally { database.close(); }
}
/** Controller-only view for verifying a committed operation before removing its marker. */
export function readCompletedUpgradeForRecovery(commonDir: string, operationId: string) {
  const active = selectActiveInstalledCompletion(commonDir, true);
  if (active.kind !== 'upgrade.completed' || active.completion.operationId !== operationId)
    throw new Error('completed upgrade operation differs');
  return active;
}

function openStore(commonDir: string, allowMarker: boolean) {
  const location = paths(commonDir, false);
  if (!allowMarker && !pathAbsent(location.marker)) throw new Error('incomplete bootstrap; explicit repair required');
  if (!allowMarker && !pathAbsent(join(commonDir, 'factory', 'upgrade-incomplete')))
    throw new Error('incomplete upgrade; explicit recovery required');
  const file = lstatSync(location.database);
  if (!file.isFile() || file.isSymbolicLink()) throw new Error('invalid store file');
  const database = new DatabaseSync(location.database, { timeout: 100 });
  try {
    if (database.prepare('PRAGMA user_version').get()?.['user_version'] !== schemaVersion) throw new Error('incompatible schema; explicit forward maintenance required');
    if (database.prepare('PRAGMA quick_check').get()?.['quick_check'] !== 'ok') throw new Error('corrupt store; preserving data');
    if (!database.prepare('SELECT id FROM repository').get()) throw new Error('missing repository identity');
    configure(database);
    return new RepositoryStore(database);
  } catch (error) { database.close(); throw error; }
}

export class RepositoryStore {
  constructor(private readonly database: DatabaseSync,
    private readonly forwardStorage?: { path: string; marker: string; identity: string }) {}

  private assertForwardStorage() {
    if (!this.forwardStorage) return;
    const stat = lstatSync(this.forwardStorage.path, { bigint: true });
    if (!stat.isFile() || stat.isSymbolicLink() || stat.nlink !== 1n || `${stat.dev}:${stat.ino}` !== this.forwardStorage.identity
      || !pathAbsent(this.forwardStorage.marker)) throw new Error('forward store identity or marker changed');
    assertForwardSidecars(this.forwardStorage.path);
  }

  private readonly blockedInvocations = new Set<string>();
  blockAdmissions(invocationId: string) { this.blockedInvocations.add(invocationId); }
  close() { this.database.close(); }

  /** A deferred read transaction, never the writer's BEGIN IMMEDIATE admission path. */
  private cleanupRead<T>(action: () => T): T {
    const own = !this.database.isTransaction;
    if (own) this.database.exec('BEGIN');
    try {
      const value = action();
      if (own) this.database.exec('COMMIT');
      return value;
    } catch (error) {
      if (own && this.database.isTransaction) this.database.exec('ROLLBACK');
      throw error;
    }
  }

  private cleanupHighWater(table: 'invocations' | 'attempts' | 'captures' | 'observation_events') {
    if (this.database.prepare(`SELECT 1 FROM ${table} WHERE ${table === 'observation_events' ? 'cursor' : 'rowid'}<=0 LIMIT 1`).get())
      throw new Error('cleanup source cursor outside supported range');
    const statement = this.database.prepare(`SELECT coalesce(max(${table === 'observation_events' ? 'cursor' : 'rowid'}),0) AS cursor FROM ${table}`);
    statement.setReadBigInts(true);
    const cursor = String(statement.get()!['cursor']); cleanupCursor(cursor); return cursor;
  }

  /** Exact operator clearance is a committed row AND its unique event, never the absence of an owner. */
  private cleanupActivity(): CleanupActivityEvidence {
    const cleared = (invocation: 'a.invocation_id' | 'i.id') => `EXISTS (
      SELECT 1 FROM clearances c WHERE CASE WHEN typeof(c.data)='text' AND octet_length(c.data)<=16384 AND json_valid(c.data) THEN
        typeof(c.id)='text' AND octet_length(c.id) BETWEEN 1 AND 256 AND typeof(c.claim_id)='text' AND octet_length(c.claim_id) BETWEEN 1 AND 256
        AND json_type(c.data)='object' AND json_type(c.data,'$.id')='text' AND json_type(c.data,'$.claimId')='text'
        AND json_extract(c.data,'$.id')=c.id AND json_extract(c.data,'$.claimId')=c.claim_id
        AND json_type(c.data,'$.invocationId')='text' AND json_extract(c.data,'$.invocationId')=${invocation}
        AND json_extract(c.data,'$.basis')='operator_confirmed' AND json_extract(c.data,'$.inspection') IN ('not_live','unknown')
        AND json_type(c.data,'$.note')='text' AND octet_length(json_extract(c.data,'$.note')) BETWEEN 1 AND 256
        AND length(trim(json_extract(c.data,'$.note')))>0
        AND (json_type(c.data,'$.details') IS NULL OR json_type(c.data,'$.details')='object' AND octet_length(json_extract(c.data,'$.details'))<=8192)
        AND NOT EXISTS (SELECT 1 FROM json_each(c.data) WHERE key NOT IN ('id','claimId','invocationId','note','basis','inspection','details'))
        AND (SELECT count(*) FROM json_each(c.data))=6+(json_type(c.data,'$.details') IS NOT NULL)
        AND (SELECT count(*) FROM (SELECT 1 FROM observation_events e WHERE e.kind='owner.cleared' AND
          CASE WHEN typeof(e.data)='text' AND octet_length(e.data)<=8192 AND json_valid(e.data) THEN
            json_type(e.data)='object' AND json_type(e.data,'$.claimId')='text' AND json_type(e.data,'$.clearanceId')='text'
            AND json_type(e.data,'$.invocationId')='text' AND json_extract(e.data,'$.claimId')=c.claim_id
            AND json_extract(e.data,'$.clearanceId')=c.id AND json_extract(e.data,'$.invocationId')=${invocation}
            AND json_extract(e.data,'$.basis')='operator_confirmed' AND json_type(e.data,'$.at')='text'
            AND octet_length(json_extract(e.data,'$.at')) BETWEEN 1 AND 256
            AND (SELECT count(*) FROM json_each(e.data))=5
            AND NOT EXISTS (SELECT 1 FROM json_each(e.data) WHERE key NOT IN ('claimId','invocationId','clearanceId','basis','at'))
          ELSE 0 END LIMIT 2))=1
      ELSE 0 END)`;
    const attempt = this.database.prepare(`SELECT a.rowid AS cursor,
      CASE WHEN typeof(a.id)='text' AND octet_length(a.id)<=256 THEN a.id END AS id
      FROM attempts a LEFT JOIN invocations i ON i.id=a.invocation_id LEFT JOIN operations o ON o.id=a.operation_id
      WHERE (CASE WHEN typeof(a.data)='text' AND octet_length(a.data)<=65536 AND json_valid(a.data) THEN
        typeof(a.occupied)='integer' AND a.occupied=0 AND json_type(a.data)='object'
        AND typeof(a.id)='text' AND octet_length(a.id) BETWEEN 1 AND 256 AND json_extract(a.data,'$.id')=a.id
        AND json_type(a.data,'$.id')='text' AND json_type(a.data,'$.invocationId')='text' AND json_type(a.data,'$.operationId')='text'
        AND json_type(a.data,'$.runId')='text' AND json_type(a.data,'$.operationKey')='text' AND json_type(a.data,'$.kind')='text'
        AND octet_length(json_extract(a.data,'$.invocationId')) BETWEEN 1 AND 256 AND octet_length(json_extract(a.data,'$.operationId')) BETWEEN 1 AND 256
        AND octet_length(json_extract(a.data,'$.runId')) BETWEEN 1 AND 256 AND octet_length(json_extract(a.data,'$.operationKey')) BETWEEN 1 AND 256
        AND json_extract(a.data,'$.invocationId')=a.invocation_id AND json_extract(a.data,'$.operationId')=a.operation_id
        AND json_extract(a.data,'$.kind')=a.kind AND a.kind IN ('agent','command')
        AND json_extract(a.data,'$.runId')=i.run_id AND o.run_id=i.run_id AND json_extract(a.data,'$.operationKey')=o.operation_key
        AND json_type(a.data,'$.quiescent')='true' AND json_extract(a.data,'$.launch') IN ('admitted','started','not_started','unknown')
        AND (json_type(a.data,'$.outcome')='null' OR json_extract(a.data,'$.outcome') IN ('succeeded','failed','needs_input','interrupted'))
        AND (CASE WHEN json_type(a.data,'$.outcome')='null' THEN json_extract(a.data,'$.launch') IN ('admitted','started') AND json_type(a.data,'$.evidence')='null'
          ELSE json_extract(a.data,'$.launch') IN ('started','not_started','unknown')
            AND NOT (json_extract(a.data,'$.launch')='not_started' AND json_extract(a.data,'$.outcome')='succeeded')
            AND json_type(a.data,'$.evidence')='text' AND octet_length(json_extract(a.data,'$.evidence')) BETWEEN 1 AND 256
            AND instr(json_extract(a.data,'$.evidence'),char(0))=0 END)
        AND (CASE WHEN json_extract(a.data,'$.launch')='started' THEN
          json_type(a.data,'$.owner')='object' AND (SELECT count(*) FROM json_each(a.data,'$.owner'))=3
          AND NOT EXISTS (SELECT 1 FROM json_each(a.data,'$.owner') WHERE key NOT IN ('host','pid','start'))
          AND json_type(a.data,'$.owner.host')='text' AND octet_length(json_extract(a.data,'$.owner.host')) BETWEEN 1 AND 256
          AND instr(json_extract(a.data,'$.owner.host'),char(0))=0
          AND json_type(a.data,'$.owner.pid')='integer' AND json_extract(a.data,'$.owner.pid') BETWEEN 1 AND 9007199254740991
          AND (json_type(a.data,'$.owner.start')='null' OR json_type(a.data,'$.owner.start')='text' AND octet_length(json_extract(a.data,'$.owner.start')) BETWEEN 1 AND 256)
        ELSE json_type(a.data,'$.owner')='null' END)
        AND (CASE WHEN json_extract(a.data,'$.cleanupBasis')='operator_confirmed' THEN ${cleared('a.invocation_id')}
          ELSE json_type(a.data,'$.cleanupBasis') IS NULL AND json_extract(a.data,'$.launch') IN ('started','not_started','unknown')
            AND json_extract(a.data,'$.outcome') IN ('succeeded','failed','needs_input','interrupted')
            AND NOT (json_extract(a.data,'$.launch')='not_started' AND json_extract(a.data,'$.outcome')='succeeded')
            AND json_type(a.data,'$.evidence')='text' AND octet_length(json_extract(a.data,'$.evidence')) BETWEEN 1 AND 256 END)
      ELSE 0 END) IS NOT TRUE ORDER BY a.rowid LIMIT 1`);
    attempt.setReadBigInts(true);
    const blockedAttempt = attempt.get();
    if (blockedAttempt) return { status: 'blocked', source: 'attempt', id: cleanupId(blockedAttempt['id']) ? blockedAttempt['id'] : null,
      cursor: String(blockedAttempt['cursor']) };
    const invocation = this.database.prepare(`SELECT i.rowid AS cursor,
      CASE WHEN typeof(i.id)='text' AND octet_length(i.id)<=256 THEN i.id END AS id FROM invocations i WHERE (
      CASE WHEN typeof(i.data)='text' AND octet_length(i.data)<=65536 AND json_valid(i.data) THEN
        json_type(i.data)='object' AND typeof(i.id)='text' AND octet_length(i.id) BETWEEN 1 AND 256 AND json_extract(i.data,'$.id')=i.id
        AND json_type(i.data,'$.id')='text' AND json_type(i.data,'$.runId')='text' AND json_type(i.data,'$.worktreeId')='text'
        AND octet_length(json_extract(i.data,'$.runId')) BETWEEN 1 AND 256 AND octet_length(json_extract(i.data,'$.worktreeId')) BETWEEN 1 AND 256
        AND json_extract(i.data,'$.runId')=i.run_id AND json_extract(i.data,'$.worktreeId')=i.worktree_id
        AND json_extract(i.data,'$.stage') IN ('starting','running','shutting_down','finalized')
        AND (CASE WHEN json_extract(i.data,'$.stage')='finalized' THEN
          json_extract(i.data,'$.outcome') IN ('succeeded','failed','needs_input','interrupted','cancelled')
          AND json_extract(i.data,'$.cleanup') IN ('complete','unknown')
          AND (json_extract(i.data,'$.cleanup')='complete' OR ${cleared('i.id')})
        ELSE json_type(i.data,'$.outcome')='null' AND json_type(i.data,'$.cleanup') IS NULL AND ${cleared('i.id')} END)
      ELSE 0 END) IS NOT TRUE ORDER BY i.rowid LIMIT 1`);
    invocation.setReadBigInts(true);
    const blockedInvocation = invocation.get();
    return blockedInvocation ? { status: 'blocked', source: 'invocation', id: cleanupId(blockedInvocation['id']) ? blockedInvocation['id'] : null,
      cursor: String(blockedInvocation['cursor']) } : { status: 'clear' };
  }

  /** The workflow operation is a separate owned fact, not the attempt's copied operation key. */
  readCleanupOperation(input: { runId: string; operationId: string }): import('./cleanup-read.js').CleanupOperationRead {
    assertCleanupId(input.runId); assertCleanupId(input.operationId);
    return this.cleanupRead(() => {
      const statement = this.database.prepare(`SELECT rowid AS cursor,
        CASE WHEN typeof(id)='text' AND octet_length(id) BETWEEN 1 AND 256 THEN id END AS id,
        CASE WHEN typeof(run_id)='text' AND octet_length(run_id) BETWEEN 1 AND 256 THEN run_id END AS run_id,
        CASE WHEN typeof(operation_key)='text' AND octet_length(operation_key) BETWEEN 1 AND 256 THEN operation_key END AS operation_key,
        octet_length(data) AS bytes,
        CASE WHEN run_id=? AND typeof(data)='text' AND octet_length(data)<=8192 THEN data END AS data
        FROM operations WHERE id=? LIMIT 2`);
      statement.setReadBigInts(true);
      const rows = statement.all(input.runId,input.operationId), row = rows[0];
      if (!row) return { status: 'missing' };
      if (rows.length !== 1 || !cleanupId(row['id']) || !cleanupId(row['run_id']) || !cleanupId(row['operation_key']))
        return cleanupOpaque(row,'invalid-identity');
      if (row['run_id'] !== input.runId) return { status: 'foreign' };
      if (typeof row['data'] !== 'string') return cleanupOpaque(row,BigInt(String(row['bytes']))>8192n?'oversized':'malformed');
      if (BigInt(Buffer.byteLength(row['data'])) !== BigInt(String(row['bytes']))) return cleanupOpaque(row,'malformed');
      try {
        const value: unknown = JSON.parse(row['data']);
        if (!cleanupObject(value) || Object.keys(value).sort().join(',') !== 'kind,loopKey'
          || !cleanupId(value.loopKey) || !['command','agent'].includes(String(value.kind))) return cleanupOpaque(row,'unknown-format');
        return { status: 'known', id: row['id'], runId: row['run_id'], operationKey: row['operation_key'],
          kind: value.kind as 'command'|'agent', loopKey: value.loopKey, bytes: String(row['bytes']), sha256: cleanupHash(row['data']) };
      } catch { return cleanupOpaque(row,'malformed'); }
    });
  }

  /** Exact operation equality, LIMIT 2 uniqueness and SQL body/type bounds precede JavaScript decoding. */
  readCleanupOperationEvidence(input: { operationId: string }): CleanupOperationEvidence {
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(input.operationId))
      throw new Error('invalid cleanup operation identity');
    return this.cleanupRead(() => {
      const columns = `cursor,typeof(data) AS body_type,octet_length(data) AS bytes,
        CASE WHEN typeof(kind)='text' AND octet_length(kind)<=256 THEN kind END AS kind,
        CASE WHEN typeof(data)='text' AND octet_length(data)<=8192 THEN data END AS data`;
      const operation = `CASE WHEN json_valid(data) THEN json_extract(data,'$.operationId') END=?`;
      const read = (where: string, keyed: boolean, unique = true) => {
        const statement = this.database.prepare(`SELECT ${columns} FROM observation_events WHERE ${where} ORDER BY cursor DESC LIMIT ${unique ? 2 : 1}`);
        statement.setReadBigInts(true);
        return cleanupOperationEvent(keyed ? statement.all(input.operationId) : statement.all());
      };
      const snapshot = this.readCleanupSnapshot();
      const statement = this.database.prepare(`SELECT
        CASE WHEN typeof(id)='text' AND octet_length(id)<=256 THEN id END AS id,
        CASE WHEN typeof(data)='text' AND octet_length(data)<=8192 THEN data END AS data,
        CASE WHEN json_valid(data) THEN id=json_extract(data,'$.id') AND token=json_extract(data,'$.token')
          AND kind=json_extract(data,'$.kind') AND resource_key=json_extract(data,'$.resourceKey') ELSE 0 END AS consistent
        FROM owner_claims ORDER BY rowid LIMIT 2`);
      const claims: CleanupRecoveryClaim[] = statement.all().map(row => {
        const id = cleanupId(row['id']) ? row['id'] : null;
        const opaque: CleanupRecoveryClaim = { status: 'opaque', id };
        if (!id || row['consistent'] !== 1 || typeof row['data'] !== 'string') return opaque;
        let value: unknown;
        try { value = JSON.parse(row['data']); } catch { return opaque; }
        if (!cleanupObject(value) || !['worktree','dashboard','maintenance'].includes(String(value.kind))) return opaque;
        if (value.kind !== 'maintenance') return { status: 'known', id, kind: value.kind as 'worktree' | 'dashboard',
          operationId: null, maintenanceKind: null, phase: null, backupId: null, stagePath: null };
        const selected = value.maintenance;
        if (!cleanupObject(selected) || selected.repositoryId !== snapshot.repositoryId || value.resourceKey !== snapshot.repositoryId
          || !cleanupId(selected.operationId) || !['install','upgrade','dependencies','repair','uninstall','cleanup'].includes(String(selected.kind))
          || !['preparing','handoff-ready','modifying','validating'].includes(String(selected.phase))
          || !(selected.backupId === null || cleanupId(selected.backupId))
          || typeof selected.stagePath !== 'string' || Buffer.byteLength(selected.stagePath) > 4096) return opaque;
        return { status: 'known', id, kind: 'maintenance', operationId: selected.operationId,
          maintenanceKind: selected.kind as MaintenanceKind, phase: selected.phase as MaintenancePhase,
          backupId: selected.backupId as string | null, stagePath: selected.stagePath };
      });
      return { snapshot, completion: read(`kind LIKE '%.completed' AND ${operation}`, true),
        backupBound: read(`kind='maintenance.backup_bound' AND ${operation}`, true),
        newestCompletion: read("kind LIKE '%.completed'", false, false),
        newestOperation: read("kind LIKE 'maintenance.%' OR kind LIKE '%.completed'", false, false), claims,
        occupiedAttempts: Boolean(this.database.prepare('SELECT 1 FROM attempts WHERE occupied<>0 LIMIT 1').get()), activity: this.cleanupActivity() };
    });
  }

  readCleanupSnapshot(): CleanupSnapshot {
    return this.cleanupRead(() => {
      const repository = this.database.prepare(`SELECT
        CASE WHEN octet_length(id)<=256 THEN id END AS id,
        CASE WHEN octet_length(release)<=256 THEN release END AS release,
        CASE WHEN octet_length(state)<=256 THEN state END AS state FROM repository LIMIT 2`).all();
      const row = repository[0];
      if (repository.length !== 1 || !row || !cleanupId(row['id']) || !cleanupId(row['release'])
        || !['ready','incomplete','absent'].includes(String(row['state']))
        || this.database.prepare('PRAGMA user_version').get()?.['user_version'] !== 7) throw new Error('invalid cleanup repository');
      const path = this.database.prepare('PRAGMA database_list').get()?.['file'];
      if (typeof path !== 'string' || !path) throw new Error('cleanup database identity unavailable');
      const file = lstatSync(path, { bigint: true });
      if (!file.isFile() || file.isSymbolicLink() || file.nlink !== 1n || file.ino === 0n) throw new Error('invalid cleanup database identity');
      const count = this.database.prepare('SELECT count(*) AS count FROM owner_claims'); count.setReadBigInts(true);
      const claimCount = String(count.get()!['count']);
      const claims = this.database.prepare(`SELECT rowid AS cursor,
        CASE WHEN octet_length(id)<=256 THEN id END AS id,
        CASE WHEN octet_length(kind)<=256 THEN kind END AS kind, octet_length(data) AS bytes,
        CASE WHEN octet_length(data)<=8192 THEN data END AS data FROM owner_claims ORDER BY rowid LIMIT 100`);
      claims.setReadBigInts(true);
      const claimFacts: CleanupSnapshot['recovery']['claimFacts'] = [];
      let blocked = BigInt(claimCount) > 100n;
      for (const claim of claims.iterate()) {
        let valid = false;
        if (typeof claim['data'] === 'string') {
          try {
            const data: unknown = JSON.parse(claim['data']);
            valid = cleanupObject(data) && data.id === claim['id'] && data.kind === claim['kind']
              && cleanupId(claim['id']) && ['worktree','dashboard','maintenance'].includes(String(claim['kind']));
          } catch { /* Fixed opaque reason below; claim text never appears in diagnostics. */ }
        }
        if (valid) claimFacts.push({ ...cleanupIdentity(claim), status: 'known', kind: String(claim['kind']) });
        else { claimFacts.push(cleanupOpaque(claim, BigInt(String(claim['bytes'])) > 8192n ? 'oversized' : 'malformed')); blocked = true; }
      }
      const repositoryState = String(row['state']);
      return { repositoryId: row['id'], release: row['release'], schema: 7, databaseIdentity: `${file.dev}:${file.ino}`,
        highWater: { invocations: this.cleanupHighWater('invocations'), attempts: this.cleanupHighWater('attempts'),
          captures: this.cleanupHighWater('captures'), events: this.cleanupHighWater('observation_events') },
        recovery: { authority: 'unassessed', repositoryState, claimCount, claimFacts, opaque: blocked,
          sha256: blocked ? null : cleanupHash(JSON.stringify({ repositoryState, claimCount, claimFacts })) } };
    });
  }

  private cleanupFacts(table: 'invocations' | 'attempts', input: CleanupPageInput): CleanupPage<CleanupInvocationFact | CleanupAttemptFact | CleanupOpaque> {
    return this.cleanupRead(() => {
      const b = cleanupBounds(input, this.cleanupHighWater(table));
      const columns = table === 'invocations'
        ? 'CASE WHEN octet_length(run_id)<=256 THEN run_id END AS run_id,CASE WHEN octet_length(worktree_id)<=256 THEN worktree_id END AS worktree_id'
        : `CASE WHEN octet_length(invocation_id)<=256 THEN invocation_id END AS invocation_id,
          CASE WHEN octet_length(operation_id)<=256 THEN operation_id END AS operation_id,
          CASE WHEN octet_length(kind)<=256 THEN kind END AS kind,
          CASE WHEN occupied IN (0,1) THEN occupied END AS occupied`;
      const statement = this.database.prepare(`SELECT rowid AS cursor,CASE WHEN octet_length(id)<=256 THEN id END AS id,
        ${columns},octet_length(data) AS bytes,CASE WHEN octet_length(data)<=? THEN data END AS data
        FROM ${table} WHERE rowid>? AND rowid<=? ORDER BY rowid LIMIT ?`);
      statement.setReadBigInts(true);
      const result: CleanupPage<CleanupInvocationFact | CleanupAttemptFact | CleanupOpaque> = { records: [], nextCursor: b.after, through: b.through, hasMore: false, blocked: null };
      let bytes = 512; // Reserve the bounded page envelope, cursor growth and refusal diagnostic.
      for (const row of statement.iterate(Math.min(65536,b.byteBudget), b.a, b.t, b.limit + 1)) {
        if (result.records.length === b.limit) { result.hasMore = true; break; }
        const fact = table === 'invocations' ? decodeCleanupInvocation(row) : decodeCleanupAttempt(row);
        const size = Buffer.byteLength(JSON.stringify(fact)) + 1;
        if (bytes + size > b.byteBudget) { result.hasMore = true; result.blocked = 'byte-budget'; break; }
        bytes += size; result.records.push(fact); result.nextCursor = String(row['cursor']);
      }
      return result;
    });
  }

  pageCleanupInvocationFacts(input: CleanupPageInput = {}) {
    return this.cleanupFacts('invocations', input) as CleanupPage<CleanupInvocationFact | CleanupOpaque>;
  }
  pageCleanupAttemptFacts(input: CleanupPageInput = {}) {
    return this.cleanupFacts('attempts', input) as CleanupPage<CleanupAttemptFact | CleanupOpaque>;
  }
  pageCleanupCaptureHeaders(input: CleanupPageInput = {}): CleanupPage<CleanupCaptureHeader | CleanupOpaque> {
    return this.cleanupRead(() => {
      const b = cleanupBounds(input, this.cleanupHighWater('captures'));
      const statement = this.database.prepare(`SELECT rowid AS cursor,
        CASE WHEN octet_length(id)<=256 THEN id END AS id,
        CASE WHEN octet_length(invocation_id)<=256 THEN invocation_id END AS invocation_id,
        CASE WHEN octet_length(attempt_id)<=256 THEN attempt_id END AS attempt_id,
        CASE WHEN attempt_id IS NULL OR octet_length(attempt_id)<=256 THEN 1 ELSE 0 END AS identity_valid,
        (EXISTS(SELECT 1 FROM invocations WHERE id=captures.invocation_id) AND
          (attempt_id IS NULL OR EXISTS(SELECT 1 FROM attempts WHERE id=captures.attempt_id AND invocation_id=captures.invocation_id))) AS owner_valid,
        CASE WHEN octet_length(channel)<=256 THEN channel END AS channel,
        CASE WHEN octet_length(state)<=256 THEN state END AS state,
        CASE WHEN typeof(sequence)='integer' THEN sequence END AS sequence,
        (SELECT coalesce(sum(octet_length(text)),0) FROM capture_chunks WHERE capture_id=captures.id) AS bytes
        FROM captures WHERE rowid>? AND rowid<=? ORDER BY rowid LIMIT ?`);
      statement.setReadBigInts(true);
      const result: CleanupPage<CleanupCaptureHeader | CleanupOpaque> = { records: [], nextCursor: b.after, through: b.through, hasMore: false, blocked: null };
      let bytes = 512;
      for (const row of statement.iterate(b.a, b.t, b.limit + 1)) {
        if (result.records.length === b.limit) { result.hasMore = true; break; }
        const header = decodeCleanupHeader(row), size = Buffer.byteLength(JSON.stringify(header)) + 1;
        if (bytes + size > b.byteBudget) { result.hasMore = true; result.blocked = 'byte-budget'; break; }
        result.records.push(header); bytes += size; result.nextCursor = String(row['cursor']);
      }
      return result;
    });
  }

  private cleanupCaptureHeader(captureId: string) {
    const statement = this.database.prepare(`SELECT rowid AS cursor,
      CASE WHEN octet_length(id)<=256 THEN id END AS id,
      CASE WHEN octet_length(invocation_id)<=256 THEN invocation_id END AS invocation_id,
      CASE WHEN octet_length(attempt_id)<=256 THEN attempt_id END AS attempt_id,
      CASE WHEN attempt_id IS NULL OR octet_length(attempt_id)<=256 THEN 1 ELSE 0 END AS identity_valid,
      (EXISTS(SELECT 1 FROM invocations WHERE id=captures.invocation_id) AND
        (attempt_id IS NULL OR EXISTS(SELECT 1 FROM attempts WHERE id=captures.attempt_id AND invocation_id=captures.invocation_id))) AS owner_valid,
      CASE WHEN octet_length(channel)<=256 THEN channel END AS channel,
      CASE WHEN octet_length(state)<=256 THEN state END AS state,
      CASE WHEN typeof(sequence)='integer' THEN sequence END AS sequence,
      (SELECT coalesce(sum(octet_length(text)),0) FROM capture_chunks WHERE capture_id=captures.id) AS bytes,
      (SELECT count(*) FROM capture_chunks WHERE capture_id=captures.id) AS chunk_count,
      (SELECT CASE WHEN typeof(coalesce(max(sequence),0))='integer' THEN coalesce(max(sequence),0) END FROM capture_chunks WHERE capture_id=captures.id) AS chunk_last
      FROM captures WHERE id=?`);
    statement.setReadBigInts(true);
    return statement.get(captureId);
  }

  measureCleanupCaptures(keys: CleanupCaptureKey[]): CleanupCaptureMeasurement[] {
    if (!Array.isArray(keys) || keys.length > 100) throw new Error('invalid cleanup measurement keys');
    const seen = new Set<string>();
    for (const key of keys) {
      assertCleanupId(key.invocationId); assertCleanupId(key.captureId);
      const identity = JSON.stringify([key.invocationId,key.captureId]);
      if (seen.has(identity)) throw new Error('duplicate cleanup measurement key');
      seen.add(identity);
    }
    return this.cleanupRead(() => keys.map(key => {
      const row = this.cleanupCaptureHeader(key.captureId);
      if (!row || row['invocation_id'] !== key.invocationId) return { ...key, status: row ? 'foreign' : 'missing', logicalPayloadBytes: null, header: null };
      const header = decodeCleanupHeader(row);
      if (header.status === 'opaque') return { ...key, status: 'opaque', logicalPayloadBytes: null, header };
      return { ...key, status: header.state === 'pruned' ? 'pruned' : header.logicalPayloadBytes === '0' ? 'empty' : 'present',
        logicalPayloadBytes: header.logicalPayloadBytes, header };
    }));
  }

  /** Exact ownership and a SQL byte preflight precede every payload string crossing into JavaScript. */
  readCleanupCapture(input: CleanupCaptureKey & { after?: string; limit?: number; byteBudget?: number }): CleanupCapturePage {
    assertCleanupId(input.invocationId); assertCleanupId(input.captureId);
    const after = input.after ?? '0', a = cleanupCursor(after), limit = input.limit ?? 20, byteBudget = input.byteBudget ?? 262144;
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 20 || !Number.isSafeInteger(byteBudget)
      || byteBudget < 1 || byteBudget > 262144) throw new Error('invalid cleanup capture page');
    return this.cleanupRead(() => {
      const row = this.cleanupCaptureHeader(input.captureId);
      const result: CleanupCapturePage = { status: row ? 'foreign' : 'missing', header: null, chunks: [], nextSequence: after, hasMore: false, blocked: null };
      if (!row || row['invocation_id'] !== input.invocationId) return result;
      const header = decodeCleanupHeader(row); result.header = header;
      if (header.status === 'opaque') { result.status = 'opaque'; result.blocked = 'unknown-header'; return result; }
      if (a > BigInt(header.lastSequence)) throw new Error('invalid cleanup capture continuation');
      if (header.state === 'pruned') { result.status = 'pruned'; return result; }
      result.status = 'present';
      if (row['chunk_count'] !== row['sequence'] || row['chunk_last'] !== row['sequence']) {
        result.blocked = 'sequence-gap'; result.hasMore = true; return result;
      }
      const statement = this.database.prepare(`SELECT CASE WHEN typeof(sequence)='integer' THEN sequence END AS sequence,octet_length(text) AS bytes,
        CASE WHEN octet_length(text)<=? THEN text END AS text FROM capture_chunks
        WHERE capture_id=? AND sequence>? ORDER BY sequence LIMIT ?`);
      statement.setReadBigInts(true);
      let bytes = Buffer.byteLength(JSON.stringify(result)) + 64;
      for (const chunk of statement.iterate(Math.min(65536,byteBudget),input.captureId,a,limit)) {
        if (chunk['sequence'] !== BigInt(result.nextSequence) + 1n) { result.blocked = 'sequence-gap'; break; }
        if (typeof chunk['text'] !== 'string') { result.blocked = 'byte-budget'; break; }
        const item = { sequence: String(chunk['sequence']), text: chunk['text'] };
        if (Buffer.from(item.text).toString('utf8') !== item.text || BigInt(Buffer.byteLength(item.text)) !== chunk['bytes']) {
          result.blocked = 'sequence-gap'; break;
        }
        const size = Buffer.byteLength(JSON.stringify(item)) + 1;
        if (bytes + size > byteBudget) { result.blocked = 'byte-budget'; break; }
        result.chunks.push(item); result.nextSequence = item.sequence; bytes += size;
      }
      result.hasMore = BigInt(result.nextSequence) < BigInt(header.lastSequence);
      return result;
    });
  }

  readCleanupAttempt(input: { invocationId: string; attemptId: string }): CleanupAttemptRead {
    assertCleanupId(input.invocationId); assertCleanupId(input.attemptId);
    return this.cleanupRead(() => {
      const statement = this.database.prepare(`SELECT rowid AS cursor,CASE WHEN octet_length(id)<=256 THEN id END AS id,
        CASE WHEN octet_length(invocation_id)<=256 THEN invocation_id END AS invocation_id,
        CASE WHEN octet_length(operation_id)<=256 THEN operation_id END AS operation_id,
        CASE WHEN octet_length(kind)<=256 THEN kind END AS kind,
        CASE WHEN occupied IN (0,1) THEN occupied END AS occupied,
        octet_length(data) AS bytes,CASE WHEN invocation_id=? AND octet_length(data)<=65536 THEN data END AS data
        FROM attempts WHERE id=?`);
      statement.setReadBigInts(true);
      const row = statement.get(input.invocationId,input.attemptId);
      if (!row || row['invocation_id'] !== input.invocationId) return { status: row ? 'foreign' : 'missing', fact: null };
      const fact = decodeCleanupAttempt(row);
      return { status: fact.status, fact };
    });
  }

  readCleanupEvent(input: { invocationId: string; cursor: string }): CleanupEventRead {
    assertCleanupId(input.invocationId); const cursor = cleanupCursor(input.cursor);
    return this.cleanupRead(() => {
      const statement = this.database.prepare(`SELECT cursor,NULL AS id,CASE WHEN octet_length(kind)<=256 THEN kind END AS kind,
        octet_length(data) AS bytes,CASE WHEN octet_length(data)<=8192 THEN data END AS data FROM observation_events WHERE cursor=?`);
      statement.setReadBigInts(true);
      const row = statement.get(cursor);
      if (!row) return { status: 'missing', cursor: input.cursor };
      if (typeof row['data'] !== 'string') return cleanupOpaque(row,'oversized');
      if (BigInt(Buffer.byteLength(row['data'])) !== row['bytes']) return cleanupOpaque(row,'malformed');
      let value: unknown;
      try { value = JSON.parse(row['data']); } catch { return cleanupOpaque(row,'malformed'); }
      if (!cleanupObject(value)) return cleanupOpaque(row,'malformed');
      if (Object.hasOwn(value,'invocationId')) {
        if (!cleanupId(value.invocationId)) return cleanupOpaque(row,'malformed');
        if (value.invocationId !== input.invocationId) return { status: 'foreign', cursor: input.cursor };
      } else {
        const attemptOwned = cleanupId(value.attemptId) && !!this.database.prepare('SELECT 1 FROM attempts WHERE id=? AND invocation_id=?').get(value.attemptId,input.invocationId);
        const captureOwned = cleanupId(value.captureId) && !!this.database.prepare('SELECT 1 FROM captures WHERE id=? AND invocation_id=?').get(value.captureId,input.invocationId);
        if (!attemptOwned && !captureOwned) return { status: 'foreign', cursor: input.cursor };
      }
      if (!this.database.prepare('SELECT 1 FROM invocations WHERE id=?').get(input.invocationId)) return cleanupOpaque(row,'invalid-identity');
      const data = typeof row['kind'] === 'string' ? decodeCleanupEvent(row['kind'],value) : null;
      return data ? { ...cleanupIdentity(row), status: 'known', kind: String(row['kind']), data } : cleanupOpaque(row,'unknown-format');
    });
  }

  private async transaction<T>(action: () => T): Promise<T> {
    const deadline = performance.now() + 5000;
    while (true) {
      try { this.database.exec('BEGIN IMMEDIATE'); break; }
      catch (error) {
        const code = (error as { errcode?: number }).errcode;
        if (code === undefined || (code & 255) !== 5 || performance.now() >= deadline) throw error;
        await delay(100 + Math.floor(Math.random() * 20));
      }
    }
    try {
      this.assertForwardStorage();
      const result = action();
      this.database.exec('COMMIT');
      return result;
    } catch (error) {
      if (this.database.isTransaction) this.database.exec('ROLLBACK');
      throw error;
    }
  }

  private event(kind: string, data: object) {
    if (Buffer.byteLength(JSON.stringify(data)) > 8192) throw new Error('event metadata exceeds limit');
    this.database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run(kind, JSON.stringify({ ...data, at: new Date().toISOString() }));
  }

  private ready() {
    if (this.database.prepare('SELECT state FROM repository').get()?.['state'] !== 'ready') throw new Error('installation not ready; explicit maintenance required');
    if (this.database.prepare("SELECT id FROM owner_claims WHERE kind='maintenance'").get()) throw new Error('maintenance claimed; startup refused');
  }

  async createRun(): Promise<Run> {
    return this.transaction(() => {
      this.ready();
      const run = { id: randomUUID(), additionalLimit: 20, codeLimit: 2, formatLimit: 1 };
      this.database.prepare('INSERT INTO runs(id,data) VALUES (?,?)').run(run.id, JSON.stringify(run));
      this.event('run.created', { runId: run.id });
      return run;
    });
  }

  async registerWorktree(input: { path: string; registration: string }): Promise<Worktree> {
    const path = realpathSync(input.path);
    text(input.registration, 'Git registration');
    return this.transaction(() => {
      this.ready();
      const existing = this.database.prepare('SELECT data FROM worktrees WHERE path=?').get(path);
      if (existing) {
        const worktree = JSON.parse(String(existing['data'])) as Worktree;
        if (worktree.registration !== input.registration) throw new Error('worktree registration changed; explicit correction required');
        return worktree;
      }
      const worktree = { id: randomUUID(), path, registration: input.registration };
      this.database.prepare('INSERT INTO worktrees(id,path,data) VALUES (?,?,?)').run(worktree.id, path, JSON.stringify(worktree));
      this.event('worktree.registered', { worktreeId: worktree.id });
      return worktree;
    });
  }

  /** Reserve an absent destination without creating it. Ownership must precede Git mutation. */
  async reserveWorktree(destination: string): Promise<Worktree> {
    const path = join(realpathSync(dirname(destination)), basename(destination));
    if (existsSync(path)) throw new Error('worktree destination already exists');
    return this.transaction(() => {
      this.ready();
      const worktree = { id: randomUUID(), path, registration: 'reserved' };
      this.database.prepare('INSERT INTO worktrees(id,path,data) VALUES (?,?,?)').run(worktree.id, path, JSON.stringify(worktree));
      this.event('worktree.reserved', { worktreeId: worktree.id });
      return worktree;
    });
  }

  readWorktree(id: string): Worktree {
    const row = this.database.prepare('SELECT data FROM worktrees WHERE id=?').get(id);
    if (!row) throw new Error('worktree not found');
    return JSON.parse(String(row['data'])) as Worktree;
  }

  findWorktreeByPath(path:string):Worktree|undefined {
    const row=this.database.prepare('SELECT data FROM worktrees WHERE path=?').get(path);
    return row?JSON.parse(String(row['data'])) as Worktree:undefined;
  }

  /** Bounded original-claim finalization; never probes Git or rewrites an existing anchor. */
  async recordWorktreePreparation(input:{id:string;claimId:string;token:string}) {
    return this.transaction(()=>{
      const claim=this.readClaim(input.claimId);
      if(claim.token!==input.token||claim.kind!=='worktree'||claim.resourceKey!==input.id||!claim.invocationId)throw new Error('claim/token no longer matches worktree');
      const invocation=this.readInvocation(claim.invocationId),worktree=this.readWorktree(input.id);
      if(invocation.stage==='finalized'||worktree.registration!=='reserved'||worktree.preparation)throw new Error('preparation evidence cannot be replaced');
      worktree.preparation={identity:preparationIdentity(worktree.path),invocationId:invocation.id,claimId:claim.id};
      this.database.prepare('UPDATE worktrees SET data=? WHERE id=?').run(JSON.stringify(worktree),worktree.id);
      this.event('worktree.preparation_saved',{worktreeId:worktree.id,invocationId:invocation.id,claimId:claim.id});
    });
  }

  async reconcileWorktreePreparation(input:{id:string;claimId:string;token:string;registration:string}) {
    text(input.registration,'Git registration');
    return this.transaction(()=>{
      this.ready();
      const claim=this.readClaim(input.claimId);
      if(claim.token!==input.token||claim.kind!=='worktree'||claim.resourceKey!==input.id||!claim.invocationId)throw new Error('claim/token no longer matches worktree');
      const current=this.readInvocation(claim.invocationId),worktree=this.readWorktree(input.id),saved=worktree.preparation;
      if(current.stage!=='starting'||this.blockedInvocations.has(current.id)||worktree.registration!=='reserved')throw new Error('prepared worktree is not eligible for reconciliation');
      if(!saved)throw new Error('reserved worktree lacks original preparation identity evidence; explicit recovery required');
      const prior=this.readInvocation(saved.invocationId);
      if(prior.worktreeId!==worktree.id||prior.runId!==current.runId||prior.id===current.id)throw new Error('prepared checkout recovery requires the original retained run');
      if(!(prior.stage==='finalized'&&prior.cleanup==='complete')&&!this.database.prepare('SELECT id FROM clearances WHERE claim_id=?').get(saved.claimId))throw new Error('original preparation requires safe cleanup or exact operator clearance');
      if(this.database.prepare('SELECT a.id FROM attempts a JOIN invocations i ON i.id=a.invocation_id WHERE i.worktree_id=? AND a.occupied=1 LIMIT 1').get(worktree.id))throw new Error('prepared worktree activity remains occupied');
      assertPreparationIdentity(worktree.path,saved.identity);
      worktree.registration=input.registration;
      this.database.prepare('UPDATE worktrees SET data=? WHERE id=?').run(JSON.stringify(worktree),worktree.id);
      this.event('worktree.reconciled',{worktreeId:worktree.id,invocationId:current.id,preparationInvocationId:prior.id,claimId:claim.id});
    });
  }

  async finalizeWorktree(input: { id: string; claimId: string; token: string; registration: string }) {
    text(input.registration, 'Git registration');
    return this.transaction(() => {
      const claim = this.database.prepare('SELECT resource_key FROM owner_claims WHERE id=? AND token=? AND kind=?').get(input.claimId, input.token, 'worktree');
      if (!claim || claim['resource_key'] !== input.id) throw new Error('claim/token no longer matches worktree');
      const worktree = this.readWorktree(input.id);
      if (worktree.registration !== 'reserved') throw new Error('worktree is not reserved');
      if (realpathSync(worktree.path) !== worktree.path) throw new Error('worktree destination changed');
      worktree.registration = input.registration;
      this.database.prepare('UPDATE worktrees SET data=? WHERE id=?').run(JSON.stringify(worktree), input.id);
      this.event('worktree.registered', { worktreeId: input.id });
    });
  }

  hasOccupiedActivity(invocationId: string) {
    this.readInvocation(invocationId);
    return !!this.database.prepare('SELECT id FROM attempts WHERE invocation_id=? AND occupied=1 LIMIT 1').get(invocationId);
  }

  readInvocationCapture(input: { invocationId: string; id: string; after?: number; limit?: number }) {
    const row=this.database.prepare('SELECT attempt_id FROM captures WHERE id=? AND invocation_id=?').get(input.id,input.invocationId);
    if (!row) throw new Error('capture does not belong to selected invocation');
    return { id: input.id, attemptId:row['attempt_id']===null?null:String(row['attempt_id']), ...this.readCapture(input) };
  }

  /** Bounded detail pages expose independent row and text cursors; never join full captures. */
  readHistory(id: string, options: { afterAttempt?: number; afterCapture?: number; limit?: number } = {}) {
    const afterAttempt = options.afterAttempt ?? 0, afterCapture = options.afterCapture ?? 0, limit = options.limit ?? 50;
    if (![afterAttempt, afterCapture].every(value => Number.isSafeInteger(value) && value >= 0) || !Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error('invalid history page');
    const invocation = this.readInvocation(id);
    const attemptRows = this.database.prepare('SELECT rowid AS cursor,data FROM attempts WHERE invocation_id=? AND rowid>? ORDER BY rowid LIMIT ?').all(id, afterAttempt, limit + 1);
    const attempts = attemptRows.slice(0, limit).map(row => JSON.parse(String(row['data'])) as Attempt);
    const captureRows = this.database.prepare('SELECT rowid AS cursor,id,attempt_id,state,channel,sequence FROM captures WHERE invocation_id=? AND rowid>? ORDER BY rowid LIMIT ?').all(id, afterCapture, limit + 1);
    let textBytes = 0;
    const captures = captureRows.slice(0, limit).map(row => {
      const captureId = String(row['id']);
      const page = this.readCapture({ id: captureId, limit: 200, byteBudget: 262144 - textBytes });
      const chunks: CaptureChunk[] = [];
      for (const chunk of page.chunks) {
        const size = Buffer.byteLength(JSON.stringify(chunk));
        if (textBytes + size > 262144) break;
        textBytes += size; chunks.push(chunk);
      }
      const nextSequence = chunks.at(-1)?.sequence ?? 0;
      return { id: captureId, attemptId: row['attempt_id']===null?null:String(row['attempt_id']), state: page.state, channel: page.channel, chunks, nextSequence,
        hasMore: page.state !== 'pruned' && nextSequence < Number(row['sequence']) };
    });
    const clearanceRow = this.database.prepare("SELECT data FROM clearances WHERE json_extract(data,'$.invocationId')=? ORDER BY rowid DESC LIMIT 1").get(id);
    return { invocation, worktree: this.readWorktree(invocation.worktreeId), attempts, captures, notifications: this.readNotificationDeliveries(id), acknowledgment: this.readNotificationAcknowledgment(id), accounting: this.readAccounting(invocation.runId),
      clearance: clearanceRow ? JSON.parse(String(clearanceRow['data'])) as Clearance : null,
      attemptsNextCursor: Number(attemptRows.slice(0, limit).at(-1)?.['cursor'] ?? afterAttempt), hasMoreAttempts: attemptRows.length > limit,
      capturesNextCursor: Number(captureRows.slice(0, limit).at(-1)?.['cursor'] ?? afterCapture), hasMoreCaptures: captureRows.length > limit };
  }

  validateReference(input: { id: string; runId: string; question?: boolean }) {
    const row = this.database.prepare('SELECT c.channel,c.state,i.run_id FROM captures c JOIN invocations i ON c.invocation_id=i.id WHERE c.id=?').get(input.id);
    if (!row || row['run_id'] !== input.runId || row['state'] !== 'complete' || (input.question && row['channel'] !== 'request')) throw new Error('missing, incomplete or foreign-run context reference');
  }

  async saveInvocationMetadata(id: string, metadata: object) {
    return this.transaction(() => {
      const invocation = this.readInvocation(id);
      invocation.metadata = metadata;
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation), id);
      this.event('invocation.inputs', { invocationId: id });
    });
  }

  async finishInvocation(id: string, outcome: string, cleanup: 'complete' | 'unknown') {
    return this.transaction(() => {
      const invocation = this.readInvocation(id);
      if (invocation.stage === 'finalized') throw new Error('invocation already finalized');
      if (cleanup === 'complete' && this.database.prepare('SELECT id FROM attempts WHERE invocation_id=? AND occupied=1').get(id)) throw new Error('activity is not quiescent');
      invocation.stage = 'finalized'; invocation.outcome = outcome; invocation.cleanup = cleanup;
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation), id);
      this.recordNotificationAttention(invocation);
      this.event('invocation.finalized', { invocationId: id, outcome, cleanup });
    });
  }

  async finalizeInvocation(input: {id:string;outcome:string;cleanup:'complete'|'unknown';claimId:string;token:string;retainClaim?:boolean | 'successPreference'}) {
    if (!['succeeded','failed','needs_input','interrupted','cancelled'].includes(input.outcome) || !['complete','unknown'].includes(input.cleanup)) throw new Error('invalid finalization facts');
    return this.transaction(() => {
      const claim = this.database.prepare('SELECT id FROM owner_claims WHERE id=? AND token=? AND invocation_id=?').get(input.claimId,input.token,input.id);
      if (!claim) throw new Error('claim/token no longer matches invocation');
      const invocation = this.readInvocation(input.id);
      if (invocation.stage === 'finalized') throw new Error('invocation already finalized');
      if (input.cleanup === 'complete' && this.hasOccupiedActivity(input.id)) throw new Error('activity is not quiescent');
      if (input.outcome === 'succeeded' && input.cleanup !== 'complete') throw new Error('success requires complete cleanup');
      const successNoticePlanned = input.outcome === 'succeeded' && input.retainClaim === 'successPreference' && this.readNotificationPreferences().successNotices;
      invocation.stage = 'finalized'; invocation.outcome = input.outcome; invocation.cleanup = input.cleanup;
      if (successNoticePlanned) invocation.successNoticePlanned = true;
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation),input.id);
      this.recordNotificationAttention(invocation);
      this.event('invocation.finalized',{invocationId:input.id,outcome:input.outcome,cleanup:input.cleanup});
      if (input.cleanup === 'complete' && input.retainClaim !== true && !successNoticePlanned) {
        this.database.prepare('DELETE FROM owner_claims WHERE id=? AND token=?').run(input.claimId,input.token);
        this.event('owner.released',{claimId:input.claimId,basis:'quiescent'});
      }
      return { successNoticePlanned };
    });
  }

  async startInvocation(input: { runId: string; worktreeId: string; owner: Owner }): Promise<Invocation & { claim: Claim }> {
    validateOwner(input.owner);
    return this.transaction(() => {
      this.ready();
      if (this.database.prepare("SELECT id FROM owner_claims WHERE kind='worktree' AND resource_key=?").get(input.worktreeId)) throw new Error('worktree already claimed');
      const invocation: Invocation = { id: randomUUID(), runId: input.runId, worktreeId: input.worktreeId, stage: 'starting', outcome: null };
      const claim: Claim = { id: randomUUID(), token: randomUUID(), kind: 'worktree', resourceKey: input.worktreeId, invocationId: invocation.id, owner: input.owner };
      this.database.prepare('INSERT INTO invocations(id,run_id,worktree_id,data) VALUES (?,?,?,?)').run(invocation.id, invocation.runId, invocation.worktreeId, JSON.stringify(invocation));
      this.database.prepare('INSERT INTO owner_claims(id,token,kind,resource_key,invocation_id,data) VALUES (?,?,?,?,?,?)')
        .run(claim.id, claim.token, claim.kind, claim.resourceKey, claim.invocationId, JSON.stringify(claim));
      this.event('invocation.started', { invocationId: invocation.id, runId: invocation.runId });
      this.event('owner.claimed', { claimId: claim.id, invocationId: invocation.id });
      return { ...invocation, claim };
    });
  }

  readInvocation(id: string): Invocation {
    const row = this.database.prepare('SELECT data FROM invocations WHERE id=?').get(id);
    if (!row) throw new Error('invocation not found');
    return JSON.parse(String(row['data'])) as Invocation;
  }

  readNotificationDeliveries(invocationId: string): NotificationDelivery[] {
    this.readInvocation(invocationId);
    return this.database.prepare('SELECT data FROM notification_deliveries WHERE invocation_id=? ORDER BY rowid LIMIT 1').all(invocationId)
      .map(row => JSON.parse(String(row['data'])) as NotificationDelivery);
  }

  readNotificationPreferences(): NotificationPreferences {
    const row = this.database.prepare('SELECT success_notices,reminders,updated_at FROM notification_preferences WHERE id=1').get();
    return row ? { successNotices: row['success_notices'] === 1, reminders: row['reminders'] === 1, updatedAt: String(row['updated_at']) }
      : { successNotices: false, reminders: false, updatedAt: null };
  }

  private recordNotificationAttention(invocation: Invocation) {
    const questions = this.database.prepare("SELECT id FROM captures WHERE invocation_id=? AND channel='request' AND state='complete' LIMIT 1").get(invocation.id);
    if (invocation.outcome !== 'succeeded' || invocation.cleanup === 'unknown' || questions)
      this.database.prepare('INSERT OR IGNORE INTO notification_attention(invocation_id) VALUES (?)').run(invocation.id);
  }

  readReminderGroups(options: { limit?: number } = {}) {
    const limit = options.limit ?? 20;
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error('invalid reminder page');
    const rows = this.database.prepare('SELECT data FROM notification_reminder_groups ORDER BY rowid DESC LIMIT ?').all(limit + 1);
    return { groups: rows.slice(0, limit).map(row => JSON.parse(String(row['data'])) as ReminderGroup), hasMore: rows.length > limit };
  }

  private requireDashboardClaim(claim: Claim) {
    const row = this.database.prepare("SELECT token,data FROM owner_claims WHERE id=? AND kind='dashboard' AND resource_key=?").get(claim.id, claim.resourceKey);
    if (!row || row['token'] !== claim.token || JSON.stringify(JSON.parse(String(row['data']))) !== JSON.stringify(claim))
      throw new Error('dashboard claim changed');
  }

  /** A committed identity is never reused after a crash or uncertain submission. */
  async reserveReminderGroup(claim: Claim): Promise<ReminderGroup | null> {
    return this.transaction(() => {
      this.requireDashboardClaim(claim);
      if (!this.readNotificationPreferences().reminders) return null;
      if (this.database.prepare('SELECT id FROM notification_reminder_groups WHERE claim_id=? AND unsettled=1 LIMIT 1').get(claim.id))
        throw new Error('reminder cleanup or recording remains unknown');
      const rows = this.database.prepare('SELECT a.invocation_id FROM notification_attention a LEFT JOIN notification_acknowledgments k ON k.invocation_id=a.invocation_id WHERE k.invocation_id IS NULL ORDER BY a.rowid LIMIT 101').all();
      if (!rows.length) return null;
      const invocationIds = rows.slice(0, 100).map(row => String(row['invocation_id']));
      const at = new Date().toISOString();
      const group: ReminderGroup = { id: randomUUID(), kind: 'reminder', claimId: claim.id, invocationIds, count: invocationIds.length, hasMore: rows.length > 100,
        state: 'reserved', cleanup: 'unknown', visibleDelivery: false, createdAt: at, updatedAt: at };
      this.database.prepare('INSERT INTO notification_reminder_groups(id,claim_id,unsettled,data) VALUES (?,?,1,?)').run(group.id, claim.id, JSON.stringify(group));
      this.event('notification.reminder_reserved', { groupId: group.id, count: group.count, hasMore: group.hasMore });
      return group;
    });
  }

  async saveReminderGroupResult(claim: Claim, id: string, result: { state: NotificationDelivery['state']; reason?: string; cleanup: NotificationDelivery['cleanup'] }): Promise<ReminderGroup> {
    if (!['submitted','failed','timed_out','unknown'].includes(result.state) || !['complete','unknown'].includes(result.cleanup) ||
      (result.cleanup === 'unknown' && result.state !== 'unknown') ||
      (result.reason !== undefined && (typeof result.reason !== 'string' || !/^[a-z_]{1,64}$/.test(result.reason)))) throw new Error('invalid reminder result');
    return this.transaction(() => {
      this.requireDashboardClaim(claim);
      const row = this.database.prepare('SELECT claim_id,data FROM notification_reminder_groups WHERE id=?').get(id);
      if (!row || row['claim_id'] !== claim.id) throw new Error('reminder reservation missing');
      const saved = JSON.parse(String(row['data'])) as ReminderGroup;
      if (saved.state !== 'reserved') return saved;
      const record: ReminderGroup = { ...saved, state: result.state, cleanup: result.cleanup, updatedAt: new Date().toISOString() };
      if (result.reason !== undefined) record.reason = result.reason;
      this.database.prepare('UPDATE notification_reminder_groups SET unsettled=?,data=? WHERE id=?').run(result.cleanup === 'unknown' ? 1 : 0, JSON.stringify(record), id);
      this.event('notification.reminder_recorded', { groupId: id, state: record.state });
      return record;
    });
  }

  async saveNotificationPreferences(input: unknown): Promise<NotificationPreferences> {
    if (!exactObject(input, ['successNotices', 'reminders']) || typeof input['successNotices'] !== 'boolean' || typeof input['reminders'] !== 'boolean')
      throw new NotificationMetadataError(400, 'invalid notification preferences');
    return this.transaction(() => {
      this.ready();
      const updatedAt = new Date().toISOString();
      this.database.prepare('INSERT INTO notification_preferences(id,success_notices,reminders,updated_at) VALUES (1,?,?,?) ON CONFLICT(id) DO UPDATE SET success_notices=excluded.success_notices,reminders=excluded.reminders,updated_at=excluded.updated_at')
        .run(input['successNotices'] ? 1 : 0, input['reminders'] ? 1 : 0, updatedAt);
      this.event('notification.preferences_saved', {});
      return this.readNotificationPreferences();
    });
  }

  readNotificationAcknowledgment(invocationId: string): NotificationAcknowledgment | null {
    this.readInvocation(invocationId);
    const row = this.database.prepare('SELECT acknowledged_at FROM notification_acknowledgments WHERE invocation_id=?').get(invocationId);
    return row ? { id: `${invocationId}:acknowledgment`, invocationId, acknowledgedAt: String(row['acknowledged_at']) } : null;
  }

  async acknowledgeNotification(input: unknown): Promise<NotificationAcknowledgment> {
    if (!exactObject(input, ['invocationId']) || typeof input['invocationId'] !== 'string' || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(input['invocationId']))
      throw new NotificationMetadataError(400, 'invalid acknowledgment target');
    const invocationId = input['invocationId'];
    return this.transaction(() => {
      this.ready();
      let invocation: Invocation;
      try { invocation = this.readInvocation(invocationId); }
      catch (error) {
        if (error instanceof Error && error.message === 'invocation not found') throw new NotificationMetadataError(404, error.message);
        throw error;
      }
      if (invocation.stage !== 'finalized') throw new NotificationMetadataError(400, 'acknowledgment requires a finalized invocation');
      const existing = this.readNotificationAcknowledgment(invocationId);
      if (existing) return existing;
      const acknowledgedAt = new Date().toISOString();
      this.database.prepare('INSERT INTO notification_acknowledgments(invocation_id,acknowledged_at) VALUES (?,?)').run(invocationId, acknowledgedAt);
      this.event('notification.acknowledged', { invocationId });
      return { id: `${invocationId}:acknowledgment`, invocationId, acknowledgedAt };
    });
  }

  /** Reserve once after finalization. Unknown is durable before any external submission. */
  async reserveInitialNotification(invocationId: string): Promise<NotificationDelivery | null> {
    return this.transaction(() => {
      const invocation = this.readInvocation(invocationId);
      if (invocation.stage !== 'finalized' || !invocation.cleanup) throw new Error('notification requires a saved final summary');
      const questions = Number(this.database.prepare("SELECT count(*) AS count FROM captures WHERE invocation_id=? AND channel='request' AND state='complete'").get(invocationId)?.['count'] ?? 0);
      if (invocation.outcome === 'succeeded' && !invocation.successNoticePlanned) return null;
      const id = `${invocationId}:initial`;
      if (this.database.prepare('SELECT id FROM notification_deliveries WHERE id=?').get(id)) return null;
      const at = new Date().toISOString();
      const record: NotificationDelivery = { id, invocationId, kind: 'initial', state: 'unknown', reason: 'submission_unconfirmed', cleanup: 'unknown', visibleDelivery: false,
        issues: { outcome: invocation.outcome ?? 'unknown', cleanup: invocation.cleanup, questions }, createdAt: at, updatedAt: at };
      this.database.prepare('INSERT INTO notification_deliveries(id,invocation_id,kind,data) VALUES (?,?,?,?)').run(id, invocationId, 'initial', JSON.stringify(record));
      return record;
    });
  }

  async saveInitialNotificationResult(id: string, result: { state: NotificationDelivery['state']; reason?: string; cleanup: NotificationDelivery['cleanup'] }): Promise<NotificationDelivery> {
    if (!['submitted','failed','timed_out','unknown'].includes(result.state) || !['complete','unknown'].includes(result.cleanup) ||
      (result.cleanup === 'unknown' && result.state !== 'unknown') ||
      (result.reason !== undefined && (typeof result.reason !== 'string' || !/^[a-z_]{1,64}$/.test(result.reason)))) throw new Error('invalid notification result');
    return this.transaction(() => {
      const row = this.database.prepare('SELECT data FROM notification_deliveries WHERE id=?').get(id);
      if (!row) throw new Error('notification reservation missing');
      const saved = JSON.parse(String(row['data'])) as NotificationDelivery;
      if (saved.reason !== 'submission_unconfirmed') return saved;
      const record: NotificationDelivery = { ...saved, state: result.state, cleanup: result.cleanup, updatedAt: new Date().toISOString() };
      if (result.reason === undefined) delete record.reason;
      else record.reason = result.reason;
      this.database.prepare('UPDATE notification_deliveries SET data=? WHERE id=?').run(JSON.stringify(record), id);
      return record;
    });
  }

  async activateInvocation(id: string) {
    return this.transaction(() => {
      this.ready();
      const invocation = this.readInvocation(id);
      if (invocation.stage !== 'starting' || !this.database.prepare('SELECT id FROM owner_claims WHERE invocation_id=?').get(id)) throw new Error('invocation is not eligible for activation');
      invocation.stage = 'running';
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation), id);
      this.event('invocation.running', { invocationId: id });
    });
  }

  async stopAdmissions(id: string) {
    return this.transaction(() => {
      const invocation = this.readInvocation(id);
      if (invocation.stage === 'shutting_down' || invocation.stage === 'finalized') return;
      invocation.stage = 'shutting_down';
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation), id);
      this.event('invocation.shutting_down', { invocationId: id });
    });
  }

  async increaseAllowances(input: { runId: string; additionalLimit?: number; codeLimit?: number; formatLimit?: number; reason: string }) {
    text(input.reason, 'increase reason');
    if (input.additionalLimit === undefined && input.codeLimit === undefined && input.formatLimit === undefined) throw new Error('specify an explicit increase');
    return this.transaction(() => {
      this.ready();
      const row = this.database.prepare('SELECT data FROM runs WHERE id=?').get(input.runId);
      if (!row) throw new Error('run not found');
      const run = JSON.parse(String(row['data'])) as Run;
      run.additionalLimit = increase(run.additionalLimit, input.additionalLimit);
      run.codeLimit = increase(run.codeLimit, input.codeLimit);
      run.formatLimit = increase(run.formatLimit, input.formatLimit);
      this.database.prepare('UPDATE runs SET data=? WHERE id=?').run(JSON.stringify(run), run.id);
      this.event('allowances.increased', { ...run, reason: input.reason });
      return run;
    });
  }

  async increaseCapacity(input: { agentLimit?: number; commandLimit?: number; reason: string }) {
    text(input.reason, 'capacity increase reason');
    if (input.agentLimit === undefined && input.commandLimit === undefined) throw new Error('specify an explicit increase');
    return this.transaction(() => {
      this.ready();
      const row = this.database.prepare('SELECT agent_limit,command_limit FROM repository').get()!;
      const agents = increase(Number(row['agent_limit']), input.agentLimit);
      const commands = increase(Number(row['command_limit']), input.commandLimit);
      this.database.prepare('UPDATE repository SET agent_limit=?,command_limit=?').run(agents, commands);
      this.event('capacity.increased', { agents, commands, reason: input.reason });
    });
  }

  readAttempt(id: string): Attempt {
    const row = this.database.prepare('SELECT data FROM attempts WHERE id=?').get(id);
    if (!row) throw new Error('attempt not found');
    return JSON.parse(String(row['data'])) as Attempt;
  }

  readAccounting(runId: string) {
    if (!this.database.prepare('SELECT id FROM runs WHERE id=?').get(runId)) throw new Error('run not found');
    return {
      additionalUsed: Number(this.database.prepare("SELECT coalesce(sum(delta),0) AS n FROM allowance_ledger WHERE run_id=? AND category='additional'").get(runId)?.['n']),
      occupiedAgents: Number(this.database.prepare("SELECT count(*) AS n FROM attempts WHERE kind='agent' AND occupied=1").get()?.['n']),
      occupiedCommands: Number(this.database.prepare("SELECT count(*) AS n FROM attempts WHERE kind='command' AND occupied=1").get()?.['n']),
    };
  }

  private used(runId: string, category: string, scope: string): number {
    return Number(this.database.prepare('SELECT coalesce(sum(delta),0) AS n FROM allowance_ledger WHERE run_id=? AND category=? AND scope=?').get(runId, category, scope)?.['n']);
  }

  async admitAttempt(input: Admission, startup = false): Promise<Attempt> {
    validateAdmission(input);
    const fingerprint = JSON.stringify([input.id, input.invocationId, input.operationKey, input.kind, input.intent, input.priorAttemptId ?? null, input.loopKey ?? null]);
    return this.transaction(() => {
      if (this.blockedInvocations.has(input.invocationId)) throw new Error('capture failure blocks admission');
      const existing = this.database.prepare('SELECT data FROM attempts WHERE id=?').get(input.id);
      if (existing) {
        const attempt = JSON.parse(String(existing['data'])) as Attempt;
        if (attempt.fingerprint !== fingerprint) throw new Error('attempt identity reused with different inputs');
        return attempt; // Uncertain commit acknowledgement resolves by identity without another debit.
      }
      this.ready();
      const invocation = this.readInvocation(input.invocationId);
      if ((invocation.stage !== 'running' && !(startup && invocation.stage === 'starting' && input.kind === 'command' && (input.operationKey === `startup/build/${invocation.id}` || (input.operationKey.startsWith('startup/git/') && input.operationKey.endsWith(`/${invocation.id}`))))) || !this.database.prepare('SELECT id FROM owner_claims WHERE invocation_id=?').get(invocation.id)) throw new Error('invocation not eligible for admission');
      const limits = this.database.prepare('SELECT agent_limit,command_limit FROM repository').get()!;
      const capacity = Number(limits[input.kind === 'agent' ? 'agent_limit' : 'command_limit']);
      if (Number(this.database.prepare('SELECT count(*) AS n FROM attempts WHERE kind=? AND occupied=1').get(input.kind)?.['n']) >= capacity) throw new Error(`${input.kind} capacity exhausted`);
      const operation = this.database.prepare('SELECT id,data FROM operations WHERE run_id=? AND operation_key=?').get(invocation.runId, input.operationKey);
      const original = operation ? JSON.parse(String(operation['data'])) as { loopKey: string; kind: string } : null;
      const loopKey = input.loopKey ?? original?.loopKey ?? input.operationKey;
      if (original && (loopKey !== original.loopKey || original.kind !== input.kind)) throw new Error('operation identity cannot change kind or loop lineage');
      if (input.intent === 'initial' && (operation || input.priorAttemptId)) throw new Error('operation repeat requires additional allowance and lineage');
      if (input.intent !== 'initial') {
        if (!input.priorAttemptId) throw new Error('additional work requires prior attempt lineage');
        const prior = this.readAttempt(input.priorAttemptId);
        if (prior.runId !== invocation.runId) throw new Error('prior attempt belongs to another run');
        if (input.intent === 'format_correction') {
          let ancestor: Attempt | undefined = prior;
          while (ancestor) {
            if (ancestor.intent === 'format_correction') throw new Error('format correction cannot correct a format correction lineage');
            ancestor = ancestor.priorAttemptId ? this.readAttempt(ancestor.priorAttemptId) : undefined;
          }
        }
        const clearedFollowup = input.intent === 'followup' && prior.invocationId !== invocation.id && prior.cleanupBasis === 'operator_confirmed';
        if (!prior.quiescent || (prior.outcome === null && !clearedFollowup)) throw new Error('prior activity is not quiescent');
        const previousOperation = this.database.prepare('SELECT data FROM operations WHERE id=?').get(prior.operationId);
        const priorLoop = (JSON.parse(String(previousOperation?.['data'])) as { loopKey: string }).loopKey;
        if (priorLoop !== loopKey) throw new Error('loop lineage cannot change across additional work');
      }
      const run = JSON.parse(String(this.database.prepare('SELECT data FROM runs WHERE id=?').get(invocation.runId)?.['data'])) as Run;
      const charges: { category: string; scope: string; limit: number; diagnostic: string }[] = [];
      if (input.kind === 'agent' && input.intent !== 'initial') charges.push({ category: 'additional', scope: run.id, limit: run.additionalLimit, diagnostic: 'additional agent allowance' });
      if (input.intent === 'code_correction') charges.push({ category: 'code', scope: loopKey, limit: run.codeLimit, diagnostic: 'code correction allowance' });
      if (input.intent === 'format_correction') charges.push({ category: 'format', scope: input.priorAttemptId!, limit: run.formatLimit, diagnostic: 'format correction allowance' });
      for (const charge of charges) if (this.used(run.id, charge.category, charge.scope) >= charge.limit) throw new Error(`${charge.diagnostic} exhausted`);
      const operationId = operation ? String(operation['id']) : randomUUID();
      if (!operation) this.database.prepare('INSERT INTO operations(id,run_id,operation_key,data) VALUES (?,?,?,?)')
        .run(operationId, invocation.runId, input.operationKey, JSON.stringify({ loopKey, kind: input.kind }));
      const attempt: Attempt = { ...input, runId: invocation.runId, operationId, fingerprint, launch: 'admitted', outcome: null, quiescent: false, owner: null, evidence: null };
      this.database.prepare('INSERT INTO attempts(id,invocation_id,operation_id,kind,occupied,data) VALUES (?,?,?,?,1,?)')
        .run(attempt.id, attempt.invocationId, operationId, input.kind, JSON.stringify(attempt));
      for (const charge of charges) this.database.prepare('INSERT INTO allowance_ledger(id,attempt_id,run_id,scope,category,delta) VALUES (?,?,?,?,?,1)')
        .run(randomUUID(), attempt.id, run.id, charge.scope, charge.category);
      this.event('attempt.admitted', { attemptId: attempt.id, invocationId: invocation.id });
      return attempt;
    });
  }

  async markStarted(input: { id: string; owner: Owner }) {
    validateOwner(input.owner);
    return this.transaction(() => {
      const attempt = this.readAttempt(input.id);
      if (attempt.cleanupBasis === 'operator_confirmed') throw new Error('cleared attempt cannot be started again');
      if (attempt.launch !== 'admitted' || attempt.outcome !== null) throw new Error('attempt cannot be marked started');
      attempt.launch = 'started'; attempt.owner = input.owner;
      this.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify(attempt), attempt.id);
      this.event('attempt.started', { attemptId: attempt.id, invocationId: attempt.invocationId });
    });
  }

  async settleAttempt(input: { id: string; launch: 'started' | 'not_started' | 'unknown'; outcome: Exclude<Attempt['outcome'], null>; quiescent: boolean; evidence: string; validatedResultCaptureId?: string }) {
    text(input.evidence, 'settlement evidence');
    if (!['started', 'not_started', 'unknown'].includes(input.launch)
      || !['succeeded', 'failed', 'needs_input', 'interrupted'].includes(input.outcome)
      || typeof input.quiescent !== 'boolean') throw new Error('invalid settlement facts');
    return this.transaction(() => {
      const attempt = this.readAttempt(input.id);
      if (attempt.cleanupBasis === 'operator_confirmed' && !input.quiescent) throw new Error('settlement cannot undo explicit clearance');
      if (attempt.outcome !== null) {
        if (attempt.launch === input.launch && attempt.outcome === input.outcome && attempt.quiescent === input.quiescent && attempt.evidence === input.evidence
          && (input.validatedResultCaptureId === undefined || input.validatedResultCaptureId === attempt.agent?.validatedResultCaptureId)) return attempt;
        throw new Error('attempt already settled; preserve terminal outcome');
      }
      if (attempt.launch === 'started' && input.launch !== 'started') throw new Error('confirmed launch cannot be erased or refunded');
      if (input.launch === 'started' && attempt.launch !== 'started') throw new Error('record confirmed spawn identity before settlement');
      if (input.launch === 'not_started' && (!input.quiescent || input.outcome === 'succeeded')) throw new Error('non-launch requires quiescence and cannot succeed');
      if (attempt.kind === 'agent' && attempt.agent && input.outcome === 'succeeded' && input.validatedResultCaptureId === undefined)
        throw new Error('successful agent settlement requires a validated result capture');
      if (input.validatedResultCaptureId !== undefined) {
        if (attempt.kind !== 'agent' || !attempt.agent || input.launch !== 'started' || input.outcome !== 'succeeded' || !input.quiescent
          || typeof input.validatedResultCaptureId !== 'string'
          || !this.database.prepare("SELECT id FROM captures WHERE id=? AND attempt_id=? AND invocation_id=? AND channel='validated-result' AND state='complete'")
            .get(input.validatedResultCaptureId, attempt.id, attempt.invocationId)) throw new Error('validated result capture must be complete and owned by the successful agent attempt');
        attempt.agent.validatedResultCaptureId = input.validatedResultCaptureId;
      }
      attempt.launch = input.launch; attempt.outcome = input.outcome; attempt.quiescent = input.quiescent; attempt.evidence = input.evidence;
      this.database.prepare('UPDATE attempts SET data=?,occupied=? WHERE id=?').run(JSON.stringify(attempt), input.quiescent ? 0 : 1, attempt.id);
      if (input.launch === 'not_started') {
        for (const charge of this.database.prepare('SELECT category,scope FROM allowance_ledger WHERE attempt_id=? AND delta=1').all(attempt.id)) {
          this.database.prepare('INSERT INTO allowance_ledger(id,attempt_id,run_id,scope,category,delta) VALUES (?,?,?,?,?,-1)')
            .run(randomUUID(), attempt.id, attempt.runId, String(charge['scope']), String(charge['category']));
        }
      }
      this.event('attempt.settled', { attemptId: attempt.id, invocationId: attempt.invocationId, outcome: attempt.outcome, quiescent: attempt.quiescent });
    });
  }

  async saveAgentMetadata(id:string, metadata:NonNullable<Attempt['agent']>) {
    if (Object.hasOwn(metadata, 'validatedResultCaptureId')) throw new Error('validated result metadata can only be linked during successful settlement');
    if(Buffer.byteLength(JSON.stringify(metadata))>8192)throw new Error('agent metadata exceeds limit');
    return this.transaction(()=>{ const attempt=this.readAttempt(id); if(attempt.kind!=='agent'||attempt.launch!=='admitted')throw new Error('agent inputs must be saved before launch');
      for(const captureId of [metadata.inputsCaptureId,metadata.resultCaptureId,metadata.outputCaptureId])if(!this.database.prepare('SELECT id FROM captures WHERE id=? AND attempt_id=?').get(captureId,id))throw new Error('agent capture mismatch');
      attempt.agent=metadata;this.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify(attempt),id);this.event('attempt.inputs',{attemptId:id,invocationId:attempt.invocationId,inputsCaptureId:metadata.inputsCaptureId}); });
  }
  async saveSession(attemptId:string, event:SessionEvent): Promise<NativeSession> {
    if(!event || typeof event!=='object' || Array.isArray(event) || Object.keys(event).some(key=>!['nativeId','parentNativeId','lifecycle','usage','loadedSkills'].includes(key)))throw new Error('invalid session event');
    const raw=JSON.stringify(event);
    if(Buffer.byteLength(raw)>8192)throw new Error('session metadata exceeds limit');
    const filtered=JSON.parse(redactText(raw)) as SessionEvent;
    if(Buffer.byteLength(JSON.stringify(filtered))>8192)throw new Error('session metadata exceeds limit');
    if(!filtered.nativeId||typeof filtered.nativeId!=='string'||filtered.nativeId.length>512||!(filtered.parentNativeId===null||(typeof filtered.parentNativeId==='string'&&filtered.parentNativeId.length>0&&filtered.parentNativeId.length<=512))||!['running','succeeded','failed','stopped'].includes(filtered.lifecycle))throw new Error('invalid session event');
    if(filtered.usage !== undefined && (!filtered.usage || typeof filtered.usage!=='object' || Array.isArray(filtered.usage) || !Number.isSafeInteger(filtered.usage.tokens)||filtered.usage.tokens<0||!['self','includes-children'].includes(filtered.usage.scope)))throw new Error('invalid session usage');
    if(filtered.loadedSkills !== undefined && (!Array.isArray(filtered.loadedSkills)||filtered.loadedSkills.some(v=>typeof v!=='string'||!v)))throw new Error('invalid loaded-skill evidence');
    return this.transaction(()=>{const attempt=this.readAttempt(attemptId);if(attempt.kind!=='agent')throw new Error('session requires agent attempt');
      const prior=this.database.prepare('SELECT id FROM sessions WHERE attempt_id=? AND native_id=?').get(attemptId,filtered.nativeId);
      const session:NativeSession={id:prior?String(prior['id']):randomUUID(),attemptId,invocationId:attempt.invocationId,...filtered,usage:filtered.usage??{state:'unknown'},loadedSkills:filtered.loadedSkills??{state:'unknown'},inputsCaptureId:attempt.agent?.inputsCaptureId??null,outputCaptureId:attempt.agent?.outputCaptureId??null,resultCaptureId:attempt.agent?.resultCaptureId??null};
      if(prior)this.database.prepare('UPDATE sessions SET data=? WHERE id=?').run(JSON.stringify(session),session.id);
      else this.database.prepare('INSERT INTO sessions(id,invocation_id,attempt_id,native_id,data) VALUES (?,?,?,?,?)').run(session.id,attempt.invocationId,attemptId,filtered.nativeId,JSON.stringify(session));
      this.event('session.changed',{sessionId:session.id,attemptId,invocationId:attempt.invocationId,lifecycle:session.lifecycle});return session;});
  }
  readSessions(input:{invocationId:string;after?:number;limit?:number}) {
    this.readInvocation(input.invocationId);const after=input.after??0,limit=input.limit??50;
    if(!Number.isSafeInteger(after)||after<0||!Number.isSafeInteger(limit)||limit<1||limit>200)throw new Error('invalid session page');
    const rows=this.database.prepare('SELECT rowid AS cursor,data FROM sessions WHERE invocation_id=? AND rowid>? ORDER BY rowid LIMIT ?').all(input.invocationId,after,limit+1);
    const sessions:NativeSession[]=[];let bytes=0,nextCursor=after;
    for(const row of rows.slice(0,limit)){const data=String(row['data']);if(bytes+Buffer.byteLength(data)>1047552)break;bytes+=Buffer.byteLength(data);sessions.push(JSON.parse(data) as NativeSession);nextCursor=Number(row['cursor']);}
    return {sessions,nextCursor,hasMore:rows.some(row=>Number(row['cursor'])>nextCursor)};
  }

  readClaim(id: string): Claim {
    const row = this.database.prepare('SELECT data FROM owner_claims WHERE id=?').get(id);
    if (!row) throw new Error('claim not found');
    return JSON.parse(String(row['data'])) as Claim;
  }

  inspectActivity(invocationId: string) {
    const rows = this.database.prepare('SELECT data FROM attempts WHERE invocation_id=? AND occupied=1 ORDER BY rowid LIMIT 201').all(invocationId);
    return {attempts:rows.slice(0,200).map(row => JSON.parse(String(row['data'])) as Attempt),hasMore:rows.length > 200};
  }

  inspectOwners(): Claim[] {
    return this.database.prepare('SELECT data FROM owner_claims ORDER BY id LIMIT 200').all().map((row) => JSON.parse(String(row['data'])) as Claim);
  }

  async claimResource(input: { kind: 'dashboard' | 'maintenance'; owner: Owner }): Promise<Claim> {
    validateOwner(input.owner);
    if (!['dashboard', 'maintenance'].includes(input.kind)) throw new Error('invalid resource kind');
    return this.transaction(() => {
      this.ready();
      if (input.kind === 'maintenance' && this.database.prepare('SELECT id FROM owner_claims LIMIT 1').get()) throw new Error('active or uncertain owner blocks maintenance');
      if (this.database.prepare('SELECT id FROM owner_claims WHERE kind=?').get(input.kind)) throw new Error(`${input.kind} already claimed`);
      const resourceKey = String(this.database.prepare('SELECT id FROM repository').get()?.['id']);
      const claim: Claim = { id: randomUUID(), token: randomUUID(), kind: input.kind, resourceKey, invocationId: null, owner: input.owner };
      this.database.prepare('INSERT INTO owner_claims(id,token,kind,resource_key,invocation_id,data) VALUES (?,?,?,?,NULL,?)')
        .run(claim.id, claim.token, claim.kind, resourceKey, JSON.stringify(claim));
      this.event('owner.claimed', { claimId: claim.id, kind: claim.kind });
      return claim;
    });
  }

  /** One write transaction owns admission and the recoverable typed intent. */
  async beginMaintenance(intent: MaintenanceIntent, owner: Owner): Promise<Claim> {
    validateOwner(owner);
    if (intent.kind === 'dependencies') throw new Error('dependencies require exact installed selection admission');
    return this.transaction(() => {
      this.ready();
      if (this.database.prepare('SELECT id FROM owner_claims LIMIT 1').get()) throw new Error('active or uncertain owner blocks maintenance');
      const repositoryId = this.repositoryId();
      if (intent.repositoryId !== repositoryId || intent.phase !== 'preparing') throw new Error('maintenance intent does not match repository');
      const claim: Claim = { id: randomUUID(), token: randomUUID(), kind: 'maintenance', resourceKey: repositoryId,
        invocationId: null, owner, maintenance: intent };
      if (Buffer.byteLength(JSON.stringify(claim)) > 8192) throw new Error('maintenance claim exceeds limit');
      this.database.prepare('INSERT INTO owner_claims(id,token,kind,resource_key,invocation_id,data) VALUES (?,?,?,?,NULL,?)')
        .run(claim.id, claim.token, claim.kind, repositoryId, JSON.stringify(claim));
      this.event('maintenance.started', { operationId: intent.operationId, claimId: claim.id, kind: intent.kind });
      return claim;
    });
  }

  /** Admit only the current ready idle installation and its exact authenticated prior completion. */
  async beginDependencyMaintenance(intent: MaintenanceIntent, owner: Owner, validateOriginal: () => void): Promise<Claim> {
    validateOwner(owner);
    const boundOwner = { ...owner };
    validateDependencyMaintenanceBinding(intent.dependencies);
    if (inspectOwner(boundOwner).state !== 'known_live') throw new Error('dependency owner identity unavailable');
    return this.transaction(() => {
      this.ready();
      const repository = this.database.prepare('SELECT id,release,state FROM repository LIMIT 2').all();
      if (!this.forwardStorage || knownForwardShape(this.database) !== 'v7' || repository.length !== 1 || intent.kind !== 'dependencies'
        || intent.repositoryId !== repository[0]?.['id'] || intent.release !== repository[0]['release']
        || !/^[a-f0-9]{8}-[a-f0-9-]{27}$/i.test(intent.operationId) || !/^[a-f0-9]{64}$/.test(intent.selectionDigest)
        || intent.phase !== 'preparing' || intent.targetSchema !== 7 || !intent.targetReleaseSha256
        || !exactObject(intent.artifactDigests, ['bundle']) || intent.artifactDigests['bundle'] !== intent.targetReleaseSha256
        || intent.stagePath !== join(dirname(this.forwardStorage!.path), 'controller-staging', intent.operationId)
        || intent.backupId !== null || intent.candidate !== null || intent.forward !== undefined
        || intent.stageDigest !== null || intent.stageIdentity !== null || intent.ownedReceiptId !== null
        || intent.ticketConsumed || intent.ticketNonceHash !== null || intent.activeLauncher !== undefined
        || intent.upgradeIntentSha256 !== undefined || intent.upgradeReceipt !== undefined
        || intent.dependencies!.sourceIdentity !== this.forwardStorage?.identity
        || (intent.dependencies!.backupAttempt ?? null) !== null || (intent.dependencies!.backup ?? null) !== null || intent.dependencies!.candidateAttempt !== undefined
        || this.database.prepare('SELECT id FROM owner_claims LIMIT 1').get()
        || this.database.prepare('SELECT id FROM attempts WHERE occupied=1 LIMIT 1').get())
        throw new Error('dependency admission requires exact ready idle current installation');
      assertForwardIntegrity(this.database);
      const active = activeInstalledEvidence(this.database, intent.repositoryId, intent.release);
      if (createHash('sha256').update(JSON.stringify(active.completion)).digest('hex') !== intent.dependencies!.originalCompletionSha256
        || active.completion.manifestSha256 !== intent.targetReleaseSha256)
        throw new Error('dependency original completion changed before admission');
      validateOriginal();
      if (inspectOwner(boundOwner).state !== 'known_live') throw new Error('dependency owner changed before admission');
      const claim: Claim = { id: randomUUID(), token: randomUUID(), kind: 'maintenance', resourceKey: intent.repositoryId,
        invocationId: null, owner: boundOwner, maintenance: intent };
      const data = JSON.stringify(claim);
      if (Buffer.byteLength(data) > 8192) throw new Error('dependency maintenance claim exceeds limit');
      this.database.prepare("INSERT INTO owner_claims(id,token,kind,resource_key,invocation_id,data) VALUES (?,?,'maintenance',?,NULL,?)")
        .run(claim.id, claim.token, claim.resourceKey, data);
      this.event('maintenance.started', { operationId: intent.operationId, claimId: claim.id, kind: 'dependencies' });
      return claim;
    });
  }

  /** Exact capability check for read-only revalidation; no generic admission bypass or token replacement. */
  readDependencyMaintenance(handle: MaintenanceHandle) {
    this.assertForwardStorage();
    this.assertSoleMaintenance(handle);
    const claim = this.readMaintenanceClaim(handle.operationId), selected = claim.maintenance!;
    validateOwner(claim.owner);
    validateDependencyMaintenanceBinding(selected.dependencies);
    const repository = this.database.prepare('SELECT id,release,state FROM repository LIMIT 2').all();
    if (claim.kind !== 'maintenance' || claim.invocationId !== null || selected.kind !== 'dependencies'
      || !/^[a-f0-9]{64}$/.test(selected.selectionDigest) || selected.phase !== 'preparing' || selected.targetSchema !== 7
      || knownForwardShape(this.database) !== 'v7' || repository.length !== 1
      || repository[0]?.['id'] !== handle.repositoryId || repository[0]['release'] !== selected.release
      || repository[0]['state'] !== 'ready' || selected.dependencies.sourceIdentity !== this.forwardStorage?.identity
      || !pathAbsent(join(handle.commonDir, 'factory', 'upgrade-incomplete'))
      || this.forwardStorage?.path !== join(handle.commonDir, 'factory', 'history.sqlite')
      || (selected.backupId !== null && !/^[0-9a-f-]{36}$/i.test(selected.backupId))
      || (selected.backupId === null && ((selected.dependencies.backupAttempt ?? null) !== null || (selected.dependencies.backup ?? null) !== null))
      || (selected.dependencies.backup && (!selected.dependencies.backupAttempt || selected.dependencies.backup.id !== selected.backupId))
      || (selected.candidate !== null && (!selected.dependencies.candidateAttempt?.binding || !selected.dependencies.backup))
      || (selected.dependencies.candidateAttempt !== undefined && !selected.dependencies.backup) || selected.forward !== undefined
      || !exactObject(selected.artifactDigests, ['bundle']) || selected.artifactDigests['bundle'] !== selected.targetReleaseSha256
      || selected.stagePath !== join(handle.commonDir, 'factory/controller-staging', handle.operationId)
      || selected.ownedReceiptId !== null || selected.activeLauncher !== undefined || selected.upgradeIntentSha256 !== undefined
      || selected.upgradeReceipt !== undefined || selected.stageDigest !== null || selected.stageIdentity !== null
      || selected.ticketConsumed || selected.ticketNonceHash !== null)
      throw new Error('dependency claim/token/preparing original differs');
    assertForwardIntegrity(this.database);
    const active = activeInstalledEvidence(this.database, handle.repositoryId, selected.release);
    if (createHash('sha256').update(JSON.stringify(active.completion)).digest('hex') !== selected.dependencies.originalCompletionSha256
      || active.completion.manifestSha256 !== selected.targetReleaseSha256)
      throw new Error('dependency original completion changed after admission');
    return { claim, active };
  }

  private assertDependencyBackupOwner(claim: Claim): void {
    const owner = currentOwner();
    if (owner.host !== claim.owner.host || owner.pid !== claim.owner.pid || owner.start !== claim.owner.start
      || inspectOwner(owner).state !== 'known_live')
      throw new Error('dependency backup requires the exact live claim owner');
  }
  private saveDependencyBackupClaim(claim: Claim) {
    const data = JSON.stringify(claim);
    if (Buffer.byteLength(data) > 8192) throw new Error('dependency maintenance claim exceeds limit');
    this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?').run(data, claim.id, claim.token);
  }

  /** Allocate exactly one attempt before touching a backup directory. Failure never makes it eligible again. */
  async reserveDependencyBackupAttempt(handle: MaintenanceHandle, backupId: string, validateOriginal: () => void) {
    if (!/^[0-9a-f]{8}-[0-9a-f-]{27}$/i.test(backupId)) throw new Error('invalid dependency backup identity');
    return this.transaction(() => {
      const { claim } = this.readDependencyMaintenance(handle), selected = claim.maintenance!;
      this.assertDependencyBackupOwner(claim);
      if (selected.backupId !== null || selected.dependencies!.backupAttempt || selected.dependencies!.backup)
        throw new Error('dependency backup attempt already allocated; evidence retained');
      validateOriginal(); this.assertDependencyBackupOwner(claim);
      selected.backupId = backupId;
      selected.dependencies!.backupAttempt = null; selected.dependencies!.backup = null;
      this.saveDependencyBackupClaim(claim);
      this.event('maintenance.backup_attempted', { operationId: handle.operationId, claimId: claim.id, backupId });
    });
  }

  async bindDependencyBackupAttempt(handle: MaintenanceHandle, attempt: DependencyBackupAttemptBinding, validateOriginal: () => void) {
    validateDependencyBackupAttempt(attempt);
    return this.transaction(() => {
      const { claim } = this.readDependencyMaintenance(handle), selected = claim.maintenance!;
      this.assertDependencyBackupOwner(claim);
      if (!selected.backupId || selected.dependencies!.backupAttempt || selected.dependencies!.backup)
        throw new Error('dependency backup attempt cannot be rebound');
      validateOriginal(); this.assertDependencyBackupOwner(claim);
      selected.dependencies!.backupAttempt = attempt;
      this.saveDependencyBackupClaim(claim);
      this.event('maintenance.backup_attempt_bound', { operationId: handle.operationId, claimId: claim.id, backupId: selected.backupId });
    });
  }

  /** Receipt/bytes/counts verification is performed under the same exact final claim CAS. */
  async bindDependencyBackup(handle: MaintenanceHandle, backup: VerifiedMaintenanceBackup, validateBackup: () => void) {
    validateMaintenanceBackup(backup);
    return this.transaction(() => {
      const { claim } = this.readDependencyMaintenance(handle), selected = claim.maintenance!;
      this.assertDependencyBackupOwner(claim);
      if (!selected.dependencies!.backupAttempt || selected.dependencies!.backup || selected.backupId !== backup.id)
        throw new Error('dependency backup bind requires its sole immutable attempt');
      validateBackup(); this.assertDependencyBackupOwner(claim);
      selected.dependencies!.backup = backup;
      this.saveDependencyBackupClaim(claim);
      this.event('maintenance.backup_bound', { operationId: handle.operationId, claimId: claim.id, backupId: backup.id });
    });
  }

  /** Compare retained history in bounded pages and admit only this exact administrative suffix. */
  verifyDependencyBackupEvents(copied: DatabaseSync, claim: Claim): number {
    let cursor = 0n;
    for (;;) {
      const prior = copied.prepare('SELECT cursor,kind,data FROM observation_events WHERE cursor>? ORDER BY cursor LIMIT 128').all(cursor);
      if (!prior.length) break;
      const live = this.database.prepare('SELECT cursor,kind,data FROM observation_events WHERE cursor>? ORDER BY cursor LIMIT ?').all(cursor, prior.length);
      if (JSON.stringify(live) !== JSON.stringify(prior)) throw new Error('dependency backup historical events changed');
      cursor = BigInt(String(prior.at(-1)!['cursor']));
    }
    const suffix = this.database.prepare('SELECT cursor,kind,data FROM observation_events WHERE cursor>? ORDER BY cursor LIMIT 5').all(cursor);
    const selected = claim.maintenance!, attempt = selected.dependencies!.candidateAttempt;
    const expected = selected.dependencies!.backup ? [
      { kind: 'maintenance.backup_bound', data: { operationId: selected.operationId, claimId: claim.id, backupId: selected.backupId } },
      ...(attempt ? [{ kind: 'maintenance.candidate_attempted', data: { operationId: selected.operationId, claimId: claim.id, candidateId: attempt.id } }] : []),
      ...(attempt?.binding ? [{ kind: 'maintenance.candidate_attempt_bound', data: { operationId: selected.operationId, claimId: claim.id, candidateId: attempt.id, attemptSha256: attempt.binding.sha256 } }] : []),
      ...(selected.candidate ? [{ kind: 'maintenance.candidate_bound', data: { operationId: selected.operationId, claimId: claim.id, candidateId: attempt!.id, receiptSha256: selected.candidate.receiptSha256 } }] : [])
    ] : [];
    if (suffix.length !== expected.length || (attempt && attempt.events.length !== expected.length)) throw new Error('dependency backup administrative event count differs');
    for (const [index, row] of suffix.entries()) {
      const data = JSON.parse(String(row['data'])) as Record<string, unknown>, expectedRow = expected[index]!;
      if (row['kind'] !== expectedRow.kind || !exactObject(data, [...Object.keys(expectedRow.data), 'at'])
        || typeof data['at'] !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(data['at'])
        || Object.entries(expectedRow.data).some(([key, value]) => data[key] !== value)) throw new Error('dependency backup administrative event differs');
      if (attempt && (attempt.events[index]!.cursor !== String(row['cursor'])
        || attempt.events[index]!.sha256 !== createHash('sha256').update(JSON.stringify(row)).digest('hex')))
        throw new Error('dependency candidate administrative event bytes changed');
    }
    return suffix.length;
  }

  private lastDependencyEvent() {
    const row = this.database.prepare('SELECT cursor,kind,data FROM observation_events ORDER BY cursor DESC LIMIT 1').get()!;
    return { cursor: String(row['cursor']), sha256: createHash('sha256').update(JSON.stringify(row)).digest('hex') };
  }

  async reserveDependencyCandidateAttempt(handle: MaintenanceHandle, candidateId: string, validateBackup: () => void) {
    if (!/^[0-9a-f]{8}-[0-9a-f-]{27}$/i.test(candidateId)) throw new Error('invalid dependency candidate identity');
    return this.transaction(() => {
      const { claim } = this.readDependencyMaintenance(handle), selected = claim.maintenance!;
      this.assertDependencyBackupOwner(claim);
      if (!selected.dependencies!.backup || selected.dependencies!.candidateAttempt || selected.candidate) throw new Error('dependency candidate attempt already allocated or backup absent');
      validateBackup(); this.assertDependencyBackupOwner(claim);
      const first = this.lastDependencyEvent();
      this.event('maintenance.candidate_attempted', { operationId: handle.operationId, claimId: claim.id, candidateId });
      selected.dependencies!.candidateAttempt = { id: candidateId, binding: null, events: [first, this.lastDependencyEvent()] };
      this.saveDependencyBackupClaim(claim);
    });
  }

  async bindDependencyCandidateAttempt(handle: MaintenanceHandle, binding: DependencyCandidateAttemptBinding, validateBackup: () => void) {
    validateDependencyCandidateAttempt(binding);
    return this.transaction(() => {
      const { claim } = this.readDependencyMaintenance(handle), selected = claim.maintenance!, attempt = selected.dependencies!.candidateAttempt;
      this.assertDependencyBackupOwner(claim);
      if (!selected.dependencies!.backup || !attempt || attempt.binding || selected.candidate) throw new Error('dependency candidate attempt cannot be rebound');
      validateBackup(); this.assertDependencyBackupOwner(claim);
      this.event('maintenance.candidate_attempt_bound', { operationId: handle.operationId, claimId: claim.id, candidateId: attempt.id, attemptSha256: binding.sha256 });
      attempt.binding = binding; attempt.events.push(this.lastDependencyEvent()); this.saveDependencyBackupClaim(claim);
    });
  }

  async bindDependencyCandidate(handle: MaintenanceHandle, candidate: CandidateBinding, validateCandidate: () => void) {
    if (!exactObject(candidate, ['path', 'identity', 'treeDigest', 'receiptId', 'receiptSha256'])
      || candidate.path !== join(handle.commonDir, 'factory', `dependency-candidate-${handle.operationId}`)
      || !/^\d+:\d+$/.test(candidate.identity) || !/^[a-f0-9]{64}$/.test(candidate.treeDigest)
      || !/^[0-9a-f-]{36}$/i.test(candidate.receiptId) || !/^[a-f0-9]{64}$/.test(candidate.receiptSha256)) throw new Error('invalid dependency candidate binding');
    return this.transaction(() => {
      const { claim } = this.readDependencyMaintenance(handle), selected = claim.maintenance!, attempt = selected.dependencies!.candidateAttempt;
      this.assertDependencyBackupOwner(claim);
      if (!selected.dependencies!.backup || !attempt?.binding || selected.candidate) throw new Error('dependency candidate cannot be rebound');
      validateCandidate(); this.assertDependencyBackupOwner(claim);
      this.event('maintenance.candidate_bound', { operationId: handle.operationId, claimId: claim.id, candidateId: attempt.id, receiptSha256: candidate.receiptSha256 });
      selected.candidate = candidate; attempt.events.push(this.lastDependencyEvent()); this.saveDependencyBackupClaim(claim);
    });
  }

  /** The only historical-schema admission path, with all checks inside the writer transaction. */
  async beginForwardMaintenance(intent: MaintenanceIntent, owner: Owner): Promise<Claim> {
    validateOwner(owner);
    return this.transaction(() => {
      const shape = knownForwardShape(this.database);
      assertForwardIntegrity(this.database);
      const rows = this.database.prepare('SELECT id,release,state FROM repository LIMIT 2').all();
      if (rows.length !== 1 || rows[0]?.['state'] !== 'ready' || rows[0]['id'] !== intent.repositoryId
        || intent.kind !== 'upgrade' || intent.phase !== 'preparing' || !intent.backupId
        || !intent.forward || intent.forward.sourceShape !== shape || intent.forward.currentShape !== shape
        || intent.forward.sourceRelease !== rows[0]['release']
        || intent.forward.sourceIdentity !== this.forwardStorage?.identity
        || intent.forward.backup !== null || this.database.prepare('SELECT id FROM owner_claims LIMIT 1').get())
        throw new Error('forward admission requires exact ready idle repository and source shape');
      const expectedCompletion = intent.artifactDigests['original-completion'];
      if (expectedCompletion) {
        const last = this.database.prepare("SELECT data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed') ORDER BY cursor DESC LIMIT 1").get();
        if (!last || createHash('sha256').update(String(last['data'])).digest('hex') !== expectedCompletion)
          throw new Error('original installed completion changed before forward admission');
      }
      if (this.database.prepare('SELECT id FROM attempts WHERE occupied=1 LIMIT 1').get())
        throw new Error('occupied attempts block forward admission');
      const claim: Claim = { id: randomUUID(), token: randomUUID(), kind: 'maintenance', resourceKey: intent.repositoryId,
        invocationId: null, owner, maintenance: intent };
      const data = JSON.stringify(claim);
      if (Buffer.byteLength(data) > 8192) throw new Error('forward maintenance claim exceeds limit');
      this.database.prepare("INSERT INTO owner_claims(id,token,kind,resource_key,invocation_id,data) VALUES (?,?, 'maintenance',?,NULL,?)")
        .run(claim.id, claim.token, claim.resourceKey, data);
      this.event('maintenance.started', { operationId: intent.operationId, claimId: claim.id, kind: 'upgrade', sourceShape: shape });
      return claim;
    });
  }

  forwardShape(): ForwardShape { return knownForwardShape(this.database); }
  forwardCounts() { return forwardCounts(this.database); }
  repositoryRelease(): string {
    const rows = this.database.prepare('SELECT release FROM repository LIMIT 2').all();
    if (rows.length !== 1) throw new Error('forward repository cardinality differs');
    return String(rows[0]!['release']);
  }
  forwardIdentity(): string {
    if (!this.forwardStorage) throw new Error('forward store identity unavailable');
    this.assertForwardStorage(); return this.forwardStorage.identity;
  }

  async bindForwardBackup(input: { handle: MaintenanceHandle; backup: NonNullable<NonNullable<MaintenanceIntent['forward']>['backup']> }) {
    if (!/^[0-9a-f-]{36}$/i.test(input.backup.id) || !/^[0-9a-f-]{36}$/i.test(input.backup.receiptId)
      || !/^[0-9a-f]{64}$/.test(input.backup.sha256) || !/^[0-9a-f]{64}$/.test(input.backup.countDigest)
      || !/^[0-9a-f]{64}$/.test(input.backup.receiptSha256) || !/^\d+:\d+$/.test(input.backup.identity)
      || !Number.isSafeInteger(input.backup.bytes) || input.backup.bytes < 1 || input.backup.bytes > 512 * 1024 * 1024)
      throw new Error('invalid compact forward backup binding');
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId), intent = claim.maintenance!;
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token || claim.resourceKey !== input.handle.repositoryId
        || intent.kind !== 'upgrade' || intent.phase !== 'preparing' || !intent.forward
        || intent.forward.backup !== null || intent.backupId !== input.backup.id
        || intent.forward.currentShape !== knownForwardShape(this.database)
        || intent.forward.sourceIdentity !== this.forwardStorage?.identity
        || this.database.prepare('SELECT id FROM owner_claims WHERE id<>? LIMIT 1').get(claim.id))
        throw new Error('forward backup bind claim/token/shape differs');
      intent.forward.backup = input.backup;
      const data = JSON.stringify(claim);
      if (Buffer.byteLength(data) > 8192) throw new Error('forward maintenance claim exceeds limit');
      this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?').run(data, claim.id, claim.token);
      this.event('maintenance.backup_bound', { operationId: intent.operationId, claimId: claim.id, backupId: input.backup.id });
    });
  }

  async advanceForwardStep(handle: MaintenanceHandle): Promise<ForwardShape> {
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(handle.operationId), intent = claim.maintenance!;
      if (claim.id !== handle.claimId || claim.token !== handle.token || claim.resourceKey !== handle.repositoryId
        || intent.kind !== 'upgrade' || intent.phase !== 'modifying' || !intent.ticketConsumed
        || !intent.forward?.backup || intent.forward.backup.id !== intent.backupId
        || intent.forward.sourceIdentity !== this.forwardStorage?.identity
        || this.database.prepare('SELECT state FROM repository WHERE id=?').get(intent.repositoryId)?.['state'] !== 'incomplete'
        || this.database.prepare('SELECT id FROM owner_claims WHERE id<>? LIMIT 1').get(claim.id))
        throw new Error('forward step requires consumed exclusive upgrade handoff');
      assertForwardIntegrity(this.database);
      const next = applyForwardStep(this.database, intent.forward.currentShape);
      intent.forward.currentShape = next;
      const data = JSON.stringify(claim);
      if (Buffer.byteLength(data) > 8192) throw new Error('forward maintenance claim exceeds limit');
      this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?').run(data, claim.id, claim.token);
      this.event('maintenance.schema_advanced', { operationId: intent.operationId, claimId: claim.id, shape: next });
      assertForwardIntegrity(this.database);
      return next;
    });
  }

  readMaintenanceClaim(operationId: string): Claim {
    const row = this.database.prepare("SELECT data FROM owner_claims WHERE kind='maintenance'").get();
    if (!row) throw new Error('maintenance claim unavailable');
    const claim = JSON.parse(String(row['data'])) as Claim;
    if (!claim.maintenance || claim.maintenance.operationId !== operationId || claim.resourceKey !== this.repositoryId()
      || claim.maintenance.repositoryId !== claim.resourceKey) throw new Error('recorded maintenance operation does not match');
    if (!Object.hasOwn(claim.maintenance, 'candidate')) claim.maintenance.candidate = null;
    return claim;
  }

  assertSoleMaintenance(handle: MaintenanceHandle): void {
    const claim = this.readMaintenanceClaim(handle.operationId);
    const count = this.database.prepare('SELECT count(*) AS count FROM owner_claims').get();
    if (claim.id !== handle.claimId || claim.token !== handle.token || claim.resourceKey !== handle.repositoryId
      || count?.['count'] !== 1) throw new Error('sole maintenance claim differs');
  }

  async bindInstallCandidate(input: { handle: MaintenanceHandle; candidate: CandidateBinding;
    stageDigest: string; stageIdentity: string }): Promise<MaintenanceIntent> {
    const candidate = input.candidate;
    if (!candidate || Object.keys(candidate).sort().join(',') !== 'identity,path,receiptId,receiptSha256,treeDigest'
      || !/^\d+:\d+$/.test(candidate.identity) || !/^[a-f0-9]{64}$/.test(candidate.treeDigest)
      || !/^[a-f0-9]{64}$/.test(candidate.receiptSha256)
      || !/^[a-f0-9]{8}-[a-f0-9-]{27}$/i.test(candidate.receiptId)
      || !/^[a-f0-9]{64}$/.test(input.stageDigest) || !/^\d+:\d+$/.test(input.stageIdentity))
      throw new Error('invalid compact candidate binding');
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId), recorded = claim.maintenance!;
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token
        || claim.resourceKey !== input.handle.repositoryId || recorded.repositoryId !== input.handle.repositoryId
        || recorded.kind !== 'install' || recorded.phase !== 'preparing' || (recorded.candidate ?? null) !== null
        || input.candidate.path !== join(input.handle.commonDir, 'factory', `install-candidate-${recorded.operationId}`))
        throw new Error('install candidate claim/token/phase no longer matches');
      if (this.database.prepare('SELECT id FROM owner_claims WHERE id<>? LIMIT 1').get(claim.id))
        throw new Error('another owner blocks candidate binding');
      recorded.candidate = input.candidate;
      recorded.stageDigest = input.stageDigest;
      recorded.stageIdentity = input.stageIdentity;
      const data = JSON.stringify(claim);
      if (Buffer.byteLength(data) > 8192) throw new Error('maintenance claim exceeds limit');
      this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?')
        .run(data, claim.id, claim.token);
      this.event('maintenance.candidate_bound', { operationId: recorded.operationId, claimId: claim.id,
        treeDigest: input.candidate.treeDigest });
      return recorded;
    });
  }


  async bindUpgradeCandidate(input: { handle: MaintenanceHandle; candidate: CandidateBinding;
    stageDigest: string; stageIdentity: string; intentSha256: string; receipt: { id: string; sha256: string; identity: string }; launcher: Owner }): Promise<MaintenanceIntent> {
    validateOwner(input.launcher);
    if (inspectOwner(input.launcher).state !== 'known_live') throw new Error('upgrade launcher is not live');
    const candidate = input.candidate;
    if (!input.receipt || !/^[a-f0-9-]{36}$/i.test(input.receipt.id) || !/^[a-f0-9]{64}$/.test(input.receipt.sha256)
      || !/^\d+:\d+$/.test(input.receipt.identity)) throw new Error('invalid upgrade receipt binding');
    if (!candidate || Object.keys(candidate).sort().join(',') !== 'identity,path,receiptId,receiptSha256,treeDigest'
      || !/^\d+:\d+$/.test(candidate.identity) || !/^[a-f0-9]{64}$/.test(candidate.treeDigest)
      || !/^[a-f0-9]{64}$/.test(candidate.receiptSha256)
      || !/^[a-f0-9]{8}-[a-f0-9-]{27}$/i.test(candidate.receiptId)
      || !/^[a-f0-9]{64}$/.test(input.intentSha256) || !/^[a-f0-9]{64}$/.test(input.stageDigest) || !/^\d+:\d+$/.test(input.stageIdentity))
      throw new Error('invalid compact candidate binding');
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId), recorded = claim.maintenance!;
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token
        || claim.resourceKey !== input.handle.repositoryId || recorded.repositoryId !== input.handle.repositoryId
        || recorded.kind !== 'upgrade' || !recorded.forward?.backup || recorded.forward.backup.id !== recorded.backupId
        || !recorded.artifactDigests['original-installed'] || recorded.phase !== 'preparing' || (recorded.candidate ?? null) !== null
        || input.candidate.path !== join(input.handle.commonDir, 'factory', `install-candidate-${recorded.operationId}`))
        throw new Error('upgrade candidate claim/token/backup/phase no longer matches');
      if (this.database.prepare('SELECT id FROM owner_claims WHERE id<>? LIMIT 1').get(claim.id))
        throw new Error('another owner blocks candidate binding');
      recorded.upgradeIntentSha256 = input.intentSha256;
      recorded.upgradeReceipt = input.receipt;
      recorded.activeLauncher = input.launcher;
      recorded.candidate = input.candidate;
      recorded.stageDigest = input.stageDigest;
      recorded.stageIdentity = input.stageIdentity;
      const data = JSON.stringify(claim);
      if (Buffer.byteLength(data) > 8192) throw new Error('maintenance claim exceeds limit');
      this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?')
        .run(data, claim.id, claim.token);
      this.event('maintenance.candidate_bound', { operationId: recorded.operationId, claimId: claim.id,
        treeDigest: input.candidate.treeDigest });
      return recorded;
    });
  }

  async advanceMaintenance(input: { handle: MaintenanceHandle; expected: MaintenancePhase; next: MaintenancePhase;
    stageDigest?: string; stageIdentity?: string; ticketNonceHash?: string }) {
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId);
      if (claim.maintenance?.kind === 'dependencies') throw new Error('dependency admission has no handoff or publication authority');
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token || claim.resourceKey !== input.handle.repositoryId
        || claim.maintenance!.phase !== input.expected) throw new Error('maintenance claim/token/phase no longer matches');
      if (!((input.expected === 'preparing' && input.next === 'handoff-ready')
        || (input.expected === 'modifying' && input.next === 'validating'))) throw new Error('invalid maintenance phase transition');
      if (input.next === 'handoff-ready' && (!input.stageDigest || !input.stageIdentity || !input.ticketNonceHash))
        throw new Error('handoff requires exact stage and ticket evidence');
      Object.assign(claim.maintenance!, { phase: input.next,
        ...(input.stageDigest ? { stageDigest: input.stageDigest } : {}),
        ...(input.stageIdentity ? { stageIdentity: input.stageIdentity } : {}),
        ...(input.ticketNonceHash ? { ticketNonceHash: input.ticketNonceHash } : {}) });
      this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?')
        .run(JSON.stringify(claim), claim.id, claim.token);
      this.event('maintenance.phase', { operationId: input.handle.operationId, claimId: claim.id, phase: input.next });
      return claim.maintenance!;
    });
  }

  async consumeMaintenanceHandoff(input: { handle: MaintenanceHandle; nonceHash: string; stageDigest: string; stageIdentity: string;
    owner: Owner }) {
    validateOwner(input.owner);
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId);
      const intent = claim.maintenance!;
      if (intent.kind === 'dependencies') throw new Error('dependency admission has no handoff or publication authority');
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token || claim.resourceKey !== input.handle.repositoryId
        || intent.phase !== 'handoff-ready' || intent.ticketConsumed || intent.ticketNonceHash !== input.nonceHash
        || intent.stageDigest !== input.stageDigest || intent.stageIdentity !== input.stageIdentity)
        throw new Error('handoff claim/token/stage/nonce no longer matches');
      if (this.database.prepare('SELECT id FROM owner_claims WHERE id<>? LIMIT 1').get(claim.id))
        throw new Error('another owner blocks maintenance mutation');
      intent.phase = 'modifying'; intent.ticketConsumed = true; claim.owner = input.owner;
      this.database.prepare("UPDATE repository SET state='incomplete' WHERE id=?").run(intent.repositoryId);
      this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?')
        .run(JSON.stringify(claim), claim.id, claim.token);
      this.event('maintenance.handoff_consumed', { operationId: intent.operationId, claimId: claim.id });
      return intent;
    });
  }

  async reissueMaintenanceHandoff(input: { handle: MaintenanceHandle; nonceHash: string; stageDigest: string; stageIdentity: string }) {
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId), recorded = claim.maintenance!;
      if (recorded.kind === 'dependencies') throw new Error('dependency admission has no handoff or publication authority');
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token || claim.resourceKey !== input.handle.repositoryId
        || recorded.phase !== 'handoff-ready' || recorded.ticketConsumed || recorded.ticketNonceHash !== null
        || recorded.stageDigest !== input.stageDigest || recorded.stageIdentity !== input.stageIdentity)
        throw new Error('maintenance handoff reissue claim/token/stage no longer matches');
      recorded.ticketNonceHash = input.nonceHash;
      this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?')
        .run(JSON.stringify(claim), claim.id, claim.token);
      this.event('maintenance.handoff_reissued', { operationId: recorded.operationId, claimId: claim.id });
    });
  }

  async reclaimMaintenance(input: { operationId: string; expectedToken: string; expectedOwner: Owner;
    expectedPhase: MaintenancePhase; owner: Owner; inspection: 'not_live' | 'unknown'; note: string;
    replacementBackupId?: string; launcher?: Owner }) {
    validateOwner(input.owner);
    if (input.launcher) { validateOwner(input.launcher); if (inspectOwner(input.launcher).state !== 'known_live') throw new Error('replacement launcher is not live'); }
    text(input.note, 'maintenance clearance note');
    if (!input.note.trim()) throw new Error('nonempty maintenance clearance note required');
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.operationId);
      if (claim.maintenance?.kind === 'dependencies') throw new Error('dependency admission requires later operation-specific recovery');
      if (claim.token !== input.expectedToken) throw new Error('maintenance claim/token no longer matches');
      if (claim.owner.host !== input.expectedOwner.host || claim.owner.pid !== input.expectedOwner.pid
        || claim.owner.start !== input.expectedOwner.start || claim.maintenance?.phase !== input.expectedPhase)
        throw new Error('maintenance owner or phase changed after inspection');
      if (input.replacementBackupId && (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(input.replacementBackupId)
        || claim.maintenance?.kind !== 'upgrade' || !claim.maintenance.forward
        || claim.maintenance.forward.backup !== null || claim.maintenance.phase !== 'preparing'
        || claim.maintenance.backupId === input.replacementBackupId))
        throw new Error('forward backup replacement is not eligible');
      const clearance: Clearance = { id: randomUUID(), claimId: claim.id, note: input.note, basis: 'operator_confirmed', inspection: input.inspection };
      this.database.prepare('INSERT INTO clearances(id,claim_id,data) VALUES (?,?,?)')
        .run(clearance.id, claim.id, JSON.stringify(clearance));
      claim.token = randomUUID(); claim.owner = input.owner;
      if (input.launcher) claim.maintenance!.activeLauncher = input.launcher;
      if (input.replacementBackupId) claim.maintenance!.backupId = input.replacementBackupId;
      if (claim.maintenance?.phase === 'handoff-ready') claim.maintenance.ticketNonceHash = null;
      this.database.prepare('UPDATE owner_claims SET token=?,data=? WHERE id=? AND token=?')
        .run(claim.token, JSON.stringify(claim), claim.id, input.expectedToken);
      this.event('maintenance.reclaimed', { operationId: input.operationId, claimId: claim.id, clearanceId: clearance.id });
      return claim;
    });
  }

  /** Explicitly abandon only an unchanged, unconsumed upgrade preparation. */
  async abandonUpgradePreparation(input: { handle: MaintenanceHandle; expectedOwner: Owner; note: string;
    ownerState: 'not_live' | 'unknown'; ownerLimitation: string; launcher: Owner; validateOriginal: () => void }) {
    if (typeof input.note !== 'string' || !input.note.trim() || Buffer.byteLength(input.note) > 256
      || !['not_live', 'unknown'].includes(input.ownerState) || typeof input.ownerLimitation !== 'string'
      || !input.ownerLimitation || Buffer.byteLength(input.ownerLimitation) > 256)
      throw new Error('explicit bounded operator clearance required');
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId), selected = claim.maintenance!;
      const repository = this.database.prepare('SELECT id,release,state FROM repository').get();
      const prior = this.database.prepare("SELECT data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed') ORDER BY cursor DESC LIMIT 1").get();
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token || claim.resourceKey !== input.handle.repositoryId
        || JSON.stringify(claim.owner) !== JSON.stringify(input.expectedOwner) || selected.kind !== 'upgrade'
        || selected.phase !== 'preparing' || selected.ticketConsumed || selected.ticketNonceHash !== null
        || !selected.forward || selected.forward.sourceShape !== selected.forward.currentShape
        || selected.forward.sourceIdentity !== this.forwardStorage?.identity || knownForwardShape(this.database) !== selected.forward.sourceShape
        || repository?.['id'] !== input.handle.repositoryId || repository['state'] !== 'ready'
        || repository['release'] !== selected.forward.sourceRelease || !selected.artifactDigests['original-installed']
        || !selected.artifactDigests['original-completion'] || !prior
        || createHash('sha256').update(String(prior['data'])).digest('hex') !== selected.artifactDigests['original-completion']
        || !pathAbsent(join(input.handle.commonDir, 'factory', 'upgrade-incomplete'))
        || this.database.prepare('SELECT id FROM owner_claims WHERE id<>? LIMIT 1').get(claim.id))
        throw new Error('upgrade preparation abandonment claim or original state differs');
      const operation = join(input.handle.commonDir, 'factory', `upgrade-${selected.operationId}`);
      for (const step of ['01-old-install', '02-new-install', '03-old-toolchain', '04-new-toolchain'])
        if (!pathAbsent(join(operation, `${step}.json`))) throw new Error('upgrade publication journal blocks abandonment');
      input.validateOriginal();
      const currentInspection = inspectOwner(claim.owner), launcherInspection = inspectOwner(input.launcher);
      if (currentInspection.state === 'known_live' || launcherInspection.state === 'known_live')
        throw new Error('known-live owner or launcher cannot be cleared');
      this.event('maintenance.preparation_abandoned', { operationId: selected.operationId, claimId: claim.id,
        priorOwner: claim.owner, ownerState: currentInspection.state, ownerLimitation: currentInspection.limitation,
        priorLauncher: input.launcher, launcherState: launcherInspection.state, launcherLimitation: launcherInspection.limitation,
        childClosure: 'operator-confirmed-unknown', operatorConfirmed: true, note: input.note });
      this.database.prepare('DELETE FROM owner_claims WHERE id=? AND token=? AND kind=?')
        .run(claim.id, claim.token, 'maintenance');
    });
  }

  /** Final first-install publication commits ownership evidence, readiness and exact release together. */
  async completeFirstInstall(input: { handle: MaintenanceHandle; receiptId: string; receiptSha256: string;
    selectionDigest: string; manifestSha256: string }) {
    if (!/^[a-f0-9]{64}$/.test(input.receiptSha256) || !/^[a-f0-9]{64}$/.test(input.selectionDigest)
      || !/^[a-f0-9]{64}$/.test(input.manifestSha256) || !/^[a-f0-9-]{36}$/i.test(input.receiptId))
      throw new Error('invalid installed ownership evidence');
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId), recorded = claim.maintenance!;
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token
        || claim.resourceKey !== input.handle.repositoryId || recorded.kind !== 'install'
        || recorded.phase !== 'validating' || !recorded.ticketConsumed || !recorded.candidate
        || recorded.selectionDigest !== input.selectionDigest || recorded.targetReleaseSha256 !== input.manifestSha256)
        throw new Error('install completion claim/token/selection differs');
      const repository = this.database.prepare('SELECT id,release,state FROM repository').get();
      if (repository?.['id'] !== input.handle.repositoryId || repository['state'] !== 'incomplete'
        || repository['release'] !== recorded.release
        || this.database.prepare('SELECT id FROM owner_claims WHERE id<>? LIMIT 1').get(claim.id))
        throw new Error('install completion repository or sole claim differs');
      const completion = { version: 1, operationId: recorded.operationId, repositoryId: recorded.repositoryId,
        claimId: claim.id, selectionDigest: recorded.selectionDigest, manifestSha256: input.manifestSha256,
        receiptId: input.receiptId, receiptSha256: input.receiptSha256, controllerOwner: claim.owner, stageIdentity: recorded.stageIdentity };
      this.event('install.completed', completion);
      this.database.prepare("UPDATE repository SET state='ready' WHERE id=? AND state='incomplete'").run(recorded.repositoryId);
      this.database.prepare('DELETE FROM owner_claims WHERE id=? AND token=? AND kind=?')
        .run(claim.id, claim.token, 'maintenance');
      return completion;
    });
  }

  /** Upgrade publication switches active completion, release and ready in one transaction. */
  async completeUpgrade(input: { handle: MaintenanceHandle; receiptId: string; receiptSha256: string;
    selectionDigest: string; manifestSha256: string }) {
    if (!/^[a-f0-9]{64}$/.test(input.receiptSha256) || !/^[a-f0-9]{64}$/.test(input.selectionDigest)
      || !/^[a-f0-9]{64}$/.test(input.manifestSha256) || !/^[a-f0-9-]{36}$/i.test(input.receiptId))
      throw new Error('invalid upgrade ownership evidence');
    return this.transaction(() => {
      const claim = this.readMaintenanceClaim(input.handle.operationId), recorded = claim.maintenance!;
      const repository = this.database.prepare('SELECT id,release,state FROM repository').get();
      const prior = this.database.prepare("SELECT data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed') ORDER BY cursor DESC LIMIT 1").get();
      if (claim.id !== input.handle.claimId || claim.token !== input.handle.token
        || claim.resourceKey !== input.handle.repositoryId || recorded.kind !== 'upgrade'
        || recorded.phase !== 'validating' || !recorded.ticketConsumed || !recorded.candidate
        || recorded.selectionDigest !== input.selectionDigest || recorded.targetReleaseSha256 !== input.manifestSha256
        || !recorded.forward?.backup || recorded.forward.currentShape !== 'v7' || knownForwardShape(this.database) !== 'v7'
        || !recorded.artifactDigests['original-installed'] || !recorded.artifactDigests['original-completion']
        || !recorded.upgradeIntentSha256 || !/^[a-f0-9]{64}$/.test(recorded.upgradeIntentSha256)
        || !recorded.activeLauncher || inspectOwner(recorded.activeLauncher).state !== 'known_live'
        || recorded.activeLauncher.pid !== process.ppid
        || !recorded.upgradeReceipt || recorded.upgradeReceipt.id !== input.receiptId
        || recorded.upgradeReceipt.sha256 !== input.receiptSha256
        || !prior || createHash('sha256').update(String(prior['data'])).digest('hex') !== recorded.artifactDigests['original-completion']
        || repository?.['id'] !== input.handle.repositoryId || repository['state'] !== 'incomplete'
        || repository['release'] !== recorded.forward.sourceRelease
        || this.database.prepare('SELECT id FROM owner_claims WHERE id<>? LIMIT 1').get(claim.id))
        throw new Error('upgrade completion claim/token/original/target differs');
      const completion = { version: 1, operationId: recorded.operationId, repositoryId: recorded.repositoryId,
        claimId: claim.id, selectionDigest: recorded.selectionDigest, manifestSha256: input.manifestSha256,
        receiptId: input.receiptId, receiptSha256: input.receiptSha256, receiptIdentity: recorded.upgradeReceipt.identity,
        controllerOwner: claim.owner, launcherOwner: recorded.activeLauncher,
        originalCompletionSha256: recorded.artifactDigests['original-completion'],
        originalInstalledSha256: recorded.artifactDigests['original-installed'] };
      this.event('upgrade.completed', completion);
      this.database.prepare("UPDATE repository SET state='ready',release=? WHERE id=? AND state='incomplete'")
        .run(recorded.release, recorded.repositoryId);
      this.database.prepare('DELETE FROM owner_claims WHERE id=? AND token=? AND kind=?')
        .run(claim.id, claim.token, 'maintenance');
      return completion;
    });
  }

  /** Record explicit clearance before completing an already-committed upgrade cleanup. */
  async recordCompletedUpgradeRecovery(input: { operationId: string; receiptId: string; receiptSha256: string;
    note: string; controllerState: 'not_live' | 'unknown'; controllerLimitation: string;
    launcherState: 'not_live' | 'unknown'; launcherLimitation: string;
    originalLauncherState: 'not_live' | 'unknown'; originalLauncherLimitation: string }) {
    if (!input.note.trim() || Buffer.byteLength(input.note) > 256 || !/^[a-f0-9-]{36}$/i.test(input.operationId)
      || !/^[a-f0-9-]{36}$/i.test(input.receiptId) || !/^[a-f0-9]{64}$/.test(input.receiptSha256)
      || !['not_live','unknown'].includes(input.controllerState) || !['not_live','unknown'].includes(input.launcherState)
      || !['not_live','unknown'].includes(input.originalLauncherState) || !input.originalLauncherLimitation
      || Buffer.byteLength(input.originalLauncherLimitation) > 256
      || !input.controllerLimitation || Buffer.byteLength(input.controllerLimitation) > 256
      || !input.launcherLimitation || Buffer.byteLength(input.launcherLimitation) > 256)
      throw new Error('invalid completed upgrade clearance');
    return this.transaction(() => {
      const repository = this.database.prepare('SELECT state FROM repository').get();
      const last = this.database.prepare("SELECT kind,data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed') ORDER BY cursor DESC LIMIT 1").get();
      const data = last ? JSON.parse(String(last['data'])) as Record<string, unknown> : null;
      if (repository?.['state'] !== 'ready' || this.database.prepare('SELECT id FROM owner_claims LIMIT 1').get()
        || last?.['kind'] !== 'upgrade.completed' || data?.['operationId'] !== input.operationId
        || data['receiptId'] !== input.receiptId || data['receiptSha256'] !== input.receiptSha256)
        throw new Error('completed upgrade clearance evidence differs');
      this.event('maintenance.completed_recovery_inspected', { ...input, childClosure: 'operator-confirmed-unknown', operatorConfirmed: true });
    });
  }

  /** Narrow read-only evidence for ready-before-marker-unlink install recovery. */
  readFirstInstallCompletion(operationId: string) {
    const rows = this.database.prepare("SELECT data FROM observation_events WHERE kind='install.completed' AND json_extract(data,'$.operationId')=? LIMIT 2")
      .all(operationId);
    if (rows.length !== 1) throw new Error('unique installed completion unavailable');
    const repository = this.database.prepare('SELECT id,state FROM repository').get();
    if (repository?.['state'] !== 'ready' || this.database.prepare('SELECT id FROM owner_claims LIMIT 1').get())
      throw new Error('installed completion is not ready or claim-free');
    return { completion: JSON.parse(String(rows[0]!['data'])) as { version: number; operationId: string;
      repositoryId: string; claimId: string; selectionDigest: string; manifestSha256: string; receiptId: string;
      receiptSha256: string }, repositoryId: String(repository['id']) };
  }

  repositoryId(): string {
    const row = this.database.prepare('SELECT id FROM repository').get();
    if (!row) throw new Error('repository identity unavailable');
    return String(row['id']);
  }

  readInvocations(input: { after?: number; limit?: number } = {}) {
    const after = input.after ?? 0, limit = input.limit ?? 30;
    if (!Number.isSafeInteger(after) || after < 0 || !Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error('invalid invocation page');
    // Cards need lifecycle summaries; large supplied inputs stay in selected detail/captures.
    const rows = this.database.prepare("SELECT rowid AS cursor,json_remove(data,'$.metadata') AS data FROM invocations WHERE rowid>? ORDER BY rowid LIMIT ?").iterate(after, limit + 1);
    const invocations: Invocation[] = []; let bytes = 0, nextCursor = after, hasMore = false;
    for (const row of rows) {
      const data = String(row['data']);
      if (invocations.length === limit || bytes + Buffer.byteLength(data) > 1047552) { hasMore = true; break; }
      bytes += Buffer.byteLength(data); invocations.push(JSON.parse(data) as Invocation); nextCursor = Number(row['cursor']);
    }
    return { invocations, nextCursor, hasMore };
  }

  /** Run cards are paged by stable insertion identity, newest first. Only one invocation is read per card. */
  readRuns(input: { after?: number; limit?: number } = {}) {
    const after = input.after ?? 0, limit = input.limit ?? 30;
    if (!Number.isSafeInteger(after) || after < 0 || !Number.isSafeInteger(limit) || limit < 1 || limit > 30) throw new Error('invalid run page');
    const rows = this.database.prepare(`
      SELECT r.rowid AS cursor, r.data AS run_data,
        json_remove(i.data,'$.metadata') AS invocation_data,
        json_extract(i.data,'$.metadata.workflow') AS workflow,
        (SELECT substr(c.text,1,240) FROM capture_chunks c
          WHERE c.capture_id=json_extract(i.data,'$.metadata.inputCaptureId')
          ORDER BY c.sequence LIMIT 1) AS request_preview,
        (SELECT c.data FROM clearances c WHERE json_extract(c.data,'$.invocationId')=i.id ORDER BY c.rowid DESC LIMIT 1) AS clearance_data,
        (SELECT json_extract(e.data,'$.at') FROM observation_events e WHERE json_extract(e.data,'$.invocationId')=i.id AND e.kind='invocation.started' ORDER BY e.cursor LIMIT 1) AS started_at,
        CASE WHEN json_extract(i.data,'$.stage')='finalized' THEN
          (SELECT json_extract(e.data,'$.at') FROM observation_events e WHERE json_extract(e.data,'$.invocationId')=i.id AND e.kind='invocation.finalized' ORDER BY e.cursor DESC LIMIT 1)
          ELSE NULL END AS ended_at,
        (SELECT c.state FROM captures c WHERE c.invocation_id=i.id ORDER BY c.rowid DESC LIMIT 1) AS latest_capture_state
      FROM runs r LEFT JOIN invocations i ON i.rowid=(
        SELECT max(latest.rowid) FROM invocations latest WHERE latest.run_id=r.id)
      WHERE (?=0 OR r.rowid<?) ORDER BY r.rowid DESC LIMIT ?
    `).all(after, after, limit + 1);
    const runs: Array<Run & { latestInvocation: Invocation | null; workflow: string | null; requestPreview: string | null; clearance: Clearance | null; startedAt: string | null; endedAt: string | null; latestCaptureState: string | null }> = [];
    let bytes = 0, nextCursor = after;
    for (const row of rows.slice(0, limit)) {
      const run = JSON.parse(String(row['run_data'])) as Run;
      const latestInvocation = row['invocation_data'] === null ? null : JSON.parse(String(row['invocation_data'])) as Invocation;
      const item = { ...run, latestInvocation, workflow: row['workflow'] === null ? null : String(row['workflow']),
        requestPreview: row['request_preview'] === null ? null : String(row['request_preview']),
        clearance: row['clearance_data'] === null ? null : JSON.parse(String(row['clearance_data'])) as Clearance,
        startedAt: row['started_at'] === null ? null : String(row['started_at']), endedAt: row['ended_at'] === null ? null : String(row['ended_at']),
        latestCaptureState: row['latest_capture_state'] === null ? null : String(row['latest_capture_state']) };
      const size = Buffer.byteLength(JSON.stringify(item));
      if (bytes + size > 1047552) break;
      bytes += size; runs.push(item); nextCursor = Number(row['cursor']);
    }
    return { runs, nextCursor, hasMore: rows.some(row => Number(row['cursor']) < nextCursor) };
  }

  readRunSummary(id: string) {
    const row = this.database.prepare(`SELECT r.data AS run_data,
      json_remove(i.data,'$.metadata') AS invocation_data,
      json_extract(i.data,'$.metadata.workflow') AS workflow,
      (SELECT substr(c.text,1,240) FROM capture_chunks c
       WHERE c.capture_id=json_extract(i.data,'$.metadata.inputCaptureId')
       ORDER BY c.sequence LIMIT 1) AS request_preview,
      (SELECT c.data FROM clearances c WHERE json_extract(c.data,'$.invocationId')=i.id ORDER BY c.rowid DESC LIMIT 1) AS clearance_data,
      (SELECT json_extract(e.data,'$.at') FROM observation_events e WHERE json_extract(e.data,'$.invocationId')=i.id AND e.kind='invocation.started' ORDER BY e.cursor LIMIT 1) AS started_at,
      CASE WHEN json_extract(i.data,'$.stage')='finalized' THEN
        (SELECT json_extract(e.data,'$.at') FROM observation_events e WHERE json_extract(e.data,'$.invocationId')=i.id AND e.kind='invocation.finalized' ORDER BY e.cursor DESC LIMIT 1)
        ELSE NULL END AS ended_at,
      (SELECT c.state FROM captures c WHERE c.invocation_id=i.id ORDER BY c.rowid DESC LIMIT 1) AS latest_capture_state
      FROM runs r LEFT JOIN invocations i ON i.rowid=(SELECT max(latest.rowid) FROM invocations latest WHERE latest.run_id=r.id)
      WHERE r.id=?`).get(id);
    if (!row) throw new Error('run not found');
    const run = JSON.parse(String(row['run_data'])) as Run;
    return { ...run, latestInvocation: row['invocation_data'] === null ? null : JSON.parse(String(row['invocation_data'])) as Invocation,
      workflow: row['workflow'] === null ? null : String(row['workflow']),
      requestPreview: row['request_preview'] === null ? null : String(row['request_preview']),
      clearance: row['clearance_data'] === null ? null : JSON.parse(String(row['clearance_data'])) as Clearance,
      startedAt: row['started_at'] === null ? null : String(row['started_at']), endedAt: row['ended_at'] === null ? null : String(row['ended_at']),
      latestCaptureState: row['latest_capture_state'] === null ? null : String(row['latest_capture_state']) };
  }

  readRunInvocations(input: { runId: string; after?: number; limit?: number }) {
    const after = input.after ?? 0, limit = input.limit ?? 30;
    if (!Number.isSafeInteger(after) || after < 0 || !Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error('invalid run invocation page');
    if (!this.database.prepare('SELECT id FROM runs WHERE id=?').get(input.runId)) throw new Error('run not found');
    const rows = this.database.prepare("SELECT rowid AS cursor,json_remove(data,'$.metadata') AS data FROM invocations WHERE run_id=? AND rowid>? ORDER BY rowid LIMIT ?")
      .all(input.runId, after, limit + 1);
    const invocations: Invocation[] = []; let bytes = 0, nextCursor = after;
    for (const row of rows.slice(0, limit)) {
      const data = String(row['data']); if (bytes + Buffer.byteLength(data) > 1047552) break;
      bytes += Buffer.byteLength(data); invocations.push(JSON.parse(data) as Invocation); nextCursor = Number(row['cursor']);
    }
    return { invocations, nextCursor, hasMore: rows.some(row => Number(row['cursor']) > nextCursor) };
  }

  readSession(input: { invocationId: string; id: string }): NativeSession {
    const row = this.database.prepare('SELECT data FROM sessions WHERE invocation_id=? AND id=?').get(input.invocationId, input.id);
    if (!row) throw new Error('session not found');
    return JSON.parse(String(row['data'])) as NativeSession;
  }

  /** Select one saved target by its primary key, then return only the page containing it. */
  readAttemptPage(input: { invocationId: string; attemptId?: string; phase?: string; limit?: number }) {
    const invocation = this.readInvocation(input.invocationId);
    const limit = input.limit ?? 50;
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 50) throw new Error('invalid attempt page');
    const operation=input.attemptId?null:this.database.prepare('SELECT id FROM operations WHERE run_id=? AND operation_key=?')
      .get(invocation.runId, input.phase ?? '');
    const row = input.attemptId
      ? this.database.prepare('SELECT rowid AS cursor,data FROM attempts WHERE id=? AND invocation_id=?').get(input.attemptId, input.invocationId)
      : operation ? this.database.prepare('SELECT rowid AS cursor,data FROM attempts WHERE operation_id=? AND invocation_id=? ORDER BY rowid LIMIT 1')
          .get(String(operation['id']), input.invocationId) : undefined;
    if (!row) throw new Error('saved attempt or phase not found');
    const attempt = JSON.parse(String(row['data'])) as Attempt;
    if (input.phase && attempt.operationKey !== input.phase) throw new Error('attempt does not belong to phase');
    const targetCursor = Number(row['cursor']);
    const page = this.database.prepare('SELECT rowid AS cursor,data FROM attempts WHERE invocation_id=? AND rowid>=? ORDER BY rowid LIMIT ?')
      .all(input.invocationId, targetCursor, limit + 1);
    const attempts = page.slice(0, limit).map(item => JSON.parse(String(item['data'])) as Attempt);
    return { attempts, targetCursor, nextCursor: Number(page[Math.min(limit, page.length)-1]?.['cursor'] ?? targetCursor), hasMore: page.length > limit };
  }

  readSelectedEvent(input: { invocationId: string; cursor: string }) {
    this.readInvocation(input.invocationId);
    if (!/^\d+$/.test(input.cursor) || input.cursor.length > 19 || BigInt(input.cursor) > 9223372036854775807n) throw new Error('invalid event cursor');
    const row = this.database.prepare("SELECT kind,data FROM observation_events WHERE cursor=? AND json_extract(data,'$.invocationId')=?")
      .get(BigInt(input.cursor), input.invocationId);
    if (!row) throw new Error('saved event not found');
    return { cursor: input.cursor, kind: String(row['kind']), data: JSON.parse(String(row['data'])) as Record<string, unknown> };
  }

  readSavedQuestion(invocationId: string) {
    this.readInvocation(invocationId);
    const row = this.database.prepare("SELECT id FROM captures WHERE invocation_id=? AND channel='request' ORDER BY rowid DESC LIMIT 1").get(invocationId);
    if (!row) return null;
    const id = String(row['id']);
    const capture = this.readCapture({ id, limit: 50, byteBudget: 16384 });
    if (capture.state !== 'complete' || capture.hasMore) return { captureId: id, available: false };
    try {
      const value = JSON.parse(capture.chunks.map(chunk => chunk.text).join('')) as Record<string, unknown>;
      if (typeof value.question !== 'string' || typeof value.context !== 'string') return { captureId: id, available: false };
      return { captureId: id, available: true, question: value.question, context: value.context,
        suggestions: Array.isArray(value.suggestions) ? value.suggestions.filter((item): item is string => typeof item === 'string').slice(0, 20) : [] };
    } catch { return { captureId: id, available: false }; }
  }

  readDashboardClaim(): Claim | undefined {
    const row = this.database.prepare("SELECT data FROM owner_claims WHERE kind='dashboard'").get();
    return row ? JSON.parse(String(row['data'])) as Claim : undefined;
  }

  async publishDashboardEndpoint(input: { claimId: string; token: string; url: string; instanceId: string }) {
    const url = new URL(input.url);
    if (url.origin !== input.url || url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || !url.port) throw new Error('invalid loopback endpoint');
    text(input.instanceId, 'host instance');
    return this.transaction(() => {
      this.ready();
      const claim = this.readClaim(input.claimId);
      if (claim.kind !== 'dashboard' || claim.token !== input.token || claim.resourceKey !== this.repositoryId() || claim.endpoint) throw new Error('dashboard claim cannot publish endpoint');
      claim.endpoint = { url: input.url, instanceId: input.instanceId };
      this.database.prepare('UPDATE owner_claims SET data=? WHERE id=? AND token=?').run(JSON.stringify(claim), claim.id, claim.token);
      this.event('dashboard.published', { claimId: claim.id, ...claim.endpoint });
      return claim;
    });
  }

  readClearances(input: { claimId: string }): Clearance[] {
    return this.database.prepare('SELECT data FROM clearances WHERE claim_id=? ORDER BY id LIMIT 200').all(input.claimId)
      .map((row) => JSON.parse(String(row['data'])) as Clearance);
  }

  async clearOwner(input: { claimId: string; token: string; operatorConfirmed: boolean; note: string; inspection: 'known_live' | 'not_live' | 'unknown'; details?: object }) {
    if (input.inspection === 'known_live') throw new Error('known-live owner cannot be cleared');
    if (!['not_live', 'unknown'].includes(input.inspection)) throw new Error('invalid owner inspection');
    if (input.operatorConfirmed !== true) throw new Error('explicit operator confirmation required');
    text(input.note, 'clearance note');
    if (!input.note.trim()) throw new Error('nonempty clearance note required');
    if (input.details !== undefined && Buffer.byteLength(JSON.stringify(input.details)) > 8192) throw new Error('clearance inspection details exceed limit');
    return this.transaction(() => {
      const row = this.database.prepare('SELECT data FROM owner_claims WHERE id=? AND token=?').get(input.claimId, input.token);
      if (!row) throw new Error('claim/token no longer matches');
      const claim = JSON.parse(String(row['data'])) as Claim;
      if (claim.kind === 'maintenance') throw new Error('maintenance claims require explicit operation-preserving recovery');
      const clearance: Clearance = { id: randomUUID(), claimId: claim.id, ...(claim.invocationId ? {invocationId:claim.invocationId} : {}), note: input.note, basis: 'operator_confirmed', inspection: input.inspection as 'not_live' | 'unknown', ...(input.details ? {details:input.details} : {}) };
      this.database.prepare('INSERT INTO clearances(id,claim_id,data) VALUES (?,?,?)').run(clearance.id, claim.id, JSON.stringify(clearance));
      for (const row of this.database.prepare('SELECT data FROM attempts WHERE invocation_id=? AND occupied=1').all(claim.invocationId)) {
        const attempt = JSON.parse(String(row['data'])) as Attempt;
        attempt.quiescent = true; attempt.cleanupBasis = 'operator_confirmed';
        this.database.prepare('UPDATE attempts SET occupied=0,data=? WHERE id=?').run(JSON.stringify(attempt), attempt.id);
      }
      this.database.prepare('DELETE FROM owner_claims WHERE id=? AND token=?').run(claim.id, claim.token);
      this.event('owner.cleared', { claimId: claim.id, ...(claim.invocationId ? {invocationId:claim.invocationId} : {}), clearanceId: clearance.id, basis: clearance.basis });
      return clearance;
    });
  }

  async releaseClaim(input: { claimId: string; token: string; basis: 'quiescent' }) {
    if (input.basis !== 'quiescent') throw new Error('automatic release requires quiescence evidence');
    return this.transaction(() => {
      const row = this.database.prepare('SELECT data FROM owner_claims WHERE id=?').get(input.claimId);
      if (!row) throw new Error('claim/token no longer matches');
      const claim = JSON.parse(String(row['data'])) as Claim;
      if (claim.token !== input.token) throw new Error('claim/token no longer matches');
      if (claim.kind === 'maintenance' && claim.maintenance) throw new Error('typed maintenance claims require validated completion');
      if (this.database.prepare('SELECT a.id FROM attempts a JOIN owner_claims c ON c.invocation_id=a.invocation_id WHERE c.id=? AND a.occupied=1').get(input.claimId)) throw new Error('owned activity is not quiescent');
      if (this.database.prepare('SELECT id FROM notification_reminder_groups WHERE claim_id=? AND unsettled=1 LIMIT 1').get(input.claimId))
        throw new Error('reminder cleanup or recording remains unknown');
      this.database.prepare('DELETE FROM owner_claims WHERE id=? AND token=?').run(input.claimId, input.token);
      this.event('owner.released', { claimId: input.claimId, basis: input.basis });
    });
  }

  async createCapture(input: { invocationId: string; attemptId?: string; channel: string }) {
    if (!['stdout', 'stderr', 'result', 'validated-result', 'request', 'report', 'event', 'context'].includes(input.channel)) throw new Error('unsupported capture channel');
    return this.transaction(() => {
      const invocation = this.readInvocation(input.invocationId);
      if (invocation.stage === 'finalized') throw new Error('invocation finalized');
      if (input.attemptId && this.readAttempt(input.attemptId).invocationId !== input.invocationId) throw new Error('capture attempt belongs to another invocation');
      const capture = { id: randomUUID(), ...input, state: 'open' as CaptureState };
      this.database.prepare('INSERT INTO captures(id,invocation_id,attempt_id,channel,state) VALUES (?,?,?,?,?)')
        .run(capture.id, input.invocationId, input.attemptId ?? null, input.channel, 'open');
      this.event('capture.created', { captureId: capture.id, invocationId: input.invocationId, attemptId: input.attemptId ?? null, channel: input.channel });
      return capture;
    });
  }

  async appendCapture(input: { id: string; chunks: CaptureChunk[]; state?: CaptureState }) {
    if (!Array.isArray(input.chunks) || input.chunks.length > 200) throw new Error('invalid capture batch');
    if (input.state !== undefined && !['open','complete','partial','unknown','pruned'].includes(input.state)) throw new Error('invalid capture state');
    let bytes = 0;
    for (const chunk of input.chunks) {
      if (typeof chunk.text !== 'string' || Buffer.from(chunk.text).toString('utf8') !== chunk.text || !Number.isSafeInteger(chunk.sequence) || chunk.sequence < 1) throw new Error('invalid capture chunk');
      const size = Buffer.byteLength(chunk.text);
      if (size > 65536) throw new Error('capture chunk exceeds 64 KiB');
      bytes += size;
    }
    if (bytes > 262144) throw new Error('capture batch exceeds 256 KiB');
    return this.transaction(() => {
      const row = this.database.prepare('SELECT state,sequence,invocation_id,attempt_id FROM captures WHERE id=?').get(input.id);
      if (!row) throw new Error('capture not found');
      let sequence = Number(row['sequence']);
      if ((input.chunks.length && input.chunks[0]!.sequence <= sequence) || (!input.chunks.length && input.state === row['state'] && row['state'] !== 'open')) {
        let prior = input.chunks[0]?.sequence ?? 1;
        for (const chunk of input.chunks) {
          if (chunk.sequence !== prior++ || this.database.prepare('SELECT text FROM capture_chunks WHERE capture_id=? AND sequence=?').get(input.id, chunk.sequence)?.['text'] !== chunk.text) throw new Error('capture sequence conflicts with committed data');
        }
        if (input.state !== undefined && input.state !== row['state']) throw new Error('capture retry state conflicts with committed data');
        return { sequence, state: row['state'] as CaptureState };
      }
      if (row['state'] !== 'open') throw new Error('capture is complete or closed');
      for (const chunk of input.chunks) {
        if (chunk.sequence !== sequence + 1) throw new Error('capture sequence must be contiguous and unique');
        this.database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)').run(input.id, chunk.sequence, chunk.text);
        sequence++;
      }
      const state = input.state ?? 'open';
      this.database.prepare('UPDATE captures SET sequence=?,state=? WHERE id=?').run(sequence, state, input.id);
      this.event('capture.appended', { captureId: input.id, invocationId: row['invocation_id'], attemptId: row['attempt_id'], sequence, state, bytes });
      return { sequence, state };
    });
  }

  readCapture(input: { id: string; after?: number; limit?: number; byteBudget?: number }) {
    const after = input.after ?? 0, limit = input.limit ?? 200, byteBudget = input.byteBudget ?? 1047552;
    if (!Number.isSafeInteger(after) || after < 0 || !Number.isSafeInteger(limit) || limit < 1 || limit > 200
      || !Number.isSafeInteger(byteBudget) || byteBudget < 0 || byteBudget > 1047552) throw new Error('invalid capture page');
    const row = this.database.prepare('SELECT state,sequence,channel FROM captures WHERE id=?').get(input.id);
    const state = row ? String(row['state']) as CaptureState : 'missing';
    const chunks: CaptureChunk[] = [];
    let size = 0;
    if (row && state !== 'pruned' && byteBudget > 0) {
      // SQLite returns text only while the raw bytes fit this page's remaining budget.
      // A larger first chunk becomes a continuation, without entering JavaScript memory.
      const statement = this.database.prepare('SELECT sequence,CASE WHEN octet_length(text)<=? THEN text ELSE NULL END AS text FROM capture_chunks WHERE capture_id=? AND sequence>? ORDER BY sequence LIMIT ?');
      for (const chunk of statement.iterate(byteBudget, input.id, after, limit)) {
        if (chunk['text'] === null) break;
        const item = { sequence: Number(chunk['sequence']), text: String(chunk['text']) };
        const bytes = Buffer.byteLength(JSON.stringify(item)) + 1;
        if (size + bytes > byteBudget) break;
        size += bytes; chunks.push(item);
      }
    }
    const nextSequence = chunks.at(-1)?.sequence ?? after;
    return { state, channel: row ? String(row['channel']) : null, chunks, nextSequence, hasMore: !!row && state !== 'pruned' && nextSequence < Number(row['sequence']) };
  }

  readEvents(input: { after: string; limit?: number }) {
    if (!/^\d+$/.test(input.after) || input.after.length > 19 || BigInt(input.after) > 9223372036854775807n) throw new Error('invalid event cursor');
    const limit = input.limit ?? 200;
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 200) throw new Error('event limit must be 1-200');
    const statement = this.database.prepare('SELECT cursor,kind,data FROM observation_events WHERE cursor>? ORDER BY cursor LIMIT ?');
    statement.setReadBigInts(true);
    const events: { cursor: string; kind: string; data: object }[] = [];
    let size = 0;
    for (const row of statement.iterate(BigInt(input.after), limit)) {
      const event = { cursor: String(row['cursor']), kind: String(row['kind']), data: JSON.parse(String(row['data'])) as object };
      const bytes = Buffer.byteLength(JSON.stringify(event)) + 1;
      if (size + bytes > 1047552) break;
      size += bytes; events.push(event);
    }
    const gap = BigInt(input.after) > 0n && !this.database.prepare('SELECT cursor FROM observation_events WHERE cursor=?').get(BigInt(input.after));
    return { events, nextCursor: events.at(-1)?.cursor ?? input.after, gap };
  }

  readEventHead() {
    return { cursor: String(this.database.prepare('SELECT max(cursor) AS cursor FROM observation_events').get()?.['cursor'] ?? 0) };
  }

  readInvocationEvents(input: { invocationId: string; after?: string; before?: string; tail?: boolean; limit?: number }) {
    this.readInvocation(input.invocationId);
    const after = input.after ?? '0';
    for (const value of [after, input.before].filter((value): value is string => value !== undefined)) {
      if (!/^\d+$/.test(value) || value.length > 19 || BigInt(value) > 9223372036854775807n) throw new Error('invalid event cursor');
    }
    if ((input.before !== undefined && (input.after !== undefined || input.tail)) || (input.tail && input.after !== undefined)) throw new Error('ambiguous event window');
    const limit = input.limit ?? 200;
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 200) throw new Error('event limit must be 1-200');
    const reverse = input.tail || input.before !== undefined;
    const statement = this.database.prepare(reverse
      ? "SELECT cursor,kind,data FROM observation_events WHERE json_extract(data,'$.invocationId')=? AND cursor<? ORDER BY cursor DESC LIMIT ?"
      : "SELECT cursor,kind,data FROM observation_events WHERE json_extract(data,'$.invocationId')=? AND cursor>? ORDER BY cursor LIMIT ?");
    statement.setReadBigInts(true);
    const events: { cursor: string; kind: string; data: object }[] = [];
    let size = 0;
    const bound = reverse ? BigInt(input.before ?? '9223372036854775807') : BigInt(after);
    for (const row of statement.iterate(input.invocationId, bound, limit + 1)) {
      if (events.length === limit) break;
      const event = { cursor: String(row['cursor']), kind: String(row['kind']), data: JSON.parse(String(row['data'])) as object };
      const bytes = Buffer.byteLength(JSON.stringify(event)) + 1;
      if (size + bytes > 1047552) break;
      size += bytes; events.push(event);
    }
    if (reverse) events.reverse();
    const nextCursor = events.at(-1)?.cursor ?? after;
    const previousCursor = events[0]?.cursor ?? input.before ?? '0';
    const hasMore = !reverse && !!this.database.prepare("SELECT cursor FROM observation_events WHERE json_extract(data,'$.invocationId')=? AND cursor>? ORDER BY cursor LIMIT 1")
      .get(input.invocationId, BigInt(nextCursor));
    const hasEarlier = !!events.length && !!this.database.prepare("SELECT cursor FROM observation_events WHERE json_extract(data,'$.invocationId')=? AND cursor<? ORDER BY cursor DESC LIMIT 1")
      .get(input.invocationId, BigInt(previousCursor));
    const gap = !reverse && BigInt(after) > 0n && !this.database.prepare("SELECT cursor FROM observation_events WHERE json_extract(data,'$.invocationId')=? AND cursor=?")
      .get(input.invocationId, BigInt(after));
    return { events, nextCursor, previousCursor, hasMore, hasEarlier, gap };
  }
}
