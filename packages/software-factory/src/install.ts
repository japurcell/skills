import { readPreparationRequest, validateSelectedPython, sameSelection, fileCopy, copyTree, normalizeToolchain, runManagedInstallCommand, npmEnvironment, validateToolchain } from './install-preparation.js';
export { validateSelectedPython, runManagedInstallCommand } from './install-preparation.js';
import { createHash, randomUUID } from 'node:crypto';
import { closeSync, constants, fsyncSync, lstatSync, mkdirSync, openSync, writeSync } from 'node:fs';
import { join, sep } from 'node:path';
import { currentOwner, inspectOwner } from './native/process.js';
import { atomicPublicationSupportProfile } from './atomic-publication.js';
import { selectUpgradeProviders, validateInstallSelection, type VerifiedInstallSelection } from './installation-bindings.js';
import { validateReleaseBundle } from './release.js';
import { beginRepositoryBootstrap, prepareForwardSchema, measureMaintenanceStage, prepareMaintenanceHandoff, type MaintenanceSelection } from './maintenance.js';
import { openMaintenanceStore } from './store.js';
import { directoryIdentity, scanOwnedTree, verifyBoundInstallCandidate, writeCandidateReceipt,
  type CandidateReceipt } from './install-candidate.js';
import { repositoryIdentity } from './workspace.js';
import { captureOriginalInstallation, assertOriginalInstallation } from './upgrade-original.js';
import { writePublicationRecord } from './install-publication-state.js';
import { prepareUpgradeIntent } from './upgrade-publication-state.js';

const LOCK_SHA = 'bea7cfb5a835aba203893966dde3e964418b12c69f8680e53a65b3603b9467d6';

