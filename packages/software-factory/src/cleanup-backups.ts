import { createHash } from 'node:crypto';
import { lstatSync, realpathSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { readPublicationRecord } from './install-publication-state.js';
import { readInstalledReceipt } from './install-publication.js';
import { backupFileDigest, maintenanceBackupPath, openImmutableMaintenanceBackup } from './maintenance-backup.js';
import { assertForwardIntegrity, assertForwardRuntime, forwardCounts, knownForwardShape, type ForwardShape } from './schema-forward.js';
import { openCleanupReadStore, type CleanupActivityEvidence, type CleanupOperationEvidence, type CleanupOperationEvent, type CleanupRecoveryClaim } from './store.js';
import { readUpgradeInstalledReceipt } from './upgrade-installed.js';
import { upgradeDirectory } from './upgrade-publication-state.js';
import { repositoryIdentity } from './workspace.js';
import { cleanupObject } from './cleanup-read.js';

export interface CleanupBackupKey { operationId: string; backupId: string }
export interface CleanupObservedParent { path: string; identity: string; provenance: 'currently-observed' }
export interface OwnedBackup {
  status: 'owned'; selection: CleanupBackupKey; repository: { root: string; common: string; id: string; factoryIdentity: string };
  source: { shape: ForwardShape; release: string; identity: string };
  file: { path: string; identity: string; sha256: string; bytes: number; countDigest: string };
  parents: CleanupObservedParent[];
  authority: { completionCursor: string; completionSha256: string; receiptId: string; receiptSha256: string;
    backupReceiptSha256: string; originalSha256: string; intentSha256: string; claimId: string };
}
export interface CleanupRecoveryDependency {
  reason: 'bootstrap-marker' | 'upgrade-marker' | 'claim' | 'occupied-attempt' | 'repository-not-ready'
    | 'operation-unassessed' | 'activity-unassessed' | 'authority-changed' | 'repository-unavailable';
  claim?: CleanupRecoveryClaim;
  activity?: CleanupActivityEvidence;
}
export type CleanupRecoveryDependencies = { status: 'clear'; authority: 'proven'; repositoryId: string; newestCompletionCursor: string; dependencies: [] }
  | { status: 'blocked'; authority: 'unassessed'; dependencies: CleanupRecoveryDependency[] };
export interface ProtectedBackup {
  status: 'protected'; selection: CleanupBackupKey; ownership: 'authenticated' | 'unassessed';
  backup: OwnedBackup | null; dependencies: CleanupRecoveryDependency[];
}
export interface BackupRefusal {
  status: 'refused'; selection: CleanupBackupKey | null;
  reason: 'invalid-selection' | 'unsupported-platform' | 'authority-missing' | 'authority-ambiguous'
    | 'authority-invalid' | 'unsupported-kind' | 'backup-invalid' | 'repository-unavailable';
}
export type CleanupBackupResolution = OwnedBackup | ProtectedBackup | BackupRefusal;

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SHA = /^[a-f0-9]{64}$/;
const SHAPES = ['v3','v4-base','v4-plus','v5','v6','v7'];
const hash = (bytes: Buffer | string) => createHash('sha256').update(bytes).digest('hex');
const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
function requireFact(value: unknown): asserts value { if (!value) throw new Error('cleanup backup authority refused'); }
function exact(value: unknown, fields: string[]): asserts value is Record<string, unknown> {
  requireFact(cleanupObject(value) && Object.keys(value).sort().join(',') === [...fields].sort().join(','));
}
function present(path: string) {
  try { lstatSync(path); return true; } catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return false; throw error; }
}
function noBackupSidecars(path: string) {
  for (const suffix of ['-wal','-shm','-journal']) requireFact(!present(`${path}${suffix}`));
}
function directory(path: string, privateMode = true): CleanupObservedParent {
  const info = lstatSync(path, { bigint: true });
  requireFact(info.isDirectory() && !info.isSymbolicLink() && info.ino !== 0n && realpathSync(path) === path
    && info.uid === BigInt(process.getuid!()) && (!privateMode || (info.mode & 0o777n) === 0o700n));
  return { path, identity: `${info.dev}:${info.ino}`, provenance: 'currently-observed' };
}
function record(path: string) {
  const before = lstatSync(path, { bigint: true });
  requireFact(before.uid === BigInt(process.getuid!()));
  const bytes = readPublicationRecord(path), after = lstatSync(path, { bigint: true });
  requireFact(before.dev === after.dev && before.ino === after.ino && after.uid === before.uid
    && Buffer.from(bytes.toString('utf8')).equals(bytes));
  const value: unknown = JSON.parse(bytes.toString('utf8'));
  requireFact(cleanupObject(value));
  return { value, sha256: hash(bytes), identity: `${before.dev}:${before.ino}` };
}
function readEvidence(common: string, operationId: string) {
  const store = openCleanupReadStore(common);
  try { return store.readCleanupOperationEvidence({ operationId }); } finally { store.close(); }
}
function known(event: CleanupOperationEvent): asserts event is Extract<CleanupOperationEvent, { status: 'known' }> {
  requireFact(event.status === 'known');
}

