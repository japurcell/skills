import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, readdirSync, realpathSync } from 'node:fs';
import { join } from 'node:path';
import { directoryIdentity, scanOwnedTree } from './install-candidate.js';
import { readInstalledReceipt } from './install-publication.js';
import { inspectInstalledUpgrade, readUpgradeCompletionAuthority } from './upgrade-installed.js';
import { publicationIntentPath, readPublicationAuthority, readPublicationRecord, verifyPublicationLayout } from './install-publication-state.js';
import { upgradeDirectory } from './upgrade-publication-state.js';
import { validateBoundProviderSources, validateRetainedProviderSources } from './installation-bindings.js';
import { validateReleaseBundle } from './release.js';
import { readOwnedReleaseManifest } from './owned-release.js';
import { readActiveInstalledCompletion, readInstalledCompletion, readRepairStoreSnapshot, openDependencyMaintenanceStore, type ActiveInstalledCompletion, type MaintenanceHandle, type Claim } from './store.js';
import { repositoryIdentity } from './workspace.js';

export type InstalledStateInspection = { readonly purpose: 'strict'; readonly retained: boolean }
  | { readonly purpose: 'dependency-repair' };
function fail(): never { throw new Error('installed binding refused'); }
function hash(bytes: Buffer): string { return createHash('sha256').update(bytes).digest('hex'); }

/** One metadata join shared with ordinary ownership. No live-byte validation is implied. */
function readInstallCompletionAuthority(common: string, active: ActiveInstalledCompletion) {
    const factory = join(common, 'factory');
    if (active.kind !== 'install.completed') fail();
    const { receipt, sha256 } = readInstalledReceipt(common);
    const { completion, repositoryId, release } = active;
    if (JSON.stringify(active.completion) !== JSON.stringify(completion) || active.release !== release
      || completion.version !== 1 || completion.operationId !== receipt.operationId
      || completion.repositoryId !== receipt.repositoryId || repositoryId !== receipt.repositoryId
      || completion.claimId !== receipt.claimId || completion.selectionDigest !== receipt.selectionDigest
      || completion.manifestSha256 !== receipt.manifestSha256 || completion.receiptId !== receipt.receiptId
      || completion.receiptSha256 !== sha256 || release !== receipt.release
      || receipt.candidate.path !== join(factory, `install-candidate-${receipt.operationId}`)) fail();
    const synthetic: Claim = { id: receipt.claimId, token: '', kind: 'maintenance', resourceKey: receipt.repositoryId,
      invocationId: null, owner: { host: '', pid: 0, start: null }, maintenance: {
        operationId: receipt.operationId, repositoryId: receipt.repositoryId, kind: 'install', release: receipt.release,
        targetReleaseSha256: receipt.manifestSha256, selectionDigest: receipt.selectionDigest, artifactDigests: {},
        targetSchema: receipt.targetSchema, stagePath: '', stageDigest: receipt.stageDigest, stageIdentity: null,
        phase: 'validating', ownedReceiptId: receipt.receiptId, backupId: null, ticketNonceHash: null,
        ticketConsumed: true, candidate: receipt.candidate,
      } };
    const layout = readPublicationAuthority(common, synthetic);
    if (!layout.intent
      || layout.intent.installIdentity !== receipt.installIdentity
      || layout.intent.toolchainIdentity !== receipt.toolchainIdentity
      || hash(readPublicationRecord(publicationIntentPath(common, receipt.operationId))) !== receipt.publicationIntentSha256) fail();
    return { receipt, sha256, completion, release, claim: synthetic, layout };
}

/** Retained ownership is authenticated independently of damaged selected runtime and Node files. */
export function readRetainedInstalledAuthority(common: string) {
  try {
    const snapshot = readRepairStoreSnapshot(common);
    const active = snapshot.active;
    if (realpathSync(common) !== common) fail();
    const factory = join(common, 'factory'), factoryIdentity = directoryIdentity(factory);
    if (active.kind === 'upgrade.completed') {
      const authority = readUpgradeCompletionAuthority(common, active), { intent, originalCandidate } = authority.layout;
      if (intent.candidate.path !== join(factory, `install-candidate-${active.completion.operationId}`)) fail();
      if (JSON.stringify(readdirSync(intent.candidate.path).sort()) !== JSON.stringify(['candidate-receipt.json'])) fail();
      const old = join(upgradeDirectory(common, intent.operationId), 'old');
      if (JSON.stringify(readdirSync(old).sort()) !== JSON.stringify(['install', 'toolchain'])) fail();
      for (const [name, expected] of [['install', intent.oldInstall], ['toolchain', intent.oldToolchain]] as const) {
        const path = join(old, name), observed = scanOwnedTree(path, 'candidate');
        if (directoryIdentity(path) !== expected.identity || observed.digest !== expected.digest
          || observed.entries !== expected.entries || observed.regularBytes !== expected.bytes) fail();
      }
      validateRetainedProviderSources(originalCandidate.providers);
      return { ...authority, active, snapshot, candidate: originalCandidate, factoryIdentity,
        installIdentity: intent.newInstall.identity, toolchainIdentity: intent.newToolchain.identity };
    }
    const authority = readInstallCompletionAuthority(common, active);
    if (JSON.stringify(readdirSync(authority.receipt.candidate.path).sort()) !== JSON.stringify(['candidate-receipt.json'])) fail();
    validateRetainedProviderSources(authority.layout.receipt.providers);
    return { ...authority, active, snapshot, candidate: authority.layout.receipt, factoryIdentity,
      installIdentity: authority.receipt.installIdentity, toolchainIdentity: authority.receipt.toolchainIdentity };
  } catch { fail(); }
}

