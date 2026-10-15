#!/usr/bin/env python3
# Generated from hooks/families/scan_secrets.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import signal
import stat
import sys
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_init  # noqa: E402
from helpers.common import emit_json, read_json_input  # noqa: E402


SCRIPT_NAME = Path(__file__).name
TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".csv",
    ".env",
    ".go",
    ".h",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".svg",
    ".tf",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
PATTERNS = [
    ("github_classic_pat", "high", re.compile(r"gh[pousr]_[A-Za-z0-9]{36}")),
    ("github_fine_grained_pat", "high", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("aws_access_key", "high", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("stripe_live_key", "high", re.compile(r"sk_live_[0-9A-Za-z]{16,}")),
    ("slack_token", "medium", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
]
MAX_FILES = 256
MAX_FILE_BYTES = 1048576
MAX_TOTAL_BYTES = 8388608
MAX_GIT_OUTPUT_BYTES = 8388608
MAX_SCAN_SECONDS = 8.0
MAX_RETAINED_FINDINGS = 100
MAX_PROCESSED_FINDINGS = 1000
MAX_LOG_RECORD_BYTES = 65536
LOG_LOCK_TIMEOUT_SECONDS = 1.0
LOG_LOCK_POLL_SECONDS = 0.05
CANDIDATE_STAGED = "staged"
CANDIDATE_WORKTREE = "worktree"
CANDIDATE_UNTRACKED = "untracked"
CANDIDATE_UNMERGED_STAGES = ("unmerged-base", "unmerged-ours", "unmerged-theirs")
CANDIDATE_UNMERGED_WORKTREE = "unmerged-worktree"
INCOMPLETE_LOG: dict[str, object] | None = None
SCAN_ACTION = "scan"


SCAN_PHASE = "initialization"
INCOMPLETE_CAUSES = {
    "git_unavailable": ("Git is unavailable", "Check Git availability in the hook environment.", ""),
    "audit_unavailable": ("audit storage is unavailable", "Check hook audit storage.", ""),
    "input_invalid": ("hook input is invalid", "Check the provider hook envelope.", ""),
    "git_failed": ("Git command failed", "Check repository accessibility and Git health.", ""),
    "git_capture_failed": ("Git capture failed", "Check temporary storage and Git execution.", ""),
    "git_descendant_running": ("Git left a running descendant", "Check Git process completion and retry.", ""),
    "git_head_invalid": ("Git HEAD verification failed", "Check repository HEAD and integrity.", ""),
    "git_output_invalid": ("Git output is invalid", "Check Git compatibility and repository integrity.", ""),
    "repository_unavailable": ("repository inspection failed", "Check repository accessibility.", ""),
    "scan_timeout": ("scan time limit reached", "Check repository size and Git responsiveness, then retry.", "seconds"),
    "git_timeout": ("Git time limit reached", "Check Git responsiveness and retry.", "seconds"),
    "snapshot_count_limit": ("candidate snapshot limit exceeded", "Check pending snapshots and unintended generated artifacts.", "snapshots"),
    "file_bytes_limit": ("candidate byte limit exceeded", "Check pending file sizes and unintended generated artifacts.", "bytes"),
    "total_bytes_limit": ("total candidate byte limit exceeded", "Check pending scan size and unintended generated artifacts.", "bytes"),
    "git_output_limit": ("Git capture byte limit exceeded", "Check pending scan size and Git output volume.", "bytes"),
    "git_input_limit": ("Git request byte limit exceeded", "Check pending scan size.", "bytes"),
    "candidate_unsafe": ("candidate cannot be read safely", "Check pending file types and repository boundaries.", ""),
    "candidate_read_failed": ("candidate read failed", "Check pending file accessibility.", ""),
    "log_unavailable": ("scan log is unavailable", "Check secure hook log storage.", ""),
    "log_unsafe": ("scan log cannot be accessed safely", "Check secure hook log storage and file types.", ""),
    "log_lock_timeout": ("scan log lock time limit reached", "Check concurrent hook log writers and retry.", "seconds"),
    "log_configuration_invalid": ("scan log rotation configuration is invalid", "Check hook log rotation settings.", ""),
    "log_record_limit": ("scan log record byte limit exceeded", "Check hook log rotation settings and scan volume.", "bytes"),
    "internal_error": ("internal scanner failure", "Check the hook installation and retry.", ""),
}
INCOMPLETE_OPERATIONS = {
    "initialization", "input", "repository", "git_repository", "git_head",
    "git_candidates", "git_index", "git_diff", "git_command",
    "candidate_read", "candidate_scan", "scan_log",
}


class ScanFailure(RuntimeError):
    """Carry only scanner-owned vocabulary and bounded numeric measurements."""

    def __init__(self, cause: str, operation: str | None = None, **numbers: int) -> None:
        self.cause = cause if cause in INCOMPLETE_CAUSES else "internal_error"
        phase = SCAN_PHASE if operation is None else operation
        self.operation = phase if phase in INCOMPLETE_OPERATIONS else "initialization"
        self.numbers = {
            key: value for key, value in numbers.items()
            if key in {"exit_status", "measured", "limit", "seconds"}
            and type(value) is int
            and (-2147483648 if key == "exit_status" else 0) <= value <= 9223372036854775807
        }
        super().__init__(self.cause)

    def diagnostic(self) -> dict[str, object]:
        return {"cause": self.cause, "operation": self.operation, **self.numbers}

    def detail(self) -> str:
        description, recovery, unit = INCOMPLETE_CAUSES[self.cause]
        measures = []
        if "exit_status" in self.numbers:
            measures.append(f"exit status {self.numbers['exit_status']}")
        if "measured" in self.numbers:
            measures.append(f"measured {self.numbers['measured']} {unit}".rstrip())
        if "limit" in self.numbers:
            measures.append(f"limit {self.numbers['limit']} {unit}".rstrip())
        if "seconds" in self.numbers:
            measures.append(f"limit {self.numbers['seconds']} seconds")
        suffix = f" ({', '.join(measures)})" if measures else ""
        return f"{self.cause}/{self.operation}: {description}{suffix}. {recovery}"


class GitCommandError(ScanFailure):
    pass


class ScanSecurityError(ScanFailure):
    pass


class ScanLimitExceeded(ScanSecurityError):
    pass


def enforce_deadline(deadline: float | None) -> None:
    if deadline is not None and time.monotonic() >= deadline:
        raise ScanLimitExceeded("scan_timeout", seconds=int(MAX_SCAN_SECONDS))


def noop() -> None:
    emit_json({})
    raise SystemExit(0)
# BEGIN PROVIDER ADAPTER
def emit_block_denial(reason: str) -> None:
    emit_json({"decision": "deny", "reason": reason})
# END PROVIDER ADAPTER


def read_payload() -> dict:
    try:
        payload = read_json_input()
    except ValueError as exc:
        raise ScanSecurityError("input_invalid", "input") from exc
    if not isinstance(payload, dict):
        raise ScanSecurityError("input_invalid", "input")
    return payload


def git_available() -> bool:
    return shutil.which("git") is not None


def run_git(
    args: list[str],
    *,
    cwd: Path,
    text: bool = True,
    allow_nonzero: bool = False,
    deadline: float | None = None,
    input_bytes: bytes | None = None,
) -> str | bytes | None:
    import subprocess

    global SCAN_PHASE
    options = args[:args.index("--")] if "--" in args else args
    command = args[1] if args and args[0] == "--literal-pathspecs" else args[0] if args else ""
    operation = {
        "rev-parse": "git_head" if args[1:3] == ["--verify", "HEAD"] else "git_repository",
        "symbolic-ref": "git_head", "show-ref": "git_head",
        "ls-files": "git_index" if "--stage" in options else "git_candidates",
        "diff": "git_candidates" if "--name-only" in options else "git_diff",
        "cat-file": "git_index", "show": "git_index",
    }.get(command, "git_command")
    SCAN_PHASE = operation
    git_executable = shutil.which("git")
    if git_executable is None:
        raise GitCommandError("git_unavailable")

    now = time.monotonic()
    command_deadline = now + 5.0
    if deadline is not None:
        command_deadline = min(command_deadline, deadline)
    if command_deadline <= now:
        raise ScanLimitExceeded("scan_timeout", seconds=int(MAX_SCAN_SECONDS))

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = ""
    env["GIT_LITERAL_PATHSPECS"] = "1"
    popen_options: dict[str, object] = {
        "cwd": str(cwd),
        "env": env,
        "stdin": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "posix":
        popen_options["start_new_session"] = True
    if os.name == "nt":
        popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    try:
        with contextlib.ExitStack() as resources:
            capture = resources.enter_context(tempfile.TemporaryFile(mode="w+b"))
            if input_bytes is not None:
                if len(input_bytes) > MAX_GIT_OUTPUT_BYTES:
                    raise ScanLimitExceeded("git_input_limit", operation, measured=len(input_bytes), limit=MAX_GIT_OUTPUT_BYTES)
                request = resources.enter_context(tempfile.TemporaryFile(mode="w+b"))
                request.write(input_bytes)
                request.seek(0)
                popen_options["stdin"] = request
            process = subprocess.Popen([git_executable, *args], stdout=capture, **popen_options)
            observed_descendants: list[int] = []
            try:
                while True:
                    size = os.fstat(capture.fileno()).st_size
                    if size > MAX_GIT_OUTPUT_BYTES:
                        raise ScanLimitExceeded("git_output_limit", operation, measured=size, limit=MAX_GIT_OUTPUT_BYTES)
                    if time.monotonic() >= command_deadline:
                        enforce_deadline(deadline)
                        raise ScanLimitExceeded("git_timeout", operation, seconds=5)
                    return_code = process.poll()
                    if return_code is not None:
                        break
                    try:
                        process.wait(timeout=min(0.02, max(0.0, command_deadline - time.monotonic())))
                    except subprocess.TimeoutExpired:
                        pass

                if os.name == "posix":
                    try:
                        os.killpg(process.pid, 0)
                    except ProcessLookupError:
                        pass
                    else:
                        raise GitCommandError("git_descendant_running")
                elif os.name == "nt":
                    observed_descendants = _windows_git_descendants(process.pid)
                    if observed_descendants:
                        raise GitCommandError("git_descendant_running")
                size = os.fstat(capture.fileno()).st_size
                if size > MAX_GIT_OUTPUT_BYTES:
                    raise ScanLimitExceeded("git_output_limit", operation, measured=size, limit=MAX_GIT_OUTPUT_BYTES)
                if return_code != 0:
                    if allow_nonzero and size == 0:
                        if args == ["rev-parse", "--verify", "HEAD"] and return_code == 128:
                            return None
                        if (len(args) == 4 and args[:3] == ["show-ref", "--verify", "--quiet"]
                                and return_code == 1):
                            return None
                    raise GitCommandError("git_failed", operation, exit_status=return_code)
                capture.seek(0)
                raw_output = capture.read(size)
                if len(raw_output) != size:
                    raise GitCommandError("git_output_invalid")
                return os.fsdecode(raw_output) if text else raw_output
            except BaseException:
                _stop_git_process(process, subprocess, observed_descendants)
                raise
    except OSError as exc:
        raise GitCommandError("git_capture_failed") from exc


def _windows_git_descendants(
    parent_pid: int, ancestor_pids: set[int] | None = None,
) -> list[int]:
    import ctypes
    from ctypes import wintypes

    class ProcessEntry(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD), ("usage", wintypes.DWORD),
            ("pid", wintypes.DWORD), ("default_heap", ctypes.c_void_p),
            ("module", wintypes.DWORD), ("threads", wintypes.DWORD),
            ("parent_pid", wintypes.DWORD), ("priority", ctypes.c_long),
            ("flags", wintypes.DWORD), ("name", ctypes.c_wchar * 260),
        ]

    kernel = ctypes.windll.kernel32
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        return []
    parents: dict[int, int] = {}
    try:
        entry = ProcessEntry()
        entry.size = ctypes.sizeof(entry)
        if kernel.Process32FirstW(snapshot, ctypes.byref(entry)):
            while True:
                parents[int(entry.pid)] = int(entry.parent_pid)
                if not kernel.Process32NextW(snapshot, ctypes.byref(entry)):
                    break
    finally:
        kernel.CloseHandle(snapshot)
    descendants: set[int] = set()
    frontier = {parent_pid}
    if ancestor_pids:
        frontier.update(ancestor_pids)
    while frontier:
        children = {pid for pid, parent in parents.items() if parent in frontier}
        children -= descendants
        descendants.update(children)
        frontier = children
    return list(descendants)


def _stop_git_process(
    process: object, subprocess_module: object,
    observed_descendants: list[int] | None = None,
) -> None:
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.windll.kernel32
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        cleanup_deadline = time.monotonic() + 0.75
        known_descendants = set(observed_descendants or [])
        quiet_scans = 0
        while time.monotonic() < cleanup_deadline:
            known_descendants.update(_windows_git_descendants(process.pid, known_descendants))
            handles = []
            for pid in [process.pid, *sorted(known_descendants)]:
                handle = kernel.OpenProcess(0x00100001, False, pid)
                if not handle:
                    continue
                if kernel.WaitForSingleObject(handle, 0) == 0x102:
                    handles.append(handle)
                else:
                    kernel.CloseHandle(handle)
            try:
                if not handles:
                    quiet_scans += 1
                    if quiet_scans >= 2:
                        break
                    time.sleep(min(0.01, max(0.0, cleanup_deadline - time.monotonic())))
                    continue
                quiet_scans = 0
                for handle in handles:
                    kernel.TerminateProcess(handle, 1)
                for handle in handles:
                    remaining_ms = max(0, min(50, int((cleanup_deadline - time.monotonic()) * 1000)))
                    kernel.WaitForSingleObject(handle, remaining_ms)
            finally:
                for handle in handles:
                    kernel.CloseHandle(handle)
        if process.poll() is None:
            process.kill()
        try:
            process.wait(timeout=max(0.0, cleanup_deadline - time.monotonic()))
        except subprocess_module.TimeoutExpired:
            pass
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        elif process.poll() is None:
            process.terminate()
    except (OSError, ProcessLookupError):
        if process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass
    cleanup_deadline = time.monotonic() + 0.25
    group_alive = True
    while time.monotonic() < cleanup_deadline:
        if os.name == "posix":
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                group_alive = False
                break
            except OSError:
                break
        elif process.poll() is not None:
            group_alive = False
            break
        time.sleep(0.01)
    if group_alive:
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            elif process.poll() is None:
                process.kill()
        except (OSError, ProcessLookupError):
            if process.poll() is None:
                try:
                    process.kill()
                except OSError:
                    pass
    try:
        process.wait(timeout=0.25)
    except subprocess_module.TimeoutExpired:
        pass


def repo_root(work_dir: Path, *, deadline: float | None = None) -> Path:
    output = run_git(["rev-parse", "--show-toplevel"], cwd=work_dir, deadline=deadline)
    if isinstance(output, str):
        root = output.strip()
        if root:
            return Path(root)
    return work_dir


def repository_marker_exists(work_dir: Path) -> bool:
    try:
        current = work_dir.resolve(strict=False)
    except OSError as exc:
        raise ScanSecurityError("repository_unavailable", "repository") from exc

    for directory in (current, *current.parents):
        try:
            (directory / ".git").lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ScanSecurityError("repository_unavailable", "repository") from exc
        return True
    return False


def is_inside_git_repo(work_dir: Path, *, deadline: float | None = None) -> bool:
    try:
        output = run_git(
            ["rev-parse", "--is-inside-work-tree"],
            cwd=work_dir,
            deadline=deadline,
        )
    except GitCommandError:
        if repository_marker_exists(work_dir):
            raise
        return False
    return isinstance(output, str) and output.strip() == "true"


def has_head(root: Path, *, deadline: float | None = None) -> bool:
    head = run_git(
        ["rev-parse", "--verify", "HEAD"],
        cwd=root,
        allow_nonzero=True,
        deadline=deadline,
    )
    if head is not None:
        return True
    branch = run_git(["symbolic-ref", "--quiet", "HEAD"], cwd=root, deadline=deadline)
    if not isinstance(branch, str) or not branch.startswith("refs/heads/") or branch.count("\n") != 1:
        raise GitCommandError("git_head_invalid", "git_head")
    branch_exists = run_git(
        ["show-ref", "--verify", "--quiet", branch.rstrip("\n")],
        cwd=root,
        allow_nonzero=True,
        deadline=deadline,
    )
    if branch_exists is not None:
        raise GitCommandError("git_head_invalid", "git_head")
    return False


def decode_nul_paths(output: bytes) -> list[str]:
    if not output:
        return []
    if not output.endswith(b"\0"):
        raise GitCommandError("git_output_invalid", "git_candidates")
    return [os.fsdecode(path) for path in output[:-1].split(b"\0") if path]


def collect_unmerged_files(
    root: Path, *, deadline: float | None = None,
) -> list[tuple[str, str]]:
    output = run_git(
        ["ls-files", "--unmerged", "-z", "--"],
        cwd=root, text=False, deadline=deadline,
    )
    if not isinstance(output, bytes) or (output and not output.endswith(b"\0")):
        raise GitCommandError("git_output_invalid", "git_candidates")
    candidates: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for record in output[:-1].split(b"\0") if output else []:
        header, separator, raw_path = record.partition(b"\t")
        match = re.fullmatch(rb"[0-7]{6} (?:[0-9a-f]{40}|[0-9a-f]{64}) ([123])", header)
        if not separator or not raw_path or match is None:
            raise GitCommandError("git_output_invalid", "git_candidates")
        path = os.fsdecode(raw_path)
        _validate_candidate_parts(path)
        source = CANDIDATE_UNMERGED_STAGES[int(match.group(1)) - 1]
        candidate = (source, path)
        if candidate in seen:
            raise GitCommandError("git_output_invalid", "git_candidates")
        seen.add(candidate)
        candidates.append(candidate)
        if len(candidates) > MAX_FILES:
            raise ScanLimitExceeded("snapshot_count_limit", "git_candidates", measured=len(candidates), limit=MAX_FILES)
    return candidates


def collect_files(
    root: Path,
    scope: str,
    root_has_head: bool,
    *,
    deadline: float | None = None,
) -> list[tuple[str, str]]:
    candidates = collect_unmerged_files(root, deadline=deadline)
    unmerged_paths = {path for _, path in candidates}
    diff_options = [
        "--name-only",
        "-z",
        "--no-ext-diff",
        "--no-color",
        "--no-textconv",
        "--diff-filter=ACMRTUXB",
    ]

    cached_revision = ["HEAD"] if root_has_head else []
    if scope in {"staged", "diff"}:
        output = run_git(
            ["diff", "--cached", *diff_options, *cached_revision, "--"],
            cwd=root,
            text=False,
            deadline=deadline,
        )
        if isinstance(output, bytes):
            candidates.extend(
                (CANDIDATE_STAGED, path) for path in decode_nul_paths(output)
                if path not in unmerged_paths
            )

    if scope == "diff":
        output = run_git(
            ["diff", *diff_options, "--"],
            cwd=root,
            text=False,
            deadline=deadline,
        )
        if isinstance(output, bytes):
            candidates.extend(
                (CANDIDATE_UNMERGED_WORKTREE if path in unmerged_paths else CANDIDATE_WORKTREE, path)
                for path in decode_nul_paths(output)
            )
        output = run_git(
            ["ls-files", "-z", "--others", "--exclude-standard"],
            cwd=root,
            text=False,
            deadline=deadline,
        )
        if isinstance(output, bytes):
            candidates.extend(
                (CANDIDATE_UNTRACKED, path) for path in decode_nul_paths(output)
            )

    unique_candidates = sorted(
        {(source, path) for source, path in candidates if path},
        key=lambda candidate: (candidate[1], candidate[0]),
    )
    if len(unique_candidates) > MAX_FILES:
        raise ScanLimitExceeded("snapshot_count_limit", "git_candidates", measured=len(unique_candidates), limit=MAX_FILES)
    return unique_candidates


def _is_reparse_point(details: os.stat_result) -> bool:
    attributes = getattr(details, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & flag)


def _validate_candidate_parts(path: str) -> tuple[str, ...]:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or not parsed.parts or any(part in {"", ".", ".."} for part in parsed.parts):
        raise ScanSecurityError("candidate_unsafe", "candidate_read")
    return parsed.parts


def _read_bounded_descriptor(descriptor: int) -> bytes:
    details = os.fstat(descriptor)
    if not stat.S_ISREG(details.st_mode) or _is_reparse_point(details):
        raise ScanSecurityError("candidate_unsafe", "candidate_read")
    if details.st_size > MAX_FILE_BYTES:
        raise ScanLimitExceeded("file_bytes_limit", "candidate_read", measured=details.st_size, limit=MAX_FILE_BYTES)

    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, min(65536, MAX_FILE_BYTES + 1 - total))
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        total += len(chunk)
        if total > MAX_FILE_BYTES:
            raise ScanLimitExceeded("file_bytes_limit", "candidate_read", measured=total, limit=MAX_FILE_BYTES)


def _read_worktree_candidate(root: Path, path: str, *, allow_missing: bool = False) -> bytes | None:
    parts = _validate_candidate_parts(path)
    try:
        root_path = root.resolve(strict=True)
    except OSError as exc:
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    directory_flag = getattr(os, "O_DIRECTORY", 0)

    if os.open in os.supports_dir_fd and directory_flag:
        descriptors: list[int] = []
        try:
            current = os.open(root_path, os.O_RDONLY | directory_flag)
            descriptors.append(current)
            for component in parts[:-1]:
                details = os.stat(component, dir_fd=current, follow_symlinks=False)
                if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
                    raise ScanSecurityError("candidate_unsafe", "candidate_read")
                current = os.open(
                    component,
                    os.O_RDONLY | directory_flag | no_follow,
                    dir_fd=current,
                )
                descriptors.append(current)
            details = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
                raise ScanSecurityError("candidate_unsafe", "candidate_read")
            descriptor = os.open(parts[-1], os.O_RDONLY | no_follow, dir_fd=current)
            descriptors.append(descriptor)
            return _read_bounded_descriptor(descriptor)
        except (OSError, ValueError) as exc:
            if allow_missing and isinstance(exc, FileNotFoundError):
                return None
            if isinstance(exc, ScanSecurityError):
                raise
            raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
        finally:
            for descriptor in reversed(descriptors):
                try:
                    os.close(descriptor)
                except OSError:
                    pass

    candidate = root_path.joinpath(*parts)
    current = root_path
    try:
        for component in parts:
            current = current / component
            details = current.lstat()
            if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
                raise ScanSecurityError("candidate_unsafe", "candidate_read")
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root_path)
        descriptor = os.open(candidate, os.O_RDONLY | no_follow)
    except (OSError, ValueError) as exc:
        if allow_missing and isinstance(exc, FileNotFoundError):
            return None
        if isinstance(exc, ScanSecurityError):
            raise
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    try:
        return _read_bounded_descriptor(descriptor)
    except OSError as exc:
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    finally:
        os.close(descriptor)


def read_candidate_bytes(
    root: Path,
    path: str,
    source: str,
    *,
    deadline: float | None = None,
) -> bytes | None:
    if source == CANDIDATE_STAGED or source in CANDIDATE_UNMERGED_STAGES:
        _validate_candidate_parts(path)
        if source == CANDIDATE_STAGED:
            index_object = f":./{path}"
        else:
            stage = CANDIDATE_UNMERGED_STAGES.index(source) + 1
            index_object = f":{stage}:./{path}"
        size_output = run_git(
            ["cat-file", "-s", index_object],
            cwd=root,
            text=False,
            deadline=deadline,
        )
        if not isinstance(size_output, bytes):
            raise GitCommandError("git_output_invalid", "git_index")
        try:
            size = int(size_output.strip())
        except ValueError as exc:
            raise GitCommandError("git_output_invalid", "git_index") from exc
        if size < 0:
            raise GitCommandError("git_output_invalid", "git_index")
        if size > MAX_FILE_BYTES:
            raise ScanLimitExceeded("file_bytes_limit", "git_index", measured=size, limit=MAX_FILE_BYTES)
        output = run_git(
            ["show", "--no-textconv", index_object],
            cwd=root,
            text=False,
            deadline=deadline,
        )
        if not isinstance(output, bytes) or len(output) != size:
            raise GitCommandError("git_output_invalid", "git_index")
        return output

    return _read_worktree_candidate(root, path, allow_missing=source == CANDIDATE_UNMERGED_WORKTREE)


def read_index_candidates(
    root: Path, candidates: list[tuple[str, str]], *, deadline: float | None = None,
) -> dict[tuple[str, str], bytes]:
    index_candidates = [candidate for candidate in candidates
                        if candidate[0] == CANDIDATE_STAGED
                        or candidate[0] in CANDIDATE_UNMERGED_STAGES]
    if not index_candidates:
        return {}
    if len(index_candidates) == 1:
        source, path = index_candidates[0]
        content = read_candidate_bytes(root, path, source, deadline=deadline)
        if content is None:
            raise GitCommandError("git_output_invalid", "git_index")
        return {(source, path): content}

    paths: list[str] = []
    for source, path in index_candidates:
        _validate_candidate_parts(path)
        if path not in paths:
            paths.append(path)
    resolved: dict[tuple[str, str], bytes] = {}
    expected_candidates = set(index_candidates)
    cursor = 0
    while cursor < len(paths):
        start = cursor
        argument_bytes = 0
        while cursor < len(paths):
            # Allow for Windows quoting/escaping and separators as well as
            # POSIX encoded arguments. Keep long path lists below argv limits.
            path_bytes = len(os.fsencode(paths[cursor])) * 2 + 3
            if cursor > start and argument_bytes + path_bytes > 8192:
                break
            argument_bytes += path_bytes
            cursor += 1
        batch_paths = paths[start:cursor]
        index_output = run_git(
            ["--literal-pathspecs", "ls-files", "--stage", "-z", "--", *batch_paths],
            cwd=root, text=False, deadline=deadline,
        )
        if not isinstance(index_output, bytes) or not index_output.endswith(b"\0"):
            raise GitCommandError("git_output_invalid", "git_index")
        for record in index_output[:-1].split(b"\0"):
            enforce_deadline(deadline)
            header, separator, raw_path = record.partition(b"\t")
            match = re.fullmatch(rb"[0-7]{6} ([0-9a-f]{40}|[0-9a-f]{64}) ([0-3])", header)
            if not separator or not raw_path or match is None:
                raise GitCommandError("git_output_invalid", "git_index")
            path = os.fsdecode(raw_path)
            if "/".join(_validate_candidate_parts(path)) != path:
                raise GitCommandError("git_output_invalid", "git_index")
            if path not in batch_paths:
                # Literal pathspecs still expand directory prefixes. Resolve a
                # descendant only when its own exact path is selected, so it
                # cannot be counted twice when it belongs to a later batch.
                if any(path.startswith(parent + "/") for parent in batch_paths):
                    continue
                raise GitCommandError("git_output_invalid", "git_index")
            stage = int(match.group(2))
            source = CANDIDATE_STAGED if stage == 0 else CANDIDATE_UNMERGED_STAGES[stage - 1]
            candidate = (source, path)
            if candidate not in expected_candidates or candidate in resolved:
                raise GitCommandError("git_output_invalid", "git_index")
            resolved[candidate] = match.group(1)
    if len(resolved) != len(index_candidates):
        raise GitCommandError("git_output_invalid", "git_index")

    # Only object IDs enter the line-delimited batch protocol, so filenames with
    # delimiters stay safe without the NUL batch-input option added in Git 2.38.
    metadata = run_git(
        ["cat-file", "--batch-check"], cwd=root, text=False,
        input_bytes=b"".join(resolved[candidate] + b"\n" for candidate in index_candidates),
        deadline=deadline,
    )
    if not isinstance(metadata, bytes) or not metadata.endswith(b"\n"):
        raise GitCommandError("git_output_invalid", "git_index")
    headers = metadata[:-1].split(b"\n")
    if len(headers) != len(index_candidates):
        raise GitCommandError("git_output_invalid", "git_index")

    # Resolve and bound every snapshot before requesting content. Use immutable
    # object IDs for the second call, so index edits cannot change these reads.
    objects: list[tuple[tuple[str, str], bytes, int, bytes]] = []
    total_bytes = 0
    for candidate, header in zip(index_candidates, headers):
        enforce_deadline(deadline)
        match = re.fullmatch(rb"([0-9a-f]{40}|[0-9a-f]{64}) blob ([0-9]+)", header)
        if match is None or match.group(1) != resolved[candidate]:
            raise GitCommandError("git_output_invalid", "git_index")
        try:
            size = int(match.group(2))
        except ValueError as exc:
            raise GitCommandError("git_output_invalid", "git_index") from exc
        if size > MAX_FILE_BYTES:
            raise ScanLimitExceeded("file_bytes_limit", "git_index", measured=size, limit=MAX_FILE_BYTES)
        total_bytes += size
        if total_bytes > MAX_TOTAL_BYTES:
            raise ScanLimitExceeded("total_bytes_limit", measured=total_bytes, limit=MAX_TOTAL_BYTES)
        objects.append((candidate, match.group(1), size, header + b"\n"))

    contents: dict[tuple[str, str], bytes] = {}
    cursor = 0
    while cursor < len(objects):
        start = cursor
        capture_bytes = 0
        while cursor < len(objects):
            _, _, size, header = objects[cursor]
            framed_size = len(header) + size + 1
            if capture_bytes + framed_size > MAX_GIT_OUTPUT_BYTES:
                break
            capture_bytes += framed_size
            cursor += 1
        batch = objects[start:cursor]
        output = run_git(
            ["cat-file", "--batch"], cwd=root, text=False,
            input_bytes=b"".join(oid + b"\n" for _, oid, _, _ in batch), deadline=deadline,
        )
        if not isinstance(output, bytes) or len(output) != capture_bytes:
            raise GitCommandError("git_output_invalid", "git_index")
        offset = 0
        for candidate, _, size, header in batch:
            if output[offset:offset + len(header)] != header:
                raise GitCommandError("git_output_invalid", "git_index")
            offset += len(header)
            end = offset + size
            if output[end:end + 1] != b"\n":
                raise GitCommandError("git_output_invalid", "git_index")
            contents[candidate] = output[offset:end]
            offset = end + 1
    return contents


def is_env_path(path: str) -> bool:
    return bool(re.search(r"(^|/)\.env($|[.])", path.lower()))


def is_credential_path(path: str) -> bool:
    lowered = path.lower()
    base_name = lowered.rsplit("/", 1)[-1]
    if base_name in {"credentials", ".git-credentials"}:
        return True
    if base_name.startswith("credentials."):
        return True

    return any(
        re.search(pattern, lowered)
        for pattern in (
            r"(^|/)\.ssh(/|$)",
            r"(^|/)\.aws(/|$)",
            r"(^|/)\.gnupg(/|$)",
            r"(^|/)\.?credentials(/|$)",
            r"(^|/)\.?secrets(/|$)",
        )
    )


def is_text_candidate(path: str, raw_bytes: bytes) -> bool:
    if b"\0" in raw_bytes:
        return False
    try:
        raw_bytes.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return Path(path).suffix.lower() in TEXT_EXTENSIONS


def enumerate_file_lines(text: str) -> list[tuple[int, str]]:
    return [(index + 1, line) for index, line in enumerate(text.splitlines())]


def decode_ascii_scan_text(raw_bytes: bytes) -> str:
    return "".join(
        chr(value) if value in {9, 10, 13} or 32 <= value <= 126 else " "
        for value in raw_bytes
    )


def emit_diff_added_lines(
    root: Path,
    path: str,
    source: str,
    *,
    root_has_head: bool,
    deadline: float | None = None,
) -> list[tuple[int, str]]:
    if source not in {CANDIDATE_STAGED, CANDIDATE_WORKTREE}:
        raise ScanSecurityError("candidate_unsafe", "git_diff")
    cached_options = ["--cached"] if source == CANDIDATE_STAGED else []
    cached_revision = ["HEAD"] if source == CANDIDATE_STAGED and root_has_head else []
    output = run_git(
        [
            "diff",
            *cached_options,
            "--no-ext-diff",
            "--no-color",
            "--no-textconv",
            "--unified=0",
            "--src-prefix=a/",
            "--dst-prefix=b/",
            "--output-indicator-new=+",
            "--output-indicator-old=-",
            "--output-indicator-context= ",
            *cached_revision,
            "--",
            path,
        ],
        cwd=root,
        text=False,
        deadline=deadline,
    )
    if not isinstance(output, bytes):
        return []
    if output and (not output.startswith(b"diff --git ") or not output.endswith(b"\n")):
        raise GitCommandError("git_output_invalid", "git_diff")

    lines: list[tuple[int, str]] = []
    current_line: int | None = None
    in_hunk = False
    for raw_line in output.splitlines():
        if raw_line.startswith(b"diff --git "):
            in_hunk = False
            current_line = None
            continue
        if raw_line.startswith(b"@@"):
            match = re.search(rb"\+(\d+)", raw_line)
            current_line = int(match.group(1)) if match else None
            in_hunk = current_line is not None
            continue
        if not in_hunk or current_line is None:
            continue
        if raw_line.startswith(b"+"):
            lines.append((current_line, os.fsdecode(raw_line[1:])))
            current_line += 1
        elif raw_line.startswith(b"-") or raw_line.startswith(b"\\"):
            continue
        elif raw_line.startswith(b" "):
            current_line += 1
        else:
            raise GitCommandError("git_output_invalid", "git_diff")
    return lines


def redact_match(match: str) -> str:
    if len(match) <= 8:
        return "[REDACTED]"
    return f"{match[:4]}...{match[-4:]}"


def _normalize_allowlist_value(value: str) -> str:
    return value.strip(" ")


def _has_forbidden_allowlist_separator(value: str) -> bool:
    return any(unicodedata.category(character) == "Cc" for character in value) or bool(
        re.search(r"\\(?:n|r|t|x0[9ad]|u000[9ad])", value, re.IGNORECASE)
    )


def parse_allowlist(raw_allowlist: str | None) -> list[dict[str, str]]:
    if not raw_allowlist:
        return []
    try:
        decoded = json.loads(raw_allowlist)
    except (TypeError, ValueError):
        return []
    if not isinstance(decoded, list) or len(decoded) > 64:
        return []

    entries: list[dict[str, str]] = []
    for raw_entry in decoded:
        if not isinstance(raw_entry, dict) or set(raw_entry) != {"tool", "input"}:
            return []
        tool = raw_entry.get("tool")
        tool_input = raw_entry.get("input")
        if not isinstance(tool, str) or not isinstance(tool_input, str):
            return []
        if _has_forbidden_allowlist_separator(tool) or _has_forbidden_allowlist_separator(tool_input):
            return []
        normalized_tool = _normalize_allowlist_value(tool).casefold()
        normalized_input = _normalize_allowlist_value(tool_input)
        if not normalized_tool or not normalized_input or len(normalized_tool) > 128 or len(normalized_input) > 8192:
            return []
        entries.append({"tool": normalized_tool, "input": normalized_input})
    return entries


def allowlist_contains(tool_name: str, tool_input: str, entries: list[dict[str, str]]) -> bool:
    if _has_forbidden_allowlist_separator(tool_name) or _has_forbidden_allowlist_separator(tool_input):
        return False
    normalized_tool = _normalize_allowlist_value(tool_name).casefold()
    normalized_input = _normalize_allowlist_value(tool_input)
    return any(
        entry["tool"] == normalized_tool and entry["input"] == normalized_input
        for entry in entries
    )


def _assert_safe_log_path(path: Path, *, allow_missing: bool = True) -> os.stat_result | None:
    try:
        details = path.lstat()
    except FileNotFoundError:
        if allow_missing:
            return None
        raise ScanSecurityError("log_unavailable", "scan_log") from None
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc
    if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
        raise ScanSecurityError("log_unsafe", "scan_log")
    return details


def _ensure_secure_log_directory(directory: Path) -> None:
    try:
        directory.mkdir(parents=True, mode=0o700, exist_ok=True)
        details = _assert_safe_log_path(directory, allow_missing=False)
        if details is None or not stat.S_ISDIR(details.st_mode):
            raise ScanSecurityError("log_unsafe", "scan_log")
        os.chmod(directory, 0o700)
    except ScanSecurityError:
        raise
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc


def _open_secure_regular(path: Path, flags: int) -> int:
    _assert_safe_log_path(path)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    binary = getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags | no_follow | binary, 0o600)
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc
    try:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode) or _is_reparse_point(details):
            raise ScanSecurityError("log_unsafe", "scan_log")
        try:
            os.fchmod(descriptor, 0o600)
        except (AttributeError, OSError):
            os.chmod(path, 0o600)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def rotate_scan_log(
    log_path: Path,
    incoming_bytes: int,
    max_bytes: int = 1048576,
    backups: int = 3,
) -> None:
    if max_bytes < 1 or backups < 1 or backups > 100:
        raise ScanSecurityError("log_configuration_invalid", "scan_log")
    if incoming_bytes < 1 or incoming_bytes > MAX_LOG_RECORD_BYTES:
        raise ScanLimitExceeded("log_record_limit", "scan_log", measured=incoming_bytes, limit=MAX_LOG_RECORD_BYTES)
    if incoming_bytes > max_bytes:
        raise ScanLimitExceeded("log_record_limit", "scan_log", measured=incoming_bytes, limit=max_bytes)
    details = _assert_safe_log_path(log_path)
    if details is None:
        return
    if not stat.S_ISREG(details.st_mode):
        raise ScanSecurityError("log_unsafe", "scan_log")
    if details.st_size + incoming_bytes <= max_bytes:
        return

    paths = [log_path.with_name(f"{log_path.name}.{index}") for index in range(1, backups + 2)]
    for path in paths:
        details = _assert_safe_log_path(path)
        if details is not None and not stat.S_ISREG(details.st_mode):
            raise ScanSecurityError("log_unsafe", "scan_log")

    try:
        for index in range(backups, 0, -1):
            current = log_path.with_name(f"{log_path.name}.{index}")
            next_path = log_path.with_name(f"{log_path.name}.{index + 1}")
            if not current.exists():
                continue
            if index == backups:
                os.remove(current)
            else:
                os.replace(current, next_path)
                os.chmod(next_path, 0o600)
        first_backup = log_path.with_name(f"{log_path.name}.1")
        os.replace(log_path, first_backup)
        os.chmod(first_backup, 0o600)
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc


