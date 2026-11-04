import { maintenanceBackupPath as forwardBackupPath, openImmutableMaintenanceBackup as openImmutableForwardBackup, backupFileDigest as fileDigest, runMaintenanceBackup as runForwardBackup } from './maintenance-backup.js';
import { createHash, randomUUID } from 'node:crypto';
import { closeSync, constants, fstatSync, fsyncSync, lstatSync, mkdirSync, openSync, readSync, readdirSync,
  realpathSync, renameSync, writeSync } from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { pathToFileURL } from 'node:url';
import { currentOwner, inspectOwner } from './native/process.js';
import { verifyPublicationLayout } from './install-publication-state.js';
import { directoryIdentity, verifyBoundInstallCandidate } from './install-candidate.js';
import { assertLocalPlacement } from './placement.js';
import { schemaVersion, initializeSchema } from './schema.js';
import { openForwardMaintenanceStore, openMaintenanceStore, openRepositoryStore } from './store.js';
import { validateDependencyMaintenanceBinding } from './store.js';
import type { CandidateBinding, Claim, MaintenanceHandle, MaintenanceIntent, MaintenanceKind, MaintenancePhase, Owner } from './store.js';
import { repositoryIdentity } from './workspace.js';
import { assertOriginalInstallation, type OriginalInstallation } from './upgrade-original.js';
import { assertForwardIntegrity, forwardCounts, knownForwardShape } from './schema-forward.js';
import type { ForwardShape } from './schema-forward.js';
import { assertDependencyMaintenance } from './dependency-maintenance.js';

const MAX_RECORD_BYTES = 8192;
const SHA = /^[0-9a-f]{64}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const KINDS: MaintenanceKind[] = ['install', 'upgrade', 'dependencies', 'repair', 'uninstall', 'cleanup'];
export interface MaintenanceSelection {
  release: string; selectionDigest: string; targetReleaseSha256: string | null;
  artifactDigests: Record<string, string>; targetSchema: number;
}
interface BootstrapPayload { version: 1; root: string; commonDir: string; claim: Claim }
interface BootstrapRecord extends BootstrapPayload { digest: string }
interface HandoffTicket {
  version: 1; operationId: string; repositoryId: string; root: string; commonDir: string;
  claimId: string; token: string; stagePath: string; stageIdentity: string; stageDigest: string; nonce: string;
  release: string; selectionDigest: string; targetReleaseSha256: string | null;
  artifactDigests: Record<string, string>; targetSchema: number; exitReceiptPath: string;
  candidate?: CandidateBinding | null;
}
interface ExitReceipt { version: 1; operationId: string; claimId: string; stageDigest: string; nonce: string }

