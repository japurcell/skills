// Qualification only. The coordinator independently trusts the OS/controller installation.
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { closeSync, fstatSync, lstatSync, openSync, readSync, realpathSync } from 'node:fs';
import { captureMetadataProcess } from './windows-storage-loader-metadata.mjs';

const scope = 'windows-storage-loader-metadata-bootstrap';
const blocked = reason => ({ scope, schema: 1, state: 'blocked', reason,
  selectionAuthority: false, buildAuthority: false, nativeAuthority: false });
const baseKeys = ['scope', 'schema', 'state', 'reason', 'selectionAuthority', 'buildAuthority', 'nativeAuthority'];
const observedKeys = [...baseKeys, 'windowsRoot', 'windowsVersion', 'powershellVersion', 'architecture',
  'powershellSha256', 'powershellBytes', 'stability'];
const reasons = ['arguments', 'platform', 'controller-prerequisite', 'source', 'process', 'protocol', 'host', 'filesystem', 'bounds', 'changed'];
const closed = (value, keys) => value && typeof value === 'object' && !Array.isArray(value) &&
  Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
const version = (value, pattern) => typeof value === 'string' && value.length <= 64 && pattern.test(value);
const nodeSha256 = 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5';
const host = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe';
// Selected independently from known commit2229249, not from bootstrap output.
const source10 = Object.freeze({
  'qualification/windows-storage-loader-fixture.py': '8676a0e70ead3fc73b7ae2decabd1b892744ce859c59f20ef0f75f1e95799122',
  'qualification/windows-storage-loader-canary.c': '76f389bd6180b0832b218e6e2a016c0db05633ff50479205cf94ebd5593f2f46',
  'qualification/windows-storage-loader-child.mjs': 'f9f469c43810f4e6f31fb1e9aefa3869072bd78c8f0746065422645b84607f11',
  'qualification/windows-storage-loader.qualification.mjs': 'bd88c7e023b3108dbb8f502861510d60df31c4a8f233e939b89e7aab62e42694',
  'test/windows-storage-loader-contract.test.mjs': '31967f38c9abad2d61db0dd877f45db043835ecd5ab391640ae46b66de02f884',
  'qualification/windows-storage-loader.md': 'a10d314f8b17660760ee9091f2b771088d6ded5efef28c3a701c980921d57df0',
  'qualification/windows-storage-loader-metadata.mjs': 'bd31e066ef26dc48bf63e53fef383e04ece818341ed04a1c384b09643d0c3103',
  'qualification/windows-storage-loader-metadata.ps1': 'e95c861ce45fb57dd16a628aea0e1ef33e07efaf22049aa5746f4e594ed4cd4e',
  'qualification/windows-owned-image-host-profile.ps1': '30bf941fd0f62f33af6d9c0c779ac102d5e37efd94620896fdb9d501aecbf7d9',
  'qualification/windows-owned-image-diagnostics.ps1': 'eb1e0116d3b6115d97fab9666ac1626410d92dca471fb5195588ecafa4d8b420',
});

export function validateBootstrapWire(bytes) {
  const fail = () => { throw new Error('bootstrap-wire'); };
  if (!Buffer.isBuffer(bytes) || bytes.length > 4096) fail();
  let value;
  try { value = JSON.parse(bytes.toString('utf8')); } catch { fail(); }
  if (bytes.toString('utf8') !== `${JSON.stringify(value)}\n` ||
      !closed(value, value?.state === 'observed' ? observedKeys : baseKeys) || value.scope !== scope || value.schema !== 1 ||
      value.selectionAuthority !== false || value.buildAuthority !== false || value.nativeAuthority !== false) fail();
  if (value.state === 'blocked') {
    if (!reasons.includes(value.reason)) fail();
  } else if (value.state !== 'observed' || value.reason !== 'none' || value.windowsRoot !== 'C:\\Windows' ||
      !version(value.windowsVersion, /^10\.0\.[0-9]+\.[0-9]+$/) ||
      !version(value.powershellVersion, /^5\.1\.[0-9]+\.[0-9]+$/) || value.architecture !== 'x64' ||
      typeof value.powershellSha256 !== 'string' || !/^[0-9a-f]{64}$/.test(value.powershellSha256) ||
      !Number.isSafeInteger(value.powershellBytes) || value.powershellBytes < 1 || value.powershellBytes > 134217728 ||
      value.stability !== 'observed-equal') fail();
  return value;
}

