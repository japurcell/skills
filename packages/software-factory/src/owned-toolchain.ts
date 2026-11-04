import { directoryIdentity, scanOwnedTree, type TreeEntry, type TreeEvidence } from './install-candidate.js';

export type ToolchainInspectionMode = { readonly purpose: 'strict' } | { readonly purpose: 'dependency-repair' };
export interface OwnedToolchainInspection {
  identity: string;
  expected: { rows: TreeEntry[] };
  observed: TreeEvidence;
  missing: string[];
  changed: string[];
}

/** Receipt-owned subtree rows, without confusing missing files with missing ownership. */
export function toolchainRows(entries: readonly TreeEntry[]): TreeEntry[] {
  const root = entries.find(row => row.path === 'toolchain');
  if (!root || root.type !== 'directory' || root.mode !== 0o700) throw new Error('owned toolchain root record missing');
  return entries.filter(row => row.path.startsWith('toolchain/')).map(row => ({ ...row, path: row.path.slice(10) }));
}

/** Only known regular file byte damage or absence can be selected for later repair. */
export function inspectOwnedToolchain(path: string, identity: string, rows: TreeEntry[],
  mode: ToolchainInspectionMode = { purpose: 'strict' }): OwnedToolchainInspection {
  if (directoryIdentity(path) !== identity) throw new Error('owned toolchain root identity differs');
  const expected = new Map<string, TreeEntry>();
  let previous = '', bytes = 0;
  if (!Array.isArray(rows) || rows.length < 1 || rows.length > 8192) throw new Error('owned toolchain inventory bound differs');
  for (const row of rows) {
    if (!row || typeof row.path !== 'string' || !row.path || row.path.includes('\\') || row.path.startsWith('/')
      || row.path.split('/').some(part => !part || part === '.' || part === '..')
      || Buffer.byteLength(row.path) > 512 || Buffer.compare(Buffer.from(previous), Buffer.from(row.path)) >= 0
      || !['directory', 'file'].includes(row.type)
      || Object.keys(row).sort().join(',') !== (row.type === 'file' ? 'bytes,mode,path,sha256,type' : 'mode,path,type')
      || row.mode !== 0o700 && (row.type !== 'file' || row.mode !== 0o600)
      || row.type === 'file' && (!Number.isSafeInteger(row.bytes) || row.bytes! < 0 || row.bytes! > 128 * 1024 * 1024
        || typeof row.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(row.sha256)))
      throw new Error('owned toolchain inventory row invalid');
    const parent = row.path.slice(0, row.path.lastIndexOf('/'));
    if (row.path.includes('/') && expected.get(parent)?.type !== 'directory') throw new Error('owned toolchain parent record missing');
    expected.set(row.path, row); previous = row.path;
    if (row.type === 'file') bytes += row.bytes!;
  }
  if (bytes > 512 * 1024 * 1024) throw new Error('owned toolchain inventory byte bound differs');
  const observed = scanOwnedTree(path, 'candidate'), present = new Set<string>(), changed: string[] = [], missing: string[] = [];
  for (const row of observed.rows) {
    const owned = expected.get(row.path);
    if (!owned || owned.type !== row.type || owned.mode !== row.mode) throw new Error('unowned or incompatible toolchain entry');
    present.add(row.path);
    if (row.type === 'file' && (owned.bytes !== row.bytes || owned.sha256 !== row.sha256)) changed.push(row.path);
  }
  for (const row of rows) if (!present.has(row.path)) {
    if (row.type !== 'file') throw new Error('owned toolchain directory missing');
    missing.push(row.path);
  }
  if (mode.purpose !== 'dependency-repair' && (missing.length || changed.length)) throw new Error('owned toolchain inventory differs');
  if (directoryIdentity(path) !== identity) throw new Error('owned toolchain root changed during inspection');
  return { identity, expected: { rows }, observed, missing, changed };
}