function hash(bytes: string | Buffer) { return createHash('sha256').update(bytes).digest('hex'); }
function mustHash(value: unknown, name: string): string {
  if (typeof value !== 'string' || !SHA.test(value)) throw new Error(`invalid ${name} digest`);
  return value;
}
function absent(path: string): boolean {
  try { lstatSync(path); return false; }
  catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return true; throw error; }
}
function identity(path: string): string {
  const stat = lstatSync(path, { bigint: true });
  if (!stat.isDirectory() || stat.isSymbolicLink() || stat.ino === 0n || realpathSync(path) !== path)
    throw new Error('maintenance stage directory identity unavailable');
  return `${stat.dev}:${stat.ino}`;
}
function selected(value: MaintenanceSelection) {
  if (typeof value.release !== 'string' || Buffer.byteLength(value.release) < 1 || Buffer.byteLength(value.release) > 256
    || value.release.includes('\0')) throw new Error('invalid maintenance release');
  mustHash(value.selectionDigest, 'selection');
  if (value.targetReleaseSha256 !== null) mustHash(value.targetReleaseSha256, 'target release');
  if (value.targetSchema !== schemaVersion) throw new Error('target schema must be current');
  if (!value.artifactDigests || typeof value.artifactDigests !== 'object' || Array.isArray(value.artifactDigests)
    || Object.keys(value.artifactDigests).length < 1 || Object.keys(value.artifactDigests).length > 16)
    throw new Error('invalid artifact digest selection');
  for (const [name, digest] of Object.entries(value.artifactDigests)) {
    if (!/^[a-z][a-z0-9-]{0,31}$/.test(name)) throw new Error('invalid artifact digest name');
    mustHash(digest, name);
  }
}
function validOwner(owner: Owner) {
  if (!owner || typeof owner.host !== 'string' || Buffer.byteLength(owner.host) < 1 || Buffer.byteLength(owner.host) > 256
    || owner.host.includes('\0') || !Number.isSafeInteger(owner.pid) || owner.pid < 1
    || (owner.start !== null && (typeof owner.start !== 'string' || Buffer.byteLength(owner.start) < 1
      || Buffer.byteLength(owner.start) > 256 || owner.start.includes('\0')))) throw new Error('invalid maintenance owner');
}
function intent(operationId: string, repositoryId: string, kind: MaintenanceKind, location: string, value: MaintenanceSelection): MaintenanceIntent {
  selected(value);
  return { operationId, repositoryId, kind, release: value.release,
    targetReleaseSha256: value.targetReleaseSha256, selectionDigest: value.selectionDigest,
    artifactDigests: Object.fromEntries(Object.entries(value.artifactDigests).sort(([a], [b]) => a.localeCompare(b))),
    targetSchema: value.targetSchema, stagePath: join(location, 'controller-staging', operationId),
    stageDigest: null, stageIdentity: null, phase: 'preparing', ownedReceiptId: null, backupId: null,
    ticketNonceHash: null, ticketConsumed: false, candidate: null };
}
function readRecord(path: string): Buffer {
  const observed = lstatSync(path, { bigint: true });
  if (!observed.isFile() || observed.isSymbolicLink() || observed.size < 1n || observed.size > BigInt(MAX_RECORD_BYTES))
    throw new Error('incomplete or nonregular maintenance record');
  if (process.platform !== 'win32' && (observed.mode & 0o077n) !== 0n) throw new Error('maintenance record is not private');
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0));
  try {
    const opened = fstatSync(fd, { bigint: true });
    if (!opened.isFile() || opened.dev !== observed.dev || opened.ino !== observed.ino || opened.size !== observed.size)
      throw new Error('maintenance record identity changed');
    const bytes = Buffer.alloc(Number(opened.size));
    let count = 0;
    while (count < bytes.length) {
      const length = readSync(fd, bytes, count, bytes.length - count, count);
      if (length === 0) throw new Error('partial maintenance record');
      count += length;
    }
    const ended = fstatSync(fd, { bigint: true }), current = lstatSync(path, { bigint: true });
    if (ended.size !== opened.size || ended.mtimeNs !== opened.mtimeNs || current.dev !== opened.dev || current.ino !== opened.ino
      || current.isSymbolicLink()) throw new Error('maintenance record changed while reading');
    return bytes;
  } finally { closeSync(fd); }
}
function flushDirectory(path: string) {
  if (process.platform === 'win32') return;
  const fd = openSync(path, constants.O_RDONLY);
  try { fsyncSync(fd); } finally { closeSync(fd); }
}
function writeRecord(path: string, record: object) {
  const bytes = Buffer.from(`${JSON.stringify(record)}\n`);
  if (bytes.length < 1 || bytes.length > MAX_RECORD_BYTES) throw new Error('maintenance record exceeds limit');
  const fd = openSync(path, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | (constants.O_NOFOLLOW ?? 0), 0o600);
  try {
    let offset = 0;
    while (offset < bytes.length) offset += writeSync(fd, bytes, offset, bytes.length - offset, offset);
    fsyncSync(fd);
  } finally { closeSync(fd); }
  if (!readRecord(path).equals(bytes)) throw new Error('maintenance record verification failed');
  flushDirectory(dirname(path));
}
function parseMarker(path: string, root: string, commonDir: string): BootstrapRecord {
  const parsed: unknown = JSON.parse(readRecord(path).toString('utf8'));
  if (!parsed || typeof parsed !== 'object') throw new Error('invalid bootstrap marker');
  const marker = parsed as BootstrapRecord;
  if (marker.version !== 1 || marker.root !== root || marker.commonDir !== commonDir || !marker.claim
    || marker.claim.kind !== 'maintenance' || marker.claim.maintenance?.kind !== 'install'
    || marker.claim.resourceKey !== marker.claim.maintenance.repositoryId || !UUID.test(marker.claim.maintenance.operationId)
    || marker.claim.maintenance.phase !== 'preparing' || marker.claim.maintenance.targetSchema !== schemaVersion
    || !UUID.test(marker.claim.id) || !UUID.test(marker.claim.token) || !UUID.test(marker.claim.resourceKey)
    || !SHA.test(marker.claim.maintenance.selectionDigest)
    || (marker.claim.maintenance.targetReleaseSha256 !== null && !SHA.test(marker.claim.maintenance.targetReleaseSha256))
    || marker.claim.maintenance.stagePath !== join(commonDir, 'factory', 'controller-staging', marker.claim.maintenance.operationId)
    || marker.digest !== hash(JSON.stringify({ version: marker.version, root: marker.root, commonDir: marker.commonDir, claim: marker.claim })))
    throw new Error('bootstrap marker identity or digest invalid');
  validOwner(marker.claim.owner);
  selected({ release: marker.claim.maintenance.release, selectionDigest: marker.claim.maintenance.selectionDigest,
    targetReleaseSha256: marker.claim.maintenance.targetReleaseSha256,
    artifactDigests: marker.claim.maintenance.artifactDigests, targetSchema: marker.claim.maintenance.targetSchema });
  assertRecordedIntent(commonDir, marker.claim);
  return marker;
}
function sameBootstrapOperation(marker: BootstrapRecord, claim: Claim) {
  const original = marker.claim.maintenance!, current = claim.maintenance;
  return claim.id === marker.claim.id && claim.resourceKey === marker.claim.resourceKey && current?.operationId === original.operationId
    && current.kind === 'install' && current.release === original.release && current.selectionDigest === original.selectionDigest
    && current.targetReleaseSha256 === original.targetReleaseSha256 && current.targetSchema === original.targetSchema
    && current.stagePath === original.stagePath && JSON.stringify(current.artifactDigests) === JSON.stringify(original.artifactDigests);
}
/** Install-owned marker check also works after the exact completion transaction releases its claim. */
export async function assertInstallBootstrapMarker(repository: string, operationId: string, claimId: string,
  selectionDigest: string, manifestSha256: string): Promise<{ root: string; common: string; markerClaim: Claim }> {
  const { root, common } = await repositoryIdentity(repository);
  const marker = parseMarker(join(common, 'factory', 'bootstrap-incomplete'), root, common);
  const initial = marker.claim.maintenance!;
  if (initial.operationId !== operationId || marker.claim.id !== claimId || initial.selectionDigest !== selectionDigest
    || initial.targetReleaseSha256 !== manifestSha256) throw new Error('install bootstrap operation differs');
  return { root, common, markerClaim: marker.claim };
}
function assertRecordedIntent(commonDir: string, claim: Claim): MaintenanceIntent {
  const recorded = claim.maintenance;
  if (!recorded || claim.kind !== 'maintenance' || !UUID.test(claim.id) || !UUID.test(claim.token)
    || !UUID.test(claim.resourceKey) || !UUID.test(recorded.operationId)
    || recorded.repositoryId !== claim.resourceKey || !KINDS.includes(recorded.kind)
    || !(['preparing', 'handoff-ready', 'modifying', 'validating'] as string[]).includes(recorded.phase)
    || recorded.stagePath !== join(commonDir, 'factory', 'controller-staging', recorded.operationId)
    || (recorded.stageDigest !== null && !SHA.test(recorded.stageDigest))
    || (recorded.ticketNonceHash !== null && !SHA.test(recorded.ticketNonceHash))
    || (recorded.stageIdentity !== null && !/^\d+:\d+$/.test(recorded.stageIdentity))
    || typeof recorded.ticketConsumed !== 'boolean'
    || (recorded.stageDigest === null) !== (recorded.stageIdentity === null)
    || (recorded.kind === 'install' && (recorded.candidate ?? null) !== null && !recorded.stageDigest)
    || (recorded.phase !== 'preparing' && (!recorded.stageDigest || !recorded.stageIdentity))
    || ((recorded.candidate ?? null) !== null && (!recorded.candidate || typeof recorded.candidate !== 'object'
      || Array.isArray(recorded.candidate) || Object.keys(recorded.candidate).sort().join(',') !== 'identity,path,receiptId,receiptSha256,treeDigest'
      || typeof recorded.candidate.path !== 'string'
      || recorded.candidate.path !== join(commonDir, 'factory', `install-candidate-${recorded.operationId}`)
      || typeof recorded.candidate.identity !== 'string' || !/^\d+:\d+$/.test(recorded.candidate.identity)
      || !SHA.test(recorded.candidate.treeDigest) || !UUID.test(recorded.candidate.receiptId)
      || !SHA.test(recorded.candidate.receiptSha256))))
    throw new Error('recorded maintenance intent invalid');
  if (recorded.kind === 'dependencies' || recorded.dependencies !== undefined) {
    validateDependencyMaintenanceBinding(recorded.dependencies);
    if (recorded.kind !== 'dependencies' || recorded.phase !== 'preparing' || recorded.forward !== undefined
      || (recorded.backupId !== null && !UUID.test(recorded.backupId))
      || (recorded.backupId === null && (recorded.dependencies?.backupAttempt || recorded.dependencies?.backup))
      || (recorded.dependencies?.backup && (!recorded.dependencies.backupAttempt || recorded.dependencies.backup.id !== recorded.backupId))
      || recorded.candidate !== null || recorded.stageDigest !== null
      || recorded.stageIdentity !== null || recorded.ticketConsumed || recorded.ticketNonceHash !== null)
      throw new Error('dependency admission has no backup or publication authority');
  }
  if (recorded.forward !== undefined) {
    const forward = recorded.forward, backup = forward.backup;
    if (!forward || typeof forward !== 'object' || Array.isArray(forward)
      || Object.keys(forward).sort().join(',') !== 'backup,currentShape,sourceIdentity,sourceRelease,sourceShape'
      || recorded.kind !== 'upgrade' || !UUID.test(recorded.backupId ?? '')
      || typeof forward.sourceRelease !== 'string' || Buffer.byteLength(forward.sourceRelease) < 1
      || Buffer.byteLength(forward.sourceRelease) > 256 || !/^\d+:\d+$/.test(forward.sourceIdentity)
      || !(['v3','v4-base','v4-plus','v5','v6','v7'] as string[]).includes(forward.sourceShape)
      || !(['v3','v4-base','v4-plus','v5','v6','v7'] as string[]).includes(forward.currentShape)
      || (backup !== null && (!backup || typeof backup !== 'object' || Array.isArray(backup)
        || Object.keys(backup).sort().join(',') !== 'bytes,countDigest,id,identity,receiptId,receiptSha256,sha256'
        || backup.id !== recorded.backupId || !SHA.test(backup.sha256)
        || !SHA.test(backup.countDigest) || !UUID.test(backup.receiptId) || !SHA.test(backup.receiptSha256)
        || !/^\d+:\d+$/.test(backup.identity)
        || !Number.isSafeInteger(backup.bytes) || backup.bytes < 1 || backup.bytes > 512 * 1024 * 1024)))
      throw new Error('recorded forward intent invalid');
  }
  selected({ release: recorded.release, selectionDigest: recorded.selectionDigest,
    targetReleaseSha256: recorded.targetReleaseSha256, artifactDigests: recorded.artifactDigests,
    targetSchema: recorded.targetSchema });
  validOwner(claim.owner);
  return recorded;
}
function verifyInstallCandidate(commonDir: string, claim: Claim, required: boolean): void {
  const recorded = assertRecordedIntent(commonDir, claim);
  if (recorded.kind === 'upgrade' && recorded.artifactDigests['original-installed']) {
    if (!recorded.candidate || !recorded.targetReleaseSha256) {
      if (required) throw new Error('upgrade candidate absent or unbound');
      return;
    }
    if (!recorded.upgradeIntentSha256 || !SHA.test(recorded.upgradeIntentSha256))
      throw new Error('upgrade publication intent unbound');
    const directory = join(commonDir, 'factory', `upgrade-${recorded.operationId}`);
    const bytes = readRecord(join(directory, 'intent.json'));
    const intent = JSON.parse(bytes.toString('utf8')) as Record<string, unknown>;
    if (hash(bytes) !== recorded.upgradeIntentSha256 || intent['version'] !== 1
      || intent['operationId'] !== recorded.operationId || intent['repositoryId'] !== recorded.repositoryId
      || intent['claimId'] !== claim.id || intent['selectionDigest'] !== recorded.selectionDigest
      || intent['originalSha256'] !== recorded.artifactDigests['original-installed']
      || intent['backupReceiptSha256'] !== recorded.forward?.backup?.receiptSha256
      || intent['operationIdentity'] !== directoryIdentity(directory)
      || intent['oldDirectoryIdentity'] !== directoryIdentity(join(directory, 'old'))
      || hash(JSON.stringify(JSON.parse(readRecord(join(directory, 'original.json')).toString('utf8'))))
        !== recorded.artifactDigests['original-installed']
      || intent['stageDigest'] !== recorded.stageDigest || intent['stageIdentity'] !== recorded.stageIdentity
      || JSON.stringify(intent['candidate']) !== JSON.stringify(recorded.candidate))
      throw new Error('upgrade publication intent changed');
    const receiptPath = join(directory, 'new-receipt.json'), receiptInfo = lstatSync(receiptPath);
    const receiptBytes = readRecord(receiptPath), receipt = JSON.parse(receiptBytes.toString('utf8')) as Record<string, unknown>;
    const receiptAfter = lstatSync(receiptPath);
    if (!recorded.upgradeReceipt || !receiptInfo.isFile() || receiptInfo.isSymbolicLink() || receiptInfo.nlink !== 1
      || `${receiptInfo.dev}:${receiptInfo.ino}` !== recorded.upgradeReceipt.identity
      || receiptAfter.dev !== receiptInfo.dev || receiptAfter.ino !== receiptInfo.ino || receiptAfter.nlink !== 1
      || hash(receiptBytes) !== recorded.upgradeReceipt.sha256 || receipt['receiptId'] !== recorded.upgradeReceipt.id
      || receipt['operationId'] !== recorded.operationId || receipt['claimId'] !== claim.id
      || receipt['intentSha256'] !== recorded.upgradeIntentSha256)
      throw new Error('upgrade installed receipt binding changed');
    if (!recorded.ticketConsumed) verifyBoundInstallCandidate(recorded.candidate, {
      operationId: recorded.operationId, repositoryId: recorded.repositoryId, claimId: claim.id,
      selectionDigest: recorded.selectionDigest, manifestSha256: recorded.targetReleaseSha256 });
    return;
  }
  if (recorded.kind !== 'install') return;
  const path = join(commonDir, 'factory', `install-candidate-${recorded.operationId}`);
  if (!recorded.candidate) {
    if (required || !absent(path)) throw new Error('install candidate absent or unbound; operation requires inspection');
    return;
  }
  verifyPublicationLayout(commonDir, claim);
}
function redacted(intent: MaintenanceIntent) {
  const { operationId, repositoryId, kind, release, selectionDigest, targetReleaseSha256, artifactDigests,
    targetSchema, stagePath, stageDigest, phase, ownedReceiptId, backupId, candidate } = intent;
  return { operationId, repositoryId, kind, release, selectionDigest, targetReleaseSha256, artifactDigests,
    targetSchema, stagePath, stageDigest, phase, ownedReceiptId, backupId, candidate: candidate ?? null,
    ...(intent.forward ? { forward: { sourceShape: intent.forward.sourceShape,
      currentShape: intent.forward.currentShape, backupBound: intent.forward.backup !== null } } : {}),
    ...(intent.dependencies ? { dependencies: { originalSha256: intent.dependencies.originalSha256,
      originalCompletionSha256: intent.dependencies.originalCompletionSha256,
      expectedToolchainSha256: intent.dependencies.expectedToolchainSha256,
      observedToolchainSha256: intent.dependencies.observedToolchainSha256,
      backupAttempted: intent.backupId !== null, backupAttemptRecorded: Boolean(intent.dependencies.backupAttempt),
      backupBound: Boolean(intent.dependencies.backup) } } : {}) };
}
function handle(claim: Claim, commonDir: string): MaintenanceHandle {
  if (!claim.maintenance) throw new Error('typed maintenance claim required');
  return { operationId: claim.maintenance.operationId, claimId: claim.id, token: claim.token,
    repositoryId: claim.resourceKey, commonDir };
}
function assertFactory(directory: string) {
  const stat = lstatSync(directory);
  if (!stat.isDirectory() || stat.isSymbolicLink() || realpathSync(directory) !== directory)
    throw new Error('factory storage must be an owned directory, not a symlink');
  assertLocalPlacement(directory);
}
function configure(database: DatabaseSync) {
  database.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON');
  if (database.prepare('PRAGMA journal_mode').get()?.['journal_mode'] !== 'wal'
    || database.prepare('PRAGMA synchronous').get()?.['synchronous'] !== 2
    || database.prepare('PRAGMA foreign_keys').get()?.['foreign_keys'] !== 1)
    throw new Error('required SQLite durability settings unavailable');
}
function createBootstrapDatabase(path: string, claim: Claim) {
  const directory = dirname(path), children = readdirSync(directory);
  if (children.some(name => name !== 'bootstrap-incomplete'))
    throw new Error('bootstrap database recovery requires marker-only storage; inspect other children');
  const fd = openSync(path, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | (constants.O_NOFOLLOW ?? 0), 0o600);
  closeSync(fd);
  const database = new DatabaseSync(path, { timeout: 100 });
  try {
    configure(database);
    initializeSchema(database, { repository: { id: claim.resourceKey, release: claim.maintenance!.release },
      claim: { id: claim.id, token: claim.token, resourceKey: claim.resourceKey, data: JSON.stringify(claim) } });
  } finally { database.close(); }
}

