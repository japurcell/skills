import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { join } from 'node:path';
import { directoryIdentity } from './install-candidate.js';
import { readInstalledReceipt } from './install-publication.js';
import { inspectInstalledUpgrade } from './upgrade-installed.js';
import { publicationIntentPath, readPublicationRecord, verifyPublicationLayout } from './install-publication-state.js';
import { validateBoundProviderSources, validateRetainedProviderSources } from './installation-bindings.js';
import { validateReleaseBundle } from './release.js';
import { readOwnedReleaseManifest } from './owned-release.js';
import { readActiveInstalledCompletion, readInstalledCompletion, openDependencyMaintenanceStore, type ActiveInstalledCompletion, type MaintenanceHandle, type Claim } from './store.js';
import { repositoryIdentity } from './workspace.js';

export type InstalledStateInspection = { readonly purpose: 'strict'; readonly retained: boolean }
  | { readonly purpose: 'dependency-repair' };
function fail(): never { throw new Error('installed binding refused'); }
function hash(bytes: Buffer): string { return createHash('sha256').update(bytes).digest('hex'); }

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
    const layout = verifyPublicationLayout(common, synthetic, toolchainMode);
    if (!layout.intent || layout.install !== 'published' || layout.toolchain !== 'published' || !layout.toolchainInspection
      || layout.intent.installIdentity !== receipt.installIdentity
      || layout.intent.toolchainIdentity !== receipt.toolchainIdentity
      || hash(readPublicationRecord(publicationIntentPath(common, receipt.operationId))) !== receipt.publicationIntentSha256) fail();
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