// Already-created child only. The reused transport remains1MiB/8192/294s+1s.
// Bootstrap wire is separately4096bytes; exit1 cannot become an observation.
export async function observeBootstrapProcess(child, options = {}) {
  if (!closed(options, []) && !closed(options, ['deadlineMs'])) throw new Error('bootstrap-process');
  const captured = await captureMetadataProcess(child, options);
  if (captured.state !== 'captured') throw new Error('bootstrap-process');
  const value = validateBootstrapWire(captured.bytes);
  if (value.state !== 'observed') throw new Error('bootstrap-wire');
  return value;
}

// This fixed script is parsed locally, never executed by portable author tests.
// It relies on independently trusted/protected Windows and WinPS installations.
// Only fixed built-ins; no module imports, discovered executable, Add-Type or P/Invoke.
export const bootstrapScript = String.raw`
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$script:PSModuleAutoLoadingPreference = 'None'
$reason = 'host'
$stream = $null
$hash = $null
try {
    $fixedHost = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
    if (-not [Environment]::Is64BitProcess -or $PSVersionTable.PSVersion.Major -ne 5 -or
        $PSVersionTable.PSVersion.Minor -ne 1 -or
        -not [string]::Equals($PSHOME, 'C:\Windows\System32\WindowsPowerShell\v1.0', [StringComparison]::OrdinalIgnoreCase) -or
        -not [string]::Equals($env:SystemRoot, 'C:\Windows', [StringComparison]::OrdinalIgnoreCase) -or
        -not [string]::Equals([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName, $fixedHost, [StringComparison]::OrdinalIgnoreCase)) { throw 'host' }
    $windowsVersion = [Environment]::OSVersion.Version.ToString()
    $powershellVersion = $PSVersionTable.PSVersion.ToString()
    if ($windowsVersion.Length -gt 64 -or $windowsVersion -cnotmatch '^10\.0\.[0-9]+\.[0-9]+$' -or
        $powershellVersion.Length -gt 64 -or $powershellVersion -cnotmatch '^5\.1\.[0-9]+\.[0-9]+$') { throw 'host' }
    $reason = 'filesystem'
    $current = $fixedHost
    for ($depth = 0; $depth -lt 16; $depth++) {
        if (([IO.File]::GetAttributes($current) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'filesystem' }
        $parent = [IO.Directory]::GetParent($current)
        if ($null -eq $parent) { break }
        $current = $parent.FullName
        if ($depth -eq 15) { throw 'bounds' }
    }
    $stream = [IO.FileStream]::new($fixedHost, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $size = $stream.Length
    if ($size -lt 1 -or $size -gt 134217728) { throw 'bounds' }
    $stamp = [IO.File]::GetLastWriteTimeUtc($fixedHost).Ticks
    $hash = [Security.Cryptography.SHA256]::Create()
    $before = ([BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    $stream.Position = 0
    $after = ([BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    if ($before -cne $after -or $stream.Length -ne $size -or [IO.File]::GetLastWriteTimeUtc($fixedHost).Ticks -ne $stamp) { throw 'changed' }
    $wire = '{"scope":"windows-storage-loader-metadata-bootstrap","schema":1,"state":"observed","reason":"none","selectionAuthority":false,"buildAuthority":false,"nativeAuthority":false,"windowsRoot":"C:\\Windows","windowsVersion":"' + $windowsVersion + '","powershellVersion":"' + $powershellVersion + '","architecture":"x64","powershellSha256":"' + $before + '","powershellBytes":' + $size.ToString([Globalization.CultureInfo]::InvariantCulture) + ',"stability":"observed-equal"}'
    if ([Text.Encoding]::UTF8.GetByteCount($wire) + 1 -gt 4096) { throw 'bounds' }
    [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
    [Console]::Out.Write($wire + [char]10)
    $reason = 'none'
} catch {
    $reason = [string]$_.Exception.Message
    if ($reason -cnotin @('host', 'filesystem', 'bounds', 'changed')) { $reason = 'filesystem' }
} finally {
    if ($null -ne $stream) { $stream.Dispose() }
    if ($null -ne $hash) { $hash.Dispose() }
}
if ($reason -cne 'none') { exit 1 }
exit 0
`;

