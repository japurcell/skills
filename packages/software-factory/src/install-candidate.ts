import { createHash } from 'node:crypto';
import { closeSync, constants, fstatSync, fsyncSync, lstatSync, openSync, readSync, readdirSync, realpathSync, writeSync } from 'node:fs';
import { basename, dirname, join, posix, resolve } from 'node:path';
import type { Stats } from 'node:fs';
import type { CandidateBinding } from './store.js';

const SHA = /^[a-f0-9]{64}$/;
const UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
const MAX_ENTRIES = 8192, MAX_BYTES = 512 * 1024 * 1024, MAX_FILE = 128 * 1024 * 1024;
const MAX_RECEIPT = 8 * 1024 * 1024;
const BAD_PART = /^(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)/i;

export interface TreeEntry { type: 'directory' | 'file'; path: string; mode: number; bytes?: number; sha256?: string }
export interface TreeEvidence { digest: string; entries: number; regularBytes: number; rows: TreeEntry[] }
export interface CandidateReceipt {
  schema: 1; receiptId: string; operationId: string; repositoryId: string; claimId: string;
  selectionDigest: string; manifestSha256: string; nodeArchiveSha256: string; toolchainLockSha256: string;
  omittedLinks: string[]; providers: object; rootIdentity: string; treeDigest: string;
  entries: TreeEntry[];
}

