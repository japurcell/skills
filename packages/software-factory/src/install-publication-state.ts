import { createHash } from 'node:crypto';
import { closeSync, constants, fstatSync, fsyncSync, lstatSync, openSync, readSync, readdirSync, writeSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { directoryIdentity, readBoundInstallCandidateReceipt, scanOwnedTree, verifyBoundInstallCandidate,
  type CandidateReceipt, type TreeEntry } from './install-candidate.js';
import type { Claim } from './store.js';

const SHA = /^[0-9a-f]{64}$/;
const ID = /^\d+:\d+$/;
const MAX_RECORD = 8192;
export interface PublicationIntent {
  version: 1; operationId: string; repositoryId: string; claimId: string; selectionDigest: string;
  candidateReceiptSha256: string; candidateIdentity: string; installIdentity: string; toolchainIdentity: string;
}
export interface PublicationLayout { receipt: CandidateReceipt; intent: PublicationIntent | null;
  install: 'candidate' | 'published'; toolchain: 'candidate' | 'published' }
function fail(message: string): never { throw new Error(`install publication: ${message}`); }
function absent(path: string): boolean {
  try { lstatSync(path); return false; }
  catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return true; throw error; }
}
function exact(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join(',') !== [...keys].sort().join(','))
    fail('publication record fields invalid');
  return value as Record<string, unknown>;
}
export function publicationIntentPath(common: string, operationId: string): string {
  return join(common, 'factory', `install-publication-${operationId}.json`);
}
export function readPublicationRecord(path: string): Buffer {
  const observed = lstatSync(path);
  if (!observed.isFile() || observed.isSymbolicLink() || observed.nlink !== 1 || observed.size < 1
    || observed.size > MAX_RECORD || (process.platform !== 'win32' && (observed.mode & 0o777) !== 0o600))
    fail('publication record type or bound invalid');
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0));
  try {
    const before = fstatSync(fd);
    if (before.dev !== observed.dev || before.ino !== observed.ino || before.size !== observed.size) fail('publication record identity changed');
    const bytes = Buffer.alloc(before.size);
    for (let offset = 0; offset < bytes.length;) {
      const count = readSync(fd, bytes, offset, bytes.length - offset, offset);
      if (!count) fail('publication record truncated'); offset += count;
    }
    const after = fstatSync(fd), current = lstatSync(path);
    if (after.dev !== before.dev || after.ino !== before.ino || after.mtimeMs !== before.mtimeMs
      || current.dev !== before.dev || current.ino !== before.ino || current.size !== before.size)
      fail('publication record changed while reading');
    return bytes;
  } finally { closeSync(fd); }
}
export function writePublicationRecord(path: string, value: object): string {
  const bytes = Buffer.from(`${JSON.stringify(value)}\n`);
  if (bytes.length < 1 || bytes.length > MAX_RECORD) fail('publication record exceeds bound');
  const fd = openSync(path, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | (constants.O_NOFOLLOW ?? 0), 0o600);
  try { for (let offset = 0; offset < bytes.length;) offset += writeSync(fd, bytes, offset, bytes.length - offset, offset);
    fsyncSync(fd); } finally { closeSync(fd); }
  if (!readPublicationRecord(path).equals(bytes)) fail('publication record changed after write');
  if (process.platform !== 'win32') {
    const directory = openSync(dirname(path), constants.O_RDONLY);
    try { fsyncSync(directory); } finally { closeSync(directory); }
  }
  return createHash('sha256').update(bytes).digest('hex');
}
function subtreeRows(receipt: CandidateReceipt, name: 'install' | 'toolchain'): TreeEntry[] {
  const root = receipt.entries.find(row => row.path === name);
  if (!root || root.type !== 'directory' || root.mode !== 0o700) fail('candidate subtree receipt missing');
  return receipt.entries.filter(row => row.path.startsWith(`${name}/`))
    .map(row => ({ ...row, path: row.path.slice(name.length + 1) }));
}
function verifySubtree(path: string, expectedIdentity: string, rows: TreeEntry[]): void {
  if (directoryIdentity(path) !== expectedIdentity) fail('published subtree identity differs');
  const measured = scanOwnedTree(path, 'candidate');
  if (JSON.stringify(measured.rows) !== JSON.stringify(rows)) fail('published subtree inventory differs');
}
export function verifyPublicationLayout(common: string, claim: Claim): PublicationLayout {
  const recorded = claim.maintenance;
  if (!recorded || recorded.kind !== 'install' || !recorded.candidate || !recorded.targetReleaseSha256)
    fail('bound install claim required');
  const binding = recorded.candidate;
  const expected = { operationId: recorded.operationId, repositoryId: recorded.repositoryId,
    claimId: claim.id, selectionDigest: recorded.selectionDigest, manifestSha256: recorded.targetReleaseSha256 };
  const intentPath = publicationIntentPath(common, recorded.operationId);
  if (absent(intentPath)) {
    const receipt = verifyBoundInstallCandidate(binding, expected);
    if (!absent(join(common, 'factory', 'install')) || !absent(join(common, 'factory', 'toolchain')))
      fail('unowned publication target collision');
    return { receipt, intent: null, install: 'candidate', toolchain: 'candidate' };
  }
  const receipt = readBoundInstallCandidateReceipt(binding, expected);
  const intent = exact(JSON.parse(readPublicationRecord(intentPath).toString('utf8')),
    ['version', 'operationId', 'repositoryId', 'claimId', 'selectionDigest', 'candidateReceiptSha256',
      'candidateIdentity', 'installIdentity', 'toolchainIdentity']) as unknown as PublicationIntent;
  if (intent.version !== 1 || intent.operationId !== recorded.operationId || intent.repositoryId !== recorded.repositoryId
    || intent.claimId !== claim.id || intent.selectionDigest !== recorded.selectionDigest
    || intent.candidateReceiptSha256 !== binding.receiptSha256 || intent.candidateIdentity !== binding.identity
    || !ID.test(intent.installIdentity) || !ID.test(intent.toolchainIdentity) || !SHA.test(binding.receiptSha256)
    || !recorded.ticketConsumed || !['modifying', 'validating'].includes(recorded.phase))
    fail('publication intent differs from claim');
  const positions = {} as { install: 'candidate' | 'published'; toolchain: 'candidate' | 'published' };
  for (const name of ['install', 'toolchain'] as const) {
    const source = join(binding.path, name), target = join(common, 'factory', name);
    const atSource = !absent(source), atTarget = !absent(target);
    if (atSource === atTarget) fail('publication step has missing or conflicting tree');
    positions[name] = atSource ? 'candidate' : 'published';
    verifySubtree(atSource ? source : target, intent[`${name}Identity`], subtreeRows(receipt, name));
  }
  if (positions.toolchain === 'published' && positions.install !== 'published') fail('publication order differs');
  const expectedRoot = ['candidate-receipt.json', ...(['install', 'toolchain'] as const).filter(name => positions[name] === 'candidate')].sort();
  if (JSON.stringify(readdirSync(binding.path).sort()) !== JSON.stringify(expectedRoot)) fail('candidate remainder differs');
  return { receipt, intent, ...positions };
}
