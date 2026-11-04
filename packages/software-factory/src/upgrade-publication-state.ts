import { createHash, randomUUID } from 'node:crypto';
import { isAbsolute, join, resolve } from 'node:path';
import { closeSync, constants, fstatSync, lstatSync, openSync, readFileSync, readdirSync } from 'node:fs';
import { directoryIdentity, readBoundInstallCandidateReceipt, scanOwnedTree, verifyBoundInstallCandidate } from './install-candidate.js';
import { readPublicationRecord, writePublicationRecord } from './install-publication-state.js';
import { openMaintenanceStore, type CandidateBinding, type MaintenanceHandle } from './store.js';
import { assertOriginalInstallation, type OriginalInstallation } from './upgrade-original.js';
import { inspectOwnedToolchain, toolchainRows, type OwnedToolchainInspection, type ToolchainInspectionMode } from './owned-toolchain.js';

interface TreeBinding { identity: string; digest: string; entries: number; bytes: number }
interface AtomicBinding { interpreter: { path: string; identity: string; sha256: string }; helper: { path: string; identity: string; sha256: string }; pythonVersion: string; launcher: import('./store.js').Owner }
export interface UpgradeIntent {
  version: 1; operationId: string; repositoryId: string; claimId: string; selectionDigest: string;
  originalSha256: string; backupReceiptSha256: string; candidate: CandidateBinding;
  stageDigest: string; stageIdentity: string; operationIdentity: string; oldDirectoryIdentity: string;
  markerTemplateIdentity: string; markerTemplateSha256: string; atomicBinding: AtomicBinding;
  oldInstall: TreeBinding; oldToolchain: TreeBinding; newInstall: TreeBinding; newToolchain: TreeBinding;
}
function hash(bytes: string | Buffer): string { return createHash('sha256').update(bytes).digest('hex'); }
function tree(path: string): TreeBinding {
  const identity = directoryIdentity(path), result = scanOwnedTree(path, 'candidate');
  return { identity, digest: result.digest, entries: result.entries, bytes: result.regularBytes };
}
export function upgradeDirectory(common: string, operationId: string): string {
  if (!/^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(operationId))
    throw new Error('invalid upgrade operation identity');
  return join(common, 'factory', `upgrade-${operationId}`);
}
/** Bind every move's source identity before the one-use ticket can be prepared. */
export function prepareUpgradeIntent(handle: MaintenanceHandle, candidate: CandidateBinding,
  stage: { stageDigest: string; stageIdentity: string }, atomicBinding: AtomicBinding): { intent: UpgradeIntent; sha256: string; receipt: { id: string; sha256: string; identity: string } } {
  const common = handle.commonDir, directory = upgradeDirectory(common, handle.operationId);
  const original = JSON.parse(readPublicationRecord(join(directory, 'original.json')).toString('utf8')) as OriginalInstallation;
  const store = openMaintenanceStore(common);
  try {
    const claim = store.readMaintenanceClaim(handle.operationId), selected = claim.maintenance!;
    if (claim.id !== handle.claimId || claim.token !== handle.token || claim.resourceKey !== handle.repositoryId
      || selected.kind !== 'upgrade' || selected.phase !== 'preparing' || !selected.forward?.backup
      || !selected.targetReleaseSha256 || selected.candidate || selected.stageDigest || selected.stageIdentity
      || JSON.stringify(atomicBinding.launcher) !== JSON.stringify(original.launcher)
      || selected.artifactDigests['original-installed'] !== hash(JSON.stringify(original)))
      throw new Error('upgrade intent claim or original evidence differs');
    assertOriginalInstallation(common, original);
    verifyBoundInstallCandidate(candidate, { operationId: handle.operationId, repositoryId: handle.repositoryId,
      claimId: handle.claimId, selectionDigest: selected.selectionDigest, manifestSha256: selected.targetReleaseSha256 });
    const templatePath = join(directory, 'marker-template.json');
    const markerTemplateSha256 = writePublicationRecord(templatePath, { version: 1, operationId: handle.operationId,
      repositoryId: handle.repositoryId, claimId: handle.claimId, selectionDigest: selected.selectionDigest,
      originalSha256: selected.artifactDigests['original-installed'], candidateReceiptSha256: candidate.receiptSha256 });
    const markerFile = lstatSync(templatePath);
    if (!markerFile.isFile() || markerFile.isSymbolicLink() || markerFile.nlink !== 1)
      throw new Error('upgrade marker template identity invalid');
    const markerTemplateIdentity = `${markerFile.dev}:${markerFile.ino}`;
    const intent: UpgradeIntent = { version: 1, operationId: handle.operationId, repositoryId: handle.repositoryId,
      claimId: handle.claimId, selectionDigest: selected.selectionDigest, markerTemplateIdentity, markerTemplateSha256,
      originalSha256: selected.artifactDigests['original-installed']!, backupReceiptSha256: selected.forward.backup.receiptSha256,
      candidate, ...stage, atomicBinding, operationIdentity: directoryIdentity(directory), oldDirectoryIdentity: directoryIdentity(join(directory, 'old')),
      oldInstall: original.install, oldToolchain: original.toolchain,
      newInstall: tree(join(candidate.path, 'install')), newToolchain: tree(join(candidate.path, 'toolchain')) };
    const sha256 = writePublicationRecord(join(directory, 'intent.json'), intent);
    const receiptPath = join(directory, 'new-receipt.json'), receiptId = randomUUID();
    const receiptSha256 = writePublicationRecord(receiptPath, { version: 1, kind: 'upgrade', receiptId,
      operationId: handle.operationId, repositoryId: handle.repositoryId, claimId: handle.claimId,
      release: selected.release, targetSchema: selected.targetSchema, selectionDigest: selected.selectionDigest,
      manifestSha256: selected.targetReleaseSha256, candidate, ...stage, intentSha256: sha256,
      originalSha256: intent.originalSha256, backupReceiptSha256: intent.backupReceiptSha256, launcher: atomicBinding.launcher,
      authoring: original.receipt.authoring });
    const receiptInfo = lstatSync(receiptPath);
    if (!receiptInfo.isFile() || receiptInfo.isSymbolicLink() || receiptInfo.nlink !== 1)
      throw new Error('upgrade receipt identity invalid');
    return { intent, sha256, receipt: { id: receiptId, sha256: receiptSha256, identity: `${receiptInfo.dev}:${receiptInfo.ino}` } };
  } finally { store.close(); }
}

