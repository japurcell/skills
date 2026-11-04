// Qualification only. Frozen source and externally trusted host prerequisites apply.
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { closeSync, fstatSync, lstatSync, mkdirSync, openSync, readSync, realpathSync, writeFileSync } from 'node:fs';
import { captureMetadataProcess, validateControllerSelection, validateSdkRegistrationMetadataWire } from './windows-storage-loader-metadata.mjs';

const selectionSha256 = '10f2bd54b5e47122e4d5283ba83a72e776ba3b87fdf74d8eb68d02908257bf98';
const sourceCommit = '5405a163b4e591705f9888440ec5cb8933c48d2c';
const nodeSha256 = 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5';
const fail = () => { throw new Error('metadata-collection'); };

export function validateCollectionSelection(bytes) {
  if (!Buffer.isBuffer(bytes) || bytes.length !== 1540 ||
      createHash('sha256').update(bytes).digest('hex') !== selectionSha256) fail();
  const selected = validateControllerSelection(bytes);
  if (selected.sourceCommit !== sourceCommit) fail();
  return selected;
}

function validateResult(bytes, exitCode) {
  const value = validateSdkRegistrationMetadataWire(bytes, selectionSha256);
  if (exitCode !== (value.state === 'observed' ? 0 : 1) ||
      value.host.windowsVersion !== '10.0.26100.0' || value.host.powershellVersion !== '5.1.26100.33648') fail();
  return value;
}

// Already-created inert child seam only; no caller-selected executable or mode.
export async function observeCollectionProcess(child, options = {}) {
  if (Object.keys(options).some(key => key !== 'deadlineMs')) fail();
  const captured = await captureMetadataProcess(child, { ...options, exitCodes: [0, 1] });
  if (captured.state !== 'captured') fail();
  validateResult(captured.bytes, captured.exitCode);
  return { bytes: captured.bytes, exitCode: captured.exitCode };
}

const captureDiagnostics = Object.freeze({
  deadline: 'metadata-refused-outer-deadline', exit: 'metadata-refused-outer-exit',
  eof: 'metadata-refused-outer-eof', stderr: 'metadata-refused-outer-stderr',
  bounds: 'metadata-refused-outer-bounds', process: 'metadata-refused-outer-process',
});
const innerDiagnostics = Object.freeze({
  deadline: 'metadata-refused-inner-deadline', exit: 'metadata-refused-inner-exit',
  eof: 'metadata-refused-inner-eof', stderr: 'metadata-refused-inner-stderr',
  bounds: 'metadata-refused-inner-bounds', process: 'metadata-refused-inner-process',
  protocol: 'metadata-refused-inner-protocol', changed: 'metadata-refused-inner-changed',
});

// Classifies an already-created child. It neither starts a process nor admits files.
export async function classifyCollectionProcess(child, options = {}) {
  if (Object.keys(options).some(key => key !== 'deadlineMs')) fail();
  const captured = await captureMetadataProcess(child, { ...options, exitCodes: [0, 1] });
  if (captured.state !== 'captured') return { diagnostic: captureDiagnostics[captured.reason] ?? 'metadata-refused-prerequisite' };
  try {
    const value = JSON.parse(captured.bytes.toString('utf8'));
    const keys = ['scope', 'state', 'reason', 'selectionAuthority', 'buildAuthority', 'nativeAuthority'];
    if (value && typeof value === 'object' && !Array.isArray(value) &&
        Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key)) &&
        captured.bytes.toString('utf8') === `${JSON.stringify({ scope: value.scope, state: value.state, reason: value.reason,
          selectionAuthority: value.selectionAuthority, buildAuthority: value.buildAuthority, nativeAuthority: value.nativeAuthority })}\n` && captured.exitCode === 1 &&
        value.scope === 'windows-storage-loader-metadata' && value.state === 'blocked' &&
        value.selectionAuthority === false && value.buildAuthority === false && value.nativeAuthority === false &&
        typeof value.reason === 'string' && Object.hasOwn(innerDiagnostics, value.reason)) return { diagnostic: innerDiagnostics[value.reason] };
    validateResult(captured.bytes, captured.exitCode);
    return { bytes: captured.bytes, exitCode: captured.exitCode };
  } catch {
    return { diagnostic: 'metadata-refused-wire' };
  }
}

function nonReparse(path) {
  let current = resolve(path);
  for (let depth = 0; depth < 64; depth++) {
    if (lstatSync(current).isSymbolicLink()) fail();
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
    if (depth === 63) fail();
  }
  if (realpathSync.native(path).toLowerCase() !== resolve(path).toLowerCase()) fail();
}

function snapshot(path, cap, includeBytes = false) {
  nonReparse(path);
  const descriptor = openSync(path, 'r');
  try {
    const before = fstatSync(descriptor);
    if (!before.isFile() || before.size < 1 || before.size > cap) fail();
    const hash = createHash('sha256'); const chunks = []; const buffer = Buffer.alloc(65536);
    let total = 0;
    while (total <= cap) {
      const size = readSync(descriptor, buffer, 0, Math.min(buffer.length, cap + 1 - total), null);
      if (size === 0) break;
      total += size;
      if (total > cap) fail();
      hash.update(buffer.subarray(0, size));
      if (includeBytes) chunks.push(Buffer.from(buffer.subarray(0, size)));
    }
    const after = fstatSync(descriptor);
    if (total !== before.size || before.size !== after.size || before.mtimeMs !== after.mtimeMs ||
        before.ctimeMs !== after.ctimeMs || before.ino !== after.ino || before.dev !== after.dev) fail();
    nonReparse(path);
    return { sha256: hash.digest('hex'), bytes: includeBytes ? Buffer.concat(chunks) : null };
  } finally { closeSync(descriptor); }
}

