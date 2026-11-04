import { createHash, randomUUID } from 'node:crypto';
import { lstatSync, mkdirSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { directoryIdentity, scanOwnedTree, readInventoryReceipt, writeInventoryReceipt, type TreeEvidence } from './install-candidate.js';
import { readPreparationRequest, privateFile, sameSelection, fileCopy, normalizeToolchain, npmEnvironment, validateToolchain, runManagedInstallCommand, flushDirectory } from './install-preparation.js';
import { validateInstallSelection } from './installation-bindings.js';
import { readPublicationRecord, writePublicationRecord } from './install-publication-state.js';
import { admitDependencyMaintenance, assertDependencyMaintenanceAtLocation, inspectDependencyMaintenanceSelection, prepareDependencyBackup } from './dependency-maintenance.js';
import { currentOwner, inspectOwner } from './native/process.js';
import { inspectClaimedDependencyOwnership } from './installed-state.js';
import { toolchainRows } from './owned-toolchain.js';
import { openDependencyMaintenanceStore, type CandidateBinding, type Claim, type MaintenanceHandle } from './store.js';
import { repositoryIdentity } from './workspace.js';

const hash = (bytes: string | Buffer) => createHash('sha256').update(bytes).digest('hex');
function fail(message: string): never { throw new Error(`dependency candidate: ${message}`); }
function candidatePath(handle: MaintenanceHandle) { return join(handle.commonDir, 'factory', `dependency-candidate-${handle.operationId}`); }
function owned(claim: Claim) {
  const owner = currentOwner();
  if (owner.host !== claim.owner.host || owner.pid !== claim.owner.pid || owner.start !== claim.owner.start
    || inspectOwner(owner).state !== 'known_live') fail('exact live claim owner required');
}
function inputFacts(requestPath: string) {
  const request = readPreparationRequest(requestPath, 'dependencies');
  const copied = validateInstallSelection({ bundleRoot: request.snapshot.bundleRoot,
    manifestSha256: request.source.manifestSha256, nodeArchivePath: request.snapshot.nodeArchivePath });
  const source = validateInstallSelection(request.source); sameSelection(copied, source);
  const node = scanOwnedTree(request.snapshot.extractedNodeRoot, 'node');
  if (node.digest !== request.snapshot.nodeTree.digest || node.entries !== request.snapshot.nodeTree.entries
    || node.regularBytes !== request.snapshot.nodeTree.regularBytes
    || JSON.stringify(request.snapshot.nodeTree.omittedLinks) !== JSON.stringify(['bin/corepack', 'bin/npm', 'bin/npx']))
    fail('authenticated extracted Node request differs');
  const executable = join(request.snapshot.extractedNodeRoot, 'bin/node');
  if (process.platform === 'win32' || process.execPath !== executable) fail('selected authenticated preparer Node required');
  for (const suffix of ['npm', 'npm/cache', 'npm/home']) directoryIdentity(join(request.stageRoot, suffix));
  return { request, copied, source, node, requestSha256: hash(privateFile(requestPath, 64 * 1024)),
    bundleIdentity: directoryIdentity(request.snapshot.bundleRoot), nodeIdentity: directoryIdentity(request.snapshot.extractedNodeRoot) };
}
function identities(path: string, tree: TreeEvidence) {
  return tree.rows.map(row => { const stat = lstatSync(join(path, row.path)); return { path: row.path, identity: `${stat.dev}:${stat.ino}` }; });
}
function attemptFacts(handle: MaintenanceHandle, claim: Claim, requestSha256: string, inputs: {
  bundleIdentity: string; nodeIdentity: string; node: TreeEvidence; source: ReturnType<typeof validateInstallSelection>;
}) {
  const selected = claim.maintenance!, attempt = selected.dependencies!.candidateAttempt!;
  const original = structuredClone(claim);
  original.maintenance!.candidate = null;
  original.maintenance!.dependencies!.candidateAttempt!.binding = null;
  original.maintenance!.dependencies!.candidateAttempt!.events = attempt.events.slice(0, 2);
  return { version: 1, kind: 'dependencies', operationId: handle.operationId, repositoryId: handle.repositoryId,
    claimId: handle.claimId, candidateId: attempt.id, selectionDigest: selected.selectionDigest,
    originalSha256: selected.dependencies!.originalSha256, originalCompletionSha256: selected.dependencies!.originalCompletionSha256,
    backupReceiptSha256: selected.dependencies!.backup!.receiptSha256, backupAttemptSha256: selected.dependencies!.backupAttempt!.sha256,
    declarationSha256: selected.dependencies!.declarationSha256, lockSha256: selected.dependencies!.lockSha256,
    requestSha256, allocatedClaimSha256: hash(JSON.stringify(original)), rootIdentity: directoryIdentity(candidatePath(handle)),
    bootstrap: { manifestSha256: inputs.source.bundle.manifestSha256, nodeArchiveSha256: inputs.source.node.sha256,
      bundleIdentity: inputs.bundleIdentity, nodeIdentity: inputs.nodeIdentity,
      nodeTree: { digest: inputs.node.digest, entries: inputs.node.entries, regularBytes: inputs.node.regularBytes } } };
}

/** Validate retained candidate evidence without executing candidate code or changing state. */
export function verifyDependencyCandidateArtifacts(handle: MaintenanceHandle, claim: Claim, prospective?: CandidateBinding) {
  const selected = claim.maintenance!, attempt = selected.dependencies!.candidateAttempt, binding = prospective ?? selected.candidate;
  if (!attempt?.binding) fail('candidate attempt is unbound; evidence retained');
  const path = candidatePath(handle), recorded = attempt.binding;
  if (directoryIdentity(path) !== recorded.rootIdentity) fail('candidate root identity changed');
  const attemptPath = join(path, 'candidate-attempt.json'), bytes = readPublicationRecord(attemptPath), stat = lstatSync(attemptPath);
  const record = JSON.parse(bytes.toString('utf8')) as Record<string, unknown>;
  const original = structuredClone(claim);
  original.maintenance!.candidate = null; original.maintenance!.dependencies!.candidateAttempt!.binding = null;
  original.maintenance!.dependencies!.candidateAttempt!.events = attempt.events.slice(0, 2);
  const expected = { version: 1, kind: 'dependencies', operationId: handle.operationId, repositoryId: handle.repositoryId,
    claimId: handle.claimId, candidateId: attempt.id, selectionDigest: selected.selectionDigest,
    originalSha256: selected.dependencies!.originalSha256, originalCompletionSha256: selected.dependencies!.originalCompletionSha256,
    backupReceiptSha256: selected.dependencies!.backup!.receiptSha256, backupAttemptSha256: selected.dependencies!.backupAttempt!.sha256,
    declarationSha256: selected.dependencies!.declarationSha256, lockSha256: selected.dependencies!.lockSha256,
    requestSha256: recorded.requestSha256, allocatedClaimSha256: hash(JSON.stringify(original)), rootIdentity: recorded.rootIdentity,
    bootstrap: record['bootstrap'] };
  if (`${stat.dev}:${stat.ino}` !== recorded.identity || hash(bytes) !== recorded.sha256 || JSON.stringify(record) !== JSON.stringify(expected))
    fail('immutable candidate attempt changed');
  const names = readdirSync(path).sort();
  if (!binding) {
    if (names.some(name => !['candidate-attempt.json', 'candidate-receipt.json', 'toolchain'].includes(name))) fail('unowned partial candidate inventory');
    return;
  }
  if (Object.keys(binding).sort().join(',') !== 'identity,path,receiptId,receiptSha256,treeDigest'
    || !/^[a-f0-9]{64}$/.test(binding.treeDigest) || !/^[a-f0-9]{64}$/.test(binding.receiptSha256)
    || !/^[0-9a-f]{8}-[0-9a-f-]{27}$/i.test(binding.receiptId)
    || binding.path !== path || binding.identity !== recorded.rootIdentity
    || names.join(',') !== 'candidate-attempt.json,candidate-receipt.json,toolchain') fail('candidate exact root inventory changed');
  const receiptBytes = readInventoryReceipt(join(path, 'candidate-receipt.json'));
  if (hash(receiptBytes) !== binding.receiptSha256) fail('candidate receipt changed');
  const receipt = JSON.parse(receiptBytes.toString('utf8')) as Record<string, unknown>;
  const tree = scanOwnedTree(path, 'candidate', true), rows = identities(path, tree);
  // A self-consistent new receipt cannot authenticate changed candidate bytes.
  // Recheck the central original's expected inventory at the final binding/inspection boundary.
  const originalExpected = inspectClaimedDependencyOwnership(handle).layout.toolchainInspection!.expected.rows;
  if (JSON.stringify(toolchainRows(tree.rows)) !== JSON.stringify(originalExpected))
    fail('fixed expected toolchain closure differs at binding');
  const expectedReceipt = { version: 1, kind: 'dependencies', receiptId: binding.receiptId, operationId: handle.operationId,
    repositoryId: handle.repositoryId, claimId: handle.claimId, candidateId: attempt.id, selectionDigest: selected.selectionDigest,
    manifestSha256: selected.targetReleaseSha256, declarationSha256: selected.dependencies!.declarationSha256,
    lockSha256: selected.dependencies!.lockSha256, backupReceiptSha256: selected.dependencies!.backup!.receiptSha256,
    attemptSha256: recorded.sha256, rootIdentity: recorded.rootIdentity, treeDigest: tree.digest,
    entryCount: tree.entries, regularBytes: tree.regularBytes, entries: tree.rows, identities: rows };
  if (tree.digest !== binding.treeDigest || JSON.stringify(receipt) !== JSON.stringify(expectedReceipt)) fail('candidate bytes, modes or identities changed');
  return expectedReceipt;
}

export async function verifyDependencyCandidate(repository: string, handle: MaintenanceHandle) {
  const location = await repositoryIdentity(repository);
  assertDependencyMaintenanceAtLocation(location, handle);
  const store = openDependencyMaintenanceStore(handle.commonDir);
  try {
    const claim = store.readDependencyMaintenance(handle).claim;
    if (!claim.maintenance!.candidate) fail('candidate is not bound');
    verifyDependencyCandidateArtifacts(handle, claim);
    return { operationId: handle.operationId, candidateBound: true as const,
      candidateDigest: claim.maintenance!.candidate.treeDigest, receiptSha256: claim.maintenance!.candidate.receiptSha256 };
  } finally { store.close(); }
}

/** One immutable toolchain-only attempt, under the same exact preparing claim and verified backup. */
export async function prepareDependencyCandidate(requestPath: string, handle: MaintenanceHandle) {
  const initial = inputFacts(requestPath), request = initial.request, location = await repositoryIdentity(request.repository);
  const validate = () => {
    const plan = assertDependencyMaintenanceAtLocation(location, handle);
    if (plan.selectionDigest !== request.dependencySelectionDigest || plan.source.bundleRoot !== request.source.bundleRoot
      || plan.source.manifestSha256 !== request.source.manifestSha256) fail('claimed fixed source selection differs');
    return plan;
  };
  const plan = validate(), store = openDependencyMaintenanceStore(handle.commonDir);
  try {
    let claim = store.readDependencyMaintenance(handle).claim; owned(claim);
    const candidateId = randomUUID(); await store.reserveDependencyCandidateAttempt(handle, candidateId, validate);
    const path = candidatePath(handle); mkdirSync(path, { mode: 0o700 }); flushDirectory(dirname(path));
    claim = store.readDependencyMaintenance(handle).claim; owned(claim);
    const record = attemptFacts(handle, claim, initial.requestSha256, initial);
    const attemptPath = join(path, 'candidate-attempt.json'), sha256 = writePublicationRecord(attemptPath, record), stat = lstatSync(attemptPath);
    await store.bindDependencyCandidateAttempt(handle, { rootIdentity: record.rootIdentity,
      identity: `${stat.dev}:${stat.ino}`, sha256, requestSha256: initial.requestSha256 }, validate);
    const toolchain = join(path, 'toolchain'); mkdirSync(toolchain, { mode: 0o700 });
    for (const name of ['package.json', 'package-lock.json']) fileCopy(join(request.snapshot.bundleRoot, 'toolchain', name), join(toolchain, name));
    const before = inputFacts(requestPath);
    if (JSON.stringify(before) !== JSON.stringify(initial)) fail('authenticated input changed before npm');
    validate(); owned(store.readDependencyMaintenance(handle).claim);
    await runManagedInstallCommand(join(request.snapshot.extractedNodeRoot, 'bin/node'),
      [join(request.snapshot.extractedNodeRoot, 'lib/node_modules/npm/bin/npm-cli.js'), 'ci', '--ignore-scripts', '--no-bin-links',
        '--audit=false', '--fund=false', '--update-notifier=false', '--cache', join(request.stageRoot, 'npm/cache'),
        '--userconfig', join(request.stageRoot, 'npm/user.npmrc'), '--globalconfig', join(request.stageRoot, 'npm/global.npmrc'),
        ...(request.npm.offline ? ['--offline'] : [])], toolchain, npmEnvironment(request.stageRoot));
    normalizeToolchain(join(toolchain, 'node_modules')); validateToolchain(toolchain);
    writePublicationRecord(join(toolchain, 'manifest.json'), { schema: 1, node: '24.22.1', typescript: '7.0.2',
      dependencies: { '@types/node': '24.19.2', typescript: '7.0.2' } });
    const actual = scanOwnedTree(toolchain, 'candidate');
    if (JSON.stringify(actual.rows) !== JSON.stringify(plan.toolchain.expected.rows)) fail('fixed expected toolchain closure differs');
    const after = inputFacts(requestPath);
    if (JSON.stringify(after) !== JSON.stringify(initial)) fail('authenticated input changed after npm');
    validate(); claim = store.readDependencyMaintenance(handle).claim; owned(claim);
    const tree = scanOwnedTree(path, 'candidate', true), receiptId = randomUUID();
    const receipt = { version: 1, kind: 'dependencies', receiptId, operationId: handle.operationId, repositoryId: handle.repositoryId,
      claimId: handle.claimId, candidateId, selectionDigest: claim.maintenance!.selectionDigest,
      manifestSha256: claim.maintenance!.targetReleaseSha256, declarationSha256: claim.maintenance!.dependencies!.declarationSha256,
      lockSha256: claim.maintenance!.dependencies!.lockSha256, backupReceiptSha256: claim.maintenance!.dependencies!.backup!.receiptSha256,
      attemptSha256: sha256, rootIdentity: record.rootIdentity, treeDigest: tree.digest,
      entryCount: tree.entries, regularBytes: tree.regularBytes, entries: tree.rows, identities: identities(path, tree) };
    const receiptSha256 = writeInventoryReceipt(join(path, 'candidate-receipt.json'), receipt);
    const binding = { path, identity: record.rootIdentity, treeDigest: tree.digest, receiptId, receiptSha256 };
    await store.bindDependencyCandidate(handle, binding, () => { validate();
      if (JSON.stringify(inputFacts(requestPath)) !== JSON.stringify(initial)) fail('authenticated inputs changed before binding');
      verifyDependencyCandidateArtifacts(handle, store.readDependencyMaintenance(handle).claim, binding); });
    validate();
    return { ...handle, candidateId, candidatePath: path, candidateDigest: tree.digest, receiptSha256, candidateBound: true as const };
  } finally { store.close(); }
}

/** Private authenticated-bootstrap adapter. Every existing capability remains owned by this one process. */
export async function prepareDependencyCandidateRequest(requestPath: string) {
  const { request } = inputFacts(requestPath), source = { mode: 'repair' as const,
    bundleRoot: request.source.bundleRoot, manifestSha256: request.source.manifestSha256 };
  const plan = await inspectDependencyMaintenanceSelection(request.repository, source);
  if (plan.selectionDigest !== request.dependencySelectionDigest) fail('selected dependency digest changed');
  const handle = await admitDependencyMaintenance(request.repository, source, plan.selectionDigest);
  await prepareDependencyBackup(request.repository, handle);
  const result = await prepareDependencyCandidate(requestPath, handle);
  // Handles/tokens and inventories are intentionally absent from the bootstrap stdout receipt.
  return { operationId: result.operationId, repositoryId: result.repositoryId, claimId: result.claimId,
    candidateDigest: result.candidateDigest, receiptSha256: result.receiptSha256, candidateBound: true as const };
}