const STEP_NAMES = ['01-old-install', '02-new-install', '03-old-toolchain', '04-new-toolchain'] as const;
/** The retained template authenticates its own marker link, independently of another operation's marker. */
function readUpgradeMarkerTemplate(common: string, intent: UpgradeIntent): number {
  const path = join(upgradeDirectory(common, intent.operationId), 'marker-template.json');
  const before = lstatSync(path);
  if (!before.isFile() || before.isSymbolicLink() || ![1, 2].includes(before.nlink)
    || `${before.dev}:${before.ino}` !== intent.markerTemplateIdentity || before.size > 8192
    || (process.platform !== 'win32' && (before.mode & 0o777) !== 0o600))
    throw new Error('upgrade marker template changed');
  const marker = join(common, 'factory', 'upgrade-incomplete');
  if (before.nlink === 2) {
    const linked = lstatSync(marker);
    if (!linked.isFile() || linked.isSymbolicLink() || linked.dev !== before.dev || linked.ino !== before.ino || linked.nlink !== 2)
      throw new Error('upgrade marker link differs');
  }
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    const opened = fstatSync(fd), bytes = readFileSync(fd), after = fstatSync(fd), current = lstatSync(path);
    if (opened.dev !== before.dev || opened.ino !== before.ino || after.dev !== before.dev || after.ino !== before.ino
      || current.dev !== before.dev || current.ino !== before.ino || after.size !== before.size
      || current.nlink !== before.nlink || hash(bytes) !== intent.markerTemplateSha256)
      throw new Error('upgrade marker template changed while reading');
  } finally { closeSync(fd); }
  return before.nlink;
}

export function verifyUpgradeMarkerTemplate(common: string, intent: UpgradeIntent): void {
  if (readUpgradeMarkerTemplate(common, intent) === 1 && !absent(join(common, 'factory', 'upgrade-incomplete')))
    throw new Error('foreign upgrade marker exists');
}

