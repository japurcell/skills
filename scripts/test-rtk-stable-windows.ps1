#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
if (-not $IsWindows) {
    Write-Output 'SKIP: native Windows RTK configuration proof requires Windows.'
    exit 0
}

$root = Split-Path -Parent $PSScriptRoot
$scratch = Join-Path ([System.IO.Path]::GetTempPath()) ("rtk-stable-" + [guid]::NewGuid().ToString('N'))
$homeDir = Join-Path $scratch 'home'
$bin = Join-Path $scratch 'bin'
$oldPath = $env:PATH
$oldAppData = $env:APPDATA
New-Item -ItemType Directory -Path $homeDir, $bin -Force | Out-Null
try {
    $env:PATH = "$bin$([System.IO.Path]::PathSeparator)$oldPath"
    $env:APPDATA = Join-Path $homeDir 'AppData/Roaming'
    $binary = Join-Path $bin 'rtk.cmd'
    Set-Content -LiteralPath $binary -Value @('@echo off', 'echo rtk 0.49.9')
    $config = Join-Path $env:APPDATA 'rtk/config.toml'
    & python (Join-Path $root 'scripts/configure-rtk.py') --home $homeDir --platform win32
    if ($LASTEXITCODE -eq 0 -or (Test-Path -LiteralPath $config)) { throw 'Old RTK changed configuration.' }

    Set-Content -LiteralPath $binary -Value @('@echo off', 'echo rtk 0.50.0')
    New-Item -ItemType Directory -Path (Split-Path -Parent $config) -Force | Out-Null
    $original = "# user preference`n[hooks]`nsuppress_hook_warning = false`n[display]`ncolors = false`n"
    [System.IO.File]::WriteAllText($config, $original)
    & python (Join-Path $root 'scripts/configure-rtk.py') --home $homeDir --platform win32 --check
    if ($LASTEXITCODE -ne 0 -or ([System.IO.File]::ReadAllText($config)) -ne $original) { throw 'RTK check mutated configuration.' }
    & python (Join-Path $root 'scripts/configure-rtk.py') --home $homeDir --platform win32
    if ($LASTEXITCODE -ne 0) { throw 'Stable RTK configuration failed.' }
    $updated = [System.IO.File]::ReadAllText($config)
    if ($updated -notmatch 'suppress_hook_warning = true' -or $updated -notmatch 'colors = false') { throw 'RTK setting or user data was lost.' }
    if ([System.IO.File]::ReadAllText("$config.bak") -ne $original) { throw 'RTK backup was not exact.' }
    & python (Join-Path $root 'scripts/configure-rtk.py') --home $homeDir --platform win32
    if ($LASTEXITCODE -ne 0 -or ([System.IO.File]::ReadAllText($config)) -ne $updated) { throw 'RTK repeat run was not idempotent.' }
    $env:PATH = $oldPath
    $version = & rtk --version 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -or $version -notmatch 'rtk \d+\.\d+\.\d+') { throw 'Stable RTK is unavailable for native proof.' }
    & python (Join-Path $root 'scripts/configure-rtk.py') --home $homeDir --platform win32 --check
    if ($LASTEXITCODE -ne 0) { throw 'Native RTK is older than stable 0.50.0.' }
    $missing = & rtk read (Join-Path $homeDir 'absent-file') 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0 -or $missing -notmatch 'absent-file' -or $missing -match 'No hook installed') {
        throw 'Stable RTK missing-file diagnostic or exit was lost.'
    }
    Write-Output 'PASS: native Windows RTK stable config, preflight, backup, and idempotence.'
}
finally {
    $env:PATH = $oldPath
    $env:APPDATA = $oldAppData
    Remove-Item -LiteralPath $scratch -Recurse -Force -ErrorAction SilentlyContinue
}