def enforce_log_lock_deadline(lock_deadline: float, deadline: float | None) -> None:
    enforce_deadline(deadline)
    if time.monotonic() >= lock_deadline:
        raise ScanLimitExceeded("log_lock_timeout", "scan_log", seconds=int(LOG_LOCK_TIMEOUT_SECONDS))


def _acquire_log_lock(
    lock_fd: int,
    fcntl_module: object | None,
    msvcrt_module: object | None,
    *,
    deadline: float | None = None,
) -> str:
    lock_deadline = time.monotonic() + LOG_LOCK_TIMEOUT_SECONDS
    if deadline is not None:
        lock_deadline = min(lock_deadline, deadline)
    enforce_log_lock_deadline(lock_deadline, deadline)
    if fcntl_module is not None:
        while True:
            enforce_log_lock_deadline(lock_deadline, deadline)
            try:
                fcntl_module.flock(lock_fd, fcntl_module.LOCK_EX | fcntl_module.LOCK_NB)
                return "posix"
            except (BlockingIOError, OSError) as exc:
                if time.monotonic() >= lock_deadline:
                    raise ScanLimitExceeded("log_lock_timeout", "scan_log", seconds=int(LOG_LOCK_TIMEOUT_SECONDS)) from exc
                time.sleep(LOG_LOCK_POLL_SECONDS)
    if msvcrt_module is not None:
        if os.fstat(lock_fd).st_size == 0:
            os.write(lock_fd, b"\0")
        while True:
            enforce_log_lock_deadline(lock_deadline, deadline)
            try:
                os.lseek(lock_fd, 0, os.SEEK_SET)
                msvcrt_module.locking(lock_fd, msvcrt_module.LK_NBLCK, 1)
                return "windows"
            except OSError as exc:
                if time.monotonic() >= lock_deadline:
                    raise ScanLimitExceeded("log_lock_timeout", "scan_log", seconds=int(LOG_LOCK_TIMEOUT_SECONDS)) from exc
                time.sleep(LOG_LOCK_POLL_SECONDS)
    raise ScanSecurityError("log_unavailable", "scan_log")


