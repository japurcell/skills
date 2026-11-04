import { closeSync, constants, fsyncSync, linkSync, lstatSync, openSync, unlinkSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { atomicPublicationMove } from './atomic-publication.js';
import { readPublicationRecord } from './install-publication-state.js';
import { advanceForwardSchema, assertForwardPublication, inspectForwardSchema, measureMaintenanceStage,
  prepareMaintenanceHandoff, recordMaintenanceStage, resumeForwardSchema, type MaintenanceSelection } from './maintenance.js';
import { runManagedInstallCommand } from './install.js';
import { inspectInstalledUpgrade, readUpgradeInstalledReceipt } from './upgrade-installed.js';
import { inspectUpgradeLayout, readUpgradeIntent, upgradeDirectory, verifyUpgradeMarkerTemplate, writeUpgradeStepReceipt } from './upgrade-publication-state.js';
import { openMaintenanceStore, readCompletedUpgradeForRecovery, type MaintenanceHandle } from './store.js';
import { repositoryIdentity } from './workspace.js';
import { currentOwner, inspectOwner } from './native/process.js';
import type { Owner } from './store.js';

function flush(directory: string): void {
  if (process.platform === 'win32') throw new Error('upgrade publication durability is unqualified on Windows');
  const fd = openSync(directory, constants.O_RDONLY);
  try { fsyncSync(fd); } finally { closeSync(fd); }
}
function markerInfo(common: string, operationId: string) {
  const directory = upgradeDirectory(common, operationId), template = join(directory, 'marker-template.json');
  const marker = join(common, 'factory', 'upgrade-incomplete'), source = lstatSync(template), target = lstatSync(marker);
  if (!source.isFile() || source.isSymbolicLink() || !target.isFile() || target.isSymbolicLink()
    || source.nlink !== 2 || target.nlink !== 2 || source.dev !== target.dev || source.ino !== target.ino)
    throw new Error('upgrade marker ownership differs');
  return { marker, identity: `${source.dev}:${source.ino}` };
}
/** Create only the prebound marker; a foreign existing target is never adopted. */
export function ensureUpgradeMarker(handle: MaintenanceHandle): void {
  const claim = assertForwardPublication(handle), intent = readUpgradeIntent(handle.commonDir, claim);
  verifyUpgradeMarkerTemplate(handle.commonDir, intent);
  const source = join(upgradeDirectory(handle.commonDir, handle.operationId), 'marker-template.json');
  const target = join(handle.commonDir, 'factory', 'upgrade-incomplete');
  try { linkSync(source, target); flush(join(handle.commonDir, 'factory')); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error;
  }
  const marker = markerInfo(handle.commonDir, handle.operationId);
  if (marker.identity !== intent.markerTemplateIdentity) throw new Error('upgrade marker identity differs');
  verifyUpgradeMarkerTemplate(handle.commonDir, intent);
}
async function validateCommands(common: string, stagePath: string): Promise<void> {
  const factory = join(common, 'factory'), node = join(factory, 'install/node/bin/node');
  const npm = join(factory, 'install/node/lib/node_modules/npm/bin/npm-cli.js');
  const tsc = join(factory, 'toolchain/node_modules/typescript/bin/tsc');
  const env = { HOME: stagePath, PATH: '', LANG: 'C', LC_ALL: 'C', NO_COLOR: '1' };
  if ((await runManagedInstallCommand(node, ['--version'], factory, env)).trim() !== 'v24.22.1'
    || (await runManagedInstallCommand(node, [npm, '--version', '--update-notifier=false'], factory, env)).trim() !== '11.19.1'
    || (await runManagedInstallCommand(node, [tsc, '--version'], factory, env)).trim() !== 'Version 7.0.2')
    throw new Error('upgraded installed direct command version differs');
}
/** Commit only a fully moved, verified and receipted operation. */
export async function finishUpgradePublication(repository: string, handle: MaintenanceHandle): Promise<{ state: 'ready'; operationId: string; repositoryId: string }> {
  const location = await repositoryIdentity(repository);
  const original = JSON.parse(readPublicationRecord(join(upgradeDirectory(handle.commonDir, handle.operationId), 'original.json')).toString('utf8')) as { root: string; common: string };
  if (location.common !== handle.commonDir || location.root !== original.root || original.common !== location.common)
    throw new Error('upgrade repository differs');
  let claim = assertForwardPublication(handle), layout = inspectUpgradeLayout(handle.commonDir, claim);
  if (layout.recorded !== 4 || layout.position !== 4) throw new Error('upgrade publication remains incomplete');
  const marker = markerInfo(handle.commonDir, handle.operationId);
  if (marker.identity !== layout.intent.markerTemplateIdentity) throw new Error('upgrade marker identity differs');
  const owned = readUpgradeInstalledReceipt(handle.commonDir, handle.operationId), selected = claim.maintenance!;
  const originalCompletionSha256 = selected.artifactDigests['original-completion'];
  const originalInstalledSha256 = selected.artifactDigests['original-installed'];
  if (!originalInstalledSha256 || !originalCompletionSha256 || !selected.upgradeReceipt || selected.upgradeReceipt.sha256 !== owned.sha256
    || selected.upgradeReceipt.identity !== owned.identity || selected.upgradeReceipt.id !== owned.receipt.receiptId)
    throw new Error('upgrade ownership receipt differs');
  const active = { release: selected.release, completion: { operationId: handle.operationId, repositoryId: handle.repositoryId,
    claimId: handle.claimId, selectionDigest: selected.selectionDigest, manifestSha256: selected.targetReleaseSha256!,
    receiptId: owned.receipt.receiptId, receiptSha256: owned.sha256, receiptIdentity: owned.identity,
    originalInstalledSha256, originalCompletionSha256 } };
  inspectInstalledUpgrade(handle.commonDir, active);
  await validateCommands(handle.commonDir, selected.stagePath);
  if (selected.phase === 'modifying') await recordMaintenanceStage(handle, 'modifying', 'validating');
  claim = assertForwardPublication(handle); layout = inspectUpgradeLayout(handle.commonDir, claim);
  if (layout.recorded !== 4 || layout.position !== 4) throw new Error('upgrade layout changed before completion');
  inspectInstalledUpgrade(handle.commonDir, active);
  const store = openMaintenanceStore(handle.commonDir);
  try { await store.completeUpgrade({ handle, receiptId: owned.receipt.receiptId, receiptSha256: owned.sha256,
    selectionDigest: owned.receipt.selectionDigest, manifestSha256: owned.receipt.manifestSha256 }); }
  finally { store.close(); }
  await recoverCompletedUpgrade(repository, handle.operationId);
  return { state: 'ready', operationId: handle.operationId, repositoryId: handle.repositoryId };
}
/** Ready-before-marker cleanup proves exact committed ownership and actual new bytes first. */
export async function recoverCompletedUpgrade(repository: string, operationId: string,
  clearance?: { operatorConfirmed: boolean; note: string }): Promise<void> {
  const { root, common } = await repositoryIdentity(repository);
  const original = JSON.parse(readPublicationRecord(join(upgradeDirectory(common, operationId), 'original.json')).toString('utf8')) as { root: string; common: string };
  if (root !== original.root || common !== original.common) throw new Error('completed upgrade repository differs');
  const active = readCompletedUpgradeForRecovery(common, operationId);
  const installed = inspectInstalledUpgrade(common, active), receipt = installed.receipt;
  const evidence = active.completion as typeof active.completion & { controllerOwner?: Owner; launcherOwner?: Owner };
  const controller = evidence.controllerOwner, completingLauncher = evidence.launcherOwner;
  if (!controller || typeof controller.host !== 'string' || !Number.isSafeInteger(controller.pid)
    || controller.pid < 1 || typeof controller.start !== 'string' || !controller.start
    || !completingLauncher || typeof completingLauncher.host !== 'string' || !Number.isSafeInteger(completingLauncher.pid)
    || completingLauncher.pid < 1 || typeof completingLauncher.start !== 'string' || !completingLauncher.start)
    throw new Error('completed upgrade controller identity unavailable');
  const current = currentOwner();
  const sameController = controller.host === current.host && controller.pid === current.pid && controller.start === current.start;
  const controllerInspection = inspectOwner(controller), launcherInspection = inspectOwner(completingLauncher),
    originalLauncherInspection = inspectOwner(receipt.launcher);
  if (controllerInspection.state === 'known_live' && !sameController)
    throw new Error('known-live original controller blocks cleanup');
  if (launcherInspection.state === 'known_live' && !(sameController && completingLauncher.pid === process.ppid))
    throw new Error('known-live completing launcher blocks cleanup');
  if (originalLauncherInspection.state === 'known_live' && !(sameController && receipt.launcher.pid === process.ppid))
    throw new Error('known-live original launcher blocks cleanup');
  if (!sameController) {
    if (clearance?.operatorConfirmed !== true || !clearance.note?.trim() || Buffer.byteLength(clearance.note) > 256)
      throw new Error('explicit completed-upgrade clearance required');
    if (controllerInspection.state === 'known_live' || launcherInspection.state === 'known_live' || originalLauncherInspection.state === 'known_live')
      throw new Error('known-live original process blocks cleanup');
    const store = openMaintenanceStore(common);
    try { await store.recordCompletedUpgradeRecovery({ operationId, receiptId: receipt.receiptId, receiptSha256: installed.receiptSha256,
      note: clearance.note, controllerState: controllerInspection.state, controllerLimitation: controllerInspection.limitation,
      launcherState: launcherInspection.state, launcherLimitation: launcherInspection.limitation,
      originalLauncherState: originalLauncherInspection.state, originalLauncherLimitation: originalLauncherInspection.limitation }); }
    finally { store.close(); }
  }
  const stagePath = join(common, 'factory', 'controller-staging', operationId), stage = measureMaintenanceStage(stagePath);
  if (stage.stageDigest !== receipt.stageDigest || stage.stageIdentity !== receipt.stageIdentity)
    throw new Error('completed upgrade stage differs');
  const marker = markerInfo(common, operationId);
  await validateCommands(common, stagePath);
  inspectInstalledUpgrade(common, readCompletedUpgradeForRecovery(common, operationId));
  if (markerInfo(common, operationId).identity !== marker.identity) throw new Error('upgrade marker changed');
  unlinkSync(marker.marker);
  flush(join(common, 'factory'));
}

/** Foreground staged controller for the selected operation, after ticket consumption. */
export async function publishUpgrade(ticketPath: string): Promise<{ state: 'ready'; operationId: string; repositoryId: string }> {
  const raw = JSON.parse(readPublicationRecord(ticketPath).toString('utf8')) as Record<string, unknown>;
  if (typeof raw['operationId'] !== 'string' || typeof raw['repositoryId'] !== 'string' || typeof raw['claimId'] !== 'string'
    || typeof raw['token'] !== 'string' || typeof raw['commonDir'] !== 'string' || typeof raw['root'] !== 'string'
    || ticketPath !== join(raw['commonDir'], 'factory', 'controller-staging', raw['operationId'], 'handoff-ticket.json'))
    throw new Error('upgrade ticket identity invalid');
  const handle: MaintenanceHandle = { operationId: raw['operationId'], repositoryId: raw['repositoryId'],
    claimId: raw['claimId'], token: raw['token'], commonDir: raw['commonDir'] };
  return continueUpgrade(raw['root'], handle);
}

/** Resume the same staged operation using its newly reclaimed owner/token. */
export async function continueUpgrade(repository: string, handle: MaintenanceHandle): Promise<{ state: 'ready'; operationId: string; repositoryId: string }> {
  const initial = assertForwardPublication(handle);
  if (initial.maintenance!.phase === 'validating') return finishUpgradePublication(repository, handle);
  let step = await advanceForwardSchema(handle);
  while (step.shape !== 'v7') step = await advanceForwardSchema(handle);
  ensureUpgradeMarker(handle);
  for (;;) {
    const claim = assertForwardPublication(handle), layout = inspectUpgradeLayout(handle.commonDir, claim);
    if (layout.recorded === 4 && layout.position === 4) break;
    if (layout.position !== layout.recorded && layout.position !== layout.recorded + 1)
      throw new Error('upgrade publication checkpoint differs');
    const factory = join(handle.commonDir, 'factory'), candidate = layout.intent.candidate.path;
    const directory = upgradeDirectory(handle.commonDir, handle.operationId), old = join(directory, 'old');
    const original = JSON.parse(readPublicationRecord(join(directory, 'original.json')).toString('utf8')) as { factoryIdentity: string };
    const steps = [
      { source: join(factory, 'install'), destination: join(old, 'install'), sourceIdentity: layout.intent.oldInstall.identity,
        sourceParentIdentity: original.factoryIdentity, destinationParentIdentity: layout.intent.oldDirectoryIdentity },
      { source: join(candidate, 'install'), destination: join(factory, 'install'), sourceIdentity: layout.intent.newInstall.identity,
        sourceParentIdentity: layout.intent.candidate.identity, destinationParentIdentity: original.factoryIdentity },
      { source: join(factory, 'toolchain'), destination: join(old, 'toolchain'), sourceIdentity: layout.intent.oldToolchain.identity,
        sourceParentIdentity: original.factoryIdentity, destinationParentIdentity: layout.intent.oldDirectoryIdentity },
      { source: join(candidate, 'toolchain'), destination: join(factory, 'toolchain'), sourceIdentity: layout.intent.newToolchain.identity,
        sourceParentIdentity: layout.intent.candidate.identity, destinationParentIdentity: original.factoryIdentity },
    ];
    const selected = steps[layout.recorded];
    if (!selected) throw new Error('invalid upgrade publication step');
    if (layout.position === layout.recorded + 1) {
      flush(dirname(selected.source)); flush(dirname(selected.destination));
      const checked = inspectUpgradeLayout(handle.commonDir, assertForwardPublication(handle));
      if (checked.recorded !== layout.recorded || checked.position !== layout.position)
        throw new Error('upgrade checkpoint changed; evidence retained');
      writeUpgradeStepReceipt(handle.commonDir, checked.intent, checked.recorded);
      continue;
    }
    const binding = { interpreter: layout.intent.atomicBinding.interpreter, helper: layout.intent.atomicBinding.helper };
    const result = await atomicPublicationMove({ ...selected, binding });
    if (result !== 'moved') throw new Error(`upgrade publication move ${result}; evidence retained`);
    flush(dirname(selected.source)); flush(dirname(selected.destination));
    const checked = inspectUpgradeLayout(handle.commonDir, assertForwardPublication(handle));
    if (checked.recorded !== layout.recorded || checked.position !== layout.recorded + 1)
      throw new Error('upgrade publication move identity differs; evidence retained');
    writeUpgradeStepReceipt(handle.commonDir, checked.intent, checked.recorded);
  }
  return finishUpgradePublication(repository, handle);
}

/** Reclaim and finish only an already-consumed operation under explicit operator clearance. */
export async function resumeUpgradePublication(repository: string, operationId: string, selection: MaintenanceSelection,
  clearance: { operatorConfirmed: boolean; note: string }, launcher: Owner): Promise<{ state: 'ready'; operationId: string; repositoryId: string }> {
  const inspected = await inspectForwardSchema(repository, operationId);
  if (!inspected.intent || !['modifying', 'validating'].includes(inspected.intent.phase))
    throw new Error('consumed upgrade operation required');
  const handle = await resumeForwardSchema(repository, operationId, selection, currentOwner(), clearance, launcher);
  return continueUpgrade(repository, handle);
}

/** Reclaim and reissue an unconsumed handoff; the launcher must wait and issue a new exit receipt. */
export async function reissueUpgradeHandoff(repository: string, operationId: string, selection: MaintenanceSelection,
  clearance: { operatorConfirmed: boolean; note: string }, launcher: Owner) {
  const inspected = await inspectForwardSchema(repository, operationId);
  if (!inspected.intent || inspected.intent.phase !== 'handoff-ready') throw new Error('unconsumed upgrade handoff required');
  const handle = await resumeForwardSchema(repository, operationId, selection, currentOwner(), clearance, launcher);
  return prepareMaintenanceHandoff(repository, handle);
}