function snapshot(path, cap) {
  let current = path;
  for (let depth = 0; depth < 64; depth++) {
    if (lstatSync(current).isSymbolicLink()) throw new Error('source');
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
    if (depth === 63) throw new Error('source');
  }
  if (realpathSync.native(path).toLowerCase() !== path.toLowerCase()) throw new Error('source');
  const fd = openSync(path, 'r');
  try {
    const before = fstatSync(fd);
    if (!before.isFile() || before.size < 1 || before.size > cap) throw new Error('bounds');
    const hash = createHash('sha256');
    const buffer = Buffer.alloc(65536);
    let bytes = 0;
    while (bytes <= cap) {
      const size = readSync(fd, buffer, 0, Math.min(buffer.length, cap + 1 - bytes), null);
      if (!size) break;
      bytes += size;
      if (bytes > cap) throw new Error('bounds');
      hash.update(buffer.subarray(0, size));
    }
    const after = fstatSync(fd);
    if (bytes !== before.size || before.size !== after.size || before.mtimeMs !== after.mtimeMs ||
        before.ctimeMs !== after.ctimeMs || before.ino !== after.ino || before.dev !== after.dev) throw new Error('changed');
    return { sha256: hash.digest('hex'), bytes };
  } finally { closeSync(fd); }
}

async function main() {
  let reason = 'arguments';
  try {
    if (process.argv.length !== 3 || process.argv[2] !== '--bootstrap-only') throw new Error();
    reason = 'platform';
    if (process.platform !== 'win32' || process.arch !== 'x64') throw new Error();
    reason = 'controller-prerequisite';
    // Release marker is a fixed route guard, never installation authentication.
    if (process.version !== 'v24.22.1' || process.env.FACTORY_WINDOWS_LOADER_BOOTSTRAP_RELEASE !== 'phase-a-observation-only') throw new Error();
    const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
    reason = 'source';
    const freeze = () => {
      if (snapshot(process.execPath, 134217728).sha256 !== nodeSha256) throw new Error();
      for (const [path, hash] of Object.entries(source10)) if (snapshot(join(packageRoot, path), 1048576).sha256 !== hash) throw new Error();
    };
    freeze();
    const before = snapshot(host, 134217728);
    reason = 'process';
    const child = spawn(host, ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command', bootstrapScript], {
      cwd: packageRoot, windowsHide: true, shell: false, stdio: ['ignore', 'pipe', 'pipe'],
      env: { SystemRoot: 'C:\\Windows', WINDIR: 'C:\\Windows', OS: 'Windows_NT',
        PATH: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0;C:\\Windows\\System32',
        PSModulePath: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules' },
    });
    let value;
    let failed = false;
    try { value = await observeBootstrapProcess(child); } catch { failed = true; }
    reason = 'changed';
    freeze();
    const after = snapshot(host, 134217728);
    if (before.sha256 !== after.sha256 || before.bytes !== after.bytes) throw new Error();
    reason = 'process';
    if (failed) throw new Error();
    reason = 'changed';
    if (value.powershellSha256 !== before.sha256 || value.powershellBytes !== before.bytes) throw new Error();
    process.stdout.write(`${JSON.stringify(value)}\n`);
    return;
  } catch {
    process.stdout.write(`${JSON.stringify(blocked(reason))}\n`);
    process.exitCode = 1;
  }
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