/** A ready row and no claim do not establish clearance: authenticate the newest terminal and operation suffix too. */
function recoveryAt(common: string, evidence: CleanupOperationEvidence): CleanupRecoveryDependencies {
  const dependencies: CleanupRecoveryDependency[] = [], factory = join(common, 'factory');
  if (present(join(factory, 'bootstrap-incomplete'))) dependencies.push({ reason: 'bootstrap-marker' });
  if (present(join(factory, 'upgrade-incomplete'))) dependencies.push({ reason: 'upgrade-marker' });
  if (evidence.snapshot.recovery.repositoryState !== 'ready') dependencies.push({ reason: 'repository-not-ready' });
  for (const claim of evidence.claims) dependencies.push({ reason: 'claim', claim });
  if (evidence.snapshot.recovery.claimCount !== String(evidence.claims.length) || evidence.snapshot.recovery.opaque)
    dependencies.push({ reason: 'operation-unassessed' });
  if (evidence.occupiedAttempts) dependencies.push({ reason: 'occupied-attempt' });
  if (evidence.activity.status === 'blocked') dependencies.push({ reason: 'activity-unassessed', activity: evidence.activity });
  try {
    const terminal = evidence.newestCompletion, newest = evidence.newestOperation;
    known(terminal); known(newest);
    requireFact(terminal.data.repositoryId === evidence.snapshot.repositoryId && typeof terminal.data.operationId === 'string');
    const unique = readEvidence(common, terminal.data.operationId).completion;
    requireFact(same(unique, terminal));
    if (terminal.kind === 'upgrade.completed') {
      record(join(upgradeDirectory(common, terminal.data.operationId), 'new-receipt.json'));
      const owned = readUpgradeInstalledReceipt(common, terminal.data.operationId), receipt = owned.receipt;
      requireFact(owned.sha256 === terminal.data.receiptSha256 && owned.identity === terminal.data.receiptIdentity
        && receipt.repositoryId === evidence.snapshot.repositoryId && receipt.release === evidence.snapshot.release
        && receipt.claimId === terminal.data.claimId && receipt.selectionDigest === terminal.data.selectionDigest
        && receipt.manifestSha256 === terminal.data.manifestSha256 && receipt.receiptId === terminal.data.receiptId
        && receipt.originalSha256 === terminal.data.originalInstalledSha256);
    } else {
      requireFact(terminal.kind === 'install.completed');
      record(join(factory, 'installed-receipt.json'));
      const owned = readInstalledReceipt(common), receipt = owned.receipt;
      requireFact(owned.sha256 === terminal.data.receiptSha256 && receipt.operationId === terminal.data.operationId
        && receipt.repositoryId === evidence.snapshot.repositoryId && receipt.release === evidence.snapshot.release
        && receipt.claimId === terminal.data.claimId && receipt.selectionDigest === terminal.data.selectionDigest
        && receipt.manifestSha256 === terminal.data.manifestSha256 && receipt.receiptId === terminal.data.receiptId);
    }
    requireFact(same(newest, terminal) || newest.kind === 'maintenance.completed_recovery_inspected'
      && BigInt(newest.cursor) > BigInt(terminal.cursor) && newest.data.operationId === terminal.data.operationId
      && newest.data.receiptId === terminal.data.receiptId && newest.data.receiptSha256 === terminal.data.receiptSha256);
  } catch { dependencies.push({ reason: 'operation-unassessed' }); }
  return dependencies.length ? { status: 'blocked', authority: 'unassessed', dependencies }
    : { status: 'clear', authority: 'proven', repositoryId: evidence.snapshot.repositoryId,
        newestCompletionCursor: evidence.newestCompletion.status === 'known' ? evidence.newestCompletion.cursor : '0', dependencies: [] };
}

