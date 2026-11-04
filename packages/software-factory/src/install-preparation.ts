import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { chmodSync, closeSync, constants, fchmodSync, fstatSync, fsyncSync, lstatSync, mkdirSync, openSync, readSync, readdirSync, realpathSync, statSync, writeSync } from 'node:fs';
import { isAbsolute, join, parse, resolve, sep } from 'node:path';
import { directoryIdentity, type TreeEntry, type TreeEvidence } from './install-candidate.js';
import type { InstallSelection, VerifiedInstallSelection } from './installation-bindings.js';
const SHA = /^[a-f0-9]{64}$/;
const UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
const LOCK_SHA = 'bea7cfb5a835aba203893966dde3e964418b12c69f8680e53a65b3603b9467d6';
const OMIT = ['bin/corepack', 'bin/npm', 'bin/npx'];
const MAX_REQUEST = 64 * 1024, PREPARATION_MS = 240_000;

export interface PreparationRequest {
  python?: { path: string; identity: string; sha256: string; version: string; launcherPid: number };
  dependencySelectionDigest?: string;
  schema: 1; requestId: string; repository: string; npm: { offline: boolean };
  stageRoot: string; stageIdentity: string; source: InstallSelection;
  snapshot: { bundleRoot: string; nodeArchivePath: string; extractedNodeRoot: string;
    nodeTree: { schema: 1; digest: string; entries: number; regularBytes: number; omittedLinks: string[] } };
}
function fail(message: string): never { throw new Error(`install prepare: ${message}`); }
function exact(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== keys.length
    || keys.some(key => !Object.hasOwn(value, key))) fail('unknown or missing private request field');
  return value as Record<string, unknown>;
}
function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonicalJson((value as Record<string, unknown>)[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
export function privateFile(path: string, maximum: number): Buffer {
  const observed = lstatSync(path);
  if (!observed.isFile() || observed.isSymbolicLink() || observed.nlink !== 1 || observed.size < 1 || observed.size > maximum
    || (observed.mode & 0o077) !== 0) fail('private request type, mode or size refused');
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0));
  try {
    const before = fstatSync(fd);
    if (before.dev !== observed.dev || before.ino !== observed.ino || before.size !== observed.size) fail('request identity changed');
    const bytes = Buffer.alloc(before.size);
    for (let offset = 0; offset < bytes.length;) {
      const count = readSync(fd, bytes, offset, bytes.length - offset, offset);
      if (!count) fail('partial private request'); offset += count;
    }
    const after = fstatSync(fd), current = lstatSync(path);
    if (after.mtimeMs !== before.mtimeMs || after.ctimeMs !== before.ctimeMs || current.dev !== before.dev
      || current.ino !== before.ino || current.size !== before.size) fail('private request changed');
    return bytes;
  } finally { closeSync(fd); }
}
function checkedPath(path: unknown, kind: 'file' | 'directory'): string {
  if (typeof path !== 'string' || path.length > 4096 || !isAbsolute(path) || resolve(path) !== path)
    fail('canonical private path required');
  const root = parse(path).root;
  let current: string = root;
  for (const part of path.slice(root.length).split(sep).filter(Boolean)) {
    current = join(current, part);
    const info = lstatSync(current);
    if (info.isSymbolicLink() || (current !== path && !info.isDirectory())) fail('linked private path refused');
  }
  const info = lstatSync(path);
  if ((kind === 'file' && !info.isFile()) || (kind === 'directory' && !info.isDirectory())
    || realpathSync(path) !== path) fail('private path type refused');
  return path;
}
function stageChild(root: string, path: unknown, suffix: string, kind: 'file' | 'directory'): string {
  if (path !== join(root, suffix)) fail('private snapshot path differs');
  return checkedPath(path, kind);
}
export function validateSelectedPython(value: unknown): PreparationRequest['python'] {
  const selected = exact(value, ['path', 'identity', 'sha256', 'version', 'launcherPid']);
  const path = checkedPath(selected.path, 'file');
  const version = typeof selected.version === 'string' ? /^(\d+)\.(\d+)\.(\d+)$/.exec(selected.version) : null;
  if (typeof selected.identity !== 'string' || !/^\d+:\d+$/.test(selected.identity)
    || typeof selected.sha256 !== 'string' || !SHA.test(selected.sha256)
    || !Number.isSafeInteger(selected.launcherPid) || selected.launcherPid !== process.ppid
    || !version || (Number(version[1]) < 3 || (Number(version[1]) === 3 && Number(version[2]) < 11)))
    fail('selected Python binding invalid');
  const observed = lstatSync(path);
  if (observed.nlink !== 1 || observed.size < 1 || observed.size > 128 * 1024 * 1024
    || `${observed.dev}:${observed.ino}` !== selected.identity) fail('selected Python identity differs');
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    const before = fstatSync(fd), digest = createHash('sha256'), buffer = Buffer.alloc(1024 * 1024);
    if (before.dev !== observed.dev || before.ino !== observed.ino) fail('selected Python identity changed');
    for (let count = readSync(fd, buffer, 0, buffer.length, null); count; count = readSync(fd, buffer, 0, buffer.length, null))
      digest.update(buffer.subarray(0, count));
    const after = fstatSync(fd), current = lstatSync(path);
    if (after.dev !== before.dev || after.ino !== before.ino || after.size !== before.size
      || after.mtimeMs !== before.mtimeMs || after.ctimeMs !== before.ctimeMs
      || current.dev !== before.dev || current.ino !== before.ino || current.size !== before.size || current.nlink !== 1
      || current.mtimeMs !== before.mtimeMs || current.ctimeMs !== before.ctimeMs || digest.digest('hex') !== selected.sha256) fail('selected Python bytes changed');
  } finally { closeSync(fd); }
  return selected as unknown as PreparationRequest['python'];
}
export function readPreparationRequest(requestPath: string, purpose: 'install' | 'handoff' | 'dependencies'): PreparationRequest {
  const upgrade = purpose === 'handoff', dependencies = purpose === 'dependencies';
  checkedPath(requestPath, 'file');
  const raw = privateFile(requestPath, MAX_REQUEST);
  const parsed = JSON.parse(raw.toString('utf8')) as unknown;
  // Python emits a fixed canonical JSON form. This also rejects duplicate JSON keys.
  if (raw.toString('utf8') !== `${canonicalJson(parsed)}\n`) fail('noncanonical or duplicate private request');
  const value = exact(parsed, ['schema', 'requestId', 'repository', 'npm', 'stageRoot', 'stageIdentity', 'source', 'snapshot', ...(upgrade ? ['python'] : []), ...(dependencies ? ['dependencySelectionDigest'] : [])]);
  if (dependencies && (typeof value.dependencySelectionDigest !== 'string' || !SHA.test(value.dependencySelectionDigest))) fail('exact dependency selection digest required');
  if (upgrade) validateSelectedPython(value.python);
  if (value.schema !== 1 || typeof value.requestId !== 'string' || !UUID.test(value.requestId)) fail('private request identity invalid');
  const npm = exact(value.npm, ['offline']);
  if (typeof npm.offline !== 'boolean') fail('invalid private npm mode');
  const stageRoot = checkedPath(value.stageRoot, 'directory');
  if (typeof value.stageIdentity !== 'string' || directoryIdentity(stageRoot) !== value.stageIdentity
    || requestPath !== join(stageRoot, dependencies ? 'dependency-preparer-request.json' : 'preparer-request.json')) fail('private stage identity differs');
  const source = exact(value.source, ['bundleRoot', 'manifestSha256', 'nodeArchivePath', ...(Object.hasOwn(value.source as object, 'providers') ? ['providers'] : [])]);
  if (typeof source.bundleRoot !== 'string' || typeof source.nodeArchivePath !== 'string'
    || typeof source.manifestSha256 !== 'string' || !SHA.test(source.manifestSha256)) fail('invalid source selection');
  if (dependencies && Object.hasOwn(source, 'providers')) fail('dependency candidate providers refused');
  const snapshot = exact(value.snapshot, ['bundleRoot', 'nodeArchivePath', 'extractedNodeRoot', 'nodeTree']);
  stageChild(stageRoot, snapshot.bundleRoot, 'bundle', 'directory');
  stageChild(stageRoot, snapshot.nodeArchivePath, 'selected-node-archive', 'file');
  stageChild(stageRoot, snapshot.extractedNodeRoot, 'node', 'directory');
  const nodeTree = exact(snapshot.nodeTree, ['schema', 'digest', 'entries', 'regularBytes', 'omittedLinks']);
  if (nodeTree.schema !== 1 || typeof nodeTree.digest !== 'string' || !SHA.test(nodeTree.digest)
    || !Number.isSafeInteger(nodeTree.entries) || (nodeTree.entries as number) < 1
    || !Number.isSafeInteger(nodeTree.regularBytes) || (nodeTree.regularBytes as number) < 1
    || !Array.isArray(nodeTree.omittedLinks) || nodeTree.omittedLinks.some(link => typeof link !== 'string'))
    fail('invalid extracted Node tree evidence');
  for (const suffix of ['npm', 'npm/cache', 'npm/home']) stageChild(stageRoot, join(stageRoot, suffix), suffix, 'directory');
  for (const suffix of ['npm/user.npmrc', 'npm/global.npmrc']) {
    const config = stageChild(stageRoot, join(stageRoot, suffix), suffix, 'file');
    const info = statSync(config);
    if (info.size !== 0 || info.nlink !== 1 || (info.mode & 0o077) !== 0) fail('npm configuration must be empty and private');
  }
  if (directoryIdentity(stageRoot) !== value.stageIdentity) fail('private stage changed');
  return value as unknown as PreparationRequest;
}
export function sameSelection(a: VerifiedInstallSelection, b: VerifiedInstallSelection): void {
  if (a.bundle.version !== b.bundle.version || a.bundle.platform !== b.bundle.platform
    || a.bundle.manifestSha256 !== b.bundle.manifestSha256 || a.node.sha256 !== b.node.sha256
    || JSON.stringify(a.providers) !== JSON.stringify(b.providers)
    || JSON.stringify(a.windowsHelper?.sha256 ?? null) !== JSON.stringify(b.windowsHelper?.sha256 ?? null))
    fail('original and private selection differ');
}
export function fileCopy(source: string, destination: string, expected?: TreeEntry, mode: 0o600 | 0o700 = 0o600): void {
  const observed = lstatSync(source);
  if (!observed.isFile() || observed.isSymbolicLink() || observed.nlink !== 1 || observed.size > 128 * 1024 * 1024) fail('copy source type or bound refused');
  const input = openSync(source, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    const before = fstatSync(input);
    if (before.dev !== observed.dev || before.ino !== observed.ino || before.size !== observed.size) fail('copy source changed');
    const output = openSync(destination, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | (constants.O_NOFOLLOW ?? 0), mode);
    const digest = createHash('sha256');
    try {
      const buffer = Buffer.allocUnsafe(65536);
      for (let offset = 0; offset < before.size;) {
        const count = readSync(input, buffer, 0, Math.min(buffer.length, before.size - offset), offset);
        if (!count) fail('copy source changed');
        digest.update(buffer.subarray(0, count));
        for (let written = 0; written < count;) written += writeSync(output, buffer, written, count - written);
        offset += count;
      }
      fchmodSync(output, mode); fsyncSync(output);
    } finally { closeSync(output); }
    const after = fstatSync(input), pathInfo = lstatSync(source), target = lstatSync(destination);
    if (after.size !== before.size || after.mtimeMs !== before.mtimeMs || after.ctimeMs !== before.ctimeMs
      || pathInfo.dev !== before.dev || pathInfo.ino !== before.ino || target.size !== before.size
      || (target.mode & 0o777) !== mode || expected?.sha256 && digest.digest('hex') !== expected.sha256)
      fail('copy bytes or identity changed');
  } finally { closeSync(input); }
}
export function flushDirectory(path: string): void {
  const fd = openSync(path, constants.O_RDONLY);
  try { fsyncSync(fd); } finally { closeSync(fd); }
}
export function copyTree(source: string, destination: string, evidence: TreeEvidence): void {
  mkdirSync(destination, { mode: 0o700 });
  for (const row of evidence.rows) {
    const target = join(destination, row.path);
    if (row.type === 'directory') mkdirSync(target, { mode: 0o700 });
    else fileCopy(join(source, row.path), target, row, row.mode === 0o700 ? 0o700 : 0o600);
  }
  for (const row of evidence.rows.filter(row => row.type === 'directory').reverse()) flushDirectory(join(destination, row.path));
  flushDirectory(destination);
}
export function normalizeToolchain(path: string): void {
  let entries = 0, bytes = 0;
  const visit = (directory: string, depth: number) => {
    if (depth > 32) fail('npm tree depth exceeds bound');
    for (const name of readdirSync(directory)) {
      if (++entries > 8192) fail('npm tree entries exceed bound');
      const target = join(directory, name), info = lstatSync(target);
      if (info.isSymbolicLink() || info.isFile() && info.nlink !== 1) fail('npm created a link');
      if (info.isDirectory()) {
        visit(target, depth + 1); chmodSync(target, 0o700);
        const fd = openSync(target, constants.O_RDONLY); try { fsyncSync(fd); } finally { closeSync(fd); }
      } else if (info.isFile()) {
        bytes += info.size;
        if (info.size > 128 * 1024 * 1024 || bytes > 512 * 1024 * 1024) fail('npm tree bytes exceed bound');
        const fd = openSync(target, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
        try { fchmodSync(fd, info.mode & 0o111 ? 0o700 : 0o600); fsyncSync(fd); } finally { closeSync(fd); }
      } else fail('npm created special content');
    }
  };
  visit(path, 0); chmodSync(path, 0o700); flushDirectory(path);
}
/** Internal measured closure seam for the fixed npm and staged self-check commands. */
export async function runManagedInstallCommand(executable: string, args: string[], cwd: string, env: NodeJS.ProcessEnv): Promise<string> {
  if (process.platform === 'win32') fail('Windows preparer closure requires native qualification');
  // Give each fixed tool command a distinct POSIX process group. The direct
  // process may exit after a descendant closes its inherited pipes; group
  // absence is required before binding. Python separately proves this
  // preparer's own group closed before it publishes a public result.
  const child = spawn(executable, args, { cwd, env, detached: true, stdio: ['ignore', 'pipe', 'pipe'], shell: false });
  let output = 0, overflow = false;
  const stdout: Buffer[] = [];
  child.stdout.on('data', (chunk: Buffer) => { output += chunk.length; if (output > 64 * 1024) overflow = true; else stdout.push(chunk); });
  child.stderr.on('data', (chunk: Buffer) => { output += chunk.length; if (output > 64 * 1024) overflow = true; });
  const outcome = await new Promise<{ code: number | null; signal: NodeJS.Signals | null }>((resolveResult, reject) => {
    const timer = setTimeout(() => { if (child.pid) try { process.kill(-child.pid, 'SIGKILL'); } catch { /* closure checked below */ } }, PREPARATION_MS);
    child.once('error', error => { clearTimeout(timer); reject(error); });
    child.once('close', (code, signal) => { clearTimeout(timer); resolveResult({ code, signal }); });
  });
  let groupOpen = false;
  try { process.kill(-child.pid!, 0); groupOpen = true; }
  catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ESRCH') fail('managed process group closure unknown'); }
  if (groupOpen) {
    try { process.kill(-child.pid!, 'SIGKILL'); } catch { /* still refuse; no public success */ }
    fail('managed process group remains');
  }
  if (outcome.code !== 0 || outcome.signal || overflow) fail('managed command failed or closure unknown');
  return Buffer.concat(stdout).toString('utf8');
}
export function npmEnvironment(root: string): NodeJS.ProcessEnv {
  return { HOME: join(root, 'npm/home'), TMPDIR: join(root, 'npm/home'), PATH: '', LANG: 'C', LC_ALL: 'C', NO_COLOR: '1' };
}
export function validateToolchain(toolchain: string): void {
  const lock = JSON.parse(privateFile(join(toolchain, 'package-lock.json'), 128 * 1024).toString('utf8')) as { packages: Record<string, { version?: string }> };
  const declared = Object.keys(lock.packages).filter(name => name.startsWith('node_modules/'));
  if (declared.length < 3 || createHash('sha256').update(privateFile(join(toolchain, 'package-lock.json'), 128 * 1024)).digest('hex') !== LOCK_SHA)
    fail('toolchain lock changed');
  const nodes = readdirSync(join(toolchain, 'node_modules')).filter(name => name !== '.package-lock.json').sort();
  if (JSON.stringify(nodes) !== JSON.stringify(['@types', '@typescript', 'typescript', 'undici-types'])) fail('toolchain package set differs');
  const actual = [join(toolchain, 'node_modules/typescript/package.json'), join(toolchain, 'node_modules/@types/node/package.json')];
  for (const [index, path] of actual.entries()) {
    const version = JSON.parse(privateFile(path, 1024 * 1024).toString('utf8')).version;
    if (version !== (index === 0 ? '7.0.2' : '24.19.2')) fail('toolchain version differs');
  }
}