/** Single ownership interpretation for startup, upgrade capture and read-only selected repair inspection. */
function inspectOwnershipAtCompletion(common: string, active: ActiveInstalledCompletion, mode: InstalledStateInspection) {
  try {
    if (realpathSync(common) !== common) fail();
    const factory = join(common, 'factory');
    const retained = mode.purpose === 'dependency-repair' || mode.retained;
    const toolchainMode = mode.purpose === 'dependency-repair' ? { purpose: 'dependency-repair' as const } : { purpose: 'strict' as const };
    directoryIdentity(factory);
    if (active.kind === 'upgrade.completed') {
      const upgraded = inspectInstalledUpgrade(common, active, retained, toolchainMode);
      return { ...upgraded, active };
    }
    const { receipt, sha256, completion, release, claim } = readInstallCompletionAuthority(common, active);
    const layout = verifyPublicationLayout(common, claim, toolchainMode);
    if (layout.install !== 'published' || layout.toolchain !== 'published' || !layout.toolchainInspection) fail();
    const runtime = join(factory, 'install', 'runtime');
    const manifest = retained ? readOwnedReleaseManifest(runtime, receipt.manifestSha256) : validateReleaseBundle(runtime, receipt.manifestSha256);
    const expectedLock = layout.toolchainInspection.expected.rows.find(row => row.path === 'package-lock.json');
    if (manifest.version !== receipt.release || manifest.platform !== `${process.platform}-${process.arch}`
      || manifest.node.sha256 !== layout.receipt.nodeArchiveSha256
      || (!retained && JSON.stringify(layout.receipt.omittedLinks) !== JSON.stringify(['bin/corepack', 'bin/npm', 'bin/npx']))
      || expectedLock?.type !== 'file' || expectedLock.sha256 !== layout.receipt.toolchainLockSha256
      || expectedLock.sha256 !== hash(readFileSync(join(runtime, 'toolchain', 'package-lock.json')))
      || process.versions.node !== '24.22.1') fail();
    const nodePath = join(factory, 'install', 'node', 'bin', 'node'), nodeFile = lstatSync(nodePath);
    if (!nodeFile.isFile() || nodeFile.isSymbolicLink() || realpathSync(nodePath) !== nodePath) fail();
    if (retained) validateRetainedProviderSources(layout.receipt.providers);
    else validateBoundProviderSources(layout.receipt.providers);
    return { common, receipt, receiptSha256: sha256, completion, release, layout, nodePath, active };
  } catch { fail(); }
}

function inspectReadyOwnership(common: string, active: ActiveInstalledCompletion, mode: InstalledStateInspection) {
  if (active.kind === 'install.completed') {
    const current = readInstalledCompletion(common, active.completion.operationId);
    if (JSON.stringify(current.completion) !== JSON.stringify(active.completion)
      || current.repositoryId !== active.repositoryId || current.release !== active.release) fail();
  }
  const result = inspectOwnershipAtCompletion(common, active, mode);
  if (JSON.stringify(readActiveInstalledCompletion(common)) !== JSON.stringify(active)) fail();
  return result;
}

export async function inspectInstalledState(common: string, repository?: string,
  mode: InstalledStateInspection = { purpose: 'strict', retained: false }) {
  try {
    if (repository !== undefined && (await repositoryIdentity(repository)).common !== common) fail();
    return inspectReadyOwnership(common, readActiveInstalledCompletion(common), mode);
  } catch { fail(); }
}

/** Synchronous revalidation capability is captured only after the ordinary ready ownership gate. */
export async function captureDependencyAdmissionOwnership(common: string, repository: string) {
  const state = await inspectInstalledState(common, repository, { purpose: 'dependency-repair' });
  return { state, revalidate() { return inspectReadyOwnership(common, state.active, { purpose: 'dependency-repair' }); } };
}

/** Recheck ownership only through the exact sole preparing claim and unchanged prior completion. */
export function inspectClaimedDependencyOwnership(handle: MaintenanceHandle) {
  const store = openDependencyMaintenanceStore(handle.commonDir);
  try {
    const before = store.readDependencyMaintenance(handle);
    const state = inspectOwnershipAtCompletion(handle.commonDir, before.active, { purpose: 'dependency-repair' });
    if (JSON.stringify(store.readDependencyMaintenance(handle)) !== JSON.stringify(before)) fail();
    return state;
  } finally { store.close(); }
}

export type InstalledOwnershipFacts = ReturnType<typeof inspectOwnershipAtCompletion>;