/** Reserve an absent Git-common root; a complete intent is durable before SQLite is created. */
export async function beginRepositoryBootstrap(repository: string, selection: MaintenanceSelection, owner: Owner): Promise<MaintenanceHandle> {
  const { root, common } = await repositoryIdentity(repository);
  selected(selection);
  validOwner(owner);
  assertLocalPlacement(common);
  const directory = join(common, 'factory');
  mkdirSync(directory, { mode: 0o700 }); // Nonrecursive EEXIST is the first-installer exclusion.
  flushDirectory(common);
  assertFactory(directory);
  const operationId = randomUUID(), repositoryId = randomUUID();
  const claim: Claim = { id: randomUUID(), token: randomUUID(), kind: 'maintenance', resourceKey: repositoryId,
    invocationId: null, owner, maintenance: intent(operationId, repositoryId, 'install', directory, selection) };
  const payload: BootstrapPayload = { version: 1, root, commonDir: common, claim };
  writeRecord(join(directory, 'bootstrap-incomplete'), { ...payload, digest: hash(JSON.stringify(payload)) });
  createBootstrapDatabase(join(directory, 'history.sqlite'), claim);
  return handle(claim, common);
}

/** Existing ready stores use the same owner_claims admission gate as runners and dashboards. */
export async function beginMaintenance(repository: string, kind: MaintenanceKind, selection: MaintenanceSelection, owner: Owner): Promise<MaintenanceHandle> {
  if (!KINDS.includes(kind)) throw new Error('unsupported maintenance operation');
  if (kind === 'install') throw new Error('install requires an absent bootstrap root');
  if (kind === 'dependencies') throw new Error('dependencies require exact installed selection admission');
  const { common } = await repositoryIdentity(repository);
  selected(selection);
  const store = openRepositoryStore(common);
  try {
    const claim = await store.beginMaintenance(intent(randomUUID(), store.repositoryId(), kind, join(common, 'factory'), selection), owner);
    return handle(claim, common);
  } finally { store.close(); }
}

