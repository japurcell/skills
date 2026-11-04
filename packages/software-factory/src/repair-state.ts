import { createHash } from 'node:crypto';
import { lstatSync } from 'node:fs';
import { join } from 'node:path';
import { directoryIdentity, scanOwnedTree, type CandidateReceipt, type TreeEntry } from './install-candidate.js';
import { readPublicationRecord } from './install-publication-state.js';
import { readRetainedInstalledAuthority } from './installed-state.js';
import { inspectMaintenance, measureMaintenanceStage } from './maintenance.js';
import { inspectOwner } from './native/process.js';
import { readRepairStoreSnapshot, type ActiveInstalledCompletion } from './store.js';
import { inspectUpgradeLayout, upgradeDirectory } from './upgrade-publication-state.js';
import type { OriginalInstallation } from './upgrade-original.js';

export type RepairSourceV1 = { kind: 'installed'; activeCompletionSha256: string; installedReceiptSha256: string }
  | { kind: 'upgrade'; operationId: string; claimId: string; intentSha256: string; committedShape: string;
      priorCompletionSha256: string };
export type ObservedRootV1 = { name: 'install' | 'toolchain'; state: 'absent' }
  | { name: 'install' | 'toolchain'; state: 'present'; identity: string; inventorySha256: string; treeDigest: string };
export interface RepairAuthority {
  source: RepairSourceV1; snapshot: ReturnType<typeof readRepairStoreSnapshot>; factoryIdentity: string;
  candidate: CandidateReceipt; release: string; manifestSha256: string; active: ActiveInstalledCompletion;
  roots: { name: 'install' | 'toolchain'; identity: string; rows: TreeEntry[] }[];
  resume: null | { operationId: string; position: number; recorded: number; owner: ReturnType<typeof inspectOwner>;
    originalLauncher: ReturnType<typeof inspectOwner>; activeLauncher: ReturnType<typeof inspectOwner> | null };
}
export function repairDigest(value: unknown): string {
  return createHash('sha256').update(JSON.stringify(value)).digest('hex');
}
function fail(): never { throw new Error('repair authority refused'); }
function absent(path: string): boolean {
  try { lstatSync(path); return false; } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return true;
    throw error;
  }
}

