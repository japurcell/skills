import { createHash } from 'node:crypto';
import { lstatSync, realpathSync } from 'node:fs';
import { dirname, isAbsolute, join, resolve } from 'node:path';
import { readPublicationRecord } from './install-publication-state.js';
import { selectUpgradeProviders, validateInstallSelection, type InstallSelection } from './installation-bindings.js';
import { selectionFrom, validateSelectedPython } from './install.js';
import { inspectMaintenance } from './maintenance.js';
import { readUpgradeInstalledReceipt } from './upgrade-installed.js';
import { recoverCompletedUpgrade, reissueUpgradeHandoff, resumeUpgradePublication } from './upgrade-publication.js';
import { upgradeDirectory } from './upgrade-publication-state.js';
import { repositoryIdentity } from './workspace.js';
import { currentOwner, inspectOwner } from './native/process.js';
import type { Owner } from './store.js';

function hash(value: string) { return createHash('sha256').update(value).digest('hex'); }
function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('invalid upgrade recovery request');
  return value as Record<string, unknown>;
}
/** Called only by the staged controller on a private request from the authenticated launcher. */
export async function resumeUpgradeRequest(requestPath: string, stagePath: string) {
  if (!isAbsolute(requestPath) || resolve(requestPath) !== requestPath || realpathSync(requestPath) !== requestPath)
    throw new Error('invalid recovery request path');
  const parent = lstatSync(dirname(requestPath));
  if (!parent.isDirectory() || parent.isSymbolicLink() || (process.platform !== 'win32' && (parent.mode & 0o777) !== 0o700))
    throw new Error('recovery request directory is not private');
  const raw = object(JSON.parse(readPublicationRecord(requestPath).toString('utf8')));
  if (Object.keys(raw).sort().join(',') !== 'note,operationId,operatorConfirmed,python,repository,target,version'
    || raw['version'] !== 1 || raw['operatorConfirmed'] !== true || typeof raw['note'] !== 'string'
    || !raw['note'].trim() || Buffer.byteLength(raw['note']) > 256 || typeof raw['repository'] !== 'string'
    || typeof raw['operationId'] !== 'string' || !/^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(raw['operationId']))
    throw new Error('explicit bounded upgrade recovery request required');
  const python = validateSelectedPython(raw['python'])!, launcher = currentOwner(python.launcherPid);
  if (inspectOwner(launcher).state !== 'known_live') throw new Error('recovery launcher identity unavailable');
  const repository = raw['repository'], operationId = raw['operationId'], { root, common } = await repositoryIdentity(repository);
  if (stagePath !== join(common, 'factory', 'controller-staging', operationId)) throw new Error('upgrade recovery stage differs');
  const directory = upgradeDirectory(common, operationId);
  const original = object(JSON.parse(readPublicationRecord(join(directory, 'original.json')).toString('utf8')));
  if (original['root'] !== root || original['common'] !== common) throw new Error('upgrade recovery repository differs');
  const originalLauncher = original['launcher'] as Owner;
  if (!originalLauncher || inspectOwner(originalLauncher).state === 'known_live') throw new Error('known-live original launcher blocks recovery');
  const ticket = object(JSON.parse(readPublicationRecord(join(stagePath, 'handoff-ticket.json')).toString('utf8')));
  if (ticket['version'] !== 1 || ticket['operationId'] !== operationId || ticket['root'] !== root || ticket['commonDir'] !== common
    || ticket['stagePath'] !== stagePath || typeof ticket['selectionDigest'] !== 'string') throw new Error('upgrade recovery ticket differs');
  const target = object(raw['target']) as unknown as InstallSelection;
  const providers = selectUpgradeProviders(original['providers'], target.providers);
  const selected = validateInstallSelection({ ...target, ...(providers !== undefined ? { providers } : {}) });
  const selection = selectionFrom(selected);
  selection.artifactDigests['original-installed'] = hash(JSON.stringify(original));
  selection.artifactDigests['original-completion'] = hash(JSON.stringify(original['completion']));
  if (selection.selectionDigest !== ticket['selectionDigest'] || selection.targetReleaseSha256 !== ticket['targetReleaseSha256'])
    throw new Error('upgrade recovery target selection differs');
  const clearance = { operatorConfirmed: true, note: raw['note'] };
  const status = await inspectMaintenance(root);
  if (status.status !== 'incomplete') throw new Error('upgrade recovery operation is not incomplete');
  if (status.claims === 0 && status.marker === 'upgrade') {
    const receipt = readUpgradeInstalledReceipt(common, operationId).receipt;
    if (receipt.manifestSha256 !== selection.targetReleaseSha256 || receipt.selectionDigest !== selection.selectionDigest)
      throw new Error('completed upgrade target differs');
    await recoverCompletedUpgrade(root, operationId, clearance);
    return { state: 'ready' as const, operationId, repositoryId: receipt.repositoryId };
  }
  if (!('intent' in status) || !status.intent || status.intent.operationId !== operationId)
    throw new Error('upgrade recovery claim differs');
  if (status.intent.phase === 'handoff-ready') return { state: 'handoff-ready' as const,
    ...await reissueUpgradeHandoff(root, operationId, selection, clearance, launcher) };
  if (status.intent.phase === 'modifying' || status.intent.phase === 'validating')
    return resumeUpgradePublication(root, operationId, selection, clearance, launcher);
  throw new Error('preparing upgrade requires explicit abandonment');
}
