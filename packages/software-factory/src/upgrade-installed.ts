import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { join } from 'node:path';
import { readPublicationRecord } from './install-publication-state.js';
import { inspectUpgradeLayout, upgradeDirectory } from './upgrade-publication-state.js';
import { validateBoundProviderSources, validateRetainedProviderSources } from './installation-bindings.js';
import { validateReleaseBundle } from './release.js';
import { readOwnedReleaseManifest } from './owned-release.js';
import type { CandidateBinding, Claim, Owner } from './store.js';
import type { ToolchainInspectionMode } from './owned-toolchain.js';

export interface UpgradeInstalledReceipt {
  version: 1; kind: 'upgrade'; receiptId: string; operationId: string; repositoryId: string; claimId: string;
  release: string; targetSchema: number; selectionDigest: string; manifestSha256: string; candidate: CandidateBinding;
  stageDigest: string; stageIdentity: string; intentSha256: string; originalSha256: string; backupReceiptSha256: string;
  launcher: Owner; authoring: { path: string; sha256: string; identity: string }[];
}
function hash(bytes: Buffer): string { return createHash('sha256').update(bytes).digest('hex'); }
export function readUpgradeInstalledReceipt(common: string, operationId: string) {
  const path = join(upgradeDirectory(common, operationId), 'new-receipt.json'), before = lstatSync(path);
  const bytes = readPublicationRecord(path), after = lstatSync(path);
  if (before.dev !== after.dev || before.ino !== after.ino || before.nlink !== 1 || after.nlink !== 1)
    throw new Error('upgrade installed receipt identity changed');
  const receipt = JSON.parse(bytes.toString('utf8')) as UpgradeInstalledReceipt;
  const keys = ['version','kind','receiptId','operationId','repositoryId','claimId','release','targetSchema','selectionDigest',
    'manifestSha256','candidate','stageDigest','stageIdentity','intentSha256','originalSha256','backupReceiptSha256','launcher','authoring'].sort();
  if (JSON.stringify(Object.keys(receipt).sort()) !== JSON.stringify(keys) || receipt.version !== 1 || receipt.kind !== 'upgrade'
    || receipt.operationId !== operationId || receipt.targetSchema !== 7 || !Array.isArray(receipt.authoring)
    || !/^[a-f0-9-]{36}$/i.test(receipt.receiptId) || !/^[a-f0-9-]{36}$/i.test(receipt.claimId)
    || !/^[a-f0-9-]{36}$/i.test(receipt.repositoryId) || !/^[a-f0-9]{64}$/.test(receipt.selectionDigest)
    || !/^[a-f0-9]{64}$/.test(receipt.manifestSha256) || !/^[a-f0-9]{64}$/.test(receipt.intentSha256)
    || !/^[a-f0-9]{64}$/.test(receipt.originalSha256) || !/^[a-f0-9]{64}$/.test(receipt.backupReceiptSha256)
    || !/^[a-f0-9]{64}$/.test(receipt.stageDigest) || !/^\d+:\d+$/.test(receipt.stageIdentity)
    || !receipt.launcher || typeof receipt.launcher.host !== 'string' || !Number.isSafeInteger(receipt.launcher.pid)
    || receipt.launcher.pid < 1 || typeof receipt.launcher.start !== 'string' || !receipt.launcher.start
    || typeof receipt.release !== 'string' || receipt.release.length < 1 || receipt.release.length > 256)
    throw new Error('upgrade installed receipt invalid');
  return { receipt, sha256: hash(bytes), identity: `${before.dev}:${before.ino}` };
}

