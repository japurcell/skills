#!/usr/bin/env pwsh

$ErrorActionPreference = 'Stop'
if (-not $IsWindows) {
    Write-Output 'SKIP: native Windows scanner capture tests require Windows'
    exit 0
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python -CommandType Application | Select-Object -First 1).Source
$realGit = (Get-Command git -CommandType Application | Select-Object -First 1).Source
$workdir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
$hooks = @{
    copilot = Join-Path $repoRoot '.copilot/hooks/scripts/scan-secrets.py'
    gemini = Join-Path $repoRoot '.gemini/hooks/scripts/scan-secrets.py'
    codex = Join-Path $repoRoot '.codex/hooks/scan-secrets.py'
}

function Invoke-Case {
    param([string]$Provider, [string]$Mode, [string]$Scenario)
    $caseDir = Join-Path $workdir "$Provider-$Mode-$Scenario"
    $repo = Join-Path $caseDir 'repo'
    $bin = Join-Path $caseDir 'bin'
    New-Item -ItemType Directory -Path $repo, $bin | Out-Null
    & $realGit -C $repo init -q
    if ($LASTEXITCODE -ne 0) { throw 'Git init failed' }
    if ($Scenario -eq 'head-failure') {
        [System.IO.File]::WriteAllText((Join-Path $repo 'README.md'), "safe fixture`n")
        & $realGit -C $repo add README.md
        if ($LASTEXITCODE -ne 0) { throw 'Git add failed' }
        & $realGit -C $repo -c user.name=ScannerTest -c user.email=scanner@example.invalid -c commit.gpgsign=false commit -qm fixture
        if ($LASTEXITCODE -ne 0) { throw 'Git commit failed' }
    }

    $shim = switch ($Scenario) {
        'descendant' { '@echo off' + "`r`n" + 'if "%1 %2"=="rev-parse --is-inside-work-tree" (start "" /B cmd /c "ping -n 11 127.0.0.1 >nul" & echo true & exit /b 0)' + "`r`n" + 'exit /b 9' }
        'partial' { '@echo off' + "`r`n" + 'echo true' + "`r`n" + 'ping -n 11 127.0.0.1 >nul' }
        'oversized' { '@echo off' + "`r`n" + 'powershell -NoProfile -Command "$b = New-Object byte[] 8388609; [Console]::OpenStandardOutput().Write($b, 0, $b.Length)"' + "`r`n" + 'ping -n 11 127.0.0.1 >nul' }
        'nonzero' { "@echo off`r`nexit /b 9" }
        'head-failure' { "@echo off`r`nif `"%1 %2 %3`"==`"rev-parse --verify HEAD`" exit /b 128`r`n`"$realGit`" %*" }
        'malformed' { '@echo off' + "`r`n" + 'if "%1 %2"=="rev-parse --is-inside-work-tree" (echo true & exit /b 0)' + "`r`n" + 'if "%1 %2"=="rev-parse --show-toplevel" (echo %CD% & exit /b 0)' + "`r`n" + 'if "%1"=="diff" (echo partial-path & exit /b 0)' + "`r`n" + 'exit /b 9' }
        'capture-error' { "@echo off`r`n`"$realGit`" %*" }
        'success' { "@echo off`r`n`"$realGit`" %*" }
    }
    [System.IO.File]::WriteAllText((Join-Path $bin 'git.cmd'), $shim)
    $event = if ($Mode -eq 'block') {
        if ($Provider -eq 'gemini') { 'BeforeTool' } else { 'PreToolUse' }
    } else {
        if ($Provider -eq 'gemini') { 'SessionEnd' } else { 'Stop' }
    }
    $payload = @{ hook_event_name = $event; session_id = 'capture-windows'; cwd = $repo; reason = 'complete' } | ConvertTo-Json -Compress
    $inputPath = Join-Path $caseDir 'input.json'
    $outputPath = Join-Path $caseDir 'output.json'
    $errorPath = Join-Path $caseDir 'stderr.txt'
    [System.IO.File]::WriteAllText($inputPath, $payload)

    $savedPath = $env:PATH
    $savedMode = $env:SCAN_MODE
    $savedLog = $env:SECRETS_LOG_DIR
    $savedTemp = $env:TEMP
    $savedTmp = $env:TMP
    try {
        $env:PATH = "$bin;$savedPath"
        $env:SCAN_MODE = $Mode
        $env:SECRETS_LOG_DIR = Join-Path $caseDir 'logs'
        $env:TEMP = $caseDir
        $env:TMP = $caseDir
        $started = [Diagnostics.Stopwatch]::StartNew()
        $runner = $hooks[$Provider]
        if ($Scenario -eq 'capture-error') {
            $runner = Join-Path $caseDir 'capture-error.py'
            $hookLiteral = $hooks[$Provider] | ConvertTo-Json -Compress
            [System.IO.File]::WriteAllText($runner, "import runpy, tempfile`n" +
                "def fail(*args, **kwargs):`n    raise OSError('private capture failure detail')`n" +
                "tempfile.TemporaryFile = fail`nrunpy.run_path($hookLiteral, run_name='__main__')`n")
        }
        $process = Start-Process -FilePath $python -ArgumentList @('-I', '-S', '-B', "`"$runner`"") `
            -WorkingDirectory $repo -RedirectStandardInput $inputPath -RedirectStandardOutput $outputPath `
            -RedirectStandardError $errorPath -PassThru -NoNewWindow
        if (-not $process.WaitForExit(8000)) {
            $process.Kill($true)
            $process.WaitForExit(1000) | Out-Null
            throw "$Provider $Mode $Scenario exceeded outer watchdog"
        }
        $started.Stop()
        if ($process.ExitCode -ne 0) { throw "$Provider $Mode $Scenario exited $($process.ExitCode)" }
        if ($started.Elapsed.TotalSeconds -ge 8) { throw "$Provider $Mode $Scenario was too slow" }
        $response = Get-Content -LiteralPath $outputPath -Raw | ConvertFrom-Json -AsHashtable
        if ($Scenario -eq 'capture-error' -and ((Get-Content -LiteralPath $outputPath -Raw) -match 'private capture failure detail')) {
            throw "$Provider leaked a capture error"
        }
        $logPath = Join-Path $caseDir 'logs/scan.log'
        $log = if (Test-Path -LiteralPath $logPath) { Get-Content -LiteralPath $logPath -Raw } else { '' }
        if ($Scenario -eq 'success') {
            if ($response.Count -ne 0 -or $log -notmatch '"status":"clean"') { throw "$Provider $Mode no-HEAD scan failed" }
        } else {
            $rendered = $response | ConvertTo-Json -Compress
            if ($rendered -notmatch 'incomplete' -or $log -match '"status":"clean"' -or $log -notmatch '"status":"incomplete"') {
                throw "$Provider $Mode $Scenario returned a false clean result"
            }
            if ($Mode -eq 'block') {
                $decision = switch ($Provider) {
                    'codex' { $response.hookSpecificOutput.permissionDecision }
                    'gemini' { $response.decision }
                    'copilot' { $response.permissionDecision }
                }
                if ($decision -ne 'deny') { throw "$Provider $Scenario did not deny" }
            }
        }
        $leaked = @(Get-ChildItem -LiteralPath $caseDir -Filter 'tmp*')
        if ($leaked.Count) { throw "$Provider $Mode $Scenario leaked capture files: $($leaked.Name -join ', ')" }
    }
    finally {
        $env:PATH = $savedPath
        $env:SCAN_MODE = $savedMode
        $env:SECRETS_LOG_DIR = $savedLog
        $env:TEMP = $savedTemp
        $env:TMP = $savedTmp
    }
}

try {
    New-Item -ItemType Directory -Path $workdir | Out-Null
    foreach ($provider in @('copilot', 'gemini', 'codex')) {
        foreach ($mode in @('block', 'warn')) {
            foreach ($scenario in @('descendant', 'partial', 'oversized', 'nonzero', 'head-failure', 'malformed', 'capture-error', 'success')) {
                Invoke-Case -Provider $provider -Mode $mode -Scenario $scenario
            }
        }
    }
    Write-Output 'PASS: native Windows generated scanner capture tests'
}
finally {
    Remove-Item -LiteralPath $workdir -Recurse -Force -ErrorAction SilentlyContinue
}
