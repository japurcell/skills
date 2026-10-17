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

$failureDiagnostic = Join-Path $workdir 'fixture-failure.py'

function Write-FixtureFailure {
    param([string]$CaseDir, [int]$ExitCode)
    # This runs only after a fixture failed, outside the measured hook process.
    & $python -I -S -B $failureDiagnostic $CaseDir ([string]$ExitCode) 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Output '{"schema":"w2_fixture_failure_v1","collector":"unavailable"}'
    }
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

    $executionMarker = Join-Path $caseDir 'fixture-executed'
    $imageObserver = Join-Path $caseDir 'observe-image-pin.py'
    if ($Scenario -eq 'image-pin') {
        $imageDirectory = Join-Path $caseDir 'image-system'
        New-Item -ItemType Directory -Path $imageDirectory | Out-Null
        [System.IO.File]::WriteAllText((Join-Path $imageDirectory 'cmd.exe'), "disposable non-image fixture`n")
        New-Item -ItemType HardLink -Path (Join-Path $imageDirectory 'alias.exe') -Target (Join-Path $imageDirectory 'cmd.exe') | Out-Null
        [System.IO.File]::WriteAllText($imageObserver, @'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
image = root / 'image-system' / 'cmd.exe'
alias = image.with_name('alias.exe')
try:
    report = json.loads((root / 'image-pin.json').read_text(encoding='ascii'))
    if report != {'write_alias':32, 'rename_leaf':32, 'rename_parent':32}:
        raise SystemExit(3)
    if image.stat().st_nlink != 2 or image.read_bytes() != b'disposable non-image fixture\n':
        raise SystemExit(4)
    with alias.open('r+b'):
        pass
    renamed = image.with_name('renamed.exe')
    image.rename(renamed)
    renamed.rename(image)
    renamed_directory = image.parent.with_name('renamed-system')
    image.parent.rename(renamed_directory)
    renamed_directory.rename(image.parent)
except Exception:
    raise SystemExit(2)
'@)
    }
    $grandchildMarker = Join-Path $caseDir 'grandchild.json'
    $grandchildRunner = Join-Path $caseDir 'grandchild.py'
    $grandchildObserver = Join-Path $caseDir 'observe-grandchild.py'
    if ($Scenario -eq 'grandchild' -or $Scenario -eq 'launch-death') {
        [System.IO.File]::WriteAllText($grandchildRunner, @'
import subprocess, sys
middle = r"""
import pathlib, subprocess, sys, time
grandchild = r'''
import ctypes, json, os, pathlib, sys, time
kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.GetCurrentProcess.restype = ctypes.c_void_p
kernel.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_uint64)] * 4
kernel.GetProcessTimes.restype = ctypes.c_int
times = [ctypes.c_uint64() for _ in range(4)]
if not kernel.GetProcessTimes(kernel.GetCurrentProcess(), *(ctypes.byref(item) for item in times)):
    raise SystemExit(3)
marker = pathlib.Path(sys.argv[1])
writing = marker.with_suffix('.writing')
writing.write_text(json.dumps({'pid': os.getpid(), 'created': times[0].value}), encoding='ascii')
writing.replace(marker)
time.sleep(60)
'''
child = subprocess.Popen([sys.executable, '-I', '-S', '-B', '-c', grandchild, sys.argv[1]],
                         stdin=subprocess.DEVNULL)
deadline = time.monotonic() + 4
while not pathlib.Path(sys.argv[1]).exists():
    if child.poll() is not None or time.monotonic() >= deadline:
        raise SystemExit(3)
    time.sleep(0.01)
"""
# The intermediate exits and is reaped before the Git root emits valid output.
# The long-lived grandchild keeps the root's capture handle open.
subprocess.run([sys.executable, '-I', '-S', '-B', '-c', middle, sys.argv[1]], check=True)
print('true', flush=True)
'@)
        [System.IO.File]::WriteAllText($grandchildObserver, @'
import ctypes, json, pathlib, sys
record = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='ascii'))
if (type(record) is not dict or record.keys() != {'pid', 'created'}
        or type(record['pid']) is not int or not 0 < record['pid'] < 2**32
        or type(record['created']) is not int or record['created'] <= 0):
    raise SystemExit(3)
kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
kernel.OpenProcess.restype = ctypes.c_void_p
kernel.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_uint64)] * 4
kernel.GetProcessTimes.restype = ctypes.c_int
kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
kernel.WaitForSingleObject.restype = ctypes.c_uint32
kernel.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
kernel.TerminateProcess.restype = ctypes.c_int
kernel.CloseHandle.argtypes = [ctypes.c_void_p]
kernel.CloseHandle.restype = ctypes.c_int
# SYNCHRONIZE | QUERY_LIMITED_INFORMATION | TERMINATE. PID reuse is refused
# using creation FILETIME read on this same held process handle.
handle = kernel.OpenProcess(0x00101001, False, record['pid'])
if not handle:
    raise SystemExit(0 if ctypes.get_last_error() == 87 else 3)
