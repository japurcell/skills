import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { directoryIdentity, scanOwnedTree } from './install-candidate.js';
import { inspectInstalledOwnership } from './installed-bindings.js';
import { validateRetainedProviderSources } from './installation-bindings.js';
import { readInstalledReceipt } from './install-publication.js';
import { readUpgradeInstalledReceipt } from './upgrade-installed.js';
import { repositoryIdentity } from './workspace.js';

function hash(value: string | Buffer): string { return createHash('sha256').update(value).digest('hex'); }
function tree(path: string) {
  const identity = directoryIdentity(path), evidence = scanOwnedTree(path, 'candidate');
  return { identity, digest: evidence.digest, entries: evidence.entries, bytes: evidence.regularBytes };
}

/** Captured by the selected new runtime before admission; no old executable is launched. */
export async function captureOriginalInstallation(common: string, repository: string) {
  const installed = await inspectInstalledOwnership(common, repository, true);
  const location = await repositoryIdentity(repository);
  if (location.common !== common) throw new Error('original repository identity differs');
  const factory = join(common, 'factory');
  const original = { version: 1 as const, root: location.root, common: location.common, repositoryId: installed.receipt.repositoryId,
    release: installed.release, factoryIdentity: directoryIdentity(factory), completion: installed.completion,
    receipt: installed.receipt, receiptSha256: installed.receiptSha256,
    install: tree(join(factory, 'install')), toolchain: tree(join(factory, 'toolchain')),
    providers: installed.layout.receipt.providers,
    toolchainLockSha256: hash(readFileSync(join(factory, 'toolchain', 'package-lock.json'))) };
  return { original, digest: hash(JSON.stringify(original)), completionDigest: hash(JSON.stringify(original.completion)) };
}

export type OriginalInstallation = Awaited<ReturnType<typeof captureOriginalInstallation>>['original'];

/** Recheck the original files after admission and before replacement. */
export function assertOriginalInstallation(common: string, original: OriginalInstallation): void {
  const factory = join(common, 'factory');
  const current = 'kind' in original.receipt && original.receipt.kind === 'upgrade'
    ? readUpgradeInstalledReceipt(common, original.receipt.operationId) : readInstalledReceipt(common);
  if (original.common !== common || directoryIdentity(factory) !== original.factoryIdentity || current.sha256 !== original.receiptSha256 || JSON.stringify(current.receipt) !== JSON.stringify(original.receipt)
    || JSON.stringify(tree(join(factory, 'install'))) !== JSON.stringify(original.install)
    || JSON.stringify(tree(join(factory, 'toolchain'))) !== JSON.stringify(original.toolchain)
    || hash(readFileSync(join(factory, 'toolchain', 'package-lock.json'))) !== original.toolchainLockSha256)
    throw new Error('original installed ownership changed');
  validateRetainedProviderSources(original.providers);
}