/** Retained metadata cannot validate the global layout of a different, current operation. */
function readUpgradeIntentAuthority(common: string, claim: import('./store.js').Claim): UpgradeIntent {
  const selected = claim.maintenance;
  if (!selected || selected.kind !== 'upgrade' || !selected.candidate || !selected.upgradeIntentSha256 || !selected.upgradeReceipt
    || !selected.forward?.backup || !selected.targetReleaseSha256) throw new Error('upgrade publication intent unbound');
  const directory = upgradeDirectory(common, selected.operationId);
  const bytes = readPublicationRecord(join(directory, 'intent.json'));
  if (hash(bytes) !== selected.upgradeIntentSha256) throw new Error('upgrade publication intent changed');
  const intent = JSON.parse(bytes.toString('utf8')) as UpgradeIntent;
  const original = JSON.parse(readPublicationRecord(join(directory, 'original.json')).toString('utf8')) as OriginalInstallation;
  if (intent.version !== 1 || intent.operationId !== selected.operationId || intent.repositoryId !== selected.repositoryId
    || intent.claimId !== claim.id || intent.selectionDigest !== selected.selectionDigest
    || intent.originalSha256 !== selected.artifactDigests['original-installed']
    || intent.backupReceiptSha256 !== selected.forward.backup.receiptSha256
    || intent.stageDigest !== selected.stageDigest || intent.stageIdentity !== selected.stageIdentity
    || !intent.atomicBinding || !intent.atomicBinding.interpreter || !intent.atomicBinding.helper
    || !isAbsolute(intent.atomicBinding.interpreter.path) || resolve(intent.atomicBinding.interpreter.path) !== intent.atomicBinding.interpreter.path
    || !/^\d+:\d+$/.test(intent.atomicBinding.interpreter.identity) || !/^[a-f0-9]{64}$/.test(intent.atomicBinding.interpreter.sha256)
    || intent.atomicBinding.helper.path !== join(common, 'factory', 'controller-staging', intent.operationId, 'payload', 'native', 'atomic-publication.py')
    || !/^\d+:\d+$/.test(intent.atomicBinding.helper.identity) || !/^[a-f0-9]{64}$/.test(intent.atomicBinding.helper.sha256)
    || !/^\d+\.\d+\.\d+$/.test(intent.atomicBinding.pythonVersion)
    || JSON.stringify(intent.atomicBinding.launcher) !== JSON.stringify(original.launcher)
    || JSON.stringify(intent.candidate) !== JSON.stringify(selected.candidate)
    || intent.operationIdentity !== directoryIdentity(directory)
    || intent.oldDirectoryIdentity !== directoryIdentity(join(directory, 'old'))
    || directoryIdentity(join(common, 'factory')) !== original.factoryIdentity
    || hash(JSON.stringify(original)) !== intent.originalSha256)
    throw new Error('upgrade publication intent differs from claim');
  const receiptPath = join(directory, 'new-receipt.json'), receiptInfo = lstatSync(receiptPath);
  const receiptBytes = readPublicationRecord(receiptPath), receiptAfter = lstatSync(receiptPath);
  const receipt = JSON.parse(receiptBytes.toString('utf8')) as Record<string, unknown>;
  if (`${receiptInfo.dev}:${receiptInfo.ino}` !== selected.upgradeReceipt.identity || receiptInfo.nlink !== 1
    || receiptAfter.dev !== receiptInfo.dev || receiptAfter.ino !== receiptInfo.ino || receiptAfter.nlink !== 1
    || hash(receiptBytes) !== selected.upgradeReceipt.sha256 || receipt['receiptId'] !== selected.upgradeReceipt.id
    || receipt['intentSha256'] !== selected.upgradeIntentSha256) throw new Error('upgrade receipt binding differs');
  readUpgradeMarkerTemplate(common, intent);
  return intent;
}

/** Verify the immutable intent and current operation marker before publication. */
export function readUpgradeIntent(common: string, claim: import('./store.js').Claim): UpgradeIntent {
  const intent = readUpgradeIntentAuthority(common, claim);
  verifyUpgradeMarkerTemplate(common, intent);
  return intent;
}

