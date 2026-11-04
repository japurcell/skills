// Qualification only. Independently trusted controller/OS installation is a prerequisite.
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve, win32 } from 'node:path';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { closeSync, fstatSync, lstatSync, openSync, readSync, realpathSync } from 'node:fs';

const scope = 'windows-storage-loader-metadata';
const blocked = reason => ({ scope, state: 'blocked', reason,
  selectionAuthority: false, buildAuthority: false, nativeAuthority: false });
const fail = () => { throw new Error('metadata'); };
const hex = (value, length = 64) => typeof value === 'string' && new RegExp(`^[0-9a-f]{${length}}$`).test(value);
const closed = (value, keys) => value && typeof value === 'object' && !Array.isArray(value) &&
  Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
const text = (value, cap, empty = false) => typeof value === 'string' && value.length <= cap &&
  (empty || value.length > 0) && !/[\x00-\x1f\x7f]/.test(value);
const installationPattern = /^[A-Z]:\\Program Files(?: \(x86\))?\\Microsoft Visual Studio\\(?:18|20[0-9]{2})\\(?:BuildTools|Community|Professional|Enterprise)$/i;
const sdkPattern = /^10\.0\.[0-9]{4,6}\.[0-9]{1,6}$/;
const toolsetPattern = /^14\.[0-9]{2}\.[0-9]{5}$/;
const reasons = ['none', 'host', 'host-profile', 'bounds', 'missing-tools', 'ambiguous-tools', 'missing-sdk',
  'ambiguous-sdk', 'tool-provenance-unproven', 'sdk-provenance-unproven', 'changed', 'filesystem'];
const signatureConditions = ['none', 'status-not-valid', 'signer-absent', 'subject-mismatch', 'classification-failure'];
const sourceFiles = ['qualification/windows-storage-loader-fixture.py', 'qualification/windows-storage-loader-canary.c',
  'qualification/windows-storage-loader-child.mjs', 'qualification/windows-storage-loader.qualification.mjs',
  'test/windows-storage-loader-contract.test.mjs', 'qualification/windows-storage-loader.md',
  'qualification/windows-storage-loader-metadata.mjs', 'qualification/windows-storage-loader-metadata.ps1',
  'qualification/windows-owned-image-host-profile.ps1', 'qualification/windows-owned-image-diagnostics.ps1'];
const nodeSha256 = 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5';

export function validateControllerSelection(bytes) {
  if (!Buffer.isBuffer(bytes) || bytes.length > 16384) fail();
  let value;
  try { value = JSON.parse(bytes.toString('utf8')); } catch { fail(); }
  if (bytes.toString('utf8') !== `${JSON.stringify(value)}\n` ||
      !closed(value, ['scope', 'schema', 'sourceCommit', 'sourceSha256', 'nodeSha256', 'powershellSha256', 'windowsRoot', 'windowsVersion']) ||
      value.scope !== 'windows-storage-loader-metadata-controller' || value.schema !== 1 || !hex(value.sourceCommit, 40) ||
      !closed(value.sourceSha256, sourceFiles) || sourceFiles.some(path => !hex(value.sourceSha256[path])) ||
      value.nodeSha256 !== nodeSha256 || !hex(value.powershellSha256) ||
      typeof value.windowsRoot !== 'string' || !/^[A-Z]:\\Windows$/.test(value.windowsRoot) ||
      !text(value.windowsVersion, 64) || !/^10\.0\.[0-9]+\.[0-9]+$/.test(value.windowsVersion)) fail();
  return value;
}