export interface PreparedCandidateReceipt {
  operationId: string; repositoryId: string; claimId: string; stagePath: string; candidateDigest: string;
}
export interface PreparedInstallHandoff extends PreparedCandidateReceipt { ticketPath: string; stageDigest: string }
function fail(message: string): never { throw new Error(`install prepare: ${message}`); }
function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonicalJson((value as Record<string, unknown>)[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
export function selectionFrom(value: VerifiedInstallSelection): MaintenanceSelection {
  const artifactDigests: Record<string, string> = { bundle: value.bundle.manifestSha256, node: value.node.sha256 };
  if (value.windowsHelper) artifactDigests['windows-helper'] = value.windowsHelper.sha256;
  if (value.providers.codex) artifactDigests.codex = value.providers.codex.sha256;
  if (value.providers.copilot) artifactDigests.copilot = value.providers.copilot.manifestSha256;
  const selected = { schema: 1, release: value.bundle.version, platform: value.bundle.platform,
    manifestSha256: value.bundle.manifestSha256, nodeArchiveSha256: value.node.sha256, targetSchema: 7,
    providers: value.providers, windowsHelperSha256: value.windowsHelper?.sha256 ?? null };
  return { release: value.bundle.version, selectionDigest: createHash('sha256').update(canonicalJson(selected)).digest('hex'),
    targetReleaseSha256: value.bundle.manifestSha256, artifactDigests, targetSchema: 7 };
}
/** Authenticated private request to an incomplete, candidate-bound operation. No installed-ready effect. */
function publicationPlatformQualified(): boolean {
  const profile = atomicPublicationSupportProfile();
  return (profile === 'darwin' && process.arch === 'arm64') || profile === 'linux-x64';
}

async function prepareCandidate(requestPath: string, handoff: false): Promise<PreparedCandidateReceipt>;
async function prepareCandidate(requestPath: string, handoff: true, upgrade?: boolean): Promise<PreparedInstallHandoff>;
async function prepareCandidate(requestPath: string, handoff: boolean, upgrade = false): Promise<PreparedCandidateReceipt | PreparedInstallHandoff> {
  if (handoff && !publicationPlatformQualified())
    fail('foreground installation publication platform is not qualified');
  const request = readPreparationRequest(requestPath, handoff ? 'handoff' : 'install');
  const { common } = await repositoryIdentity(request.repository);
  const launcher = handoff ? currentOwner(validateSelectedPython(request.python)!.launcherPid) : undefined;
  if (launcher && inspectOwner(launcher).state !== 'known_live') fail('launcher identity unavailable');
  const captured = upgrade ? await captureOriginalInstallation(common, request.repository, launcher!) : null;
  const providers = captured ? selectUpgradeProviders(captured.original.providers, request.source.providers) : request.source.providers;
  const targetSource = { ...request.source, ...(providers !== undefined ? { providers } : {}) };
  const privateSelection = validateInstallSelection({ bundleRoot: request.snapshot.bundleRoot,
    manifestSha256: request.source.manifestSha256, nodeArchivePath: request.snapshot.nodeArchivePath,
    ...(providers !== undefined ? { providers } : {}) });
  const measuredNode = scanOwnedTree(request.snapshot.extractedNodeRoot, 'node');
  if (measuredNode.digest !== request.snapshot.nodeTree.digest || measuredNode.entries !== request.snapshot.nodeTree.entries
    || measuredNode.regularBytes !== request.snapshot.nodeTree.regularBytes
    || JSON.stringify(request.snapshot.nodeTree.omittedLinks) !== JSON.stringify(privateSelection.bundle.platform === 'win32-x64' ? [] : ['bin/corepack', 'bin/npm', 'bin/npx']))
    fail('extracted Node tree differs from authenticated request');
  const original = validateInstallSelection(targetSource);
  sameSelection(privateSelection, original);
  if (handoff) {
    const python = validateSelectedPython(request.python)!;
    const factory = join(common, 'factory');
    if (python.path === factory || python.path.startsWith(`${factory}${sep}`)
      || python.path === request.stageRoot || python.path.startsWith(`${request.stageRoot}${sep}`))
      fail('selected Python under replaceable or private stage');
  }
  for (const provider of [original.providers.codex?.executable, original.providers.copilot?.packageRoot,
    original.providers.copilot?.manifestFile]) {
    const factory = join(common, 'factory');
    if (provider && (provider === factory || provider.startsWith(`${factory}${sep}`)
      || provider === request.stageRoot || provider.startsWith(`${request.stageRoot}${sep}`)))
      fail('provider source under replaceable or private stage');
  }
  const selection = selectionFrom(original);
  if (captured) {
    selection.artifactDigests['original-installed'] = captured.digest;
    selection.artifactDigests['original-completion'] = captured.completionDigest;
  }
  const handle = captured ? await prepareForwardSchema(request.repository, selection, currentOwner())
    : await beginRepositoryBootstrap(request.repository, selection, currentOwner());
  if (captured) {
    assertOriginalInstallation(common, captured.original);
    const operation = join(common, 'factory', `upgrade-${handle.operationId}`);
    mkdirSync(operation, { mode: 0o700 });
    mkdirSync(join(operation, 'old'), { mode: 0o700 });
    writePublicationRecord(join(operation, 'original.json'), captured.original);
  }
  const candidate = join(common, 'factory', `install-candidate-${handle.operationId}`);
  mkdirSync(candidate, { mode: 0o700 });
  const runtimeSource = scanOwnedTree(request.snapshot.bundleRoot, 'candidate');
  mkdirSync(join(candidate, 'install'), { mode: 0o700 });
  copyTree(request.snapshot.bundleRoot, join(candidate, 'install/runtime'), runtimeSource);
  validateReleaseBundle(join(candidate, 'install/runtime'), request.source.manifestSha256);
  copyTree(request.snapshot.extractedNodeRoot, join(candidate, 'install/node'), measuredNode);
  const copiedNode = scanOwnedTree(join(candidate, 'install/node'), 'node');
  if (copiedNode.digest !== measuredNode.digest || copiedNode.entries !== measuredNode.entries) fail('copied Node tree differs');
  mkdirSync(join(candidate, 'toolchain'), { mode: 0o700 });
  for (const name of ['package.json', 'package-lock.json']) fileCopy(join(candidate, 'install/runtime/toolchain', name), join(candidate, 'toolchain', name));
  const nodeExecutable = join(candidate, 'install/node', privateSelection.bundle.platform === 'win32-x64' ? 'node.exe' : 'bin/node');
  const npmCli = join(candidate, 'install/node', privateSelection.bundle.platform === 'win32-x64' ? 'node_modules/npm/bin/npm-cli.js' : 'lib/node_modules/npm/bin/npm-cli.js');
  const npmArgs = [npmCli, 'ci', '--ignore-scripts', '--no-bin-links', '--audit=false', '--fund=false', '--update-notifier=false',
    '--cache', join(request.stageRoot, 'npm/cache'), '--userconfig', join(request.stageRoot, 'npm/user.npmrc'),
    '--globalconfig', join(request.stageRoot, 'npm/global.npmrc'), ...(request.npm.offline ? ['--offline'] : [])];
  await runManagedInstallCommand(nodeExecutable, npmArgs, join(candidate, 'toolchain'), npmEnvironment(request.stageRoot));
  normalizeToolchain(join(candidate, 'toolchain/node_modules'));
  validateToolchain(join(candidate, 'toolchain'));
  const toolchainManifest = { schema: 1, node: '24.22.1', typescript: '7.0.2',
    dependencies: { '@types/node': '24.19.2', typescript: '7.0.2' } };
  const manifestBytes = Buffer.from(`${JSON.stringify(toolchainManifest)}\n`);
  const manifestPath = join(candidate, 'toolchain/manifest.json');
  const manifestFd = openSync(manifestPath, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL, 0o600);
  try { writeSync(manifestFd, manifestBytes); fsyncSync(manifestFd); } finally { closeSync(manifestFd); }
  const compiledStage = join(common, 'factory', 'controller-staging');
  if (!upgrade) mkdirSync(compiledStage, { mode: 0o700 });
  else directoryIdentity(compiledStage);
  const stagePath = join(compiledStage, handle.operationId);
  mkdirSync(stagePath, { mode: 0o700 });
  const payload = join(stagePath, 'payload');
  mkdirSync(payload, { mode: 0o700 });
  fileCopy(nodeExecutable, join(payload, privateSelection.bundle.platform === 'win32-x64' ? 'node.exe' : 'node'), undefined, 0o700);
  fileCopy(join(candidate, 'install/runtime/package.json'), join(payload, 'package.json'));
  let atomicBinding: { interpreter: { path: string; identity: string; sha256: string }; helper: { path: string; identity: string; sha256: string }; pythonVersion: string; launcher: import('./store.js').Owner } | undefined;
  if (handoff) {
    const selectedPython = validateSelectedPython(request.python)!;
    const helperRow = runtimeSource.rows.find(row => row.path === 'native/atomic-publication.py');
    if (!helperRow || helperRow.type !== 'file' || !helperRow.sha256) fail('authenticated publication helper missing');
    const helperDirectory = join(payload, 'native'), helperPath = join(helperDirectory, 'atomic-publication.py');
    mkdirSync(helperDirectory, { mode: 0o700 });
    fileCopy(join(candidate, 'install/runtime/native/atomic-publication.py'), helperPath, helperRow);
    const helperInfo = lstatSync(helperPath);
    atomicBinding = { interpreter: { path: selectedPython.path, identity: selectedPython.identity, sha256: selectedPython.sha256 },
      helper: { path: helperPath, identity: `${helperInfo.dev}:${helperInfo.ino}`, sha256: helperRow.sha256 },
      pythonVersion: selectedPython.version, launcher: launcher! };
    writePublicationRecord(join(payload, 'atomic-binding.json'), { version: 1, ...atomicBinding,
      factoryIdentity: directoryIdentity(join(common, 'factory')) });
  }
  const distSource = scanOwnedTree(join(candidate, 'install/runtime/dist'), 'candidate');
  copyTree(join(candidate, 'install/runtime/dist'), join(payload, 'dist'), distSource);
  await runManagedInstallCommand(join(payload, privateSelection.bundle.platform === 'win32-x64' ? 'node.exe' : 'node'),
    [join(payload, 'dist/maintenance-entry.js'), '--self-check'], payload, npmEnvironment(request.stageRoot));
  const stageEvidence = measureMaintenanceStage(stagePath);
  const originalAgain = validateInstallSelection(targetSource);
  sameSelection(original, originalAgain);
  if (handoff) validateSelectedPython(request.python);
  if (directoryIdentity(request.stageRoot) !== request.stageIdentity
    || scanOwnedTree(request.snapshot.extractedNodeRoot, 'node').digest !== measuredNode.digest)
    fail('private snapshot changed before candidate binding');
  const tree = scanOwnedTree(candidate, 'candidate');
  const rootIdentity = directoryIdentity(candidate), receiptId = randomUUID();
  const receipt: CandidateReceipt = { schema: 1, receiptId, operationId: handle.operationId, repositoryId: handle.repositoryId,
    claimId: handle.claimId, selectionDigest: selection.selectionDigest, manifestSha256: request.source.manifestSha256,
    nodeArchiveSha256: privateSelection.node.sha256, toolchainLockSha256: LOCK_SHA,
    omittedLinks: request.snapshot.nodeTree.omittedLinks, providers: original.providers,
    rootIdentity, treeDigest: tree.digest, entries: tree.rows };
  const receiptSha256 = writeCandidateReceipt(join(candidate, 'candidate-receipt.json'), receipt);
  const binding = { path: candidate, identity: rootIdentity, treeDigest: tree.digest, receiptId, receiptSha256 };
  verifyBoundInstallCandidate(binding, { operationId: handle.operationId, repositoryId: handle.repositoryId,
    claimId: handle.claimId, selectionDigest: selection.selectionDigest, manifestSha256: request.source.manifestSha256 });
  const store = openMaintenanceStore(common);
  try {
    if (captured) {
      assertOriginalInstallation(common, captured.original);
      if (!atomicBinding) fail('upgrade helper binding missing');
      const { sha256: intentSha256, receipt } = prepareUpgradeIntent(handle, binding, stageEvidence, atomicBinding);
      await store.bindUpgradeCandidate({ handle, candidate: binding, intentSha256, receipt, launcher: atomicBinding.launcher, ...stageEvidence });
    } else await store.bindInstallCandidate({ handle, candidate: binding, ...stageEvidence });
  } finally { store.close(); }
  const result = { operationId: handle.operationId, repositoryId: handle.repositoryId, claimId: handle.claimId,
    stagePath, candidateDigest: tree.digest };
  if (handoff) {
    const ticket = await prepareMaintenanceHandoff(request.repository, handle);
    return { ...result, ticketPath: ticket.ticketPath, stageDigest: ticket.stageDigest };
  }
  return result;
}
/** Authenticated preparation without handoff, retained for the explicit prepare route. */
export function prepareInstallCandidate(requestPath: string): Promise<PreparedCandidateReceipt> { return prepareCandidate(requestPath, false); }
/** Trusted preparer emits a private one-use handoff ticket while it still owns the claim. */
export function prepareInstallHandoff(requestPath: string): Promise<PreparedInstallHandoff> { return prepareCandidate(requestPath, true); }

/** Authenticated installed upgrade preparation; publication remains in the staged controller. */
export function prepareUpgradeHandoff(requestPath: string): Promise<PreparedInstallHandoff> { return prepareCandidate(requestPath, true, true); }