function verifyForwardBackup(common: string, claim: Claim) {
  const intent = assertRecordedIntent(common, claim), bound = intent.forward?.backup;
  if (intent.kind !== 'upgrade' || !intent.forward || !bound || bound.id !== intent.backupId)
    throw new Error('verified forward backup binding required');
  const source = lstatSync(join(common, 'factory', 'history.sqlite'), { bigint: true });
  if (!source.isFile() || source.isSymbolicLink() || source.nlink !== 1n
    || `${source.dev}:${source.ino}` !== intent.forward.sourceIdentity
    || !absent(join(common, 'factory', 'bootstrap-incomplete')))
    throw new Error('forward source identity or marker changed');
  const path = forwardBackupPath(common, intent.operationId, bound.id), directory = dirname(path);
  for (const part of [dirname(directory), directory]) {
    const stat = lstatSync(part);
    if (!stat.isDirectory() || stat.isSymbolicLink() || realpathSync(part) !== part
      || (process.platform !== 'win32' && (stat.mode & 0o077) !== 0)) throw new Error('forward backup directory changed');
  }
  if (readdirSync(directory).sort().join(',') !== 'backup-receipt.json,backup-request.json,history.sqlite')
    throw new Error('forward backup inventory changed');
  const actual = fileDigest(path);
  if (actual.identity !== bound.identity || actual.sha256 !== bound.sha256 || actual.bytes !== bound.bytes)
    throw new Error('forward backup changed after binding');
  const receiptBytes = readRecord(join(directory, 'backup-receipt.json'));
  if (hash(receiptBytes) !== bound.receiptSha256) throw new Error('forward backup receipt changed');
  const receipt = JSON.parse(receiptBytes.toString('utf8')) as Record<string, unknown>;
  if (receipt.version !== 1 || receipt.operationId !== intent.operationId || receipt.backupId !== bound.id
    || receipt.repositoryId !== intent.repositoryId || receipt.sourceShape !== intent.forward.sourceShape
    || receipt.sourceRelease !== intent.forward.sourceRelease || receipt.sourceIdentity !== intent.forward.sourceIdentity
    || receipt.selectionDigest !== intent.selectionDigest || receipt.receiptId !== bound.receiptId
    || receipt.requestSha256 !== hash(readRecord(join(directory, 'backup-request.json')))
    || receipt.identity !== bound.identity || receipt.sha256 !== bound.sha256 || receipt.bytes !== bound.bytes
    || receipt.countDigest !== bound.countDigest) throw new Error('forward backup receipt differs');
  const copied = openImmutableForwardBackup(path);
  try {
    assertForwardIntegrity(copied);
    const rows = copied.prepare('SELECT id,release,state FROM repository LIMIT 2').all();
    if (knownForwardShape(copied) !== intent.forward.sourceShape || forwardCounts(copied).digest !== bound.countDigest
      || rows.length !== 1 || rows[0]?.['id'] !== intent.repositoryId || rows[0]['release'] !== intent.forward.sourceRelease
      || rows[0]['state'] !== 'ready'
      || copied.prepare('SELECT id,token FROM owner_claims LIMIT 2').all().length !== 1
      || copied.prepare('SELECT id FROM owner_claims').get()?.['id'] !== claim.id)
      throw new Error('forward backup rows differ from bound operation');
  } finally { copied.close(); }
}

function openControllerStore(common: string) {
  const databasePath = join(common, 'factory', 'history.sqlite');
  const file = lstatSync(databasePath);
  if (!file.isFile() || file.isSymbolicLink() || file.nlink !== 1
    || (process.platform !== 'win32' && (file.mode & 0o077) !== 0)) throw new Error('invalid controller store file');
  for (const suffix of ['-wal', '-shm', '-journal']) {
    const sidecar = `${databasePath}${suffix}`;
    if (absent(sidecar)) continue;
    const stat = lstatSync(sidecar);
    if (!stat.isFile() || stat.isSymbolicLink() || stat.nlink !== 1
      || (process.platform !== 'win32' && (stat.mode & 0o077) !== 0))
      throw new Error('invalid controller store sidecar');
  }
  try { return openMaintenanceStore(common); }
  catch (error) {
    if (!(error instanceof Error) || !error.message.includes('incompatible schema')) throw error;
    return openForwardMaintenanceStore(common);
  }
}

async function createAndBindForwardBackup(current: MaintenanceHandle, planned: MaintenanceIntent) {
  const common = current.commonDir;
  const target = forwardBackupPath(common, current.operationId, planned.backupId!);
  const backups = join(common, 'factory', 'maintenance-backups'), operationDir = dirname(dirname(target)), backupDir = dirname(target);
  for (const path of [backups, operationDir, backupDir]) {
    if (absent(path)) mkdirSync(path, { mode: 0o700 });
    else if (path === backupDir) throw new Error('forward backup target already exists; preserve for inspection');
    const stat = lstatSync(path);
    if (!stat.isDirectory() || stat.isSymbolicLink() || realpathSync(path) !== path
      || (process.platform !== 'win32' && (stat.mode & 0o077) !== 0)) throw new Error('invalid forward backup directory');
    flushDirectory(dirname(path));
  }
  await runForwardBackup(join(common, 'factory', 'history.sqlite'), target);
  if (readdirSync(backupDir).sort().join(',') !== 'backup-request.json,history.sqlite')
    throw new Error('forward backup helper left unexpected inventory');
  const details = fileDigest(target), sourceStore = openForwardMaintenanceStore(common);
  try {
    const live = sourceStore.readMaintenanceClaim(current.operationId);
    if (live.id !== current.claimId || live.token !== current.token || live.maintenance?.forward?.backup !== null
      || live.maintenance.forward.currentShape !== planned.forward!.sourceShape
      || sourceStore.forwardShape() !== planned.forward!.sourceShape
      || sourceStore.forwardIdentity() !== planned.forward!.sourceIdentity
      || sourceStore.repositoryRelease() !== planned.forward!.sourceRelease)
      throw new Error('forward backup source changed');
    const copied = openImmutableForwardBackup(target);
    try {
      assertForwardIntegrity(copied);
      if (knownForwardShape(copied) !== planned.forward!.sourceShape
        || copied.prepare('SELECT id,release,state FROM repository LIMIT 2').all().length !== 1
        || copied.prepare('SELECT id,release,state FROM repository').get()?.['id'] !== current.repositoryId
        || copied.prepare('SELECT release FROM repository').get()?.['release'] !== planned.forward!.sourceRelease
        || copied.prepare('SELECT id FROM owner_claims LIMIT 2').all().length !== 1
        || copied.prepare('SELECT token FROM owner_claims').get()?.['token'] !== current.token
        || forwardCounts(copied).digest !== sourceStore.forwardCounts().digest)
        throw new Error('forward backup content or counts differ');
      const receipt = { version: 1, receiptId: randomUUID(), operationId: current.operationId, backupId: planned.backupId,
        repositoryId: current.repositoryId, sourceShape: planned.forward!.sourceShape,
        sourceRelease: planned.forward!.sourceRelease, sourceIdentity: planned.forward!.sourceIdentity,
        selectionDigest: planned.selectionDigest,
        requestSha256: hash(readRecord(join(backupDir, 'backup-request.json'))),
        ...details, countDigest: forwardCounts(copied).digest };
      writeRecord(join(backupDir, 'backup-receipt.json'), receipt);
      await sourceStore.bindForwardBackup({ handle: current,
        backup: { id: planned.backupId!, identity: details.identity, sha256: details.sha256,
          bytes: details.bytes, countDigest: receipt.countDigest, receiptId: receipt.receiptId,
          receiptSha256: hash(`${JSON.stringify(receipt)}\n`) } });
    } finally { copied.close(); }
  } finally { sourceStore.close(); }
  return { ...current, backupId: planned.backupId! };
}

