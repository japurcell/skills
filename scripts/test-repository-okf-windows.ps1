#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$source = @'
import collections, ctypes, json, os, pathlib, shutil, subprocess, sys, tempfile, threading, time
from ctypes import wintypes

source = pathlib.Path(sys.argv[1])
assert os.name == "nt", "native Windows execution required"

def report(phase, **values):
    print("W-OKF " + json.dumps({"phase": phase, **values}, separators=(",", ":")), file=sys.stderr, flush=True)


class InvocationObserver:
    """Read-only, bounded observation of this test's one registered invocation."""

    def __init__(self):
        class ProcessEntry(ctypes.Structure):
            _fields_ = [("size", wintypes.DWORD), ("usage", wintypes.DWORD),
                ("pid", wintypes.DWORD), ("heap", ctypes.c_size_t),
                ("module", wintypes.DWORD), ("threads", wintypes.DWORD),
                ("parent", wintypes.DWORD), ("priority", wintypes.LONG),
                ("flags", wintypes.DWORD), ("image", wintypes.WCHAR * 260)]
        self.entry_type = ProcessEntry
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        self.api.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        for name in ("Process32FirstW", "Process32NextW"):
            function = getattr(self.api, name)
            function.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
            function.restype = wintypes.BOOL
        self.api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.api.OpenProcess.restype = wintypes.HANDLE
        self.api.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4)]
        self.api.GetProcessTimes.restype = wintypes.BOOL
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.CloseHandle.restype = wintypes.BOOL
        self.api.GetSystemTimeAsFileTime.argtypes = [ctypes.POINTER(wintypes.FILETIME)]
        self.api.GetSystemTimeAsFileTime.restype = None
        self.parent = os.getpid()
        self.parent_created = self.created(self.parent)
        stamp = wintypes.FILETIME()
        self.api.GetSystemTimeAsFileTime(ctypes.byref(stamp))
        self.not_before = (stamp.dwHighDateTime << 32) | stamp.dwLowDateTime
        self.started = time.monotonic()
        self.known = {}
        self.root_pid = None
        self.rows = collections.deque(maxlen=8)
        self.changes = 0
        self.error = 0
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.observe, name="okf-fixture-observer")

    def created(self, pid):
        handle = self.api.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return None
        try:
            values = [wintypes.FILETIME() for _ in range(4)]
            if not self.api.GetProcessTimes(handle, *(ctypes.byref(value) for value in values)):
                return None
            return (values[0].dwHighDateTime << 32) | values[0].dwLowDateTime
        finally:
            self.api.CloseHandle(handle)

    def sample(self):
        handle = self.api.CreateToolhelp32Snapshot(2, 0)  # TH32CS_SNAPPROCESS
        if handle == ctypes.c_void_p(-1).value:
            self.error = ctypes.get_last_error()
            return
        try:
            # Repeat the same snapshot for at most four ancestry levels. Only
            # this invocation's identities are retained, never a host inventory.
            for _ in range(4):
                entry = self.entry_type()
                entry.size = ctypes.sizeof(entry)
                present = self.api.Process32FirstW(handle, ctypes.byref(entry))
                for _ in range(8192):
                    if not present:
                        break
                    parent_created = self.parent_created if entry.parent == self.parent else self.known.get(entry.parent, (None,))[0]
                    eligible_root = entry.parent != self.parent or self.root_pid in (None, entry.pid)
                    if eligible_root and parent_created is not None and entry.pid not in self.known and len(self.known) < 12:
                        if self.created(entry.parent) == parent_created:
                            created = self.created(entry.pid)
                            if created is not None and created >= self.not_before:
                                name = "".join(character for character in entry.image if character.isascii() and (character.isalnum() or character in "._-"))[:32]
                                self.known[entry.pid] = (created, entry.parent, name)
                                if entry.parent == self.parent:
                                    self.root_pid = entry.pid
                    present = self.api.Process32NextW(handle, ctypes.byref(entry))
        finally:
            self.api.CloseHandle(handle)
        live = sorted([pid, parent, created, name] for pid, (created, parent, name) in self.known.items() if self.created(pid) == created)
        topology = live[:8]
        if not self.rows or self.rows[-1]["processes"] != topology:
            self.changes += 1
            self.rows.append({"elapsed_ms": round((time.monotonic() - self.started) * 1000), "processes": topology, "omitted": max(0, len(live) - 8)})

    def observe(self):
        try:
            for _ in range(48):
                if self.stop.is_set():
                    break
                self.sample()
                if self.stop.wait(0.25):
                    break
        except Exception as error:
            self.error = getattr(error, "winerror", None) or -1

    def finish(self, audit):
        self.stop.set()
        self.thread.join()
        try:
            audit_bytes = audit.stat().st_size
        except OSError:
            audit_bytes = 0
        report("registered-observation", elapsed_ms=round((time.monotonic() - self.started) * 1000),
            observer_error=self.error, audit_bytes=audit_bytes,
            dropped_changes=max(0, self.changes - len(self.rows)), topology=list(self.rows))


