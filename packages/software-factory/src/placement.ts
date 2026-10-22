import { spawnSync } from 'node:child_process';
import { realpathSync, statSync, statfsSync } from 'node:fs';
import { join } from 'node:path';

export interface LocalPlacement { directory: string; platform: NodeJS.Platform; filesystem: string }

// The path travels as an environment value, never executable PowerShell source.
const windowsProbe = String.raw`
$ErrorActionPreference = 'Stop'
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
$volume = New-Object System.Text.StringBuilder 32768
if (-not [FactoryVolume]::GetVolumePathNameW($env:FACTORY_PLACEMENT_PATH, $volume, $volume.Capacity)) { throw 'volume path unavailable' }
$filesystem = New-Object System.Text.StringBuilder 256
[uint32]$serial = 0; [uint32]$component = 0; [uint32]$flags = 0
if (-not [FactoryVolume]::GetVolumeInformationW($volume.ToString(), $null, 0, [ref]$serial, [ref]$component, [ref]$flags, $filesystem, $filesystem.Capacity)) { throw 'volume information unavailable' }
@{ driveType = [FactoryVolume]::GetDriveTypeW($volume.ToString()); filesystem = $filesystem.ToString() } | ConvertTo-Json -Compress
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
    const probe = spawnSync(join(systemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
      ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command', windowsProbe], {
        encoding: 'utf8', timeout: 10_000, maxBuffer: 8192, windowsHide: true,
        env: { ...process.env, FACTORY_PLACEMENT_PATH: directory },
      });
    if (probe.error || probe.status !== 0) throw new Error('native Windows placement probe failed; storage refused');
    const result: unknown = JSON.parse(probe.stdout.replace(/^\uFEFF/, ''));
    if (typeof result !== 'object' || result === null || !('driveType' in result) || result.driveType !== 3
      || !('filesystem' in result) || !['NTFS', 'ReFS'].includes(String(result.filesystem))) {
      throw new Error('unsupported storage placement: requires fixed local NTFS or ReFS');
    }
    filesystem = String(result.filesystem);
  } else {
    const type = statfsSync(directory).type;
    const local: Record<number, string> = process.platform === 'darwin' ? { 26: 'apfs', 17: 'hfs' }
      : process.platform === 'linux' ? { 0xef53: 'ext', 0x9123683e: 'btrfs', 0x58465342: 'xfs' } : {};
    filesystem = local[type];
    if (!filesystem) throw new Error(`unsupported storage placement: filesystem ${type} (${process.platform})`);
  }
  return { directory, platform: process.platform, filesystem };
}
