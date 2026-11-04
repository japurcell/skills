import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { validateInstallSelection, type InstallSelection } from './installation-bindings.js';
import { observeRepairRoots, readRepairAuthority, repairDigest, type ObservedRootV1, type RepairSourceV1 } from './repair-state.js';
import { readRepairStoreSnapshot } from './store.js';
import { validateReleaseBundle } from './release.js';
import { repositoryIdentity } from './workspace.js';

export interface RepairSelectionV1 {
  version: 1; repositoryId: string; root: string; common: string; factoryIdentity: string; source: RepairSourceV1;
  intendedRelease: string; manifestSha256: string; nodeArchiveSha256: string; dependencyAuthoritySha256: string;
  expectedInventorySha256: string; observedInventorySha256: string; roots: ObservedRootV1[];
  controllerManifestSha256: string; retainPolicy: 'repair-preserve-v1';
}
const RETAIN = ['history', 'accounting', 'source', 'index', 'application', 'authoring', 'receipts', 'backups', 'old-trees'] as const;

/** Inspection authenticates external same-selection bytes and retained ownership, and has no mutation capability. */
export async function inspectRepairSelection(repository: string, external: InstallSelection, operationId?: string) {
  try {
    if (process.platform === 'win32' || !((process.platform === 'darwin' && process.arch === 'arm64')
      || (process.platform === 'linux' && process.arch === 'x64')) || process.versions.node !== '24.22.1')
      throw new Error('unsupported repair profile');
    if (operationId !== undefined && !/^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(operationId))
      throw new Error('invalid source operation');
    const { root, common } = await repositoryIdentity(repository);
    if (root !== repository) throw new Error('canonical repository root required');
    if (external.providers !== undefined) throw new Error('repair inspection does not select provider changes');
    const selected = validateInstallSelection(external), authority = await readRepairAuthority(common, root);
    const manifest = validateReleaseBundle(selected.bundle.root, selected.bundle.manifestSha256);
    if (operationId !== undefined && authority.source.kind !== 'upgrade'
      || operationId !== undefined && authority.source.kind === 'upgrade' && authority.source.operationId !== operationId)
      throw new Error('repair source operation differs');
    const lock = authority.candidate.entries.find(row => row.path === 'toolchain/package-lock.json');
    const runtimeLock = authority.candidate.entries.find(row => row.path === 'install/runtime/toolchain/package-lock.json');
    const lockSha256 = createHash('sha256').update(readFileSync(join(selected.bundle.root, 'toolchain/package-lock.json'))).digest('hex');
    if (selected.bundle.manifestSha256 !== authority.manifestSha256 || selected.bundle.version !== authority.release
      || selected.bundle.platform !== `${process.platform}-${process.arch}`
      || selected.node.sha256 !== authority.candidate.nodeArchiveSha256
      || lock?.type !== 'file' || lock.sha256 !== authority.candidate.toolchainLockSha256
      || runtimeLock?.type !== 'file' || runtimeLock.sha256 !== lockSha256 || lock.sha256 !== lockSha256
      || JSON.stringify(authority.candidate.omittedLinks) !== JSON.stringify(['bin/corepack', 'bin/npm', 'bin/npx']))
      throw new Error('external selection differs from retained authority');
    const runtimeFiles = new Map(manifest.files.map(file => [file.path, file]));
    if (authority.candidate.entries.find(row => row.path === 'install/runtime/release-manifest.json')?.sha256 !== authority.manifestSha256)
      throw new Error('retained intended manifest inventory differs');
    for (const row of authority.candidate.entries.filter(row => row.type === 'file' && row.path.startsWith('install/runtime/'))) {
      const path = row.path.slice('install/runtime/'.length), file = runtimeFiles.get(path);
      if (path === 'release-manifest.json' ? row.sha256 !== authority.manifestSha256
        : !file || row.sha256 !== file.sha256 || row.bytes !== file.bytes)
        throw new Error('retained runtime inventory differs from intended bundle');
      runtimeFiles.delete(path);
    }
    if (runtimeFiles.size) throw new Error('retained runtime inventory is incomplete');
    const observed = observeRepairRoots(common, authority);
    if (JSON.stringify(readRepairStoreSnapshot(common)) !== JSON.stringify(authority.snapshot))
      throw new Error('repair snapshot changed');
    const again = validateInstallSelection(external);
    if (JSON.stringify(again) !== JSON.stringify(selected)
      || JSON.stringify(observeRepairRoots(common, authority)) !== JSON.stringify(observed))
      throw new Error('repair observation changed');
    const selection: RepairSelectionV1 = { version: 1, repositoryId: authority.snapshot.repositoryId, root, common,
      factoryIdentity: authority.factoryIdentity, source: authority.source, intendedRelease: authority.release,
      manifestSha256: authority.manifestSha256, nodeArchiveSha256: authority.candidate.nodeArchiveSha256,
      dependencyAuthoritySha256: repairDigest({ providers: authority.candidate.providers, lockSha256: authority.candidate.toolchainLockSha256 }),
      expectedInventorySha256: observed.expectedInventorySha256, observedInventorySha256: observed.observedInventorySha256,
      roots: observed.roots, controllerManifestSha256: selected.bundle.manifestSha256, retainPolicy: 'repair-preserve-v1' };
    const needed = Object.values(observed.damage).some(value => value !== 0);
    const action = authority.resume ? authority.resume.owner.state === 'known_live' ? 'refused' : 'resume-upgrade' : needed ? 'repair' : 'healthy';
    return { version: 1, action, source: { kind: authority.source.kind, state: authority.snapshot.state,
      operationId: authority.source.kind === 'upgrade' ? authority.source.operationId : authority.active.completion.operationId },
      selectionSha256: repairDigest(selection), selection, damage: observed.damage,
      impact: { replace: needed || authority.resume ? ['install', 'toolchain'] : [], retain: RETAIN },
      nativeSupport: { platform: `${process.platform}-${process.arch}`, inspection: true, repairImplemented: false },
      ...(authority.resume ? { resume: { operationId: authority.resume.operationId, recorded: authority.resume.recorded,
        position: authority.resume.position, owner: authority.resume.owner.state, clearanceRequired: true,
        command: ['resume-upgrade', '--repository', root, '--bundle-root', external.bundleRoot,
          '--manifest-sha256', external.manifestSha256, '--node-archive', external.nodeArchivePath,
          '--operation', authority.resume.operationId, '--operator-confirmed', '--note', '<required clearance note>'] } } : {}) };
  } catch {
    return { version: 1, action: 'refused' as const, reason: 'unprovable-repair-authority',
      nativeSupport: { platform: `${process.platform}-${process.arch}`, inspection: process.platform !== 'win32', repairImplemented: false } };
  }
}