/** Administrative admission precedes any schema/data mutation; verified backup is then bound by exact CAS. */
export async function prepareForwardSchema(repository: string, selection: MaintenanceSelection, owner: Owner) {
  const { common } = await repositoryIdentity(repository);
  selected(selection); validOwner(owner);
  if (inspectOwner(owner).state !== 'known_live') throw new Error('forward owner identity unavailable');
  const store = openForwardMaintenanceStore(common);
  let claim: Claim;
  try {
    const operationId = randomUUID(), backupId = randomUUID(), shape = store.forwardShape();
    const planned = intent(operationId, store.repositoryId(), 'upgrade', join(common, 'factory'), selection);
    planned.backupId = backupId;
    planned.forward = { sourceShape: shape, currentShape: shape, sourceRelease: store.repositoryRelease(),
      sourceIdentity: store.forwardIdentity(), backup: null };
    claim = await store.beginForwardMaintenance(planned, owner);
  } finally { store.close(); }
  return createAndBindForwardBackup(handle(claim, common), claim.maintenance!);
}

/** Read-only status is available even when normal open rejects the marker or incomplete state. */
export async function inspectMaintenance(repository: string) {
  const { root, common } = await repositoryIdentity(repository);
  const directory = join(common, 'factory');
  if (absent(directory)) return { status: 'absent' as const, commonDir: common, marker: 'absent', database: 'absent', claims: 0 };
  try { assertFactory(directory); } catch { return { status: 'blocked' as const, commonDir: common, marker: 'unknown', database: 'unknown', claims: 0 }; }
  const markerPath = join(directory, 'bootstrap-incomplete'), databasePath = join(directory, 'history.sqlite');
  const upgradeMarkerPath = join(directory, 'upgrade-incomplete');
  let upgradeMarker: { operationId: string; claimId: string } | undefined;
  if (!absent(upgradeMarkerPath)) {
    try {
      const value = JSON.parse(readRecord(upgradeMarkerPath).toString('utf8')) as Record<string, unknown>;
      if (value['version'] !== 1 || typeof value['operationId'] !== 'string' || !UUID.test(value['operationId'])
        || typeof value['claimId'] !== 'string' || !UUID.test(value['claimId'])) throw new Error('invalid upgrade marker');
      const markerInfo = lstatSync(upgradeMarkerPath), template = lstatSync(join(directory, `upgrade-${value['operationId']}`, 'marker-template.json'));
      if (!markerInfo.isFile() || markerInfo.isSymbolicLink() || markerInfo.nlink !== 2 || template.nlink !== 2
        || markerInfo.dev !== template.dev || markerInfo.ino !== template.ino) throw new Error('upgrade marker identity differs');
      upgradeMarker = { operationId: value['operationId'], claimId: value['claimId'] };
    } catch { return { status: 'blocked' as const, commonDir: common, marker: 'invalid', database: 'unknown', claims: 0 }; }
  }
  let marker: BootstrapRecord | undefined;
  if (!absent(markerPath)) {
    try { marker = parseMarker(markerPath, root, common); }
    catch { return { status: 'blocked' as const, commonDir: common, marker: 'invalid', database: absent(databasePath) ? 'absent' : 'unknown', claims: 0 }; }
  }
  if (marker && upgradeMarker) return { status: 'blocked' as const, commonDir: common, marker: 'invalid', database: 'unknown', claims: 0 };
  if (absent(databasePath)) {
    if (readdirSync(directory).some(name => name !== 'bootstrap-incomplete'))
      return { status: 'blocked' as const, commonDir: common, marker: marker ? 'complete' : 'absent', database: 'absent', claims: 0 };
    return marker
      ? { status: 'incomplete' as const, commonDir: common, marker: 'complete', database: 'absent', claims: 0, intent: redacted(marker.claim.maintenance!) }
      : { status: 'blocked' as const, commonDir: common, marker: 'absent', database: 'absent', claims: 0 };
  }
  try {
    const info = lstatSync(databasePath);
    if (!info.isFile() || info.isSymbolicLink() || info.nlink !== 1
      || (process.platform !== 'win32' && (info.mode & 0o077) !== 0)) throw new Error('nonprivate database');
    for (const suffix of ['-wal', '-shm', '-journal']) {
      const sidecar = `${databasePath}${suffix}`;
      if (absent(sidecar)) continue;
      const stat = lstatSync(sidecar);
      if (!stat.isFile() || stat.isSymbolicLink() || stat.nlink !== 1
        || (process.platform !== 'win32' && (stat.mode & 0o077) !== 0)) throw new Error('nonprivate database sidecar');
    }
    const database = new DatabaseSync(databasePath, { readOnly: true, timeout: 100 });
    try {
      const observedShape = knownForwardShape(database);
      assertForwardIntegrity(database);
      const row = database.prepare('SELECT id,state FROM repository').get();
      if (!row) throw new Error('missing repository');
      const claims = database.prepare('SELECT data FROM owner_claims LIMIT 2').all();
      const typed = claims.map(entry => JSON.parse(String(entry['data'])) as Claim).find(claim => claim.maintenance);
      if (typed) assertRecordedIntent(common, typed);
      if (typed?.maintenance?.kind === 'dependencies') await assertDependencyMaintenance(root, handle(typed, common));
      if (typed?.maintenance?.forward?.backup) verifyForwardBackup(common, typed);
      if (typed) verifyInstallCandidate(common, typed, false);
      if (typed && claims.length !== 1) throw new Error('typed maintenance claim is not exclusive');
      if (upgradeMarker && typed && (typed.maintenance?.operationId !== upgradeMarker.operationId || typed.id !== upgradeMarker.claimId))
        throw new Error('upgrade marker and claim disagree');
      if (marker && (marker.claim.resourceKey !== row['id'] || (typed && !sameBootstrapOperation(marker, typed))))
        throw new Error('marker and database disagree');
      if (row['state'] === 'incomplete' && !typed) throw new Error('incomplete repository without recorded operation');
      if (!marker && typed?.maintenance?.kind === 'install' && row['state'] === 'incomplete')
        throw new Error('incomplete install missing bootstrap marker');
      const summary = typed?.maintenance ? redacted(typed.maintenance) : marker ? redacted(marker.claim.maintenance!) : undefined;
      return { status: marker || upgradeMarker || row['state'] !== 'ready' || typed ? 'incomplete' as const : 'ready' as const,
        commonDir: common, marker: marker ? 'complete' : upgradeMarker ? 'upgrade' : 'absent', database: observedShape === 'v7' ? 'current' : observedShape, claims: claims.length,
        ...(typed ? { owner: { ...typed.owner, ...inspectOwner(typed.owner) } } : {}),
        ...(summary ? { intent: summary } : {}) };
    } finally { database.close(); }
  } catch {
    return { status: 'blocked' as const, commonDir: common, marker: marker ? 'complete' : 'absent', database: 'invalid', claims: 0 };
  }
}

