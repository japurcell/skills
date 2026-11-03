import { closeSync, constants, fsyncSync, linkSync, lstatSync, openSync, unlinkSync } from 'node:fs';
import { join } from 'node:path';
import { readPublicationRecord } from './install-publication-state.js';
import { assertForwardPublication, measureMaintenanceStage, recordMaintenanceStage } from './maintenance.js';
import { runManagedInstallCommand } from './install.js';
import { inspectInstalledUpgrade, readUpgradeInstalledReceipt } from './upgrade-installed.js';
import { inspectUpgradeLayout, readUpgradeIntent, upgradeDirectory, verifyUpgradeMarkerTemplate } from './upgrade-publication-state.js';
import { openMaintenanceStore, readCompletedUpgradeForRecovery, type MaintenanceHandle } from './store.js';
import { repositoryIdentity } from './workspace.js';

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
export async function recoverCompletedUpgrade(repository: string, operationId: string): Promise<void> {
  const { root, common } = await repositoryIdentity(repository);
  const original = JSON.parse(readPublicationRecord(join(upgradeDirectory(common, operationId), 'original.json')).toString('utf8')) as { root: string; common: string };
  if (root !== original.root || common !== original.common) throw new Error('completed upgrade repository differs');
  const active = readCompletedUpgradeForRecovery(common, operationId);
  const installed = inspectInstalledUpgrade(common, active), receipt = installed.receipt;
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