/** Advisory only. No maintenance capability is acquired or released by this reader. */
export async function inspectCleanupRecoveryDependencies(repository: string): Promise<CleanupRecoveryDependencies> {
  if (process.platform !== 'darwin' && process.platform !== 'linux')
    return { status: 'blocked', authority: 'unassessed', dependencies: [{ reason: 'repository-unavailable' }] };
  try {
    assertForwardRuntime();
    const { common } = await repositoryIdentity(repository), sentinel = '00000000-0000-4000-8000-000000000000';
    directory(common, false); directory(join(common, 'factory'));
    const evidence = readEvidence(common, sentinel), result = recoveryAt(common, evidence);
    if (!same(evidence, readEvidence(common, sentinel))) return { status: 'blocked', authority: 'unassessed', dependencies: [{ reason: 'authority-changed' }] };
    return result;
  } catch { return { status: 'blocked', authority: 'unassessed', dependencies: [{ reason: 'repository-unavailable' }] }; }
}

function authenticateBackup(root: string, common: string, selection: CleanupBackupKey, evidence: CleanupOperationEvidence): OwnedBackup {
  const completion = evidence.completion; known(completion);
  requireFact(completion.kind === 'upgrade.completed' && completion.data.operationId === selection.operationId
    && completion.data.repositoryId === evidence.snapshot.repositoryId);
  const factory = join(common, 'factory'), upgrade = upgradeDirectory(common, selection.operationId);
  const path = maintenanceBackupPath(common, selection.operationId, selection.backupId), backup = dirname(path);
  const parents = [directory(root, false), directory(common, false), directory(factory), directory(upgrade),
    directory(join(factory, 'maintenance-backups')), directory(dirname(backup)), directory(backup)];
  record(join(upgrade, 'new-receipt.json'));
  const installed = readUpgradeInstalledReceipt(common, selection.operationId), receipt = installed.receipt;
  requireFact(installed.sha256 === completion.data.receiptSha256 && installed.identity === completion.data.receiptIdentity
    && receipt.receiptId === completion.data.receiptId && receipt.claimId === completion.data.claimId
    && receipt.repositoryId === completion.data.repositoryId && receipt.selectionDigest === completion.data.selectionDigest
    && receipt.manifestSha256 === completion.data.manifestSha256 && receipt.originalSha256 === completion.data.originalInstalledSha256);
  const originalRecord = record(join(upgrade, 'original.json')), original = originalRecord.value;
  exact(original, ['version','launcher','root','common','repositoryId','release','factoryIdentity','completion','receipt','receiptSha256',
    'install','toolchain','providers','toolchainLockSha256']);
  requireFact(hash(JSON.stringify(original)) === receipt.originalSha256 && original.version === 1
    && original.root === root && original.common === common && original.repositoryId === evidence.snapshot.repositoryId
    && original.factoryIdentity === parents[2]!.identity && typeof original.release === 'string'
    && cleanupObject(original.completion) && original.completion.repositoryId === original.repositoryId
    && hash(JSON.stringify(original.completion)) === completion.data.originalCompletionSha256
    && cleanupObject(original.receipt) && original.receipt.repositoryId === original.repositoryId
    && original.receipt.operationId === original.completion.operationId && original.receipt.release === original.release
    && hash(`${JSON.stringify(original.receipt)}\n`) === original.receiptSha256 && same(original.launcher, receipt.launcher));
  const intentRecord = record(join(upgrade, 'intent.json')), intent = intentRecord.value;
  exact(intent, ['version','operationId','repositoryId','claimId','selectionDigest','originalSha256','backupReceiptSha256','candidate',
    'stageDigest','stageIdentity','operationIdentity','oldDirectoryIdentity','markerTemplateIdentity','markerTemplateSha256','atomicBinding',
    'oldInstall','oldToolchain','newInstall','newToolchain']);
  requireFact(intentRecord.sha256 === receipt.intentSha256 && intent.version === 1 && intent.operationId === selection.operationId
    && intent.repositoryId === receipt.repositoryId && intent.claimId === receipt.claimId && intent.selectionDigest === receipt.selectionDigest
    && intent.originalSha256 === receipt.originalSha256 && intent.backupReceiptSha256 === receipt.backupReceiptSha256
    && intent.stageDigest === receipt.stageDigest && intent.stageIdentity === receipt.stageIdentity
    && intent.operationIdentity === parents[3]!.identity && same(intent.candidate, receipt.candidate)
    && same(intent.oldInstall, original.install) && same(intent.oldToolchain, original.toolchain)
    && cleanupObject(intent.atomicBinding) && same(intent.atomicBinding.launcher, original.launcher));
  const boundRecord = record(join(backup, 'backup-receipt.json')), bound = boundRecord.value;
  exact(bound, ['version','receiptId','operationId','backupId','repositoryId','sourceShape','sourceRelease','sourceIdentity',
    'selectionDigest','requestSha256','sha256','identity','bytes','countDigest']);
  requireFact(boundRecord.sha256 === receipt.backupReceiptSha256 && bound.version === 1
    && bound.operationId === selection.operationId && bound.backupId === selection.backupId
    && bound.repositoryId === receipt.repositoryId && bound.selectionDigest === receipt.selectionDigest
    && typeof bound.receiptId === 'string' && UUID.test(bound.receiptId)
    && typeof bound.sourceShape === 'string' && SHAPES.includes(bound.sourceShape)
    && bound.sourceRelease === original.release && bound.sourceIdentity === evidence.snapshot.databaseIdentity
    && typeof bound.identity === 'string' && /^\d+:\d+$/.test(bound.identity)
    && typeof bound.sha256 === 'string' && SHA.test(bound.sha256) && typeof bound.countDigest === 'string' && SHA.test(bound.countDigest)
    && Number.isSafeInteger(bound.bytes) && Number(bound.bytes) > 0 && Number(bound.bytes) <= 512 * 1024 * 1024);
  const request = record(join(backup, 'backup-request.json'));
  exact(request.value, ['source','target']);
  requireFact(request.sha256 === bound.requestSha256 && request.value.source === join(factory, 'history.sqlite') && request.value.target === path);
  noBackupSidecars(path);
  const file = backupFileDigest(path), info = lstatSync(path, { bigint: true });
  requireFact(info.uid === BigInt(process.getuid!()) && same(file, { sha256: bound.sha256, identity: bound.identity, bytes: bound.bytes }));
  const copied = openImmutableMaintenanceBackup(path);
  try {
    // The shared exact-shape decoder must not fetch an unbounded malicious sqlite_schema body first.
    requireFact(!copied.prepare(`SELECT 1 FROM sqlite_schema WHERE typeof(type)<>'text' OR octet_length(type)>256
      OR typeof(name)<>'text' OR octet_length(name)>256 OR typeof(tbl_name)<>'text' OR octet_length(tbl_name)>256
      OR (sql IS NOT NULL AND (typeof(sql)<>'text' OR octet_length(sql)>8192)) LIMIT 1`).get());
    requireFact(knownForwardShape(copied) === bound.sourceShape);
    assertForwardIntegrity(copied);
    requireFact(forwardCounts(copied).digest === bound.countDigest);
    const repositories = copied.prepare(`SELECT CASE WHEN typeof(id)='text' AND octet_length(id)<=256 THEN id END AS id,
      CASE WHEN typeof(release)='text' AND octet_length(release)<=256 THEN release END AS release,
      CASE WHEN typeof(state)='text' AND octet_length(state)<=256 THEN state END AS state FROM repository LIMIT 2`).all();
    requireFact(repositories.length === 1 && repositories[0]!['id'] === receipt.repositoryId
      && repositories[0]!['release'] === bound.sourceRelease && repositories[0]!['state'] === 'ready');
    const claims = copied.prepare(`SELECT CASE WHEN typeof(data)='text' AND octet_length(data)<=8192 THEN data END AS data,
      CASE WHEN json_valid(data) THEN id=json_extract(data,'$.id') AND token=json_extract(data,'$.token')
        AND kind=json_extract(data,'$.kind') AND resource_key=json_extract(data,'$.resourceKey') AND invocation_id IS NULL ELSE 0 END AS consistent
      FROM owner_claims LIMIT 2`).all();
    requireFact(claims.length === 1 && claims[0]!['consistent'] === 1 && typeof claims[0]!['data'] === 'string');
    const claim: unknown = JSON.parse(claims[0]!['data'] as string);
    requireFact(cleanupObject(claim) && claim.id === receipt.claimId && claim.kind === 'maintenance' && claim.invocationId === null
      && claim.resourceKey === receipt.repositoryId && cleanupObject(claim.maintenance));
    const selected = claim.maintenance;
    requireFact(selected.kind === 'upgrade' && selected.phase === 'preparing' && selected.operationId === selection.operationId
      && selected.backupId === selection.backupId && selected.repositoryId === receipt.repositoryId
      && selected.selectionDigest === receipt.selectionDigest && selected.targetReleaseSha256 === receipt.manifestSha256
      && selected.release === receipt.release && selected.targetSchema === receipt.targetSchema
      && selected.candidate === null && selected.ticketConsumed === false && selected.ticketNonceHash === null
      && cleanupObject(selected.artifactDigests) && selected.artifactDigests['original-installed'] === receipt.originalSha256
      && selected.artifactDigests['original-completion'] === completion.data.originalCompletionSha256
      && cleanupObject(selected.forward) && selected.forward.sourceShape === bound.sourceShape
      && selected.forward.currentShape === bound.sourceShape && selected.forward.sourceRelease === bound.sourceRelease
      && selected.forward.sourceIdentity === bound.sourceIdentity && selected.forward.backup === null);
  } finally { copied.close(); }
  noBackupSidecars(path);
  requireFact(same(file, backupFileDigest(path)) && parents.every(parent => directory(parent.path, parent.path !== root && parent.path !== common).identity === parent.identity));
  return { status: 'owned', selection, repository: { root, common, id: receipt.repositoryId, factoryIdentity: parents[2]!.identity },
    source: { shape: bound.sourceShape as ForwardShape, release: bound.sourceRelease as string, identity: bound.sourceIdentity as string },
    file: { path, ...file, countDigest: bound.countDigest as string }, parents,
    authority: { completionCursor: completion.cursor, completionSha256: completion.sha256, receiptId: receipt.receiptId,
      receiptSha256: installed.sha256, backupReceiptSha256: receipt.backupReceiptSha256, originalSha256: receipt.originalSha256,
      intentSha256: receipt.intentSha256, claimId: receipt.claimId } };
}

