#!/usr/bin/env pwsh

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$hook = Join-Path $repoRoot '.codex/hooks/scan-secrets.py'
$python = (Get-Command python -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$git = (Get-Command git -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$workdir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())

function Invoke-Scanner {
    param([string]$Event, [string]$Mode)
    $payload = @{ hook_event_name = $Event; session_id = 'm4-windows'; cwd = $workdir } | ConvertTo-Json -Compress
    $env:SCAN_MODE = $Mode
    $env:SECRETS_LOG_DIR = Join-Path $workdir 'logs'
    Push-Location $workdir
    try {
        $output = $payload | & $python -I -S -B $hook
        if ($LASTEXITCODE -ne 0) { throw "Scanner exited $LASTEXITCODE" }
        return ($output | ConvertFrom-Json -AsHashtable)
    }
    finally { Pop-Location }
}

try {
    New-Item -ItemType Directory -Path $workdir | Out-Null
    & $git -C $workdir init -q
    if ($LASTEXITCODE -ne 0) { throw 'Git init failed' }
    [System.IO.File]::WriteAllText((Join-Path $workdir 'credentials.txt'), 'sk_live_1234567890abcdefghij')

    $pretool = Invoke-Scanner -Event PreToolUse -Mode block
    if ($pretool.hookSpecificOutput.hookEventName -cne 'PreToolUse' -or
        $pretool.hookSpecificOutput.permissionDecision -cne 'deny') { throw 'PreToolUse denial was invalid' }
    $stop = Invoke-Scanner -Event Stop -Mode block
    if ($stop.decision -cne 'block') { throw 'Stop response was invalid' }
    $warn = Invoke-Scanner -Event PreToolUse -Mode warn
    if (-not $warn.systemMessage.Contains('Potential secrets detected')) { throw 'Warning was absent' }
    if (($pretool | ConvertTo-Json -Compress) -match 'sk_live_1234567890abcdefghij') { throw 'Secret leaked to hook response' }

    Remove-Item -LiteralPath (Join-Path $workdir 'credentials.txt')
    $clean = Invoke-Scanner -Event PreToolUse -Mode block
    if ($clean.Count -ne 0) { throw 'Clean response was not empty' }
    Write-Output 'PASS: Codex scanner Windows envelopes'
}
finally {
    Remove-Item -LiteralPath $workdir -Recurse -Force -ErrorAction SilentlyContinue
}