/** Verify committed upgrade bytes without executing either the old runtime or a provider. */
export function inspectInstalledUpgrade(common: string, active: { completion: { operationId: string; repositoryId: string;
  claimId: string; selectionDigest: string; manifestSha256: string; receiptId: string; receiptSha256: string;
  originalInstalledSha256?: string; originalCompletionSha256?: string; receiptIdentity?: string }; release: string }, retained = false,
  toolchainMode: ToolchainInspectionMode = { purpose: 'strict' }) {
  const { receipt, sha256, identity } = readUpgradeInstalledReceipt(common, active.completion.operationId), completion = active.completion;
  if (completion.repositoryId !== receipt.repositoryId || completion.claimId !== receipt.claimId
    || completion.selectionDigest !== receipt.selectionDigest || completion.manifestSha256 !== receipt.manifestSha256
    || completion.receiptId !== receipt.receiptId || completion.receiptSha256 !== sha256 || completion.receiptIdentity !== identity
    || active.release !== receipt.release
    || completion.originalInstalledSha256 !== receipt.originalSha256)
    throw new Error('upgrade installed completion differs');
  const claim: Claim = { id: receipt.claimId, token: '', kind: 'maintenance', resourceKey: receipt.repositoryId,
    invocationId: null, owner: { host: '', pid: 0, start: null }, maintenance: {
      operationId: receipt.operationId, repositoryId: receipt.repositoryId, kind: 'upgrade', release: receipt.release,
      targetReleaseSha256: receipt.manifestSha256, selectionDigest: receipt.selectionDigest,
      artifactDigests: { 'original-installed': receipt.originalSha256 }, targetSchema: receipt.targetSchema,
      stagePath: '', stageDigest: receipt.stageDigest, stageIdentity: receipt.stageIdentity, phase: 'validating',
      ownedReceiptId: receipt.receiptId, backupId: null, ticketNonceHash: null, ticketConsumed: true,
      candidate: receipt.candidate, upgradeIntentSha256: receipt.intentSha256,
      upgradeReceipt: { id: receipt.receiptId, sha256, identity },
      forward: { sourceShape: 'v7', currentShape: 'v7', sourceRelease: '', sourceIdentity: '', backup: {
        id: '', identity: '', sha256: '', bytes: 0, countDigest: '', receiptId: '', receiptSha256: receipt.backupReceiptSha256 } },
    } };
  const layout = inspectUpgradeLayout(common, claim, toolchainMode);
  if (layout.recorded !== 4 || layout.position !== 4
    || JSON.stringify(layout.intent.atomicBinding.launcher) !== JSON.stringify(receipt.launcher))
    throw new Error('upgrade installed layout incomplete');
  const original = JSON.parse(readPublicationRecord(join(upgradeDirectory(common, receipt.operationId), 'original.json')).toString('utf8')) as { completion?: unknown; receipt?: { authoring?: unknown } };
  if (completion.originalCompletionSha256 !== hash(Buffer.from(JSON.stringify(original.completion)))
    || JSON.stringify(original.receipt?.authoring) !== JSON.stringify(receipt.authoring))
    throw new Error('upgrade authoring ownership differs');
  const factory = join(common, 'factory'), runtime = join(factory, 'install', 'runtime');
  const manifest = retained ? readOwnedReleaseManifest(runtime, receipt.manifestSha256) : validateReleaseBundle(runtime, receipt.manifestSha256);
  if (manifest.version !== receipt.release || manifest.platform !== `${process.platform}-${process.arch}`
    || manifest.node.sha256 !== layout.originalCandidate.nodeArchiveSha256
    || layout.toolchainInspection?.expected.rows.find(row => row.path === 'package-lock.json')?.sha256 !== layout.originalCandidate.toolchainLockSha256
    || hash(readFileSync(join(runtime, 'toolchain', 'package-lock.json'))) !== layout.originalCandidate.toolchainLockSha256
    || (!retained && JSON.stringify(layout.originalCandidate.omittedLinks) !== JSON.stringify(['bin/corepack', 'bin/npm', 'bin/npx']))
    || process.versions.node !== '24.22.1') throw new Error('upgrade installed selection differs');
  if (retained) validateRetainedProviderSources(layout.originalCandidate.providers);
  else validateBoundProviderSources(layout.originalCandidate.providers);
  const nodePath = join(factory, 'install', 'node', 'bin', 'node'), file = lstatSync(nodePath);
  if (!file.isFile() || file.isSymbolicLink() || realpathSync(nodePath) !== nodePath)
    throw new Error('upgrade installed Node differs');
  return { common, receipt, receiptSha256: sha256, completion, release: active.release,
    layout: { receipt: layout.originalCandidate, toolchainInspection: layout.toolchainInspection }, nodePath };
}
