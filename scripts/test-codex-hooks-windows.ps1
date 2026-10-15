#!/usr/bin/env pwsh

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$hook = Join-Path $repoRoot '.codex/hooks/scan-secrets.py'
$python = (Get-Command python -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$git = (Get-Command git -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
$workdir = Join-Path $fixtureRoot 'repo'
$fixtureHome = Join-Path $fixtureRoot 'home'
$savedEnvironment = @{}
foreach ($name in @('HOME', 'USERPROFILE', 'CODEX_HOME', 'XDG_CONFIG_HOME', 'SCAN_MODE', 'SCAN_SCOPE',
                   'SECRETS_LOG_DIR', 'AUDIT_LOG', 'OBSERVABILITY_LOG_PATH', 'OBSERVABILITY_TESTING',
                   'SKIP_SECRETS_SCAN', 'SECRETS_ALLOWLIST', 'GIT_CONFIG_NOSYSTEM', 'GIT_CONFIG_GLOBAL')) {
    $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}

function Invoke-Scanner {
    param([string]$Event, [string]$Mode)
    $payload = @{ hook_event_name = $Event; session_id = 'm4-windows'; cwd = $workdir } | ConvertTo-Json -Compress
    $env:SCAN_MODE = $Mode
    $env:SECRETS_LOG_DIR = Join-Path $fixtureRoot 'logs'
    Push-Location $workdir
    try {
        $output = $payload | & $python -I -S -B $hook
        if ($LASTEXITCODE -ne 0) { throw "Scanner exited $LASTEXITCODE" }
        return ($output | ConvertFrom-Json -AsHashtable)
    }
    finally { Pop-Location }
}

try {
    New-Item -ItemType Directory -Path $workdir, $fixtureHome -Force | Out-Null
    $env:HOME = $fixtureHome
    $env:USERPROFILE = $fixtureHome
    $env:CODEX_HOME = Join-Path $fixtureHome '.codex'
    $env:XDG_CONFIG_HOME = Join-Path $fixtureHome '.config'
    $env:AUDIT_LOG = Join-Path $fixtureRoot 'audit.log'
    $env:OBSERVABILITY_LOG_PATH = Join-Path $fixtureRoot 'observability.jsonl'
    $env:OBSERVABILITY_TESTING = '1'
    $env:SCAN_SCOPE = 'diff'
    $env:SKIP_SECRETS_SCAN = $null
    $env:SECRETS_ALLOWLIST = $null
    $env:GIT_CONFIG_NOSYSTEM = '1'
    $env:GIT_CONFIG_GLOBAL = Join-Path $fixtureRoot 'gitconfig'
    [System.IO.File]::WriteAllText($env:GIT_CONFIG_GLOBAL, '')
    & $git -C $workdir init -q
    if ($LASTEXITCODE -ne 0) { throw 'Git init failed' }
    [System.IO.File]::WriteAllText((Join-Path $workdir 'credentials.txt'), 'sk_live_1234567890abcdefghij')

    $pretool = Invoke-Scanner -Event PreToolUse -Mode block
    if ($pretool.hookSpecificOutput.hookEventName -cne 'PreToolUse' -or
        $pretool.hookSpecificOutput.permissionDecision -cne 'deny') { throw 'PreToolUse denial was invalid' }
    $stop = Invoke-Scanner -Event Stop -Mode block
    if ($stop.decision -cne 'block') { throw 'Stop response was invalid' }
    $warn = Invoke-Scanner -Event PreToolUse -Mode warn
    # The anchored expression permits only the bounded, attributable suffix.
    $warningPattern = '^scan-secrets warning: tool scan; potential secrets detected\. security_outcome=findings; audit_outcome=written; enforcement=allow; build=[0-9a-f]{16}; profile=pending_snapshots_v1; route=pending_scan; cause=findings\.$'
    if ($warn.Count -ne 1 -or $warn.systemMessage -cnotmatch $warningPattern) { throw 'Warning was absent or lacked bounded attribution' }
    foreach ($response in @($pretool, $stop, $warn)) {
        if (($response | ConvertTo-Json -Compress) -match 'sk_live_1234567890abcdefghij') { throw 'Secret leaked to hook response' }
    }

    Remove-Item -LiteralPath (Join-Path $workdir 'credentials.txt')
    $clean = Invoke-Scanner -Event PreToolUse -Mode block
    if ($clean.Count -ne 0) { throw 'Clean response was not empty' }
    Write-Output 'PASS: Codex scanner Windows envelopes'
}
finally {
    foreach ($name in $savedEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')
    }
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
}