def _release_log_lock(
    lock_fd: int,
    lock_kind: str,
    fcntl_module: object | None,
    msvcrt_module: object | None,
) -> None:
    if lock_kind == "posix" and fcntl_module is not None:
        fcntl_module.flock(lock_fd, fcntl_module.LOCK_UN)
    elif lock_kind == "windows" and msvcrt_module is not None:
        os.lseek(lock_fd, 0, os.SEEK_SET)
        msvcrt_module.locking(lock_fd, msvcrt_module.LK_UNLCK, 1)


def append_scan_log(**kwargs: object) -> None:
    global SCAN_PHASE
    SCAN_PHASE = "scan_log"
    try:
        _append_scan_log(**kwargs)
    except ScanFailure:
        raise
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc


def _append_scan_log(
    *,
    log_path: Path,
    status: str,
    session_id: str,
    timestamp: str,
    mode: str,
    scope: str,
    repo_root_path: Path,
    env_files: list[str],
    findings: list[dict[str, object]],
    omitted_findings: int = 0,
    findings_truncated: bool = False,
    note: str = "",
    deadline: float | None = None,
    diagnostic: dict[str, object] | None = None,
) -> None:
    enforce_deadline(deadline)
    _ensure_secure_log_directory(log_path.parent)
    payload: dict[str, object] = {
        "timestamp": timestamp,
        "sessionId": session_id,
        "repoRoot": str(repo_root_path),
        "mode": mode,
        "scope": scope,
        "status": status,
    }
    if status == "incomplete":
        # Incomplete records cannot carry payload-derived identifiers or paths.
        payload = {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "mode": mode, "scope": scope, "status": status, "action": SCAN_ACTION}
        if diagnostic is not None:
            payload["diagnostic"] = diagnostic
    if note:
        payload["note"] = note
    if env_files:
        payload["envFiles"] = env_files
    if findings:
        payload["findings"] = findings
    if omitted_findings:
        payload["omittedFindings"] = omitted_findings
    if findings_truncated:
        payload["findingsTruncated"] = True

    record = (json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    if len(record) > MAX_LOG_RECORD_BYTES:
        raise ScanLimitExceeded("log_record_limit", "scan_log", measured=len(record), limit=MAX_LOG_RECORD_BYTES)

    try:
        import fcntl
    except ImportError:
        fcntl = None

    try:
        import msvcrt
    except ImportError:
        msvcrt = None

    lock_path = log_path.with_name(f"{log_path.name}.lock")
    lock_fd = _open_secure_regular(lock_path, os.O_CREAT | os.O_RDWR)
    lock_kind = ""
    try:
        lock_kind = _acquire_log_lock(lock_fd, fcntl, msvcrt, deadline=deadline)
        enforce_deadline(deadline)
        try:
            max_bytes = int(os.environ.get("AUDIT_LOG_MAX_BYTES", "1048576"))
            backups = int(os.environ.get("AUDIT_LOG_MAX_BACKUPS", "3"))
        except ValueError as exc:
            raise ScanSecurityError("log_configuration_invalid", "scan_log") from exc
        rotate_scan_log(log_path, len(record), max_bytes, backups)
        enforce_deadline(deadline)
        log_fd = _open_secure_regular(log_path, os.O_APPEND | os.O_CREAT | os.O_WRONLY)
        with os.fdopen(log_fd, "ab") as handle:
            handle.write(record)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if lock_kind:
            try:
                _release_log_lock(lock_fd, lock_kind, fcntl, msvcrt)
            except OSError:
                pass
        os.close(lock_fd)


def build_findings_json(findings: list[tuple[str, str, str, int, str]]) -> list[dict[str, object]]:
    return [
        {
            "pattern": pattern_name,
            "severity": severity,
            "path": path,
            "line": line_number,
            "redactedMatch": redacted,
        }
        for pattern_name, severity, path, line_number, redacted in findings
    ]


def record_finding(
    findings: list[tuple[str, str, str, int, str]],
    finding: tuple[str, str, str, int, str],
    processed_findings: int,
) -> tuple[int, bool]:
    processed_findings += 1
    if len(findings) < MAX_RETAINED_FINDINGS:
        findings.append(finding)
    return processed_findings, processed_findings >= MAX_PROCESSED_FINDINGS


def emit_output(findings_count: int, log_path: Path, checked_files: int = 0, skipped: bool = False) -> None:
    if findings_count > 0:
        emit_json({"systemMessage": f"scan-secrets warning: {SCAN_ACTION}; potential secrets detected."})
        return
    if HOOK_EVENT == "Stop":
        if skipped:
            emit_json({"systemMessage": "scan-secrets: skipped"})
        else:
            emit_json({"systemMessage": f"scan-secrets: pass; {checked_files} modified {'file' if checked_files == 1 else 'files'}"})
        return
    emit_json({})


def normalized_mode_from_env() -> str:
    mode = os.environ.get("SCAN_MODE", "block")
    if mode not in {"warn", "block"}:
        return "block"
    return mode


def enforce_scan_budget(scan_started: float, total_bytes: int, *, now: float | None = None) -> None:
    current_time = time.monotonic() if now is None else now
    if current_time - scan_started > MAX_SCAN_SECONDS:
        raise ScanLimitExceeded("scan_timeout", seconds=int(MAX_SCAN_SECONDS))
    if total_bytes > MAX_TOTAL_BYTES:
        raise ScanLimitExceeded("total_bytes_limit", measured=total_bytes, limit=MAX_TOTAL_BYTES)


def handle_unexpected_exception(exc: Exception) -> int:
    mode = normalized_mode_from_env()
    failure = exc if isinstance(exc, ScanFailure) else ScanFailure("internal_error")
    detail = failure.detail()
    outcome = "blocked" if mode == "block" else "warning"
    reason = (f"scan-secrets {outcome}: {SCAN_ACTION}; scan incomplete; "
              f"potential secrets could not be checked. {detail}")
    print(reason, file=sys.stderr)
    if INCOMPLETE_LOG is not None:
        try:
            append_scan_log(**INCOMPLETE_LOG, status="incomplete", env_files=[], findings=[],
                            note=detail, diagnostic=failure.diagnostic())
        except Exception:
            # Reporting must preserve the first failure even if logging also fails.
            pass
    if mode == "block":
        emit_block_denial(reason)
    else:
        emit_json({"systemMessage": reason})
    return 0
# BEGIN PROVIDER ADAPTER
SESSION_ID_KEYS = ("session_id",)
DEFAULT_SECRETS_LOG_PATH = Path.home() / ".gemini" / "hooks" / "secrets"
HOOK_EVENT = ""


def resolve_work_dir(payload: dict) -> Path:
    hook_cwd = str(payload.get("cwd") or "")
    return Path(hook_cwd or os.environ.get("GEMINI_PROJECT_DIR") or Path.cwd())
# END PROVIDER ADAPTER



def findings_denial_reason(scan_log: Path) -> str:
    return f"scan-secrets blocked: {SCAN_ACTION}; potential secrets detected."

def resolve_scan_log() -> Path:
    log_dir_str = os.environ.get("SECRETS_LOG_DIR", str(DEFAULT_SECRETS_LOG_PATH))
    log_path = Path(log_dir_str)
    if log_path.is_dir() or not log_path.suffix:
        scan_log = log_path / "scan.log"
    elif log_path.suffix.lower() == ".log":
        if log_path.parent.exists() and log_path.parent.is_file():
            scan_log = log_path.parent.parent / "secrets" / log_path.name
        else:
            scan_log = log_path
    else:
        scan_log = log_path / "scan.log"
    return scan_log


def main() -> int:
    global INCOMPLETE_LOG, SCAN_ACTION, SCAN_PHASE
    scan_started = time.monotonic()
    scan_deadline = scan_started + MAX_SCAN_SECONDS
    mode = normalized_mode_from_env()

    # Prepare disposable-safe failure logging before initialization or input fails.
    scan_log = resolve_scan_log()
    INCOMPLETE_LOG = {
        "log_path": scan_log, "session_id": "", "timestamp": "", "mode": mode,
        "scope": "diff", "repo_root_path": Path.cwd(),
    }
    if not git_available():
        raise GitCommandError("git_unavailable", "initialization")
    if not audit_init():
        raise ScanSecurityError("audit_unavailable", "initialization")

    SCAN_PHASE = "input"
    payload = read_payload()
    event = payload.get("hook_event_name")
    SCAN_ACTION = (
        "session-end scan"
        if event in {"Stop", "SessionEnd", "agentStop", "subagentStop"}
        or payload.get("reason") == "complete"
        else "tool scan"
    )
    session_id = ""
    for key in SESSION_ID_KEYS:
        value = payload.get(key)
        if value:
            session_id = str(value)
            break
    timestamp = str(payload.get("timestamp") or "")

    scope = os.environ.get("SCAN_SCOPE", "diff")
    if scope not in {"diff", "staged"}:
        scope = "diff"

    SCAN_PHASE = "repository"
    work_dir = resolve_work_dir(payload)

    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    INCOMPLETE_LOG = {
        "log_path": scan_log,
        "session_id": session_id,
        "timestamp": timestamp,
        "mode": mode,
        "scope": scope,
        "repo_root_path": work_dir,
    }

    if os.environ.get("SKIP_SECRETS_SCAN") == "true":
        append_scan_log(
            log_path=scan_log,
            status="skipped",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=work_dir,
            env_files=[],
            findings=[],
            note="scan disabled by SKIP_SECRETS_SCAN",
            deadline=scan_deadline,
        )
        emit_output(0, scan_log, skipped=True)
        return 0

    if not is_inside_git_repo(work_dir, deadline=scan_deadline):
        append_scan_log(
            log_path=scan_log,
            status="skipped",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=work_dir,
            env_files=[],
            findings=[],
            note="not inside git repository",
            deadline=scan_deadline,
        )
        emit_output(0, scan_log, skipped=True)
        return 0

    root = repo_root(work_dir, deadline=scan_deadline)
    root_has_head = has_head(root, deadline=scan_deadline)
    candidates = collect_files(root, scope, root_has_head, deadline=scan_deadline)
    SCAN_PHASE = "candidate_scan"

    if not candidates:
        append_scan_log(
            log_path=scan_log,
            status="clean",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=root,
            env_files=[],
            findings=[],
            note="no modified files to scan",
            deadline=scan_deadline,
        )
        emit_output(0, scan_log)
        return 0

    allowlist = parse_allowlist(os.environ.get("SECRETS_ALLOWLIST"))
    env_files: list[str] = []
    findings: list[tuple[str, str, str, int, str]] = []
    processed_findings = 0
    stop_scanning = False
    total_bytes = 0
    index_contents = read_index_candidates(root, candidates, deadline=scan_deadline)

    for source, path in candidates:
        SCAN_PHASE = "candidate_read"
        enforce_scan_budget(scan_started, total_bytes)
        if (source, path) in index_contents:
            raw_bytes = index_contents.pop((source, path))
        else:
            raw_bytes = read_candidate_bytes(root, path, source, deadline=scan_deadline)
        if raw_bytes is None:
            continue
        SCAN_PHASE = "candidate_scan"
        total_bytes += len(raw_bytes)
        enforce_scan_budget(scan_started, total_bytes)

        if is_env_path(path) and path not in env_files:
            env_files.append(path)

        if is_credential_path(path):
            allowlist_text = f"{path}:1:credential_path:[SENSITIVE PATH]"
            if not allowlist_contains("scan_secrets", allowlist_text, allowlist):
                processed_findings, stop_scanning = record_finding(
                    findings,
                    ("credential_path", "critical", path, 1, "[SENSITIVE PATH]"),
                    processed_findings,
                )

        if stop_scanning:
            break

        if not is_text_candidate(path, raw_bytes):
            candidate_lines = enumerate_file_lines(decode_ascii_scan_text(raw_bytes))
        elif (scope == "staged" or not root_has_head or source == CANDIDATE_UNTRACKED
              or source in CANDIDATE_UNMERGED_STAGES or source == CANDIDATE_UNMERGED_WORKTREE):
            candidate_lines = enumerate_file_lines(raw_bytes.decode("utf-8", errors="replace"))
        else:
            candidate_lines = emit_diff_added_lines(
                root,
                path,
                source,
                root_has_head=root_has_head,
                deadline=scan_deadline,
            )

        SCAN_PHASE = "candidate_scan"
        for line_number, line_text in candidate_lines:
            enforce_scan_budget(scan_started, total_bytes)
            for pattern_name, severity, regex in PATTERNS:
                enforce_scan_budget(scan_started, total_bytes)
                for match in regex.finditer(line_text):
                    enforce_scan_budget(scan_started, total_bytes)
                    match_value = match.group(0)
                    allowlist_text = f"{path}:{line_number}:{pattern_name}:{match_value}"
                    if allowlist_contains("scan_secrets", allowlist_text, allowlist):
                        continue
                    processed_findings, stop_scanning = record_finding(
                        findings,
                        (pattern_name, severity, path, line_number, redact_match(match_value)),
                        processed_findings,
                    )
                    if stop_scanning:
                        break
                if stop_scanning:
                    break
            if stop_scanning:
                break
        if stop_scanning:
            break

    enforce_scan_budget(scan_started, total_bytes)

    if not findings:
        append_scan_log(
            log_path=scan_log,
            status="clean",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=root,
            env_files=env_files,
            findings=[],
            deadline=scan_deadline,
        )
        emit_output(0, scan_log, checked_files=len(candidates))
        return 0

    findings_json = build_findings_json(findings)
    omitted_findings = processed_findings - len(findings)
    enforce_scan_budget(scan_started, total_bytes)
    append_scan_log(
        log_path=scan_log,
        status="findings",
        session_id=session_id,
        timestamp=timestamp,
        mode=mode,
        scope=scope,
        repo_root_path=root,
        env_files=env_files,
        findings=findings_json,
        omitted_findings=omitted_findings,
        findings_truncated=stop_scanning or omitted_findings > 0,
        deadline=scan_deadline,
    )
    if mode == "block":
        emit_block_denial(findings_denial_reason(scan_log))
        return 0

    emit_output(processed_findings, scan_log)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(handle_unexpected_exception(exc))