// Fixed module-relative source context only. No caller-supplied path or hash map.
export function verifyCollectionSources() {
  if (arguments.length !== 0) fail();
  const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
  const bytes = snapshot(join(packageRoot, 'qualification/windows-storage-loader-metadata-controller-selection.json'), 16384, true).bytes;
  const selected = validateCollectionSelection(bytes);
  for (const [path, sha256] of Object.entries(selected.sourceSha256)) {
    if (snapshot(join(packageRoot, path), 1048576).sha256 !== sha256) fail();
  }
  return { selected, bytes };
}

// Fixed filenames only. Revalidation prevents callers from bypassing wire/exit policy.
export function prepareCollectionArtifacts(bytes, exitCode, rootDirectory, collectionSourceCommit) {
  const value = validateResult(bytes, exitCode);
  if (typeof collectionSourceCommit !== 'string' || !/^[0-9a-f]{40}$/.test(collectionSourceCommit) ||
      typeof rootDirectory !== 'string' || rootDirectory.length > 1024) fail();
  nonReparse(rootDirectory);
  if (!lstatSync(rootDirectory).isDirectory()) fail();
  const control = { scope: 'windows-storage-loader-metadata-execution-control', schema: 1,
    phase: 'metadata-only', sourceCommit, collectionSourceCommit, sourceSelectionSha256: selectionSha256,
    state: value.state, collectorExitCode: exitCode,
    selectionAuthority: false, buildAuthority: false, nativeAuthority: false };
  const artifactDirectory = join(rootDirectory, 'factory-metadata-collect-upload');
  mkdirSync(artifactDirectory, { mode: 0o700 });
  writeFileSync(join(artifactDirectory, 'metadata.json'), bytes, { flag: 'wx', mode: 0o600 });
  writeFileSync(join(artifactDirectory, 'control.json'), `${JSON.stringify(control)}\n`, { flag: 'wx', mode: 0o600 });
  return { state: value.state, exitCode, artifactDirectory };
}

async function main() {
  try {
    if (process.argv.length !== 2 || process.platform !== 'win32' || process.arch !== 'x64' ||
        process.version !== 'v24.22.1') fail();
    const privateRoot = process.env.FACTORY_PRIVATE_ROOT;
    const collectionSourceCommit = process.env.FACTORY_COLLECTION_SOURCE_COMMIT;
    if (typeof privateRoot !== 'string' || !/^[A-Z]:\\/i.test(privateRoot) ||
        typeof collectionSourceCommit !== 'string' || !/^[0-9a-f]{40}$/.test(collectionSourceCommit)) fail();
    nonReparse(privateRoot);
    const runtimeLeaf = dirname(dirname(process.execPath));
    if (dirname(runtimeLeaf).toLowerCase() !== resolve(privateRoot).toLowerCase() ||
        !/^factory-metadata-collect-node-[0-9a-f]{32}$/.test(runtimeLeaf.slice(dirname(runtimeLeaf).length + 1))) fail();
    const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
    const { bytes: selectedBytes } = verifyCollectionSources();
    const freezeSources = () => {
      if (snapshot(process.execPath, 134217728).sha256 !== nodeSha256) fail();
      verifyCollectionSources();
    };
    freezeSources();
    const inputDirectory = join(privateRoot, 'factory-metadata-collect-input');
    mkdirSync(inputDirectory, { mode: 0o700 });
    const inputSelection = join(inputDirectory, 'controller-selection.json');
    writeFileSync(inputSelection, selectedBytes, { flag: 'wx', mode: 0o600 });
    if (snapshot(inputSelection, 16384).sha256 !== selectionSha256) fail();
    const hostHome = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0';
    // Sole fixed route. No inherited credentials, options, PATH lookup or discovered tool.
    const child = spawn(process.execPath, [join(packageRoot, 'qualification/windows-storage-loader-metadata.mjs'), '--metadata-only'], {
      cwd: packageRoot, windowsHide: true, shell: false, stdio: ['ignore', 'pipe', 'pipe'],
      env: { SystemRoot: 'C:\\Windows', WINDIR: 'C:\\Windows', OS: 'Windows_NT',
        PATH: `${hostHome};C:\\Windows\\System32`, PSModulePath: `${hostHome}\\Modules`,
        FACTORY_WINDOWS_LOADER_METADATA_SELECTION: inputSelection,
        FACTORY_WINDOWS_LOADER_METADATA_SELECTION_SHA256: selectionSha256 },
    });
    const captured = await classifyCollectionProcess(child);
    freezeSources();
    if (snapshot(inputSelection, 16384).sha256 !== selectionSha256) fail();
    if (captured.diagnostic) {
      process.stdout.write(`${captured.diagnostic}\n`);
      process.exitCode = 1;
      return;
    }
    const result = prepareCollectionArtifacts(captured.bytes, captured.exitCode, privateRoot, collectionSourceCommit);
    process.stdout.write('metadata-artifacts-ready\n');
    process.exitCode = result.exitCode;
  } catch {
    // No raw stdout/stderr, candidate error text, environment or partial artifacts escape.
    process.stdout.write('metadata-refused-prerequisite\n');
    process.exitCode = 1;
  }
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