function nonReparsePath(path) {
  if (typeof path !== 'string' || path.length > 1024 || !/^[A-Z]:\\/i.test(path) ||
      win32.normalize(path).toLowerCase() !== path.toLowerCase() || /[;*?\[\]\x00-\x1f\x7f]/.test(path) ||
      /(?:[ .]\\|[ .]$)/.test(path) || path.slice(2).includes(':')) fail();
  let current = path;
  for (let depth = 0; depth < 64; depth++) {
    if (lstatSync(current).isSymbolicLink()) fail();
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
    if (depth === 63) fail();
  }
  if (realpathSync.native(path).toLowerCase() !== path.toLowerCase()) fail();
}
function frozenFile(path, cap, includeBytes = false) {
  nonReparsePath(path);
  const descriptor = openSync(path, 'r');
  try {
    const before = fstatSync(descriptor);
    if (!before.isFile() || before.size < 1 || before.size > cap) fail();
    const digest = createHash('sha256');
    const buffer = Buffer.alloc(65536);
    const chunks = [];
    let total = 0;
    while (total <= cap) {
      const size = readSync(descriptor, buffer, 0, Math.min(buffer.length, cap + 1 - total), null);
      if (size === 0) break;
      total += size;
      if (total > cap) fail();
      digest.update(buffer.subarray(0, size));
      if (includeBytes) chunks.push(Buffer.from(buffer.subarray(0, size)));
    }
    const after = fstatSync(descriptor);
    if (total !== before.size || before.size !== after.size || before.mtimeMs !== after.mtimeMs ||
        before.ctimeMs !== after.ctimeMs || before.ino !== after.ino || before.dev !== after.dev) fail();
    nonReparsePath(path);
    return { sha256: digest.digest('hex'), bytes: includeBytes ? Buffer.concat(chunks) : null };
  } finally { closeSync(descriptor); }
}