/** Only a recorded complete marker can resume an absent database after inspected owner clearance. */
export async function reclaimMaintenance(repository: string, operationId: string, owner: Owner,
  clearance: { operatorConfirmed: boolean; note: string; replacementBackupId?: string; launcher?: Owner }): Promise<MaintenanceHandle> {
  if (clearance.operatorConfirmed !== true || !clearance.note?.trim() || Buffer.byteLength(clearance.note) > 256)
    throw new Error('explicit bounded operator clearance required');
  const { root, common } = await repositoryIdentity(repository);
  const directory = join(common, 'factory'); assertFactory(directory);
  const markerPath = join(directory, 'bootstrap-incomplete');
  const marker = absent(markerPath) ? undefined : parseMarker(markerPath, root, common);
  const databasePath = join(directory, 'history.sqlite');
  if (marker && marker.claim.maintenance!.operationId !== operationId) throw new Error('recorded operation differs from repair request');
  if (absent(databasePath)) {
    if (!marker) throw new Error('absent database has no recorded bootstrap intent');
    if (inspectOwner(marker.claim.owner).state === 'known_live') throw new Error('known-live owner cannot be reclaimed');
    createBootstrapDatabase(databasePath, marker.claim);
  }
  const store = openControllerStore(common);
  try {
    const claim = store.readMaintenanceClaim(operationId);
    if (claim.maintenance?.kind === 'dependencies') throw new Error('dependency admission requires later operation-specific recovery');
    assertRecordedIntent(common, claim);
    if (claim.maintenance?.forward?.backup) verifyForwardBackup(common, claim);
    else if (claim.maintenance?.forward && !clearance.replacementBackupId)
      throw new Error('unbound forward backup requires explicit fresh backup recovery');
    if (claim.maintenance?.kind === 'install' && !marker) throw new Error('bootstrap marker missing; repair refused');
    if (marker && !sameBootstrapOperation(marker, claim))
      throw new Error('bootstrap marker and claim identity differ');
    verifyInstallCandidate(common, claim, false);
    if (claim.maintenance?.stageDigest || claim.maintenance?.stageIdentity) {
      const measured = stageEvidence(claim.maintenance!.stagePath);
      if (measured.stageDigest !== claim.maintenance?.stageDigest || measured.stageIdentity !== claim.maintenance?.stageIdentity)
        throw new Error('recorded maintenance stage changed; repair refused');
    }
    const inspection = inspectOwner(claim.owner);
    if (claim.maintenance?.activeLauncher && inspectOwner(claim.maintenance.activeLauncher).state === 'known_live')
      throw new Error('known-live original launcher cannot be reclaimed');
    if (claim.maintenance?.activeLauncher && !clearance.launcher) throw new Error('replacement launcher binding required');
    if (inspection.state === 'known_live') throw new Error('known-live owner cannot be reclaimed');
    return handle(await store.reclaimMaintenance({ operationId, expectedToken: claim.token,
      expectedOwner: claim.owner, expectedPhase: claim.maintenance!.phase, owner,
      inspection: inspection.state, note: clearance.note,
      ...(clearance.replacementBackupId ? { replacementBackupId: clearance.replacementBackupId } : {}),
      ...(clearance.launcher ? { launcher: clearance.launcher } : {}) }), common);
  } finally { store.close(); }
}

function stageEvidence(stagePath: string) {
  const stageIdentity = identity(stagePath);
  const payload = join(stagePath, 'payload');
  const payloadIdentity = identity(payload);
  const files: string[] = [];
  const directories: string[] = [];
  const stageEntries = readdirSync(stagePath);
  if (stageEntries.length > 64) throw new Error('stage sidecar inventory exceeds limit');
  for (const entry of stageEntries) {
    if (entry !== 'payload' && entry !== 'handoff-ticket.json' && !/^handoff-ticket-[0-9a-f-]{36}\.tmp$/.test(entry)
      && !/^handoff-exit-[0-9a-f-]{36}\.json$/.test(entry)) throw new Error('foreign stage root content');
    if (entry !== 'payload') {
      const sidecar = lstatSync(join(stagePath, entry));
      if (!sidecar.isFile() || sidecar.isSymbolicLink() || sidecar.size < 1 || sidecar.size > MAX_RECORD_BYTES
        || (process.platform !== 'win32' && (sidecar.mode & 0o077) !== 0))
        throw new Error('nonprivate or nonregular stage sidecar');
    }
  }
  const walk = (directory: string, prefix: string) => {
    for (const entry of readdirSync(directory).sort()) {
      const relative = prefix ? `${prefix}/${entry}` : entry;
      const path = join(directory, entry), info = lstatSync(path);
      if (info.isSymbolicLink() || !/^[a-zA-Z0-9._/-]+$/.test(relative) || relative.split('/').includes('..'))
        throw new Error('linked or unsafe stage path');
      if (info.isDirectory()) { directories.push(relative); walk(path, relative); }
      else if (info.isFile()) files.push(relative);
      else throw new Error('nonregular stage content');
      if (files.length > 512) throw new Error('stage inventory exceeds limit');
    }
  };
  walk(payload, '');
  if (files.length < 1) throw new Error('empty stage payload');
  const digest = createHash('sha256');
  for (const relative of directories.sort()) { digest.update('D'); digest.update(relative); digest.update('\0'); }
  let total = 0;
  for (const relative of files) {
    const path = join(payload, relative), info = lstatSync(path, { bigint: true });
    if (!info.isFile() || info.isSymbolicLink() || info.size < 0n || info.size > 256n * 1024n * 1024n)
      throw new Error('nonregular or oversized stage file');
    const size = Number(info.size);
    total += size;
    if (total > 256 * 1024 * 1024) throw new Error('stage payload exceeds limit');
    digest.update('F'); digest.update(relative); digest.update('\0'); digest.update(String(size)); digest.update('\0');
    digest.update(String(info.mode & 0o777n)); digest.update('\0');
    const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
    try {
      const before = fstatSync(fd, { bigint: true }), buffer = Buffer.allocUnsafe(65536);
      if (!before.isFile() || before.dev !== info.dev || before.ino !== info.ino || before.size !== info.size)
        throw new Error('stage content changed');
      for (let offset = 0; offset < size;) {
        const count = readSync(fd, buffer, 0, Math.min(buffer.length, size - offset), offset);
        if (!count) throw new Error('stage content changed');
        digest.update(buffer.subarray(0, count)); offset += count;
      }
      const after = fstatSync(fd, { bigint: true }), current = lstatSync(path, { bigint: true });
      if (after.size !== before.size || after.mtimeNs !== before.mtimeNs || current.isSymbolicLink()
        || current.dev !== before.dev || current.ino !== before.ino) throw new Error('stage content changed');
    } finally { closeSync(fd); }
  }
  if (identity(stagePath) !== stageIdentity || identity(payload) !== payloadIdentity)
    throw new Error('stage identity changed');
  return { stageIdentity, stageDigest: digest.digest('hex') };
}
/** Read-only payload limit and identity proof for a preparer that leaves the phase unchanged. */
export function measureMaintenanceStage(stagePath: string) { return stageEvidence(stagePath); }

