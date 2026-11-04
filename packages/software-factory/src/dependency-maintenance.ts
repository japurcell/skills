import { createHash, randomUUID } from 'node:crypto';
import { lstatSync, mkdirSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { directoryIdentity, scanOwnedTree } from './install-candidate.js';
import { captureDependencyAdmissionOwnership, inspectClaimedDependencyOwnership, type InstalledOwnershipFacts } from './installed-state.js';
import { currentOwner, inspectOwner } from './native/process.js';
import { readPublicationRecord, writePublicationRecord } from './install-publication-state.js';
import { maintenanceBackupPath, backupFileDigest, openImmutableMaintenanceBackup, executeMaintenanceBackupRequest, flushBackupDirectory } from './maintenance-backup.js';
import { assertForwardIntegrity, forwardCounts, knownForwardShape } from './schema-forward.js';
import { validateReleaseBundle } from './release.js';
import { openDependencyMaintenanceStore, type Claim, type DependencyMaintenanceBinding, type DependencyBackupAttemptBinding, type VerifiedMaintenanceBackup, type MaintenanceHandle, type MaintenanceIntent, type Owner } from './store.js';
import { repositoryIdentity } from './workspace.js';

export interface DependencySelectionSource { mode: 'repair'; bundleRoot: string; manifestSha256: string }
function hash(bytes: string | Buffer): string { return createHash('sha256').update(bytes).digest('hex'); }
function sourceSelection(value: DependencySelectionSource): DependencySelectionSource {
  if (!value || typeof value !== 'object' || Object.keys(value).sort().join(',') !== 'bundleRoot,manifestSha256,mode'
    || value.mode !== 'repair' || typeof value.bundleRoot !== 'string' || Buffer.byteLength(value.bundleRoot) > 4096
    || typeof value.manifestSha256 !== 'string' || !/^[a-f0-9]{64}$/.test(value.manifestSha256))
    throw new Error('exact fixed dependency repair selection required');
  return { mode: 'repair', bundleRoot: value.bundleRoot, manifestSha256: value.manifestSha256 };
}

function originalFacts(root: string, state: InstalledOwnershipFacts) {
  const factory = join(state.common, 'factory'), selected = state.layout.toolchainInspection;
  if (!selected) throw new Error('dependency selected ownership unavailable');
  const file = lstatSync(join(factory, 'history.sqlite'));
  if (!file.isFile() || file.isSymbolicLink() || file.nlink !== 1 || (file.mode & 0o777) !== 0o600)
    throw new Error('dependency source database identity unavailable');
  const installPath = join(factory, 'install'), installIdentity = directoryIdentity(installPath);
  const install = scanOwnedTree(installPath, 'candidate');
  return { version: 1 as const, root, common: state.common, repositoryId: state.receipt.repositoryId,
    factoryIdentity: directoryIdentity(factory), sourceIdentity: `${file.dev}:${file.ino}`, active: state.active,
    receiptSha256: state.receiptSha256,
    install: { identity: installIdentity, digest: install.digest, entries: install.entries, bytes: install.regularBytes },
    toolchain: { identity: selected.identity, expectedSha256: hash(JSON.stringify(selected.expected.rows)),
      observedSha256: selected.observed.digest, entries: selected.observed.entries, bytes: selected.observed.regularBytes,
      missing: selected.missing, changed: selected.changed } };
}

function selectionPlan(root: string, source: DependencySelectionSource, state: InstalledOwnershipFacts) {
  const manifest = validateReleaseBundle(source.bundleRoot, source.manifestSha256), original = originalFacts(root, state);
  const selected = state.layout.toolchainInspection!;
  const declarationSha256 = hash(readFileSync(join(source.bundleRoot, 'toolchain/package.json')));
  const lockSha256 = hash(readFileSync(join(source.bundleRoot, 'toolchain/package-lock.json')));
  if (manifest.version !== state.release || source.manifestSha256 !== state.receipt.manifestSha256
    || manifest.platform !== `${process.platform}-${process.arch}`
    || selected.expected.rows.find(row => row.path === 'package.json')?.sha256 !== declarationSha256
    || selected.expected.rows.find(row => row.path === 'package-lock.json')?.sha256 !== lockSha256)
    throw new Error('dependency repair must select the exact installed manifest and lock');
  const originalSha256 = hash(JSON.stringify(original)), originalCompletionSha256 = hash(JSON.stringify(state.active.completion));
  const selection = { version: 1 as const, kind: 'dependencies' as const, source, repositoryId: original.repositoryId,
    release: state.release, targetSchema: 7 as const, declarationSha256, lockSha256, originalSha256, originalCompletionSha256 };
  return { ...selection, selectionDigest: hash(JSON.stringify(selection)), original, toolchain: selected };
}
export type DependencyMaintenanceSelection = ReturnType<typeof selectionPlan>;

/** Describe the exact fixed release selection without admitting or changing repository state. */
export async function inspectDependencyMaintenanceSelection(repository: string, value: DependencySelectionSource): Promise<DependencyMaintenanceSelection> {
  const source = sourceSelection(value), location = await repositoryIdentity(repository);
  const captured = await captureDependencyAdmissionOwnership(location.common, repository);
  return selectionPlan(location.root, source, captured.state);
}

/** Administrative claim only. Backup, candidate, stage and mutation authority are deliberately absent. */
export async function admitDependencyMaintenance(repository: string, value: DependencySelectionSource, expectedSelectionDigest: string,
  owner: Owner = currentOwner()): Promise<MaintenanceHandle> {
  if (!/^[a-f0-9]{64}$/.test(expectedSelectionDigest)) throw new Error('exact dependency selection digest required');
  const source = sourceSelection(value), location = await repositoryIdentity(repository);
  const captured = await captureDependencyAdmissionOwnership(location.common, repository);
  const plan = selectionPlan(location.root, source, captured.state);
  if (plan.selectionDigest !== expectedSelectionDigest) throw new Error('dependency selection changed before admission');
  const operationId = randomUUID();
  const dependencies: DependencyMaintenanceBinding = { version: 1, bundleRoot: source.bundleRoot,
    originalSha256: plan.originalSha256, originalCompletionSha256: plan.originalCompletionSha256,
    expectedToolchainSha256: plan.original.toolchain.expectedSha256, observedToolchainSha256: plan.original.toolchain.observedSha256,
    sourceIdentity: plan.original.sourceIdentity, factoryIdentity: plan.original.factoryIdentity,
    toolchainIdentity: plan.original.toolchain.identity, declarationSha256: plan.declarationSha256, lockSha256: plan.lockSha256,
    backupAttempt: null, backup: null };
  const intent: MaintenanceIntent = { operationId, repositoryId: plan.repositoryId, kind: 'dependencies', release: plan.release,
    targetReleaseSha256: source.manifestSha256, selectionDigest: plan.selectionDigest, artifactDigests: { bundle: source.manifestSha256 },
    targetSchema: 7, stagePath: join(location.common, 'factory/controller-staging', operationId), stageDigest: null, stageIdentity: null,
    phase: 'preparing', ownedReceiptId: null, backupId: null, ticketNonceHash: null, ticketConsumed: false, candidate: null, dependencies };
  const store = openDependencyMaintenanceStore(location.common);
  try {
    const claim = await store.beginDependencyMaintenance(intent, owner, () => {
      const checked = selectionPlan(location.root, source, captured.revalidate());
      if (checked.selectionDigest !== plan.selectionDigest || checked.originalSha256 !== plan.originalSha256)
        throw new Error('dependency ownership changed during admission');
    });
    return { operationId, repositoryId: plan.repositoryId, claimId: claim.id, token: claim.token, commonDir: location.common };
  } finally { store.close(); }
}

/** Recheck the exact handle and its original expected/observed facts. No new selection is adopted. */
function assertOriginalSelection(location: { root: string; common: string }, handle: MaintenanceHandle) {
  if (location.common !== handle.commonDir) throw new Error('dependency repository identity changed');
  const store = openDependencyMaintenanceStore(location.common);
  try {
    const before = store.readDependencyMaintenance(handle), selected = before.claim.maintenance!;
    const state = inspectClaimedDependencyOwnership(handle), binding = selected.dependencies!;
    const source = sourceSelection({ mode: 'repair', bundleRoot: binding.bundleRoot, manifestSha256: selected.targetReleaseSha256! });
    const plan = selectionPlan(location.root, source, state);
    if (plan.selectionDigest !== selected.selectionDigest || plan.originalSha256 !== binding.originalSha256
      || plan.originalCompletionSha256 !== binding.originalCompletionSha256
      || plan.original.toolchain.expectedSha256 !== binding.expectedToolchainSha256
      || plan.original.toolchain.observedSha256 !== binding.observedToolchainSha256
      || plan.original.factoryIdentity !== binding.factoryIdentity || plan.original.toolchain.identity !== binding.toolchainIdentity
      || plan.declarationSha256 !== binding.declarationSha256 || plan.lockSha256 !== binding.lockSha256
      || JSON.stringify(store.readDependencyMaintenance(handle)) !== JSON.stringify(before))
      throw new Error('dependency claimed original or selection changed');
    return plan;
  } finally { store.close(); }
}

export async function assertDependencyMaintenance(repository: string, handle: MaintenanceHandle) {
  const location = await repositoryIdentity(repository), plan = assertOriginalSelection(location, handle);
  const store = openDependencyMaintenanceStore(location.common);
  try {
    const { claim } = store.readDependencyMaintenance(handle);
    if (claim.maintenance!.dependencies!.backupAttempt) readDependencyBackupAttempt(handle, claim);
    if (claim.maintenance!.dependencies!.backup) verifyDependencyBackup(handle, claim, claim.maintenance!.dependencies!.backup!);
    return plan;
  } finally { store.close(); }
}

function requireBackupOwner(claim: Claim): void {
  const owner = currentOwner();
  if (claim.owner.host !== owner.host || claim.owner.pid !== owner.pid || claim.owner.start !== owner.start
    || inspectOwner(owner).state !== 'known_live') throw new Error('dependency backup requires the exact live claim owner');
}
function attemptRecord(handle: MaintenanceHandle, claim: Claim, directories: { rootIdentity: string; operationIdentity: string; directoryIdentity: string }) {
  const selected = claim.maintenance!, dependencies = selected.dependencies!;
  const target = maintenanceBackupPath(handle.commonDir, handle.operationId, selected.backupId!);
  const source = join(handle.commonDir, 'factory/history.sqlite');
  const allocated = structuredClone(claim);
  allocated.maintenance!.dependencies!.backupAttempt = null; allocated.maintenance!.dependencies!.backup = null;
  return { version: 1, kind: 'dependencies', operationId: handle.operationId, repositoryId: handle.repositoryId,
    claimId: handle.claimId, backupId: selected.backupId, source, target, sourceSchema: 7, sourceRelease: selected.release,
    sourceIdentity: dependencies.sourceIdentity, factoryIdentity: dependencies.factoryIdentity,
    selectionDigest: selected.selectionDigest, originalSha256: dependencies.originalSha256,
    originalCompletionSha256: dependencies.originalCompletionSha256,
    rootIdentity: directories.rootIdentity, operationIdentity: directories.operationIdentity, directoryIdentity: directories.directoryIdentity,
    requestSha256: hash(`${JSON.stringify({ source, target })}\n`), claimSha256: hash(JSON.stringify(allocated)) };
}
function readDependencyBackupAttempt(handle: MaintenanceHandle, claim: Claim) {
  const selected = claim.maintenance!, bound = selected.dependencies!.backupAttempt;
  if (!selected.backupId || !bound) throw new Error('dependency backup attempt is unbound; evidence retained');
  const target = maintenanceBackupPath(handle.commonDir, handle.operationId, selected.backupId), directory = dirname(target);
  if (directoryIdentity(dirname(dirname(directory))) !== bound.rootIdentity
    || directoryIdentity(dirname(directory)) !== bound.operationIdentity || directoryIdentity(directory) !== bound.directoryIdentity
    || directoryIdentity(join(handle.commonDir, 'factory')) !== selected.dependencies!.factoryIdentity)
    throw new Error('dependency backup directory identity changed');
  const path = join(directory, 'backup-attempt.json'), bytes = readPublicationRecord(path), stat = lstatSync(path);
  const expected = attemptRecord(handle, claim, bound);
  if (`${stat.dev}:${stat.ino}` !== bound.identity || hash(bytes) !== bound.sha256
    || !bytes.equals(Buffer.from(`${JSON.stringify(expected)}\n`)) || bound.requestSha256 !== expected.requestSha256)
    throw new Error('dependency backup immutable attempt changed');
  const request = readPublicationRecord(join(directory, 'backup-request.json'));
  if (hash(request) !== bound.requestSha256 || !request.equals(Buffer.from(`${JSON.stringify({ source: expected.source, target })}\n`)))
    throw new Error('dependency backup request changed');
  const allowed = ['backup-attempt.json', 'backup-request.json', 'history.sqlite', 'backup-receipt.json'];
  if (readdirSync(dirname(directory)).join(',') !== selected.backupId || readdirSync(directory).some(name => !allowed.includes(name)))
    throw new Error('dependency backup unowned inventory');
  for (const name of readdirSync(directory)) {
    const info = lstatSync(join(directory, name));
    if (!info.isFile() || info.isSymbolicLink() || info.nlink !== 1 || (info.mode & 0o777) !== 0o600)
      throw new Error('dependency backup linked or nonregular artifact');
  }
  return { expected, target, directory };
}
function verifyCopiedDependencyBackup(handle: MaintenanceHandle, claim: Claim, target: string) {
  const copied = openImmutableMaintenanceBackup(target);
  try {
    assertForwardIntegrity(copied);
    const selected = claim.maintenance!, repository = copied.prepare('SELECT id,release,state FROM repository LIMIT 2').all();
    const claims = copied.prepare('SELECT id,token,data FROM owner_claims LIMIT 2').all(), expectedClaim = structuredClone(claim);
    expectedClaim.maintenance!.dependencies!.backup = null;
    if (knownForwardShape(copied) !== 'v7' || repository.length !== 1 || repository[0]?.['id'] !== handle.repositoryId
      || repository[0]['release'] !== selected.release || repository[0]['state'] !== 'ready' || claims.length !== 1
      || claims[0]?.['id'] !== handle.claimId || claims[0]['token'] !== handle.token
      || claims[0]['data'] !== JSON.stringify(expectedClaim)) throw new Error('dependency backup repository or exact claim differs');
    const last = copied.prepare("SELECT kind,data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed','dependencies.completed','repair.completed','uninstall.completed','cleanup.completed') ORDER BY cursor DESC LIMIT 1").get();
    if (!last || !['install.completed', 'upgrade.completed'].includes(String(last['kind']))
      || hash(JSON.stringify(JSON.parse(String(last['data'])))) !== selected.dependencies!.originalCompletionSha256)
      throw new Error('dependency backup prior completion differs');
    return forwardCounts(copied);
  } finally { copied.close(); }
}
function verifyDependencyBackup(handle: MaintenanceHandle, claim: Claim, bound: VerifiedMaintenanceBackup) {
  const attempt = readDependencyBackupAttempt(handle, claim), selected = claim.maintenance!;
  if (bound.id !== selected.backupId || readdirSync(attempt.directory).sort().join(',') !== 'backup-attempt.json,backup-receipt.json,backup-request.json,history.sqlite')
    throw new Error('dependency backup exact inventory differs');
  const actual = backupFileDigest(attempt.target), bytes = readPublicationRecord(join(attempt.directory, 'backup-receipt.json'));
  const receipt = JSON.parse(bytes.toString('utf8')) as Record<string, unknown>;
  const expected = { version: 1, kind: 'dependencies', receiptId: bound.receiptId, operationId: handle.operationId,
    repositoryId: handle.repositoryId, claimId: handle.claimId, backupId: bound.id, sourceSchema: 7,
    sourceRelease: selected.release, sourceIdentity: selected.dependencies!.sourceIdentity,
    selectionDigest: selected.selectionDigest, originalSha256: selected.dependencies!.originalSha256,
    originalCompletionSha256: selected.dependencies!.originalCompletionSha256,
    attemptSha256: selected.dependencies!.backupAttempt!.sha256, requestSha256: selected.dependencies!.backupAttempt!.requestSha256,
    ...actual, countDigest: bound.countDigest };
  if (actual.identity !== bound.identity || actual.sha256 !== bound.sha256 || actual.bytes !== bound.bytes
    || hash(bytes) !== bound.receiptSha256 || JSON.stringify(receipt) !== JSON.stringify(expected))
    throw new Error('dependency backup receipt or bytes changed');
  const counts = verifyCopiedDependencyBackup(handle, claim, attempt.target);
  if (counts.digest !== bound.countDigest) throw new Error('dependency backup count digest differs');
  const store = openDependencyMaintenanceStore(handle.commonDir);
  try {
    const live = store.forwardCounts(), boundAlready = Boolean(selected.dependencies!.backup);
    for (const [table, count] of Object.entries(counts.rows)) {
      const expectedCount = BigInt(count) + (table === 'observation_events' && boundAlready ? 1n : 0n);
      if (BigInt(live.rows[table]!) !== expectedCount) throw new Error('dependency backup source counts changed');
    }
  } finally { store.close(); }
}

/** One attempt only. Every failure retains its allocation and private artifacts for explicit later recovery. */
export async function prepareDependencyBackup(repository: string, handle: MaintenanceHandle) {
  const location = await repositoryIdentity(repository);
  await assertDependencyMaintenance(repository, handle);
  const store = openDependencyMaintenanceStore(handle.commonDir);
  try {
    const first = store.readDependencyMaintenance(handle).claim; requireBackupOwner(first);
    const backupId = randomUUID();
    await store.reserveDependencyBackupAttempt(handle, backupId, () => { assertOriginalSelection(location, handle); });
    const target = maintenanceBackupPath(handle.commonDir, handle.operationId, backupId), directory = dirname(target);
    const backups = dirname(dirname(directory)), operation = dirname(directory);
    try { mkdirSync(backups, { mode: 0o700 }); flushBackupDirectory(dirname(backups)); }
    catch (error) { if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error; }
    directoryIdentity(backups);
    mkdirSync(operation, { mode: 0o700 }); flushBackupDirectory(backups);
    mkdirSync(directory, { mode: 0o700 }); flushBackupDirectory(operation);
    let current = store.readDependencyMaintenance(handle).claim; requireBackupOwner(current);
    const directories = { rootIdentity: directoryIdentity(backups), operationIdentity: directoryIdentity(operation), directoryIdentity: directoryIdentity(directory) };
    const record = attemptRecord(handle, current, directories), path = join(directory, 'backup-attempt.json');
    writePublicationRecord(join(directory, 'backup-request.json'), { source: record.source, target });
    const sha256 = writePublicationRecord(path, record), stat = lstatSync(path);
    const attempt: DependencyBackupAttemptBinding = { ...directories, identity: `${stat.dev}:${stat.ino}`, sha256,
      requestSha256: record.requestSha256 };
    await store.bindDependencyBackupAttempt(handle, attempt, () => { assertOriginalSelection(location, handle); });
    current = store.readDependencyMaintenance(handle).claim; requireBackupOwner(current);
    readDependencyBackupAttempt(handle, current);
    if (readdirSync(directory).sort().join(',') !== 'backup-attempt.json,backup-request.json') throw new Error('dependency backup target is not absent');
    const before = store.forwardCounts();
    assertOriginalSelection(location, handle); requireBackupOwner(current);
    await executeMaintenanceBackupRequest(join(directory, 'backup-request.json'));
    current = store.readDependencyMaintenance(handle).claim; requireBackupOwner(current); assertOriginalSelection(location, handle);
    readDependencyBackupAttempt(handle, current);
    if (readdirSync(directory).sort().join(',') !== 'backup-attempt.json,backup-request.json,history.sqlite') throw new Error('dependency backup helper inventory differs');
    const details = backupFileDigest(target), counts = verifyCopiedDependencyBackup(handle, current, target);
    if (counts.digest !== before.digest || store.forwardCounts().digest !== before.digest) throw new Error('dependency backup source counts changed');
    flushBackupDirectory(directory);
    const receiptId = randomUUID(), receipt = { version: 1, kind: 'dependencies', receiptId, operationId: handle.operationId,
      repositoryId: handle.repositoryId, claimId: handle.claimId, backupId, sourceSchema: 7, sourceRelease: current.maintenance!.release,
      sourceIdentity: current.maintenance!.dependencies!.sourceIdentity, selectionDigest: current.maintenance!.selectionDigest,
      originalSha256: current.maintenance!.dependencies!.originalSha256,
      originalCompletionSha256: current.maintenance!.dependencies!.originalCompletionSha256,
      attemptSha256: attempt.sha256, requestSha256: attempt.requestSha256, ...details, countDigest: counts.digest };
    const receiptSha256 = writePublicationRecord(join(directory, 'backup-receipt.json'), receipt);
    const bound = { id: backupId, ...details, countDigest: counts.digest, receiptId, receiptSha256 };
    await store.bindDependencyBackup(handle, bound, () => {
      assertOriginalSelection(location, handle);
      verifyDependencyBackup(handle, store.readDependencyMaintenance(handle).claim, bound);
    });
    await assertDependencyMaintenance(repository, handle);
    return { ...handle, backupId, backupBound: true as const };
  } finally { store.close(); }
}

/** Bounded read-only operational facts; private token and external provider paths never leave this seam. */
export async function inspectDependencyMaintenance(repository: string, operationId: string) {
  const { common } = await repositoryIdentity(repository), store = openDependencyMaintenanceStore(common);
  let handle: MaintenanceHandle, selected: MaintenanceIntent;
  try {
    const claim = store.readMaintenanceClaim(operationId);
    selected = claim.maintenance!;
    handle = { operationId, repositoryId: claim.resourceKey, claimId: claim.id, token: claim.token, commonDir: common };
  } finally { store.close(); }
  const plan = await assertDependencyMaintenance(repository, handle);
  return { status: 'preparing' as const, operationId, repositoryId: handle.repositoryId, claimId: handle.claimId,
    selectionDigest: plan.selectionDigest, originalSha256: plan.originalSha256, originalCompletionSha256: plan.originalCompletionSha256,
    expectedToolchainSha256: plan.original.toolchain.expectedSha256, observedToolchainSha256: plan.original.toolchain.observedSha256,
    missing: plan.toolchain.missing, changed: plan.toolchain.changed, backupBound: Boolean(selected.dependencies?.backup),
    backupAttempted: selected.backupId !== null, backupAttemptRecorded: Boolean(selected.dependencies?.backupAttempt) };
}
