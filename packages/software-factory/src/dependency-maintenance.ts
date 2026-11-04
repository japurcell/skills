import { createHash, randomUUID } from 'node:crypto';
import { lstatSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { directoryIdentity, scanOwnedTree } from './install-candidate.js';
import { captureDependencyAdmissionOwnership, inspectClaimedDependencyOwnership, type InstalledOwnershipFacts } from './installed-state.js';
import { currentOwner } from './native/process.js';
import { validateReleaseBundle } from './release.js';
import { openDependencyMaintenanceStore, type DependencyMaintenanceBinding, type MaintenanceHandle, type MaintenanceIntent, type Owner } from './store.js';
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
    toolchainIdentity: plan.original.toolchain.identity, declarationSha256: plan.declarationSha256, lockSha256: plan.lockSha256 };
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
export async function assertDependencyMaintenance(repository: string, handle: MaintenanceHandle) {
  const location = await repositoryIdentity(repository);
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

/** Bounded read-only operational facts; private token and external provider paths never leave this seam. */
export async function inspectDependencyMaintenance(repository: string, operationId: string) {
  const { common } = await repositoryIdentity(repository), store = openDependencyMaintenanceStore(common);
  let handle: MaintenanceHandle;
  try {
    const claim = store.readMaintenanceClaim(operationId);
    handle = { operationId, repositoryId: claim.resourceKey, claimId: claim.id, token: claim.token, commonDir: common };
  } finally { store.close(); }
  const plan = await assertDependencyMaintenance(repository, handle);
  return { status: 'preparing' as const, operationId, repositoryId: handle.repositoryId, claimId: handle.claimId,
    selectionDigest: plan.selectionDigest, originalSha256: plan.originalSha256, originalCompletionSha256: plan.originalCompletionSha256,
    expectedToolchainSha256: plan.original.toolchain.expectedSha256, observedToolchainSha256: plan.original.toolchain.observedSha256,
    missing: plan.toolchain.missing, changed: plan.toolchain.changed, backupBound: false as const };
}