function fail(message: string): never { throw new Error(`install candidate: ${message}`); }
function exact(value: unknown, required: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== required.length
    || required.some(key => !Object.hasOwn(value, key))) fail('unknown or missing record field');
  return value as Record<string, unknown>;
}
function safePath(relative: string): void {
  if (!relative || Buffer.byteLength(relative, 'utf8') > 512 || relative.includes('\\') || relative.startsWith('/')
    || posix.normalize(relative) !== relative || relative.split('/').length > 32
    || relative.split('/').some(part => !part || part === '.' || part === '..' || part.endsWith('.') || part.endsWith(' ')
      || BAD_PART.test(part) || /[\x00-\x1f<>:"|?*]/.test(part))) fail('unsafe inventory path');
}
function fileHash(path: string, observed: Stats): string {
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0));
  try {
    const before = fstatSync(fd);
    if (!before.isFile() || before.nlink !== 1 || before.dev !== observed.dev || before.ino !== observed.ino
      || before.size !== observed.size || before.mtimeMs !== observed.mtimeMs || before.ctimeMs !== observed.ctimeMs)
      fail('file identity changed');
    const digest = createHash('sha256'), buffer = Buffer.allocUnsafe(65536);
    for (let offset = 0; offset < before.size;) {
      const count = readSync(fd, buffer, 0, Math.min(buffer.length, before.size - offset), offset);
      if (!count) fail('file changed during read');
      digest.update(buffer.subarray(0, count)); offset += count;
    }
    const after = fstatSync(fd), current = lstatSync(path);
    if (after.dev !== before.dev || after.ino !== before.ino || after.size !== before.size
      || after.mtimeMs !== before.mtimeMs || after.ctimeMs !== before.ctimeMs
      || current.dev !== before.dev || current.ino !== before.ino || current.size !== before.size
      || current.mtimeMs !== before.mtimeMs || current.ctimeMs !== before.ctimeMs) fail('file changed during read');
    return digest.digest('hex');
  } finally { closeSync(fd); }
}
export function directoryIdentity(path: string): string {
  const info = lstatSync(path);
  if (!info.isDirectory() || info.isSymbolicLink() || info.ino === 0 || realpathSync(path) !== path
    || (process.platform !== 'win32' && (info.mode & 0o777) !== 0o700))
    fail('canonical regular directory required');
  return `${info.dev}:${info.ino}`;
}

/** Fixed byte-and-mode digest shared with the Python extracted-Node scan. */
export function scanOwnedTree(root: string, domain: 'node' | 'candidate', excludeReceipt = false): TreeEvidence {
  if (process.platform === 'win32') fail('Windows tree ownership needs native qualification');
  if (resolve(root) !== root) fail('canonical tree root required');
  const originalIdentity = directoryIdentity(root), rows: TreeEntry[] = [], folded = new Set<string>();
  let regularBytes = 0;
  const visit = (directory: string, prefix: string) => {
    for (const name of readdirSync(directory)) {
      const relative = prefix ? `${prefix}/${name}` : name;
      if (excludeReceipt && relative === 'candidate-receipt.json') continue;
      safePath(relative);
      const fold = relative.toLowerCase();
      if (folded.has(fold)) fail('case-colliding inventory path');
      folded.add(fold);
      const path = join(directory, name), info = lstatSync(path);
      if (info.isSymbolicLink() || info.nlink !== 1 && info.isFile()) fail('linked or hard-linked inventory path');
      const mode = info.mode & 0o777;
      if (info.isDirectory()) {
        if (mode !== 0o700) fail('directory mode differs');
        rows.push({ type: 'directory', path: relative, mode });
        visit(path, relative);
      } else if (info.isFile()) {
        if (mode !== 0o600 && mode !== 0o700) fail('file mode differs');
        if (!Number.isSafeInteger(info.size) || info.size > MAX_FILE) fail('file exceeds bound');
        regularBytes += info.size;
        if (regularBytes > MAX_BYTES) fail('tree bytes exceed bound');
        rows.push({ type: 'file', path: relative, mode, bytes: info.size, sha256: fileHash(path, info) });
      } else fail('special inventory entry');
      if (rows.length > MAX_ENTRIES) fail('tree entries exceed bound');
    }
  };
  visit(root, '');
  rows.sort((a, b) => Buffer.compare(Buffer.from(a.path), Buffer.from(b.path)));
  const digest = createHash('sha256');
  digest.update(domain === 'node' ? 'factory-node-tree-v1\0' : 'factory-candidate-tree-v1\0');
  for (const row of rows) {
    if (row.type === 'directory') digest.update(`D\0${row.path}\0${row.mode.toString(8)}\0`);
    else { digest.update(`F\0${row.path}\0${row.bytes}\0${row.mode.toString(8)}\0`); digest.update(Buffer.from(row.sha256!, 'hex')); }
  }
  if (directoryIdentity(root) !== originalIdentity) fail('tree root identity changed');
  return { digest: digest.digest('hex'), entries: rows.length, regularBytes, rows };
}

function readPrivate(path: string): Buffer {
  const observed = lstatSync(path);
  if (!observed.isFile() || observed.isSymbolicLink() || observed.nlink !== 1 || observed.size < 1
    || observed.size > MAX_RECEIPT || (process.platform !== 'win32' && (observed.mode & 0o077) !== 0)) fail('receipt type, mode or size refused');
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0));
  try {
    const before = fstatSync(fd);
    if (before.dev !== observed.dev || before.ino !== observed.ino || before.size !== observed.size) fail('receipt identity changed');
    const bytes = Buffer.alloc(before.size);
    for (let offset = 0; offset < bytes.length;) {
      const count = readSync(fd, bytes, offset, bytes.length - offset, offset);
      if (!count) fail('partial receipt'); offset += count;
    }
    const after = fstatSync(fd), current = lstatSync(path);
    if (after.mtimeMs !== before.mtimeMs || after.ctimeMs !== before.ctimeMs || current.dev !== before.dev
      || current.ino !== before.ino || current.size !== before.size) fail('receipt changed during read');
    return bytes;
  } finally { closeSync(fd); }
}
export function writeCandidateReceipt(path: string, receipt: CandidateReceipt): string {
  const bytes = Buffer.from(`${JSON.stringify(receipt)}\n`);
  if (bytes.length > MAX_RECEIPT) fail('receipt exceeds parse bound');
  const fd = openSync(path, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | (constants.O_NOFOLLOW ?? 0), 0o600);
  try {
    for (let offset = 0; offset < bytes.length;) offset += writeSync(fd, bytes, offset, bytes.length - offset, offset);
    fsyncSync(fd);
  } finally { closeSync(fd); }
  if (!readPrivate(path).equals(bytes)) fail('written receipt changed');
  const parentFd = openSync(dirname(path), constants.O_RDONLY);
  try { fsyncSync(parentFd); } finally { closeSync(parentFd); }
  return createHash('sha256').update(bytes).digest('hex');
}
export function readBoundInstallCandidateReceipt(binding: CandidateBinding, expected: {
  operationId: string; repositoryId: string; claimId: string; selectionDigest: string; manifestSha256: string;
}): CandidateReceipt {
  if (!binding || typeof binding.path !== 'string' || basename(binding.path) !== `install-candidate-${expected.operationId}`
    || resolve(binding.path) !== binding.path || !/^\d+:\d+$/.test(binding.identity)
    || !SHA.test(binding.treeDigest) || !UUID.test(binding.receiptId) || !SHA.test(binding.receiptSha256)) fail('invalid candidate binding');
  if (directoryIdentity(binding.path) !== binding.identity) fail('candidate root identity changed');
  const bytes = readPrivate(join(binding.path, 'candidate-receipt.json'));
  if (createHash('sha256').update(bytes).digest('hex') !== binding.receiptSha256) fail('candidate receipt hash changed');
  const receipt = exact(JSON.parse(bytes.toString('utf8')), ['schema', 'receiptId', 'operationId', 'repositoryId', 'claimId',
    'selectionDigest', 'manifestSha256', 'nodeArchiveSha256', 'toolchainLockSha256', 'omittedLinks', 'providers', 'rootIdentity', 'treeDigest', 'entries']) as unknown as CandidateReceipt;
  if (receipt.schema !== 1 || receipt.receiptId !== binding.receiptId || receipt.operationId !== expected.operationId
    || receipt.repositoryId !== expected.repositoryId || receipt.claimId !== expected.claimId
    || receipt.selectionDigest !== expected.selectionDigest || receipt.manifestSha256 !== expected.manifestSha256
    || receipt.rootIdentity !== binding.identity || receipt.treeDigest !== binding.treeDigest
    || !SHA.test(receipt.nodeArchiveSha256) || !SHA.test(receipt.toolchainLockSha256)
    || !Array.isArray(receipt.entries) || receipt.entries.length > MAX_ENTRIES || !Array.isArray(receipt.omittedLinks)
    || !receipt.providers || typeof receipt.providers !== 'object' || Array.isArray(receipt.providers)) fail('candidate receipt fields differ');
  return receipt;
}
export function verifyBoundInstallCandidate(binding: CandidateBinding, expected: {
  operationId: string; repositoryId: string; claimId: string; selectionDigest: string; manifestSha256: string;
}): CandidateReceipt {
  const receipt = readBoundInstallCandidateReceipt(binding, expected);
  const rootEntries = readdirSync(binding.path).sort();
  if (JSON.stringify(rootEntries) !== JSON.stringify(['candidate-receipt.json', 'install', 'toolchain'])) fail('candidate root inventory differs');
  const measured = scanOwnedTree(binding.path, 'candidate', true);
  if (measured.digest !== binding.treeDigest || JSON.stringify(measured.rows) !== JSON.stringify(receipt.entries))
    fail('candidate tree differs from receipt');
  return receipt;
}