/** Create a private one-use ticket only after a caller has staged a self-contained payload. */
export async function prepareMaintenanceHandoff(repository: string, current: MaintenanceHandle) {
  const { root, common } = await repositoryIdentity(repository);
  if (common !== current.commonDir) throw new Error('handoff repository differs');
  const store = openControllerStore(common);
  try {
    const claim = store.readMaintenanceClaim(current.operationId), recorded = claim.maintenance!;
    if (recorded.kind === 'dependencies') throw new Error('dependency admission has no backup, stage or handoff authority');
    assertRecordedIntent(common, claim);
    if (recorded.forward) verifyForwardBackup(common, claim);
    if (claim.id !== current.claimId || claim.token !== current.token
      || (recorded.phase !== 'preparing' && !(recorded.phase === 'handoff-ready' && recorded.ticketNonceHash === null)))
      throw new Error('maintenance claim/token/phase no longer matches');
    if (recorded.stagePath !== join(common, 'factory', 'controller-staging', current.operationId))
      throw new Error('stage path differs from recorded operation');
    const markerPath = join(common, 'factory', 'bootstrap-incomplete');
    if (recorded.kind === 'install' && absent(markerPath)) throw new Error('bootstrap marker missing; handoff refused');
    if (!absent(markerPath) && !sameBootstrapOperation(parseMarker(markerPath, root, common), claim))
      throw new Error('bootstrap marker differs from maintenance claim');
    verifyInstallCandidate(common, claim, true);
    const stage = stageEvidence(recorded.stagePath), nonce = randomUUID();
    if ((recorded.kind === 'install' || recorded.artifactDigests['original-installed'])
      && (recorded.stageDigest !== stage.stageDigest || recorded.stageIdentity !== stage.stageIdentity))
      throw new Error('prepared installation stage changed');
    const ticket: HandoffTicket = { version: 1, operationId: current.operationId, repositoryId: current.repositoryId,
      root, commonDir: common, claimId: current.claimId, token: current.token,
      stagePath: recorded.stagePath, ...stage, nonce,
      release: recorded.release, selectionDigest: recorded.selectionDigest,
      targetReleaseSha256: recorded.targetReleaseSha256, artifactDigests: recorded.artifactDigests,
      targetSchema: recorded.targetSchema, candidate: recorded.candidate ?? null,
      exitReceiptPath: join(recorded.stagePath, `handoff-exit-${nonce}.json`) };
    const ticketPath = join(recorded.stagePath, 'handoff-ticket.json');
    if (absent(ticketPath)) writeRecord(ticketPath, ticket);
    else {
      const prior = JSON.parse(readRecord(ticketPath).toString('utf8')) as HandoffTicket;
      if (prior.version !== 1 || prior.operationId !== current.operationId || prior.claimId !== current.claimId
        || prior.stagePath !== recorded.stagePath || prior.stageDigest !== stage.stageDigest)
        throw new Error('foreign handoff ticket collision');
      const replacement = join(recorded.stagePath, `handoff-ticket-${randomUUID()}.tmp`);
      writeRecord(replacement, ticket);
      renameSync(replacement, ticketPath);
      flushDirectory(recorded.stagePath);
      if (JSON.parse(readRecord(ticketPath).toString('utf8')).nonce !== nonce)
        throw new Error('handoff ticket replacement failed verification');
    }
    if (recorded.phase === 'preparing')
      await store.advanceMaintenance({ handle: current, expected: 'preparing', next: 'handoff-ready', ...stage, ticketNonceHash: hash(nonce) });
    else await store.reissueMaintenanceHandoff({ handle: current, ...stage, nonceHash: hash(nonce) });
    return { operationId: current.operationId, repositoryId: current.repositoryId, claimId: current.claimId,
      stagePath: recorded.stagePath, ticketPath, stageDigest: stage.stageDigest };
  } finally { store.close(); }
}

/** The staged entry calls this after the external launcher has written its post-wait receipt. */
export async function consumeMaintenanceHandoff(ticketPath: string) {
  if (basename(ticketPath) !== 'handoff-ticket.json') throw new Error('invalid handoff ticket path');
  const ticket = JSON.parse(readRecord(ticketPath).toString('utf8')) as HandoffTicket;
  if (ticket.version !== 1 || !UUID.test(ticket.operationId) || dirname(ticketPath) !== ticket.stagePath
    || ticket.stagePath !== join(ticket.commonDir, 'factory', 'controller-staging', ticket.operationId)
    || !UUID.test(ticket.nonce) || ticket.exitReceiptPath !== join(ticket.stagePath, `handoff-exit-${ticket.nonce}.json`))
    throw new Error('handoff ticket identity invalid');
  const receipt = JSON.parse(readRecord(ticket.exitReceiptPath).toString('utf8')) as ExitReceipt;
  if (receipt.version !== 1 || receipt.operationId !== ticket.operationId || receipt.claimId !== ticket.claimId
    || receipt.stageDigest !== ticket.stageDigest || receipt.nonce !== ticket.nonce)
    throw new Error('handoff exit receipt invalid');
  const { root, common } = await repositoryIdentity(ticket.root);
  if (root !== ticket.root || common !== ticket.commonDir) throw new Error('handoff repository identity changed');
  const stage = stageEvidence(ticket.stagePath);
  if (stage.stageDigest !== ticket.stageDigest || stage.stageIdentity !== ticket.stageIdentity)
    throw new Error('handoff stage changed');
  const markerPath = join(common, 'factory', 'bootstrap-incomplete');
  const store = openControllerStore(common);
  try {
    const claim = store.readMaintenanceClaim(ticket.operationId);
    assertRecordedIntent(common, claim);
    if (claim.maintenance?.forward) verifyForwardBackup(common, claim);
    if (ticket.release !== claim.maintenance?.release || ticket.selectionDigest !== claim.maintenance.selectionDigest
      || ticket.targetReleaseSha256 !== claim.maintenance.targetReleaseSha256
      || JSON.stringify(ticket.artifactDigests) !== JSON.stringify(claim.maintenance.artifactDigests)
      || ticket.targetSchema !== claim.maintenance.targetSchema)
      throw new Error('handoff ticket selection differs from recorded intent');
    if (JSON.stringify(ticket.candidate ?? null) !== JSON.stringify(claim.maintenance.candidate ?? null))
      throw new Error('handoff candidate binding differs');
    verifyInstallCandidate(common, claim, claim.maintenance.kind === 'install'
      || Boolean(claim.maintenance.artifactDigests['original-installed']));
    if (claim.maintenance?.kind === 'install' && absent(markerPath)) throw new Error('bootstrap marker missing; handoff refused');
    if (!absent(markerPath) && !sameBootstrapOperation(parseMarker(markerPath, root, common), claim))
      throw new Error('handoff bootstrap marker differs');
    const owner = currentOwner();
    if (inspectOwner(owner).state !== 'known_live')
      throw new Error('staged process owner identity unavailable; handoff refused');
    if (claim.maintenance?.activeLauncher) {
      const parent = currentOwner(process.ppid), expected = claim.maintenance.activeLauncher;
      if (parent.host !== expected.host || parent.pid !== expected.pid || parent.start !== expected.start
        || inspectOwner(parent).state !== 'known_live') throw new Error('handoff launcher identity differs');
    }
    return await store.consumeMaintenanceHandoff({ handle: { operationId: ticket.operationId, claimId: ticket.claimId,
      token: ticket.token, repositoryId: ticket.repositoryId, commonDir: common },
      nonceHash: hash(ticket.nonce), ...stage, owner });
  } finally { store.close(); }
}

/** Trusted phase CAS leaves publication and claim release to the installed validator. */
export async function recordMaintenanceStage(current: MaintenanceHandle, expected: MaintenancePhase, next: MaintenancePhase) {
  const store = openControllerStore(current.commonDir);
  try {
    const claim = store.readMaintenanceClaim(current.operationId);
    assertRecordedIntent(current.commonDir, claim);
    if (claim.maintenance?.forward) verifyForwardBackup(current.commonDir, claim);
    const markerPath = join(current.commonDir, 'factory', 'bootstrap-incomplete');
    if (claim.maintenance?.kind === 'install' && absent(markerPath)) throw new Error('bootstrap marker missing; phase refused');
    verifyInstallCandidate(current.commonDir, claim, claim.maintenance?.kind === 'install');
    if (!absent(markerPath)) {
      const raw = JSON.parse(readRecord(markerPath).toString('utf8')) as BootstrapRecord;
      const { root, common } = await repositoryIdentity(raw.root);
      if (common !== current.commonDir || !sameBootstrapOperation(parseMarker(markerPath, root, common), claim))
        throw new Error('bootstrap marker differs from maintenance claim');
    }
    if (claim.maintenance?.stageDigest && claim.maintenance.stageIdentity) {
      const measured = stageEvidence(claim.maintenance.stagePath);
      if (measured.stageDigest !== claim.maintenance.stageDigest || measured.stageIdentity !== claim.maintenance.stageIdentity)
        throw new Error('maintenance stage changed before phase transition');
    }
    return await store.advanceMaintenance({ handle: current, expected, next });
  }
  finally { store.close(); }
}