/** One selected tuple, never a path or filesystem discovery request. Historical counts come only from the authenticated copy. */
export async function resolveOwnedCleanupBackup(repository: string, selection: CleanupBackupKey): Promise<CleanupBackupResolution> {
  const key = cleanupObject(selection) && typeof selection.operationId === 'string' && typeof selection.backupId === 'string'
    && UUID.test(selection.operationId) && UUID.test(selection.backupId) && Object.keys(selection).sort().join(',') === 'backupId,operationId'
    ? { operationId: selection.operationId, backupId: selection.backupId } : null;
  const refuse = (reason: BackupRefusal['reason']): BackupRefusal => ({ status: 'refused', selection: key, reason });
  if (!key) return refuse('invalid-selection');
  if (process.platform !== 'darwin' && process.platform !== 'linux') return refuse('unsupported-platform');
  try {
    assertForwardRuntime();
    const { root, common } = await repositoryIdentity(repository), evidence = readEvidence(common, key.operationId);
    const recovery = recoveryAt(common, evidence);
    if (evidence.completion.status === 'missing') {
      return recovery.status === 'blocked' ? { status: 'protected', selection: key, ownership: 'unassessed', backup: null, dependencies: recovery.dependencies }
        : refuse('authority-missing');
    }
    if (evidence.completion.status === 'ambiguous') return refuse('authority-ambiguous');
    if (evidence.completion.status !== 'known') return refuse('authority-invalid');
    if (evidence.completion.kind !== 'upgrade.completed') return refuse('unsupported-kind');
    let backup: OwnedBackup;
    try { backup = authenticateBackup(root, common, key, evidence); } catch { return refuse('backup-invalid'); }
    if (!same(evidence, readEvidence(common, key.operationId)))
      return { status: 'protected', selection: key, ownership: 'unassessed', backup: null, dependencies: [{ reason: 'authority-changed' }] };
    if (recovery.status === 'blocked') return { status: 'protected', selection: key, ownership: 'authenticated', backup, dependencies: recovery.dependencies };
    return backup;
  } catch { return refuse('repository-unavailable'); }
}