/** Validate the complete authenticated expected inventory before using any path to observe a live tree. */
function expectedRows(candidate: CandidateReceipt, name: 'install' | 'toolchain'): TreeEntry[] {
  const rows = candidate.entries, owned = new Map<string, TreeEntry>(), folded = new Set<string>();
  if (!Array.isArray(rows) || rows.length < 2 || rows.length > 8192) fail();
  let previous = '', regularBytes = 0;
  const digest = createHash('sha256').update('factory-candidate-tree-v1\0');
  for (const row of rows) {
    if (!row || typeof row.path !== 'string' || !row.path || Buffer.byteLength(row.path) > 512
      || row.path.includes('\\') || row.path.split('/').length > 32
      || Buffer.compare(Buffer.from(previous), Buffer.from(row.path)) >= 0
      || row.path.split('/').some(part => !part || part === '.' || part === '..' || /[. ]$/.test(part)
        || /[\x00-\x1f<>:"|?*]/.test(part) || /^(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)/i.test(part))
      || !['install', 'toolchain'].includes(row.path.split('/')[0]!) || folded.has(row.path.toLowerCase())
      || Object.keys(row).sort().join(',') !== (row.type === 'directory' ? 'mode,path,type' : 'bytes,mode,path,sha256,type')) fail();
    if (row.path.includes('/') && owned.get(row.path.slice(0, row.path.lastIndexOf('/')))?.type !== 'directory') fail();
    if (row.type === 'directory') {
      if (row.mode !== 0o700) fail();
      digest.update(`D\0${row.path}\0${row.mode.toString(8)}\0`);
    } else if (row.type === 'file') {
      if ((row.mode !== 0o600 && row.mode !== 0o700) || !Number.isSafeInteger(row.bytes) || row.bytes! < 0
        || row.bytes! > 128 * 1024 * 1024 || typeof row.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(row.sha256)) fail();
      regularBytes += row.bytes!;
      digest.update(`F\0${row.path}\0${row.bytes}\0${row.mode.toString(8)}\0`).update(Buffer.from(row.sha256, 'hex'));
    } else fail();
    owned.set(row.path, row); folded.add(row.path.toLowerCase()); previous = row.path;
  }
  if (regularBytes > 512 * 1024 * 1024 || digest.digest('hex') !== candidate.treeDigest
    || owned.get('install')?.type !== 'directory' || owned.get('toolchain')?.type !== 'directory') fail();
  return rows.filter(row => row.path.startsWith(`${name}/`)).map(row => ({ ...row, path: row.path.slice(name.length + 1) }));
}

/** Current source union intentionally contains only implemented install/upgrade authority. */
export async function readRepairAuthority(common: string, repository: string): Promise<RepairAuthority> {
  const retained = readRetainedInstalledAuthority(common), snapshot = retained.snapshot;
  const roots = (['install', 'toolchain'] as const).map(name => ({ name,
    identity: retained[`${name}Identity`], rows: expectedRows(retained.candidate, name) }));
  if (!snapshot.claim) return { source: { kind: 'installed',
    activeCompletionSha256: repairDigest(retained.active), installedReceiptSha256: retained.sha256 },
    snapshot, factoryIdentity: retained.factoryIdentity, candidate: retained.candidate, release: retained.receipt.release,
    manifestSha256: retained.receipt.manifestSha256, active: retained.active, roots, resume: null };
  const claim = snapshot.claim!, selected = claim.maintenance!;
  const status = await inspectMaintenance(repository);
  if (status.status !== 'incomplete' || status.claims !== 1 || status.intent?.operationId !== selected.operationId
    || selected.targetSchema !== 7 || !selected.targetReleaseSha256 || !selected.upgradeIntentSha256) fail();
  const original = JSON.parse(readPublicationRecord(join(upgradeDirectory(common, selected.operationId), 'original.json')).toString('utf8')) as OriginalInstallation;
  if (original.root !== repository || original.common !== common || original.repositoryId !== snapshot.repositoryId
    || repairDigest(original.completion) !== repairDigest(snapshot.active.completion)
    || original.receiptSha256 !== retained.sha256 || JSON.stringify(original.receipt) !== JSON.stringify(retained.receipt)) fail();
  const layout = inspectUpgradeLayout(common, claim), stage = measureMaintenanceStage(selected.stagePath);
  if (stage.stageDigest !== selected.stageDigest || stage.stageIdentity !== selected.stageIdentity) fail();
  const candidate = layout.originalCandidate;
  // Damaged interrupted layouts are an IR3 bridge. Only the existing intact resume path is selected here.
  const currentRoots = (['install', 'toolchain'] as const).map(name => {
    const published = name === 'install' ? layout.position >= 2 : layout.position >= 4;
    return published ? { name, identity: name === 'install' ? layout.intent.newInstall.identity : layout.intent.newToolchain.identity,
      rows: expectedRows(candidate, name) } : roots.find(root => root.name === name)!;
  });
  expectedRows(candidate, 'install'); expectedRows(candidate, 'toolchain');
  if (JSON.stringify(readRepairStoreSnapshot(common)) !== JSON.stringify(snapshot)) fail();
  return { source: { kind: 'upgrade', operationId: selected.operationId, claimId: claim.id,
    intentSha256: selected.upgradeIntentSha256, committedShape: snapshot.shape,
    priorCompletionSha256: repairDigest(snapshot.active) }, snapshot, factoryIdentity: retained.factoryIdentity,
    candidate, release: selected.release, manifestSha256: selected.targetReleaseSha256,
    active: retained.active, roots: currentRoots, resume: { operationId: selected.operationId,
      position: layout.position, recorded: layout.recorded, owner: inspectOwner(claim.owner),
      originalLauncher: inspectOwner(original.launcher),
      activeLauncher: selected.activeLauncher ? inspectOwner(selected.activeLauncher) : null } };
}

/** Missing known descendants are damage, while unknown paths, changed kinds and replaced roots refuse. */
export function observeRepairRoots(common: string, authority: RepairAuthority) {
  const factory = join(common, 'factory');
  if (directoryIdentity(factory) !== authority.factoryIdentity) fail();
  const observations: { root: ObservedRootV1; rows: (TreeEntry & { identity: string })[]; missing: string[]; changed: string[] }[] = [];
  let entryCount = 0, byteCount = 0;
  for (const expected of authority.roots) {
    const path = join(factory, expected.name);
    if (absent(path)) {
      observations.push({ root: { name: expected.name, state: 'absent' }, rows: [],
        missing: expected.rows.map(row => row.path), changed: [] });
      continue;
    }
    if (directoryIdentity(path) !== expected.identity) fail();
    const observed = scanOwnedTree(path, 'candidate'), owned = new Map(expected.rows.map(row => [row.path, row]));
    const changed: string[] = [];
    const rows = observed.rows.map(row => {
      const intended = owned.get(row.path);
      if (!intended || intended.type !== row.type || (row.type === 'directory' && row.mode !== intended.mode)) fail();
      if (row.type === 'file' && (intended.mode !== row.mode || intended.bytes !== row.bytes || intended.sha256 !== row.sha256)) changed.push(row.path);
      const info = lstatSync(join(path, row.path));
      if (info.isSymbolicLink() || (row.type === 'file' && (!info.isFile() || info.nlink !== 1 || info.size !== row.bytes))
        || (row.type === 'directory' && !info.isDirectory()) || (info.mode & 0o777) !== row.mode) fail();
      return { ...row, identity: `${info.dev}:${info.ino}` };
    });
    entryCount += rows.length; byteCount += observed.regularBytes;
    if (entryCount > 8192 || byteCount > 512 * 1024 * 1024 || Buffer.byteLength(JSON.stringify(rows)) > 8 * 1024 * 1024) fail();
    const again = scanOwnedTree(path, 'candidate');
    if (JSON.stringify(again) !== JSON.stringify(observed) || directoryIdentity(path) !== expected.identity
      || rows.some(row => { const info = lstatSync(join(path, row.path)); return `${info.dev}:${info.ino}` !== row.identity; })) fail();
    const present = new Set(rows.map(row => row.path));
    observations.push({ root: { name: expected.name, state: 'present', identity: expected.identity,
      inventorySha256: repairDigest(rows), treeDigest: observed.digest }, rows,
      missing: expected.rows.filter(row => !present.has(row.path)).map(row => row.path), changed });
  }
  if (directoryIdentity(factory) !== authority.factoryIdentity) fail();
  if (Buffer.byteLength(JSON.stringify(observations)) > 8 * 1024 * 1024) fail();
  const roots = observations.map(item => item.root);
  const expected = authority.candidate.entries;
  let missingFiles = 0, missingDirectories = 0;
  for (const observation of observations) {
    const missing = new Set(observation.missing);
    for (const row of authority.roots.find(root => root.name === observation.root.name)!.rows) {
      if (!missing.has(row.path)) continue;
      if (row.type === 'file') missingFiles++; else missingDirectories++;
    }
  }
  const damage = authority.resume ? { missingFiles: 0, missingDirectories: 0, changedFiles: 0, absentRoots: 0 }
    : { missingFiles, missingDirectories,
      changedFiles: observations.reduce((count, item) => count + item.changed.length, 0),
      absentRoots: roots.filter(root => root.state === 'absent').length };
  return { roots, damage, expectedInventorySha256: repairDigest(expected), observedInventorySha256: repairDigest(observations) };
}