/** One crash-atomic historical DDL step. Calling again after a commit advances only the recorded next step. */
export async function advanceForwardSchema(current: MaintenanceHandle): Promise<{ shape: ForwardShape; state: 'incomplete' }> {
  const store = openForwardMaintenanceStore(current.commonDir);
  try {
    const claim = store.readMaintenanceClaim(current.operationId), intent = assertRecordedIntent(current.commonDir, claim);
    if (!intent.forward || claim.id !== current.claimId || claim.token !== current.token
      || claim.resourceKey !== current.repositoryId || intent.phase !== 'modifying' || !intent.ticketConsumed
      || !intent.stageDigest || !intent.stageIdentity || store.forwardShape() !== intent.forward.currentShape
      || store.forwardIdentity() !== intent.forward.sourceIdentity
      || store.repositoryRelease() !== intent.forward.sourceRelease)
      throw new Error('forward step claim/token/checkpoint differs');
    const live = currentOwner();
    if (inspectOwner(live).state !== 'known_live' || live.host !== claim.owner.host
      || live.pid !== claim.owner.pid || live.start !== claim.owner.start)
      throw new Error('forward step requires live staged controller owner');
    verifyForwardBackup(current.commonDir, claim);
    const stage = stageEvidence(intent.stagePath);
    if (stage.stageDigest !== intent.stageDigest || stage.stageIdentity !== intent.stageIdentity)
      throw new Error('forward stage changed');
    if (intent.forward.currentShape === 'v7') return { shape: 'v7', state: 'incomplete' };
    const shape = await store.advanceForwardStep(current);
    return { shape, state: 'incomplete' };
  } finally { store.close(); }
}

/** Revalidate the sole staged upgrade owner, backup and immutable stage before publication steps. */
export function assertForwardPublication(current: MaintenanceHandle): Claim {
  const store = openForwardMaintenanceStore(current.commonDir);
  try {
    const claim = store.readMaintenanceClaim(current.operationId), selected = assertRecordedIntent(current.commonDir, claim);
    if (claim.id !== current.claimId || claim.token !== current.token || claim.resourceKey !== current.repositoryId
      || selected.kind !== 'upgrade' || !selected.artifactDigests['original-installed'] || !selected.upgradeIntentSha256
      || !selected.forward?.backup || selected.forward.currentShape !== 'v7' || store.forwardShape() !== 'v7'
      || store.forwardIdentity() !== selected.forward.sourceIdentity || store.repositoryRelease() !== selected.forward.sourceRelease
      || !selected.ticketConsumed || !['modifying', 'validating'].includes(selected.phase))
      throw new Error('upgrade publication claim/token/checkpoint differs');
    const live = currentOwner(), parent = currentOwner(process.ppid), launcher = selected.activeLauncher;
    if (inspectOwner(live).state !== 'known_live' || live.host !== claim.owner.host
      || live.pid !== claim.owner.pid || live.start !== claim.owner.start)
      throw new Error('upgrade publication requires live staged owner');
    if (!launcher || parent.host !== launcher.host || parent.pid !== launcher.pid || parent.start !== launcher.start
      || inspectOwner(parent).state !== 'known_live') throw new Error('upgrade publication launcher differs');
    store.assertSoleMaintenance(current);
    verifyForwardBackup(current.commonDir, claim);
    verifyInstallCandidate(current.commonDir, claim, true);
    const stage = stageEvidence(selected.stagePath);
    if (stage.stageDigest !== selected.stageDigest || stage.stageIdentity !== selected.stageIdentity)
      throw new Error('upgrade publication stage changed');
    return claim;
  } finally { store.close(); }
}

/** Explicit operator clearance may release a still-unmodified preparation, never its evidence. */
export async function abandonUpgradePreparation(repository: string, operationId: string,
  clearance: { operatorConfirmed: boolean; note: string }, expectedManifestSha256?: string): Promise<void> {
  if (clearance.operatorConfirmed !== true || typeof clearance.note !== 'string' || !clearance.note.trim()
    || Buffer.byteLength(clearance.note) > 256) throw new Error('explicit bounded operator clearance required');
  const { root, common } = await repositoryIdentity(repository);
  const store = openForwardMaintenanceStore(common);
  try {
    const claim = store.readMaintenanceClaim(operationId), selected = assertRecordedIntent(common, claim);
    if (selected.kind !== 'upgrade' || selected.phase !== 'preparing' || selected.ticketConsumed
      || !selected.artifactDigests['original-installed'] || !selected.artifactDigests['original-completion']
      || (expectedManifestSha256 !== undefined && selected.targetReleaseSha256 !== expectedManifestSha256))
      throw new Error('unmodified installed upgrade preparation required');
    const operation = join(common, 'factory', `upgrade-${operationId}`);
    directoryIdentity(operation);
    const originalPath = join(operation, 'original.json');
    const original = JSON.parse(readRecord(originalPath).toString('utf8')) as OriginalInstallation;
    if (original.root !== root || original.common !== common || hash(JSON.stringify(original)) !== selected.artifactDigests['original-installed'])
      throw new Error('original installed evidence differs');
    assertOriginalInstallation(common, original);
    const ownerState = inspectOwner(claim.owner), launcherState = inspectOwner(original.launcher);
    if (ownerState.state === 'known_live' || launcherState.state === 'known_live')
      throw new Error('known-live owner or launcher cannot be cleared');
    await store.abandonUpgradePreparation({ handle: handle(claim, common), expectedOwner: claim.owner,
      note: clearance.note, ownerState: ownerState.state, ownerLimitation: ownerState.limitation,
      launcher: original.launcher, validateOriginal: () => assertOriginalInstallation(common, original) });
  } finally { store.close(); }
}

/** Redacted operation inspection is available even while normal startup rejects the old schema. */
export async function inspectForwardSchema(repository: string, operationId: string) {
  const status = await inspectMaintenance(repository);
  if (status.status !== 'incomplete' || !('intent' in status) || status.intent?.kind !== 'upgrade'
    || status.intent.operationId !== operationId) throw new Error('forward operation unavailable for inspection');
  return status;
}

/** Explicit clearance retains the original operation/selection and rotates only its owner/token. */
export async function resumeForwardSchema(repository: string, operationId: string, selection: MaintenanceSelection,
  owner: Owner, clearance: { operatorConfirmed: boolean; note: string }, launcher?: Owner): Promise<MaintenanceHandle> {
  selected(selection);
  const { common } = await repositoryIdentity(repository);
  const store = openForwardMaintenanceStore(common);
  let pendingBackup = false;
  try {
    const claim = store.readMaintenanceClaim(operationId), intent = assertRecordedIntent(common, claim);
    if (!intent.forward || intent.selectionDigest !== selection.selectionDigest
      || intent.release !== selection.release || intent.targetReleaseSha256 !== selection.targetReleaseSha256
      || intent.targetSchema !== selection.targetSchema
      || JSON.stringify(intent.artifactDigests) !== JSON.stringify(Object.fromEntries(Object.entries(selection.artifactDigests).sort(([a],[b]) => a.localeCompare(b))))
      || store.forwardShape() !== intent.forward.currentShape
      || store.forwardIdentity() !== intent.forward.sourceIdentity
      || store.repositoryRelease() !== intent.forward.sourceRelease)
      throw new Error('forward resume original or target selection differs');
    if (intent.forward.backup) verifyForwardBackup(common, claim);
    else {
      if (intent.phase !== 'preparing' || intent.forward.currentShape !== intent.forward.sourceShape)
        throw new Error('unbound forward backup cannot resume after mutation');
      pendingBackup = true;
    }
  } finally { store.close(); }
  const replacementBackupId = pendingBackup ? randomUUID() : undefined;
  const recovered = await reclaimMaintenance(repository, operationId, owner,
    { ...clearance, ...(replacementBackupId ? { replacementBackupId } : {}), ...(launcher ? { launcher } : {}) });
  if (!pendingBackup) return recovered;
  const reopened = openForwardMaintenanceStore(common);
  try { return createAndBindForwardBackup(recovered, reopened.readMaintenanceClaim(operationId).maintenance!); }
  finally { reopened.close(); }
}