with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary) / "repo"
    shutil.copytree(source / "scripts/fixtures/okf-valid-repo", root)
    shutil.copytree(source / "scripts", root / "scripts")
    adapters = (
        (source / ".github/hooks/scripts", root / ".github/hooks/scripts"),
        (source / ".gemini/hooks/scripts", root / ".gemini/hooks/scripts"),
        (source / ".codex/hooks", root / ".codex/hooks"),
    )
    for origin, target in adapters:
        target.mkdir(parents=True)
        for name in ("lint-okf.py", "repository-okf.py"):
            if (origin / name).exists():
                shutil.copy2(origin / name, target / name)
        shutil.copytree(origin / "helpers", target / "helpers")
    file = root / ".agents/instructions/repo.md"
    file.write_text(file.read_text().replace("type: Agent Instruction", "type: Agent Memory"))
    nested = root / "nested/work"
    nested.mkdir(parents=True)
    payloads = (
        (root / ".github/hooks/scripts/lint-okf.py", {"cwd": str(nested), "hook_event_name": "Stop"}),
        (root / ".gemini/hooks/scripts/lint-okf.py", {"cwd": str(nested), "hook_event_name": "AfterAgent"}),
        (root / ".codex/hooks/repository-okf.py", {"cwd": str(nested), "hook_event_name": "Stop"}),
    )
    for script, payload in payloads:
        env = {**os.environ, "AUDIT_LOG": str(root / (script.parent.parent.name + "-audit.log"))}
        started = time.monotonic()
        response = subprocess.run([sys.executable, str(script)], input=json.dumps(payload), text=True, capture_output=True, env=env, timeout=11)
        assert response.returncode == 0, (script, response.stderr)
        output = json.loads(response.stdout)
        assert "OKF101" in output["reason"], (script, output)
        assert "python scripts/lint-okf.py" in output["reason"], (script, output)
        assert len(response.stdout.encode()) < 8192, script
        report("direct-" + script.parent.parent.name, elapsed_ms=round((time.monotonic() - started) * 1000))
    registration = json.loads((source / ".codex/hooks.json").read_text())["hooks"]["Stop"][0]["hooks"][0]
    assert "git','rev-parse','--show-toplevel" in registration["commandWindows"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    observer = InvocationObserver()
    report("registered-start", parent_pid=observer.parent, parent_created=observer.parent_created)
    observer.thread.start()
    try:
        registered = subprocess.run(registration["commandWindows"], shell=True, cwd=nested,
            input=json.dumps({"cwd": str(nested), "hook_event_name": "Stop"}), text=True, capture_output=True,
            env={**os.environ, "AUDIT_LOG": str(root / "registered-audit.log")}, timeout=11)
        assert registered.returncode == 0 and "OKF101" in json.loads(registered.stdout)["reason"], registered
    except subprocess.TimeoutExpired as error:
        report("registered-timeout", stdout_bytes=len(error.stdout or b""), stderr_bytes=len(error.stderr or b""))
        raise
    finally:
        observer.finish(root / "registered-audit.log")
print("PASSED: native Windows repository OKF envelopes")
'@
if (-not $IsWindows) {
    Write-Host 'SKIP: native Windows repository OKF envelopes require Windows'
    exit 0
}
& python -c $source $root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