function absent(path: string): boolean {
  try { lstatSync(path); return false; }
  catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return true; throw error; }
}
function sameTree(path: string, expected: TreeBinding): boolean {
  try { return JSON.stringify(tree(path)) === JSON.stringify(expected); } catch { return false; }
}
function expectedReceipt(intent: UpgradeIntent, index: number) {
  const trees = [intent.oldInstall, intent.newInstall, intent.oldToolchain, intent.newToolchain];
  return { version: 1, operationId: intent.operationId, step: STEP_NAMES[index], tree: trees[index] };
}
/** Authenticate only the retained intent, template, ordered receipts and candidate receipt. */
export function readUpgradePublicationAuthority(common: string, claim: import('./store.js').Claim) {
  const intent = readUpgradeIntentAuthority(common, claim), directory = upgradeDirectory(common, intent.operationId);
  const names = readdirSync(directory).sort(), allowed = ['intent.json', 'old', 'original.json', 'marker-template.json', 'new-receipt.json',
    ...STEP_NAMES.map(name => `${name}.json`)];
  if (names.some(name => !allowed.includes(name))) throw new Error('unowned upgrade operation entry');
  let recorded = 0;
  for (let i = 0; i < STEP_NAMES.length; i++) {
    const path = join(directory, `${STEP_NAMES[i]}.json`), exists = !absent(path);
    if (!exists) continue;
    if (recorded !== i || JSON.stringify(JSON.parse(readPublicationRecord(path).toString('utf8'))) !== JSON.stringify(expectedReceipt(intent, i)))
      throw new Error('upgrade step receipt differs or is out of order');
    recorded++;
  }
  const originalCandidate = readBoundInstallCandidateReceipt(intent.candidate, { operationId: intent.operationId,
    repositoryId: intent.repositoryId, claimId: intent.claimId, selectionDigest: intent.selectionDigest,
    manifestSha256: claim.maintenance!.targetReleaseSha256! });
  return { intent, originalCandidate, recorded };
}

/** Exact ordered state includes a single rename that may have completed before its receipt. */
export function inspectUpgradeLayout(common: string, claim: import('./store.js').Claim,
  toolchainMode: ToolchainInspectionMode = { purpose: 'strict' }) {
  const { intent, originalCandidate, recorded } = readUpgradePublicationAuthority(common, claim);
  verifyUpgradeMarkerTemplate(common, intent);
  const directory = upgradeDirectory(common, intent.operationId);
  if (toolchainMode.purpose === 'dependency-repair' && recorded !== 4)
    throw new Error('repair inspection requires fully receipted published upgrade');
  const factory = join(common, 'factory'), candidate = intent.candidate.path, old = join(directory, 'old');
  let toolchainInspection: OwnedToolchainInspection | undefined;
  const valid = (step: number) => {
    const oldInstall = join(step >= 1 ? old : factory, 'install');
    const newInstall = join(step >= 2 ? factory : candidate, 'install');
    const oldToolchain = join(step >= 3 ? old : factory, 'toolchain');
    const newToolchain = join(step >= 4 ? factory : candidate, 'toolchain');
    if (!sameTree(oldInstall, intent.oldInstall) || !sameTree(newInstall, intent.newInstall)
      || !sameTree(oldToolchain, intent.oldToolchain)) return false;
    try {
      toolchainInspection = inspectOwnedToolchain(newToolchain, intent.newToolchain.identity,
        toolchainRows(originalCandidate.entries), toolchainMode);
      if (toolchainMode.purpose === 'strict' && (toolchainInspection.observed.digest !== intent.newToolchain.digest
        || toolchainInspection.observed.entries !== intent.newToolchain.entries
        || toolchainInspection.observed.regularBytes !== intent.newToolchain.bytes)) return false;
    } catch { return false; }
    const candidateNames = ['candidate-receipt.json', ...(step < 2 ? ['install'] : []), ...(step < 4 ? ['toolchain'] : [])].sort();
    const oldNames = [...(step >= 1 ? ['install'] : []), ...(step >= 3 ? ['toolchain'] : [])].sort();
    return JSON.stringify(readdirSync(candidate).sort()) === JSON.stringify(candidateNames)
      && JSON.stringify(readdirSync(old).sort()) === JSON.stringify(oldNames);
  };
  let position: number;
  if (valid(recorded)) position = recorded;
  else if (recorded < 4 && valid(recorded + 1)) position = recorded + 1;
  else throw new Error('upgrade layout identity or ordered position differs');
  return { intent, originalCandidate, recorded, position, toolchainInspection };
}

export function writeUpgradeStepReceipt(common: string, intent: UpgradeIntent, index: number): void {
  if (!Number.isInteger(index) || index < 0 || index >= STEP_NAMES.length) throw new Error('invalid upgrade step');
  writePublicationRecord(join(upgradeDirectory(common, intent.operationId), `${STEP_NAMES[index]}.json`), expectedReceipt(intent, index));
}
