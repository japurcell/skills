#!/usr/bin/env pwsh

param([switch]$Diagnostic)

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
    param([string]$Provider, [string]$Mode, [string]$Scenario, [int]$Attempt = 0)
    $caseDir = Join-Path $workdir "$Provider-$Mode-$Scenario-$Attempt"
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

    $grandchildMarker = Join-Path $caseDir 'grandchild.pid'
    $grandchildRunner = Join-Path $caseDir 'grandchild.py'
    if ($Scenario -eq 'grandchild') {
        [System.IO.File]::WriteAllText($grandchildRunner, @'
import subprocess, sys
middle = """
import pathlib, subprocess, sys
child = subprocess.Popen([sys.executable, '-I', '-S', '-B', '-c', 'import time; time.sleep(60)'],
                         stdin=subprocess.DEVNULL)
pathlib.Path(sys.argv[1]).write_text(str(child.pid), encoding='ascii')
"""
# The intermediate exits and is reaped before the Git root emits valid output.
# The long-lived grandchild keeps the root's capture handle open.
subprocess.run([sys.executable, '-I', '-S', '-B', '-c', middle, sys.argv[1]], check=True)
print('true', flush=True)
'@)
    }
    $shim = switch ($Scenario) {
        'grandchild' { "@echo off`r`nif `"%1 %2`"==`"rev-parse --is-inside-work-tree`" (`"$python`" -I -S -B `"$grandchildRunner`" `"$grandchildMarker`" & exit /b 0)`r`n`"$realGit`" %*" }
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
    if ($Provider -eq 'copilot') {
        $payload = if ($Mode -eq 'block') {
            @{
                sessionId = 'capture-windows'
                timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
                cwd = $repo
                toolName = 'bash'
                toolArgs = @{ command = 'git status --short' }
            }
        } else {
            @{
                sessionId = 'capture-windows'
                timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
                cwd = $repo
                reason = 'complete'
            }
        }
    } else {
        $event = if ($Mode -eq 'block') {
            if ($Provider -eq 'gemini') { 'BeforeTool' } else { 'PreToolUse' }
        } else {
            if ($Provider -eq 'gemini') { 'SessionEnd' } else { 'Stop' }
        }
        $payload = @{ hook_event_name = $event; session_id = 'capture-windows'; cwd = $repo; reason = 'complete' }
    }
    $payload = $payload | ConvertTo-Json -Compress
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
        if ($Diagnostic) {
            $runner = Join-Path $caseDir 'capture-fixture.py'
            $hookLiteral = $hooks[$Provider] | ConvertTo-Json -Compress
            $captureErrorLiteral = if ($Scenario -eq 'capture-error') { 'True' } else { 'False' }
            $fixture = @'
import ast, ctypes, os, pathlib, runpy, subprocess, sys, tempfile, time
hook = pathlib.Path(HOOK_LITERAL)
source = hook.parent / "helpers" / "scan_git.py"
phase_lines = {node.lineno for node in ast.walk(ast.parse(source.read_text(encoding="utf-8")))
               if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
               and target.id == "capture_step" for target in node.targets)}
started = time.monotonic()
records = 0
kernel = ctypes.WinDLL("kernel32", use_last_error=True)
kernel.GetCurrentProcess.restype = ctypes.c_void_p
kernel.GetProcessHandleCount.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
kernel.GetProcessHandleCount.restype = ctypes.c_int
def emit(phase, pid=0, code=0):
    global records
    if records >= 128:
        return
    records += 1
    handles = ctypes.c_uint32()
    ok = kernel.GetProcessHandleCount(kernel.GetCurrentProcess(), ctypes.byref(handles))
    count = handles.value if ok else 0
    elapsed = int((time.monotonic() - started) * 1000)
    print(f"W2 phase={phase} pid={pid} code={code} handles={count} ms={elapsed}", file=sys.stderr, flush=True)
original_popen = subprocess.Popen
class ObservedPopen(original_popen):
    def __init__(self, *args, **kwargs):
        emit(8001)
        try:
            super().__init__(*args, **kwargs)
        except OSError as error:
            emit(8003, code=error.winerror or error.errno or 0)
            raise
        emit(8002, pid=self.pid)
subprocess.Popen = ObservedPopen
def trace(frame, event, argument):
    if not frame.f_code.co_filename.endswith(("/scan_git.py", "\\scan_git.py")):
        return None
    name = frame.f_code.co_name
    if name == "capture_git" and event == "line" and frame.f_lineno in phase_lines:
        emit(frame.f_lineno)
    elif name in {"_windows_git_descendants", "_stop_git_process"} and event in {"call", "return"}:
        emit((9000 if name == "_windows_git_descendants" else 9100) + (1 if event == "call" else 2))
    return trace
if CAPTURE_ERROR_LITERAL:
    def fail(*args, **kwargs):
        raise OSError("private capture failure detail")
    tempfile.TemporaryFile = fail
def audit(event, arguments):
    if event == "exec":
        filename = arguments[0].co_filename
        if filename == str(hook):
            emit(10)
        elif filename.endswith(("/common.py", "\\common.py")):
            emit(11)
        elif filename.endswith(("/scan_engine.py", "\\scan_engine.py")):
            emit(12)
        elif filename.endswith(("/scan_git.py", "\\scan_git.py")):
            emit(13)
emit(1, pid=os.getpid())
sys.addaudithook(audit)
sys.settrace(trace)
try:
    runpy.run_path(str(hook), run_name="__main__")
finally:
    sys.settrace(None)
    emit(2, pid=os.getpid())
'@
            $fixture = $fixture.Replace('HOOK_LITERAL', $hookLiteral).Replace('CAPTURE_ERROR_LITERAL', $captureErrorLiteral)
            [System.IO.File]::WriteAllText($runner, $fixture)
        } elseif ($Scenario -eq 'capture-error') {
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
            # Fixture diagnostics are numeric and bounded. Never publish raw hook stderr.
            Get-Content -LiteralPath $errorPath | Where-Object {
                $_ -cmatch '^W2 phase=[0-9]+ pid=[0-9]+ code=[0-9]+ handles=[0-9]+ ms=[0-9]+$'
            } | Select-Object -First 128 | ForEach-Object { Write-Output $_ }
            throw "$Provider $Mode $Scenario exceeded outer watchdog"
        }
        $started.Stop()
        if ($Provider -eq 'gemini' -and $Mode -eq 'block' -and $Scenario -eq 'partial') {
            Get-Content -LiteralPath $errorPath | Where-Object {
                $_ -cmatch '^W2 phase=[0-9]+ pid=[0-9]+ code=[0-9]+ handles=[0-9]+ ms=[0-9]+$'
            } | Select-Object -First 128 | ForEach-Object { Write-Output $_ }
        }
        if ($process.ExitCode -ne 0) { throw "$Provider $Mode $Scenario exited $($process.ExitCode)" }
        if ($started.Elapsed.TotalSeconds -ge 8) { throw "$Provider $Mode $Scenario was too slow" }
        if ($Scenario -eq 'grandchild') {
            if (-not (Test-Path -LiteralPath $grandchildMarker)) { throw "$Provider grandchild fixture did not execute" }
            $grandchildPid = [int][System.IO.File]::ReadAllText($grandchildMarker)
            $survivor = Get-Process -Id $grandchildPid -ErrorAction SilentlyContinue
            if ($null -ne $survivor -and -not $survivor.HasExited) {
                throw "$Provider $Mode grandchild left owned descendant alive: $grandchildPid"
            }
        }
        $response = Get-Content -LiteralPath $outputPath -Raw | ConvertFrom-Json -AsHashtable
        if ($Scenario -eq 'capture-error' -and ((Get-Content -LiteralPath $outputPath -Raw) -match 'private capture failure detail')) {
            throw "$Provider leaked a capture error"
        }
        $logPath = Join-Path $caseDir 'logs/scan.log'
        $log = if (Test-Path -LiteralPath $logPath) { Get-Content -LiteralPath $logPath -Raw } else { '' }
        if ($Scenario -eq 'success') {
            $responseType = if ($response -is [System.Collections.IDictionary]) {
                'object'
            } elseif ($response -is [array]) {
                'array'
            } elseif ($null -eq $response) {
                'null'
            } else {
                'scalar'
            }
            $responseCount = if ($response -is [System.Collections.IDictionary] -or $response -is [array]) {
                $response.Count
            } else {
                0
            }
            $hasSystemMessage = $response -is [System.Collections.IDictionary] -and $response.Contains('systemMessage')
            $stdoutBytes = (Get-Item -LiteralPath $outputPath).Length
            $stderrBytes = (Get-Item -LiteralPath $errorPath).Length
            $auditState = if ($log -match '"status":"clean"') {
                'clean'
            } elseif ($log -match '"status":"incomplete"') {
                'incomplete'
            } elseif ($log -match '"status":"findings"') {
                'findings'
            } else {
                'missing-or-other'
            }
            $diagnostic = "response=$responseType fields=$responseCount has-systemMessage=$hasSystemMessage stdout-bytes=$stdoutBytes stderr-bytes=$stderrBytes audit=$auditState"
            $cleanResponse = if ($Provider -eq 'codex' -and $Mode -eq 'warn') {
                $response.Count -eq 1 -and $response.systemMessage -ceq 'scan-secrets: pass; 0 modified files'
            } else {
                $response.Count -eq 0
            }
            if (-not $cleanResponse) { throw "$Provider $Mode no-HEAD response failed ($diagnostic)" }
            if ($log -notmatch '"status":"clean"') { throw "$Provider $Mode no-HEAD audit failed ($diagnostic)" }
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
        if ($leaked.Count) {
            try {
                $active = @(Get-CimInstance Win32_Process -ErrorAction Stop |
                    Where-Object {
                        $commandLine = [string]$_.CommandLine
                        $commandLine.Contains($caseDir) -or
                            ($_.Name -ieq 'ping.exe' -and $commandLine.Contains('127.0.0.1')) -or
                            ($_.Name -ieq 'powershell.exe' -and $commandLine.Contains('8388609'))
                    } |
                    Select-Object -First 12 |
                    ForEach-Object { "$($_.Name):$($_.ProcessId)/$($_.ParentProcessId)" })
            } catch {
                $active = @('snapshot unavailable')
            }
            $processes = if ($active.Count) { $active -join ', ' } else { 'none' }
            throw "$Provider $Mode $Scenario leaked capture files: $($leaked.Name -join ', '); hook pid: $($process.Id); active process candidates: $processes"
        }
    }
    finally {
        if ($Scenario -eq 'grandchild' -and (Test-Path -LiteralPath $grandchildMarker)) {
            $grandchildPid = [int][System.IO.File]::ReadAllText($grandchildMarker)
            $owned = Get-Process -Id $grandchildPid -ErrorAction SilentlyContinue
            if ($null -ne $owned -and -not $owned.HasExited) {
                $owned.Kill()
                $owned.WaitForExit(1000) | Out-Null
            }
        }
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
            foreach ($scenario in @('grandchild', 'descendant', 'partial', 'oversized', 'nonzero', 'head-failure', 'malformed', 'capture-error', 'success')) {
                Invoke-Case -Provider $provider -Mode $mode -Scenario $scenario
            }
        }
    }
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        Invoke-Case -Provider gemini -Mode block -Scenario descendant -Attempt $attempt
        Invoke-Case -Provider gemini -Mode warn -Scenario oversized -Attempt $attempt
    }
    Write-Output 'PASS: native Windows generated scanner capture tests'
}
finally {
    Remove-Item -LiteralPath $workdir -Recurse -Force -ErrorAction SilentlyContinue
}