function validSignature(value, path) {
  if (!closed(value, ['path', 'status', 'type', 'condition', 'subject', 'issuer', 'thumbprint', 'certificateSha256']) ||
      typeof value.path !== 'string' || value.path.toLowerCase() !== path.toLowerCase() || !['Valid', 'NotSigned', 'HashMismatch', 'NotTrusted', 'UnknownError',
        'NotSupportedFileFormat', 'Incompatible'].includes(value.status) ||
      !['None', 'Authenticode', 'Catalog'].includes(value.type) || !signatureConditions.includes(value.condition) ||
      !text(value.subject, 2048, true) || !text(value.issuer, 2048, true) ||
      !(value.thumbprint === '' || hex(value.thumbprint, 40)) ||
      !(value.certificateSha256 === '' || hex(value.certificateSha256))) return false;
  if (value.condition === 'none') return value.status === 'Valid' && value.type !== 'None' &&
    /(?:^|, )O=Microsoft Corporation(?:,|$)/.test(value.subject) && hex(value.thumbprint, 40) && hex(value.certificateSha256);
  return value.status !== 'Valid' || value.condition !== 'status-not-valid';
}
function validFile(file, installations, sdkVersions) {
  if (!closed(file, ['role', 'target', 'installation', 'toolset', 'sdkVersion', 'path', 'bytes', 'sha256',
    'fileVersion', 'regular', 'reparse', 'stability', 'signature']) || !text(file.path, 1024) ||
      /[;*?\[\]<>"|]/.test(file.path) || /(?:^|\\)\.{1,2}(?:\\|$)/.test(file.path) ||
      /(?:[ .]\\|[ .]$)/.test(file.path) || !Number.isSafeInteger(file.bytes) || file.bytes < 1 ||
      file.bytes > 134217728 || !hex(file.sha256) || !text(file.fileVersion, 128, true) ||
      file.regular !== true || file.reparse !== false || file.stability !== 'observed-equal' ||
      !validSignature(file.signature, file.path)) return false;
  if (['compiler', 'linker', 'inspector', 'library-tool', 'compiler-companion'].includes(file.role)) {
    if (!installations.includes(file.installation) || !text(file.toolset, 32) || !toolsetPattern.test(file.toolset) || file.sdkVersion !== '' ||
        !['x64', 'x86'].includes(file.target)) return false;
    const prefix = `${file.installation}\\VC\\Tools\\MSVC\\${file.toolset}\\bin\\Hostx64\\${file.target}\\`;
    if (!file.path.startsWith(prefix)) return false;
    const leaf = file.path.slice(prefix.length);
    const leafs = { compiler: 'cl.exe', linker: 'link.exe', inspector: 'dumpbin.exe', 'library-tool': 'lib.exe' };
    return file.role === 'compiler-companion' ? /^[a-z0-9_.-]+\.dll$/i.test(leaf) :
      leaf.toLowerCase() === leafs[file.role] &&
      (file.role !== 'inspector' || file.target === 'x64') && (file.role !== 'library-tool' || file.target === 'x86');
  }
  if (file.role === 'installation-metadata') return installations.includes(file.installation) && file.target === 'none' &&
    file.toolset === '' && file.sdkVersion === '' && file.bytes <= 65536 &&
    file.path === `${file.installation}\\VC\\Auxiliary\\Build\\Microsoft.VCToolsVersion.default.txt`;
  if (!['sdk-header', 'sdk-library'].includes(file.role) || file.installation !== '' || file.toolset !== '' ||
      !sdkVersions.includes(file.sdkVersion)) return false;
  const prefix = /^[A-Z]:\\Program Files \(x86\)\\Windows Kits\\10\\/i.exec(file.path);
  if (!prefix) return false;
  const suffix = file.path.slice(prefix[0].length);
  if (file.role === 'sdk-header') return file.target === 'none' &&
    [`Include\\${file.sdkVersion}\\ucrt\\stdio.h`, `Include\\${file.sdkVersion}\\shared\\sdkddkver.h`,
      `Include\\${file.sdkVersion}\\um\\Windows.h`].some(path => path.toLowerCase() === suffix.toLowerCase());
  return ['x64', 'x86'].includes(file.target) &&
    [`Lib\\${file.sdkVersion}\\ucrt\\${file.target}\\ucrt.lib`,
      `Lib\\${file.sdkVersion}\\um\\${file.target}\\kernel32.lib`].some(path => path.toLowerCase() === suffix.toLowerCase());
}

// Schema validation is not cryptographic authentication. Synthetic records cannot
// acquire Microsoft, builder, input-selection or native authority through this API.
export function validateMetadataWire(bytes, selectedSha256) {
  if (!Buffer.isBuffer(bytes) || bytes.length > 1048576 || !hex(selectedSha256)) fail();
  let value;
  try { value = JSON.parse(bytes.toString('utf8')); } catch { fail(); }
  if (bytes.toString('utf8') !== `${JSON.stringify(value)}\n` ||
      !closed(value, ['scope', 'schema', 'state', 'reason', 'selectionAuthority', 'buildAuthority', 'nativeAuthority',
        'sourceSelectionSha256', 'host', 'installations', 'sdkVersions', 'files', 'sdkCoverage']) ||
      value.scope !== scope || value.schema !== 1 || !['blocked', 'observed'].includes(value.state) ||
      !reasons.includes(value.reason) || (value.state === 'observed') !== (value.reason === 'none') ||
      value.selectionAuthority !== false || value.buildAuthority !== false || value.nativeAuthority !== false ||
      value.sourceSelectionSha256 !== selectedSha256 || value.sdkCoverage !== 'prerequisite-samples-not-consumed-closure' ||
      !closed(value.host, ['powershellVersion', 'windowsVersion', 'architecture', 'profile', 'securityCommand']) ||
      !text(value.host.powershellVersion, 64) || !/^5\.1\.[0-9]+\.[0-9]+$/.test(value.host.powershellVersion) ||
      !text(value.host.windowsVersion, 64) || !/^10\.0\.[0-9]+\.[0-9]+$/.test(value.host.windowsVersion) || value.host.architecture !== 'x64' ||
      value.host.profile !== 'winps-inbox-only' || value.host.securityCommand !== 'captured-inbox-Get-AuthenticodeSignature' ||
      !Array.isArray(value.installations) || value.installations.length > 16 ||
      value.installations.some(path => typeof path !== 'string' || !installationPattern.test(path)) ||
      !Array.isArray(value.sdkVersions) || value.sdkVersions.length > 8 || value.sdkVersions.some(version => !text(version, 32) || !sdkPattern.test(version)) ||
      !Array.isArray(value.files) || value.files.length > 256) fail();
  for (const entries of [value.installations, value.sdkVersions]) {
    if (new Set(entries.map(entry => entry.toLowerCase())).size !== entries.length) fail();
  }
  const paths = new Set();
  for (const file of value.files) {
    if (!validFile(file, value.installations, value.sdkVersions) || paths.has(file.path.toLowerCase())) fail();
    paths.add(file.path.toLowerCase());
  }
  if (value.state === 'observed') {
    if (value.installations.length !== 1 || value.sdkVersions.length !== 1 ||
        value.files.some(file => file.role !== 'installation-metadata' && (file.signature.condition !== 'none' ||
          (!file.role.startsWith('sdk-') && file.fileVersion === '')))) fail();
    for (const [role, target] of [['compiler', 'x64'], ['linker', 'x64'], ['inspector', 'x64'],
      ['compiler', 'x86'], ['linker', 'x86'], ['library-tool', 'x86']]) {
      if (value.files.filter(file => file.role === role && file.target === target).length !== 1) fail();
    }
    const toolsets = new Set(value.files.filter(file => file.toolset).map(file => file.toolset));
    if (toolsets.size !== 1 || value.files.filter(file => file.role === 'sdk-header').length !== 3 ||
        value.files.filter(file => file.role === 'sdk-library').length !== 4) fail();
    for (const target of ['x64', 'x86']) for (const leaf of ['c1.dll', 'c1xx.dll', 'c2.dll']) {
      if (!value.files.some(file => file.role === 'compiler-companion' && file.target === target &&
        file.path.toLowerCase().endsWith(`\\${leaf}`))) fail();
    }
  }
  return value;
}

// Observe an already-created process. This seam supplies no executable/path route.
// Default zero exit; the fixed collector caller can explicitly accept blocked exit1.
// Both real EOF events remain mandatory, and the caller validates exit/state coupling.
export function captureMetadataProcess(child, options = {}) {
  const deadlineMs = options.deadlineMs ?? 294000;
  const exitCodes = options.exitCodes ?? [0];
  if (!Number.isSafeInteger(deadlineMs) || deadlineMs < 1 || deadlineMs > 294000 ||
      !Array.isArray(exitCodes) || !['[0]', '[0,1]'].includes(JSON.stringify(exitCodes)) ||
      Object.keys(options).some(key => !['deadlineMs', 'exitCodes'].includes(key))) throw new Error('metadata-process');
  return new Promise(resolveCapture => {
    let reason = 'none';
    let exitObserved = false;
    let stdoutEOF = false;
    let stderrEOF = false;
    let acceptedExit = false;
    let exitCode = null;
    let ended = false;
    let reap;
    const lengths = [0, 0];
    const chunks = [];
    const finish = () => {
      if (ended) return;
      ended = true;
      clearTimeout(timer); clearTimeout(reap);
      if (reason === 'none' && (!exitObserved || !stdoutEOF || !stderrEOF)) reason = 'eof';
      if (reason === 'none' && !acceptedExit) reason = 'exit';
      const state = reason === 'none' ? 'captured' : 'blocked';
      resolveCapture({ state, reason, bytes: state === 'captured' ? Buffer.concat(chunks) : null,
        exitCode, exitObserved, stdoutEOF, stderrEOF });
    };
    const stop = failure => {
      // Bounds has priority over later stderr/exit/cleanup observations.
      if (reason === 'none' || failure === 'bounds') reason = failure;
      try { child.kill('SIGKILL'); } catch { /* Unknown teardown stays blocked. */ }
      if (!reap) reap = setTimeout(() => {
        child.stdout?.destroy(); child.stderr?.destroy(); child.unref(); finish();
      }, 1000);
    };
    const timer = setTimeout(() => stop('deadline'), deadlineMs);
    for (const [index, stream] of [child.stdout, child.stderr].entries()) {
      if (!stream) { stop('process'); continue; }
      stream.on('data', chunk => {
        lengths[index] = Math.min([1048577, 8193][index], lengths[index] + chunk.length);
        if (lengths[index] > [1048576, 8192][index]) { stop('bounds'); return; }
        if (index === 1 && chunk.length) { if (reason === 'none') reason = 'stderr'; return; }
        if (reason === 'none' && index === 0) chunks.push(chunk);
      });
      stream.on('end', () => { if (index === 0) stdoutEOF = true; else stderrEOF = true; });
      stream.on('error', () => stop('process'));
    }
    child.on('error', () => stop('process'));
    child.on('exit', (code, signal) => { exitObserved = true; exitCode = code; acceptedExit = exitCodes.includes(code) && signal === null; });
    child.on('close', finish);
  });
}

async function main() {
  let reason = 'arguments';
  try {
    if (process.argv.length !== 3 || process.argv[2] !== '--metadata-only') throw new Error();
    reason = 'platform';
    if (process.platform !== 'win32' || process.arch !== 'x64') throw new Error();
    reason = 'controller-prerequisite';
    const selectedPath = process.env.FACTORY_WINDOWS_LOADER_METADATA_SELECTION;
    const selectedSha256 = process.env.FACTORY_WINDOWS_LOADER_METADATA_SELECTION_SHA256;
    if (process.version !== 'v24.22.1' || !hex(selectedSha256)) throw new Error();
    const selectedFile = frozenFile(selectedPath, 16384, true);
    if (selectedFile.sha256 !== selectedSha256) throw new Error();
    const selected = validateControllerSelection(selectedFile.bytes);
    const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
    const host = win32.join(selected.windowsRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
    const hostHome = win32.dirname(host);
    // The external coordinator authenticates this installation before starting
    // Node. Current hashes corroborate frozen identities, never bootstrap trust.
    const freeze = () => {
      if (frozenFile(selectedPath, 16384).sha256 !== selectedSha256 ||
          frozenFile(process.execPath, 134217728).sha256 !== selected.nodeSha256 ||
          frozenFile(host, 134217728).sha256 !== selected.powershellSha256) fail();
      for (const path of sourceFiles) if (frozenFile(join(packageRoot, path), 1048576).sha256 !== selected.sourceSha256[path]) fail();
    };
    freeze();
    reason = 'process';
    const child = spawn(host, ['-NoLogo', '-NoProfile', '-NonInteractive', '-File',
      join(packageRoot, 'qualification/windows-storage-loader-metadata.ps1'), '-Mode', 'metadata-only'], {
      cwd: packageRoot, windowsHide: true, shell: false, stdio: ['ignore', 'pipe', 'pipe'],
      env: { SystemRoot: selected.windowsRoot, WINDIR: selected.windowsRoot,
        OS: 'Windows_NT', PATH: `${hostHome};${win32.join(selected.windowsRoot, 'System32')}`,
        PSModulePath: win32.join(hostHome, 'Modules'),
        FACTORY_OWNED_IMAGE_INBOX: win32.join(hostHome, 'Modules'), FACTORY_OWNED_IMAGE_PROFILE: 'winps-inbox-only',
        FACTORY_WINDOWS_LOADER_METADATA_SELECTION_SHA256: selectedSha256,
        FACTORY_WINDOWS_LOADER_METADATA_WINDOWS_VERSION: selected.windowsVersion },
    });
    const captured = await captureMetadataProcess(child, { exitCodes: [0, 1] });
    reason = 'changed';
    freeze();
    reason = captured.reason;
    if (captured.state !== 'captured') throw new Error();
    reason = 'protocol';
    // Profile/host refusals cannot safely use a module-dependent serializer.
    // Their one finite canonical record is preserved, with no path-bearing facts.
    const refusal = JSON.parse(captured.bytes.toString('utf8'));
    if (closed(refusal, ['scope', 'state', 'reason', 'selectionAuthority', 'buildAuthority', 'nativeAuthority']) &&
        captured.bytes.toString('utf8') === `${JSON.stringify(refusal)}\n` && captured.exitCode === 1 &&
        refusal.scope === scope && refusal.state === 'blocked' &&
        ['host', 'host-profile', 'bounds', 'filesystem', 'arguments'].includes(refusal.reason) &&
        refusal.selectionAuthority === false && refusal.buildAuthority === false && refusal.nativeAuthority === false) {
      process.stdout.write(`${JSON.stringify(refusal)}\n`); process.exitCode = 1; return;
    }
    const metadata = validateMetadataWire(captured.bytes, selectedSha256);
    if (metadata.host.windowsVersion !== selected.windowsVersion ||
        captured.exitCode !== (metadata.state === 'observed' ? 0 : 1)) fail();
    process.stdout.write(`${JSON.stringify(metadata)}\n`);
    process.exitCode = metadata.state === 'observed' ? 0 : 1;
    return;
  } catch {
    process.stdout.write(`${JSON.stringify(blocked(reason))}\n`);
    process.exitCode = 1;
  }
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