try:
    times = [ctypes.c_uint64() for _ in range(4)]
    if not kernel.GetProcessTimes(handle, *(ctypes.byref(item) for item in times)):
        raise SystemExit(3)
    if times[0].value != record['created']:
        raise SystemExit(3)
    state = kernel.WaitForSingleObject(handle, 0)
    if state == 0:
        raise SystemExit(0)
    if state != 258:
        raise SystemExit(3)
    if sys.argv[2] == 'inspect':
        raise SystemExit(1)
    if sys.argv[2] != 'cleanup':
        raise SystemExit(3)
    if not kernel.TerminateProcess(handle, 99) and kernel.WaitForSingleObject(handle, 0) != 0:
        raise SystemExit(3)
    raise SystemExit(0 if kernel.WaitForSingleObject(handle, 1000) == 0 else 2)
finally:
    kernel.CloseHandle(handle)
'@)
    }
    $shim = switch ($Scenario) {
        'hardlinked-batch' { "@echo off`r`necho executed > `"$executionMarker`"`r`n`"$realGit`" %*" }
        'image-pin' { "@echo off`r`n`"$realGit`" %*" }
        'hostile-comspec' { "@echo off`r`n`"$realGit`" %*" }
        'launch-death' { "@echo off`r`n`"$realGit`" %*" }
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
    if ($Scenario -eq 'hardlinked-batch') {
        New-Item -ItemType HardLink -Path (Join-Path $bin 'alias.cmd') -Target (Join-Path $bin 'git.cmd') | Out-Null
    }
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
    $savedComspec = $env:COMSPEC
    $savedLog = $env:SECRETS_LOG_DIR
    $savedTemp = $env:TEMP
    $savedTmp = $env:TMP
    try {
        $env:PATH = "$bin;$savedPath"
        $env:SCAN_MODE = $Mode
        if ($Scenario -eq 'hostile-comspec') {
            $hostileComspec = Join-Path $caseDir 'hostile-comspec.cmd'
            [System.IO.File]::WriteAllText($hostileComspec, "@echo off`r`necho executed > `"$executionMarker`"`r`nexit /b 9")
            $env:COMSPEC = $hostileComspec
        }
        $env:SECRETS_LOG_DIR = Join-Path $caseDir 'logs'
        $env:TEMP = $caseDir
        $env:TMP = $caseDir
        $started = [Diagnostics.Stopwatch]::StartNew()
        $runner = $hooks[$Provider]
        if ($Diagnostic -and $Scenario -notin @('launch-death', 'image-pin')) {
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
        } elseif ($Scenario -eq 'launch-death') {
            $runner = Join-Path $caseDir 'launch-death.py'
            $hookLiteral = $hooks[$Provider] | ConvertTo-Json -Compress
            $markerLiteral = $grandchildMarker | ConvertTo-Json -Compress
            $fixture = @'
import ctypes, json, os, pathlib, runpy
class Information(ctypes.Structure):
    _fields_ = [('process', ctypes.c_void_p), ('thread', ctypes.c_void_p),
                ('pid', ctypes.c_uint32), ('tid', ctypes.c_uint32)]
original_library = ctypes.WinDLL
observer = original_library('kernel32', use_last_error=True)
observer.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_uint64)] * 4
observer.GetProcessTimes.restype = ctypes.c_int
class CreateProcessBoundary:
    def __init__(self, function):
        self.function = function
    @property
    def argtypes(self):
        return self.function.argtypes
    @argtypes.setter
    def argtypes(self, value):
        self.function.argtypes = value
    @property
    def restype(self):
        return self.function.restype
    @restype.setter
    def restype(self, value):
        self.function.restype = value
    def __call__(self, *arguments):
        result = self.function(*arguments)
        if result:
            # The real kernel returned a real suspended child. End the public
            # scanner process before its next post-creation Python operation.
            information = ctypes.cast(arguments[-1], ctypes.POINTER(Information)).contents
            times = [ctypes.c_uint64() for _ in range(4)]
            if not observer.GetProcessTimes(information.process, *(ctypes.byref(item) for item in times)):
                os._exit(98)
            marker = pathlib.Path(MARKER_LITERAL)
            writing = marker.with_suffix('.writing')
            writing.write_text(json.dumps({'pid': int(information.pid), 'created': times[0].value}), encoding='ascii')
            writing.replace(marker)
            os._exit(99)
        return result
class Library:
    def __init__(self, library):
        self.library = library
        self.create = CreateProcessBoundary(library.CreateProcessW)
    def __getattr__(self, name):
        return self.create if name == 'CreateProcessW' else getattr(self.library, name)
def library(name, *arguments, **keywords):
    result = original_library(name, *arguments, **keywords)
    return Library(result) if name.casefold() == 'kernel32' else result
ctypes.WinDLL = library
runpy.run_path(HOOK_LITERAL, run_name='__main__')
'@
            $fixture = $fixture.Replace('HOOK_LITERAL', $hookLiteral).Replace('MARKER_LITERAL', $markerLiteral)
            [System.IO.File]::WriteAllText($runner, $fixture)
        } elseif ($Scenario -eq 'image-pin') {
            $runner = Join-Path $caseDir 'image-pin.py'
            $hookLiteral = $hooks[$Provider] | ConvertTo-Json -Compress
            $rootLiteral = $caseDir | ConvertTo-Json -Compress
            $fixture = @'
import ctypes, json, os, pathlib, runpy
root = pathlib.Path(ROOT_LITERAL)
image = root / 'image-system' / 'cmd.exe'
alias = image.with_name('alias.exe')
marker = root / 'image-pin.json'
original_library = ctypes.WinDLL
observer = original_library('kernel32', use_last_error=True)
observer.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
observer.CreateFileW.restype = ctypes.c_void_p
observer.CloseHandle.argtypes = [ctypes.c_void_p]
observer.CloseHandle.restype = ctypes.c_int
class Function:
    def __init__(self, function):
        self.function = function
    @property
    def argtypes(self):
        return self.function.argtypes
    @argtypes.setter
    def argtypes(self, value):
        self.function.argtypes = value
    @property
    def restype(self):
        return self.function.restype
    @restype.setter
    def restype(self, value):
        self.function.restype = value
class SystemDirectory(Function):
    def __call__(self, buffer, count):
        directory = str(image.parent)
        if count <= len(directory):
            return len(directory) + 1
        buffer.value = directory
        return len(directory)
class CreateProcessBoundary(Function):
    def __call__(self, *arguments):
        # Refuse to probe any non-fixture image, including the real OS image.
        if arguments[0] != str(image):
            os._exit(97)
        report = {}
        handle = observer.CreateFileW(str(alias), 0x40000000, 7, None, 3, 0, None)
        if handle == ctypes.c_void_p(-1).value:
            report['write_alias'] = ctypes.get_last_error()
        else:
            observer.CloseHandle(handle)
            report['write_alias'] = 0
        for name, source, destination in (
                ('rename_leaf', image, image.with_name('renamed.exe')),
                ('rename_parent', image.parent, image.parent.with_name('renamed-system'))):
            try:
                os.rename(source, destination)
            except OSError as error:
                report[name] = error.winerror or 0
            else:
                os.rename(destination, source)
                report[name] = 0
        marker.write_text(json.dumps(report), encoding='ascii')
        # Forward to the real API. Disposable non-image content must fail launch.
        return self.function(*arguments)
class Library:
    def __init__(self, library):
        self.library = library
        self.create = CreateProcessBoundary(library.CreateProcessW)
        self.system = SystemDirectory(library.GetSystemDirectoryW)
    def __getattr__(self, name):
        if name == 'CreateProcessW':
            return self.create
        if name == 'GetSystemDirectoryW':
            return self.system
        return getattr(self.library, name)
def library(name, *arguments, **keywords):
    result = original_library(name, *arguments, **keywords)
    return Library(result) if name.casefold() == 'kernel32' else result
ctypes.WinDLL = library
runpy.run_path(HOOK_LITERAL, run_name='__main__')
'@
            $fixture = $fixture.Replace('HOOK_LITERAL', $hookLiteral).Replace('ROOT_LITERAL', $rootLiteral)
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
        if ($Scenario -eq 'launch-death') {
            if ($process.ExitCode -ne 99 -or -not (Test-Path -LiteralPath $grandchildMarker)) {
                Write-FixtureFailure -CaseDir $caseDir -ExitCode $process.ExitCode
                throw "$Provider $Mode launch-death did not reach the real post-create boundary: $($process.ExitCode)"
            }
            & $python -I -S -B $grandchildObserver $grandchildMarker inspect
            $observed = $LASTEXITCODE
            if ($observed -eq 1) { throw "$Provider $Mode launch-death left owned suspended root alive" }
            if ($observed -ne 0) { throw "$Provider $Mode launch-death ownership check failed: $observed" }
            if ($started.Elapsed.TotalSeconds -ge 8) { throw "$Provider $Mode $Scenario was too slow" }
            $leaked = @(Get-ChildItem -LiteralPath $caseDir -Filter 'tmp*')
            if ($leaked.Count) { throw "$Provider $Mode $Scenario leaked capture files: $($leaked.Name -join ', ')" }
            return
        }
        if ($process.ExitCode -ne 0) { throw "$Provider $Mode $Scenario exited $($process.ExitCode)" }
        if ($started.Elapsed.TotalSeconds -ge 8) { throw "$Provider $Mode $Scenario was too slow" }
        if ($Scenario -eq 'grandchild') {
            if (-not (Test-Path -LiteralPath $grandchildMarker)) {
                Write-FixtureFailure -CaseDir $caseDir -ExitCode $process.ExitCode
                throw "$Provider grandchild fixture did not execute"
            }
            & $python -I -S -B $grandchildObserver $grandchildMarker inspect
            $observed = $LASTEXITCODE
            if ($observed -eq 1) { throw "$Provider $Mode grandchild left owned descendant alive" }
            if ($observed -ne 0) { throw "$Provider $Mode grandchild ownership check failed: $observed" }
        }
        if ($Scenario -eq 'image-pin') {
            & $python -I -S -B $imageObserver $caseDir
            if ($LASTEXITCODE -ne 0) {
                Write-FixtureFailure -CaseDir $caseDir -ExitCode $process.ExitCode
                throw "$Provider $Mode disposable image pin sharing or lifetime control failed"
            }
        }
        if ($Scenario -in @('hardlinked-batch', 'hostile-comspec') -and (Test-Path -LiteralPath $executionMarker)) {
            throw "$Provider $Mode $Scenario executed the refused fixture"
        }
        $response = Get-Content -LiteralPath $outputPath -Raw | ConvertFrom-Json -AsHashtable
        if ($Scenario -eq 'capture-error' -and ((Get-Content -LiteralPath $outputPath -Raw) -match 'private capture failure detail')) {
            throw "$Provider leaked a capture error"
        }
        $logPath = Join-Path $caseDir 'logs/scan.log'
        $log = if (Test-Path -LiteralPath $logPath) { Get-Content -LiteralPath $logPath -Raw } else { '' }
        if ($Scenario -in @('success', 'hostile-comspec')) {
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
            if ($Scenario -eq 'hardlinked-batch') {
                $record = $log.Trim() | ConvertFrom-Json -AsHashtable
                if ($record.diagnostic.cause -ne 'git_capture_failed' -or $record.diagnostic.capture_step -ne 'spawn' -or
                    $record.diagnostic.os_errno -ne 10062) {
                    throw "$Provider $Mode hardlinked batch did not retain the original single-link refusal"
                }
            }
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
        $cleanupCode = 0
        if (($Scenario -eq 'grandchild' -or $Scenario -eq 'launch-death') -and (Test-Path -LiteralPath $grandchildMarker)) {
            & $python -I -S -B $grandchildObserver $grandchildMarker cleanup
            $cleanupCode = $LASTEXITCODE
        }
        $env:PATH = $savedPath
        $env:SCAN_MODE = $savedMode
        $env:COMSPEC = $savedComspec
        $env:SECRETS_LOG_DIR = $savedLog
        $env:TEMP = $savedTemp
        $env:TMP = $savedTmp
        if ($cleanupCode -ne 0) { throw "$Provider $Mode grandchild cleanup refused or failed: $cleanupCode" }
    }
}

try {
    New-Item -ItemType Directory -Path $workdir | Out-Null
    [System.IO.File]::WriteAllText($failureDiagnostic, @'
import json, os, pathlib, sys

def collect_audit(root):
    result = dict(state='missing', status='unknown', cause='unknown', operation='unknown',
                  capture_step='unknown', os_errno=-1)
    path = root / 'logs' / 'scan.log'
    try:
        if not path.exists():
            return result
        if not 0 < path.stat().st_size <= 65536:
            result['state'] = 'size_refused'
            return result
        with path.open('rb') as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            result['state'] = 'size_refused'
            return result
        value = json.loads(raw.splitlines()[-1])
        if type(value) is not dict:
            raise ValueError
        result['state'] = 'present'
        if value.get('status') in {'clean', 'findings', 'incomplete'}:
            result['status'] = value['status']
        diagnostic = value.get('diagnostic')
        if type(diagnostic) is not dict:
            return result
        allowed = dict(
            cause={'git_unavailable', 'git_failed', 'git_capture_failed', 'git_descendant_running',
                   'git_head_invalid', 'git_output_invalid', 'repository_unavailable', 'scan_timeout',
                   'git_timeout', 'git_output_limit', 'internal_error', 'input_invalid', 'audit_unavailable'},
            operation={'initialization', 'input', 'repository', 'git_repository', 'git_head',
                       'git_candidates', 'git_index', 'git_diff', 'git_command', 'candidate_read',
                       'candidate_scan', 'scan_log'},
            capture_step={'temporary_file', 'verify_capture', 'request_write', 'spawn', 'wait',
                          'descendants', 'consume', 'cleanup'})
        for key, choices in allowed.items():
            if type(diagnostic.get(key)) is str and diagnostic[key] in choices:
                result[key] = diagnostic[key]
        number = diagnostic.get('os_errno')
        if type(number) is int and 0 <= number <= 0xFFFFFFFF:
            result['os_errno'] = number
    except Exception:
        result['state'] = 'invalid'
    return result

def native_metadata(root):
    if os.name != 'nt':
        return []
    import ctypes
    dword, pointer = ctypes.c_uint32, ctypes.c_void_p
    class FileTime(ctypes.Structure):
        _fields_ = [('low', dword), ('high', dword)]
    class FileInformation(ctypes.Structure):
        _fields_ = [('attributes', dword), ('created', FileTime), ('accessed', FileTime),
                    ('written', FileTime), ('volume', dword), ('size_high', dword),
                    ('size_low', dword), ('links', dword), ('index_high', dword), ('index_low', dword)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetSystemDirectoryW.argtypes = [ctypes.c_wchar_p, dword]
    kernel.GetSystemDirectoryW.restype = dword
    kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, dword, dword, pointer, dword, dword, pointer]
    kernel.CreateFileW.restype = pointer
    kernel.GetFileInformationByHandle.argtypes = [pointer, ctypes.POINTER(FileInformation)]
    kernel.GetFileInformationByHandle.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = [pointer]
    kernel.CloseHandle.restype = ctypes.c_int
    directory = ctypes.create_unicode_buffer(32768)
    length = kernel.GetSystemDirectoryW(directory, len(directory))
    system_error = ctypes.get_last_error() if not length else 0
    files = [(1, root / 'bin' / 'git.cmd'),
             (2, pathlib.Path(directory.value) / 'cmd.exe' if 0 < length < len(directory) else None)]
    result = []
    for slot, path in files:
        record = dict(slot=slot, opened=0, links=0, attributes=0, os_error=0)
        result.append(record)
        if path is None:
            record['os_error'] = system_error or 122
            continue
        # Read attributes only, OPEN_EXISTING and OPEN_REPARSE_POINT. No mutation.
        handle = kernel.CreateFileW(str(path), 0x80, 7, None, 3, 0x00200000, None)
        if handle == pointer(-1).value:
            record['os_error'] = ctypes.get_last_error()
            continue
        try:
            information = FileInformation()
            if not kernel.GetFileInformationByHandle(handle, ctypes.byref(information)):
                record['os_error'] = ctypes.get_last_error()
            else:
                record.update(opened=1, links=int(information.links), attributes=int(information.attributes))
        finally:
            if not kernel.CloseHandle(handle):
                record['os_error'] = ctypes.get_last_error()
    return result

try:
    root = pathlib.Path(sys.argv[1])
    exit_code = int(sys.argv[2])
    if not -2147483648 <= exit_code <= 0xFFFFFFFF:
        exit_code = -1
    report = dict(schema='w2_fixture_failure_v1', hook_exit=exit_code,
                  audit=collect_audit(root), files=native_metadata(root))
except BaseException:
    report = dict(schema='w2_fixture_failure_v1', collector='unavailable')
print(json.dumps(report, sort_keys=True, separators=(',', ':')))
'@)
    foreach ($provider in @('copilot', 'gemini', 'codex')) {
        foreach ($mode in @('block', 'warn')) {
            foreach ($scenario in @('hardlinked-batch', 'image-pin', 'hostile-comspec', 'grandchild', 'launch-death', 'descendant', 'partial', 'oversized', 'nonzero', 'head-failure', 'malformed', 'capture-error', 'success')) {
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
