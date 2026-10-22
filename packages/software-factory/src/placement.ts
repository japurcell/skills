import { spawnSync } from 'node:child_process';
import { realpathSync, statSync, statfsSync } from 'node:fs';
import { join } from 'node:path';

export interface LocalPlacement { directory: string; platform: NodeJS.Platform; filesystem: string }

// The path travels as an environment value, never executable PowerShell source.
const windowsProbe = String.raw`
$ErrorActionPreference = 'Stop'
[Console]::Error.WriteLine('FACTORY_PLACEMENT_STAGE:entered')
[Console]::Error.Flush()
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class FactoryVolume {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool GetVolumePathNameW(string path, StringBuilder volume, uint length);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    public static extern uint GetDriveTypeW(string root);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool GetVolumeInformationW(string root, StringBuilder name, uint nameSize,
        out uint serial, out uint maxComponent, out uint flags, StringBuilder filesystem, uint filesystemSize);
}
'@
[Console]::Error.WriteLine('FACTORY_PLACEMENT_STAGE:interop_ready')
[Console]::Error.Flush()
$volume = New-Object System.Text.StringBuilder 32768
if (-not [FactoryVolume]::GetVolumePathNameW($env:FACTORY_PLACEMENT_PATH, $volume, $volume.Capacity)) { throw 'volume path unavailable' }
[Console]::Error.WriteLine('FACTORY_PLACEMENT_STAGE:volume_path')
[Console]::Error.Flush()
$filesystem = New-Object System.Text.StringBuilder 256
[uint32]$serial = 0; [uint32]$component = 0; [uint32]$flags = 0
if (-not [FactoryVolume]::GetVolumeInformationW($volume.ToString(), $null, 0, [ref]$serial, [ref]$component, [ref]$flags, $filesystem, $filesystem.Capacity)) { throw 'volume information unavailable' }
[Console]::Error.WriteLine('FACTORY_PLACEMENT_STAGE:volume_information')
[Console]::Error.Flush()
$driveType = [FactoryVolume]::GetDriveTypeW($volume.ToString())
[Console]::Error.WriteLine('FACTORY_PLACEMENT_STAGE:drive_type')
[Console]::Error.Flush()
$result = @{ driveType = $driveType; filesystem = $filesystem.ToString() } | ConvertTo-Json -Compress
[Console]::Error.WriteLine('FACTORY_PLACEMENT_STAGE:complete')
[Console]::Error.Flush()
$result
`;

/** Fail closed on unknown, network or volatile storage. This is placement evidence, not release qualification. */
export function assertLocalPlacement(path: string): LocalPlacement {
  if (typeof path !== 'string' || path.length === 0 || path.includes('\0')) throw new Error('invalid storage directory');
  const directory = realpathSync.native(path);
  if (!statSync(directory).isDirectory()) throw new Error('storage placement must be a directory');
  let filesystem: string | undefined;
  if (process.platform === 'win32') {
    if (!/^[A-Za-z]:\\/.test(directory)) throw new Error('unsupported storage placement: network or unknown path');
    const systemRoot = process.env['SystemRoot'];
    if (!systemRoot || !/^[A-Za-z]:\\/.test(systemRoot)) throw new Error('native Windows placement prerequisite missing: SystemRoot');
    const started = performance.now();
    const probe = spawnSync(join(systemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
      ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command', windowsProbe], {
        encoding: 'utf8', timeout: 10_000, maxBuffer: 8192, windowsHide: true,
        env: { ...process.env, FACTORY_PLACEMENT_PATH: directory },
      });
    if (probe.error || probe.status !== 0) {
      // Native output and Error messages can contain paths or environment values.
      // Keep only bounded process facts so a timeout is distinguishable from an exit.
      const code = (probe.error as NodeJS.ErrnoException | undefined)?.code;
      let error = 'none';
      if (probe.error) error = ['ETIMEDOUT', 'ENOBUFS', 'ENOENT', 'EACCES', 'EPERM', 'EAGAIN', 'ENOMEM', 'EMFILE', 'ENFILE'].includes(code ?? '') ? String(code) : 'other';
      let signal: string = probe.signal ?? 'none';
      if (!['none', 'SIGTERM', 'SIGKILL', 'SIGINT', 'SIGBREAK', 'SIGABRT'].includes(signal)) signal = 'other';
      let stage = 'none';
      if (typeof probe.stderr === 'string') {
        for (const marker of probe.stderr.slice(0, 8192).matchAll(/^FACTORY_PLACEMENT_STAGE:(entered|interop_ready|volume_path|volume_information|drive_type|complete)\r?$/gm)) {
          if (marker[1]) stage = marker[1];
        }
      }
      const elapsedMs = Math.round(performance.now() - started);
      throw new Error(`native Windows placement probe failed; storage refused (error=${error}; status=${probe.status ?? 'none'}; signal=${signal}; stage=${stage}; elapsedMs=${elapsedMs})`);
    }
    let result: unknown;
    try {
      result = JSON.parse(probe.stdout.replace(/^\uFEFF/, ''));
    } catch {
      // A SyntaxError may quote native stdout, including the private placement path.
      throw new Error('native Windows placement probe returned invalid JSON; storage refused');
    }
    if (typeof result !== 'object' || result === null || !('driveType' in result) || result.driveType !== 3
      || !('filesystem' in result) || !['NTFS', 'ReFS'].includes(String(result.filesystem))) {
      throw new Error('unsupported storage placement: requires fixed local NTFS or ReFS');
    }
    filesystem = String(result.filesystem);
  } else if (process.platform === 'darwin') {
    // Darwin filesystem numbers vary across hosts. df checks the kernel's
    // filesystem name for this exact directory; native output is never parsed.
    for (const candidate of ['apfs', 'hfs']) {
      const probe = spawnSync('/bin/df', ['-n', '-P', '-T', candidate, '--', directory], {
        stdio: 'ignore', timeout: 1000, env: { LC_ALL: 'C' },
      });
      if (probe.error || probe.signal || (probe.status !== 0 && probe.status !== 1)) {
        throw new Error('native Darwin placement probe failed; storage refused');
      }
      if (probe.status === 0) { filesystem = candidate; break; }
    }
    if (!filesystem) throw new Error('unsupported storage placement: requires APFS or HFS');
  } else {
    const type = statfsSync(directory).type;
    const local: Record<number, string> = process.platform === 'linux' ? { 0xef53: 'ext', 0x9123683e: 'btrfs', 0x58465342: 'xfs' } : {};
    filesystem = local[type];
    if (!filesystem) throw new Error(`unsupported storage placement: filesystem ${type} (${process.platform})`);
  }
  return { directory, platform: process.platform, filesystem };
}
