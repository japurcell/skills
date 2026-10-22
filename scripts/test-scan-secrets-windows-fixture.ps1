#!/usr/bin/env pwsh

$ErrorActionPreference = 'Stop'
$suite = Join-Path $PSScriptRoot 'test-scan-secrets-windows.ps1'
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($suite, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Native fixture failed PowerShell parsing' }
foreach ($name in @('Write-DiagnosticRunner', 'Write-WatchdogEvidence', 'Invoke-Case')) {
    $definition = $ast.Find({ param($node)
        $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name
    }, $true)
    if ($null -eq $definition) { throw "Missing fixture contract: $name" }
    . ([scriptblock]::Create($definition.Extent.Text))
}

$root = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
$names = @('PATH', 'SCAN_MODE', 'COMSPEC', 'SECRETS_LOG_DIR', 'TEMP', 'TMP', 'HOME', 'USERPROFILE',
           'APPDATA', 'LOCALAPPDATA', 'CODEX_HOME', 'XDG_CONFIG_HOME', 'AUDIT_LOG',
           'OBSERVABILITY_LOG_PATH', 'COPILOT_OBSERVABILITY_LOG_PATH', 'GEMINI_OBSERVABILITY_LOG_PATH', 'OBSERVABILITY_TESTING', 'GIT_CONFIG_NOSYSTEM', 'GIT_CONFIG_GLOBAL')
$original = @{}
foreach ($name in $names) { $original[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
try {
    New-Item -ItemType Directory -Path $root | Out-Null
    $python = (Get-Command python -CommandType Application | Select-Object -First 1).Source
    $realGit = (Get-Command git -CommandType Application | Select-Object -First 1).Source
    $workdir = $root
    $hooks = @{ copilot = Join-Path $root 'hook.py' }
    [System.IO.File]::WriteAllText($hooks.copilot, "print('fixture')`n")
    foreach ($name in $names | Where-Object { $_ -notin @('PATH', 'COMSPEC') }) {
        [Environment]::SetEnvironmentVariable($name, "inherited-$name", 'Process')
    }
    [Environment]::SetEnvironmentVariable('COMSPEC', [NullString]::Value, 'Process')
    [Environment]::SetEnvironmentVariable('AUDIT_LOG', '', 'Process')
    $inherited = @{}
    foreach ($name in $names) { $inherited[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
    function Start-Process {
        $caseRoot = Join-Path $root 'copilot-warn-success-0'
        $expected = @{
            HOME = (Join-Path $caseRoot 'home'); USERPROFILE = (Join-Path $caseRoot 'home')
            APPDATA = (Join-Path $caseRoot 'home/AppData/Roaming')
            LOCALAPPDATA = (Join-Path $caseRoot 'home/AppData/Local')
            CODEX_HOME = (Join-Path $caseRoot 'home/.codex')
            XDG_CONFIG_HOME = (Join-Path $caseRoot 'home/.config')
            AUDIT_LOG = (Join-Path $caseRoot 'audit.log')
            OBSERVABILITY_LOG_PATH = (Join-Path $caseRoot 'observability.jsonl')
            COPILOT_OBSERVABILITY_LOG_PATH = (Join-Path $caseRoot 'observability.jsonl')
            GEMINI_OBSERVABILITY_LOG_PATH = (Join-Path $caseRoot 'observability.jsonl')
            OBSERVABILITY_TESTING = '1'; GIT_CONFIG_NOSYSTEM = '1'
            GIT_CONFIG_GLOBAL = (Join-Path $caseRoot 'gitconfig')
            SECRETS_LOG_DIR = (Join-Path $caseRoot 'logs'); TEMP = $caseRoot; TMP = $caseRoot
            SCAN_MODE = 'warn'
        }
        foreach ($name in $expected.Keys) {
            if ([Environment]::GetEnvironmentVariable($name, 'Process') -cne $expected[$name]) {
                throw "Fixture did not isolate $name"
            }
        }
        throw 'fixture-observed'
    }
    try { Invoke-Case -Provider copilot -Mode warn -Scenario success; throw 'Fixture did not execute' }
    catch { if ($_.Exception.Message -cne 'fixture-observed') { throw } }
    foreach ($name in $names) {
        if ([Environment]::GetEnvironmentVariable($name, 'Process') -cne $inherited[$name]) {
            throw "Fixture did not restore $name"
        }
    }
    foreach ($name in $original.Keys) { [Environment]::SetEnvironmentVariable($name, $(if ($null -eq $original[$name]) { [NullString]::Value } else { $original[$name] }), 'Process') }

    $runner = Join-Path $root 'diagnostic.py'
    Write-DiagnosticRunner -Target $hooks.copilot -Runner $runner
    $result = & $python -I -S -B $runner
    if ($LASTEXITCODE -ne 0 -or $result -cne 'fixture') { throw 'Diagnostic wrapper changed hook execution' }
    # Cancellation is observable: returning from the hook must not leave the timer armed.
    $cancelProbe = Join-Path $root 'cancel.py'
    $literal = $runner | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText($cancelProbe, "import runpy,time`nrunpy.run_path($literal,run_name='__main__')`ntime.sleep(7)`n")
    $cancelError = Join-Path $root 'cancel-stderr.txt'
    & $python -I -S -B $cancelProbe 2> $cancelError | Out-Null
    if ($LASTEXITCODE -ne 0 -or (Get-Item -LiteralPath $cancelError).Length -ne 0) { throw 'Diagnostic timer was not cancelled' }

    # Exercise real faulthandler output, including its omission of local values.
    [System.IO.File]::WriteAllText($hooks.copilot, "import time`nprivate_local='stack-private-local'`ntime.sleep(7)`n")
    $traceError = Join-Path $root 'trace-stderr.txt'
    & $python -I -S -B $runner 2> $traceError | Out-Null
    $trace = Get-Content -LiteralPath $traceError -Raw
    if ($LASTEXITCODE -ne 0 -or $trace -notmatch 'Timeout \(0:00:06\.500000\)!' -or $trace -match 'stack-private-local') { throw 'Real traceback was missing or exposed locals' }
    $realEvidence = @(Write-WatchdogEvidence -Provider gemini -Mode block -Scenario partial -ElapsedSeconds 8 -OutputPath (Join-Path $root 'missing') -ErrorPath $traceError -LogPath (Join-Path $root 'missing-log')) -join "`n"
    if ($realEvidence -notmatch 'WATCHDOG-STACK:   File' -or $realEvidence -match 'stack-private-local') { throw 'Real traceback frames were not safely retained' }

    $outputPath = Join-Path $root 'stdout.txt'
    $errorPath = Join-Path $root 'stderr.txt'
    $logPath = Join-Path $root 'scan.log'
    [System.IO.File]::WriteAllText($outputPath, 'private-output')
    [System.IO.File]::WriteAllText($errorPath, "private-error`nTimeout (0:00:06.500000)!`nThread 0x123 (most recent call first):`n  File `"fixture.py`", line 12 in wait`nprivate-local-value`n" + ('x' * 20000))
    [System.IO.File]::WriteAllText($logPath, '{"status":"incomplete","private":"private-audit"}')
    $evidence = @(Write-WatchdogEvidence -Provider copilot -Mode warn -Scenario partial -ElapsedSeconds 8.01 -OutputPath $outputPath -ErrorPath $errorPath -LogPath $logPath) -join "`n"
    if ($evidence -notmatch 'provider=copilot mode=warn scenario=partial elapsed-seconds=8\.010 stdout-bytes=14 stderr-bytes=\d+ audit=incomplete') { throw 'Watchdog evidence omitted fixed case metadata' }
    if ($evidence -notmatch 'File "fixture.py", line 12 in wait' -or $evidence -match 'private-|x{20}' -or $evidence.Length -gt 10000) { throw 'Watchdog evidence was unsafe or lost bounded stack frames' }
    Remove-Item -LiteralPath $outputPath, $errorPath, $logPath
    $missing = @(Write-WatchdogEvidence -Provider codex -Mode block -Scenario partial -ElapsedSeconds 8 -OutputPath $outputPath -ErrorPath $errorPath -LogPath $logPath) -join "`n"
    if ($missing -notmatch 'stdout-bytes=0 stderr-bytes=0 audit=missing-or-other') { throw 'Missing watchdog artifacts hid metadata' }

    $pwsh = (Get-Process -Id $PID).Path
    $selectionError = Join-Path $root 'selection-stderr.txt'
    & $pwsh -NoProfile -File $suite -Case 'copilot/warn/typo' 2> $selectionError | Out-Null
    if ($LASTEXITCODE -eq 0 -or (Get-Content -LiteralPath $selectionError -Raw) -notmatch 'ValidateSet|Cannot validate argument') { throw 'Unknown focused selection was not rejected by validation' }
    Write-Output 'PASS: native Windows scanner fixture isolation and diagnostics contracts'
}
finally {
    foreach ($name in $original.Keys) { [Environment]::SetEnvironmentVariable($name, $(if ($null -eq $original[$name]) { [NullString]::Value } else { $original[$name] }), 'Process') }
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
