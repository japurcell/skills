#!/usr/bin/env python3
# Generated from hooks/families/scan_runtime.py by scripts/generate-hooks.py. Do not edit.
"""Protected Git acquisition and stable pending snapshots."""
from __future__ import annotations
import codecs
import hashlib
import contextlib
import os
import re
import shutil
import signal
import stat
import tempfile
import time
from collections.abc import Iterator
from pathlib import Path, PurePosixPath
from typing import BinaryIO
from .scan_types import (
    CANDIDATE_STAGED, CANDIDATE_UNMERGED_STAGES, CANDIDATE_UNMERGED_WORKTREE,
    CANDIDATE_UNTRACKED, CANDIDATE_WORKTREE, GIT_COMPLETION_WAIT_SECONDS,
    GitCommandError, ScanContext, ScanLimitExceeded, ScanSecurityError, TEXT_EXTENSIONS,
)

@contextlib.contextmanager
def capture_git(context: ScanContext,
    args: list[str],
    *,
    cwd: Path,
    allow_nonzero: bool = False,
    deadline: float | None = None,
    input_bytes: bytes | None = None,
) -> Iterator[VerifiedCapture | None]:
    import errno
    import subprocess

    options = args[:args.index("--")] if "--" in args else args
    command = args[1] if args and args[0] == "--literal-pathspecs" else args[0] if args else ""
    operation = {
        "rev-parse": "git_head" if args[1:3] == ["--verify", "HEAD"] else "git_repository",
        "symbolic-ref": "git_head", "show-ref": "git_head",
        "ls-files": "git_index" if "--stage" in options else "git_candidates",
        "diff": "git_candidates" if "--name-only" in options else "git_diff",
        "cat-file": "git_index", "show": "git_index",
    }.get(command, "git_command")
    context.phase = operation
    git_executable = shutil.which("git")
    if git_executable is None:
        raise GitCommandError("git_unavailable", operation)

    now = time.monotonic()
    command_deadline = now + 5.0
    if deadline is not None:
        command_deadline = min(command_deadline, deadline)
    if command_deadline <= now:
        raise ScanLimitExceeded("scan_timeout", seconds=int(context.limits.max_seconds))

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

    capture_step = "temporary_file"
    attempts = 0
    temporary_bytes = 0
    captured_bytes = 0

    def account_output(size):
        nonlocal temporary_bytes, captured_bytes
        growth = size - captured_bytes
        if growth < 0:
            raise GitCommandError("git_output_invalid", operation)
        captured_bytes = size
        context.charge_capture(growth)
        temporary_bytes += growth
        context.charge_temp(growth)

    try:
        with contextlib.ExitStack() as resources:
            capture = resources.enter_context(tempfile.TemporaryFile(mode="w+b"))
            capture_step = "verify_capture"
            _verify_private_capture(capture)
            if input_bytes is not None:
                if len(input_bytes) > context.limits.max_capture_bytes:
                    raise ScanLimitExceeded("git_input_limit", operation, measured=len(input_bytes), limit=context.limits.max_capture_bytes)
                capture_step = "temporary_file"
                request = resources.enter_context(tempfile.TemporaryFile(mode="w+b"))
                capture_step = "verify_capture"
                _verify_private_capture(request)
                capture_step = "request_write"
                temporary_bytes += len(input_bytes)
                context.charge_temp(len(input_bytes))
                request.write(input_bytes)
                request.seek(0)
                popen_options["stdin"] = request
            capture_step = "spawn"
            for attempt in range(3):
                if time.monotonic() >= command_deadline:
                    context.check_deadline(deadline)
                    raise ScanLimitExceeded("git_timeout", operation, seconds=5)
                try:
                    attempts = attempt + 1
                    process = subprocess.Popen([git_executable, *args], stdout=capture, **popen_options)
                    break
                except OSError as exc:
                    # Popen has no live child when launch raises. Retry only
                    # temporary process-resource exhaustion, within the original
                    # command deadline; never replay a command that ran.
                    if exc.errno != errno.EAGAIN or attempt == 2:
                        raise
                    time.sleep(min(0.01 * (2 ** attempt),
                                   max(0.0, command_deadline - time.monotonic())))
            observed_descendants: list[int] = []
            try:
                capture_step = "wait"
                while True:
                    size = os.fstat(capture.fileno()).st_size
                    account_output(size)
                    if size > context.limits.max_capture_bytes:
                        raise ScanLimitExceeded("git_output_limit", operation, measured=size, limit=context.limits.max_capture_bytes)
                    if time.monotonic() >= command_deadline:
                        context.check_deadline(deadline)
                        raise ScanLimitExceeded("git_timeout", operation, seconds=5)
                    return_code = process.poll()
                    if return_code is not None:
                        break
                    try:
                        # Short slices avoid cumulative exponential-wait overshoot
                        # across hundreds of bounded, short-lived Git calls.
                        process.wait(timeout=min(
                            GIT_COMPLETION_WAIT_SECONDS,
                            max(0.0, command_deadline - time.monotonic()),
                        ))
                    except subprocess.TimeoutExpired:
                        pass

                capture_step = "descendants"
                if os.name == "posix":
                    try:
                        os.killpg(process.pid, 0)
                    except ProcessLookupError:
                        pass
                    else:
                        raise GitCommandError("git_descendant_running", operation)
                elif os.name == "nt":
                    observed_descendants = _windows_git_descendants(process.pid)
                    if observed_descendants:
                        raise GitCommandError("git_descendant_running", operation)
                capture_step = "verify_capture"
                size = os.fstat(capture.fileno()).st_size
                account_output(size)
                if size > context.limits.max_capture_bytes:
                    raise ScanLimitExceeded("git_output_limit", operation, measured=size, limit=context.limits.max_capture_bytes)
                if return_code != 0:
                    if (allow_nonzero and return_code == 1 and size > 0
                            and args[:2] == ["diff", "--no-index"]):
                        capture_step = "consume"
                        yield VerifiedCapture(context, capture, size, deadline, operation)
                        capture_step = "cleanup"
                        return
                    if allow_nonzero and size == 0:
                        if args == ["rev-parse", "--verify", "HEAD"] and return_code == 128:
                            capture_step = "consume"
                            yield None
                            capture_step = "cleanup"
                            return
                        if (len(args) == 4 and args[:3] == ["show-ref", "--verify", "--quiet"]
                                and return_code == 1):
                            capture_step = "consume"
                            yield None
                            capture_step = "cleanup"
                            return
                    raise GitCommandError("git_failed", operation, exit_status=return_code)
                capture_step = "verify_capture"
                _verify_private_capture(capture)
                capture_step = "consume"
                yield VerifiedCapture(context, capture, size, deadline, operation)
                capture_step = "cleanup"
            except BaseException:
                _stop_git_process(process, subprocess, observed_descendants)
                raise
    except OSError as exc:
        details: dict[str, int] = {}
        if type(exc.errno) is int:
            details["os_errno"] = exc.errno
        if capture_step == "spawn":
            details["attempts"] = attempts
        raise GitCommandError("git_capture_failed", operation,
                              capture_step=capture_step, **details) from exc
    finally:
        context.release_temp(temporary_bytes)


def _verify_private_capture(handle: BinaryIO) -> None:
    details = os.fstat(handle.fileno())
    if (not stat.S_ISREG(details.st_mode) or _is_reparse_point(details)
            or (os.name == "posix" and
                (details.st_mode & 0o077 or details.st_uid != os.geteuid()))):
        raise GitCommandError("git_capture_failed", capture_step="verify_capture")


class VerifiedCapture:
    """A completed private capture, lent only while its owner is open."""

    def __init__(self, context: ScanContext, handle: BinaryIO, size: int, deadline: float | None, operation: str):
        self.context = context
        self.handle = handle
        self.size = size
        self.deadline = deadline
        self.operation = operation

    def chunks(self, offset: int = 0, length: int | None = None, chunk_bytes: int = 65536) -> Iterator[bytes]:
        length = self.size - offset if length is None else length
        if offset < 0 or length < 0 or offset + length > self.size or chunk_bytes <= 0:
            raise GitCommandError("git_output_invalid", self.operation)
        self.context.check_deadline(self.deadline)
        if os.fstat(self.handle.fileno()).st_size != self.size:
            raise GitCommandError("git_output_invalid", self.operation)
        self.handle.seek(offset)
        remaining = length
        while remaining:
            self.context.check_deadline(self.deadline)
            chunk = self.handle.read(min(remaining, chunk_bytes, 65536))
            if not chunk:
                raise GitCommandError("git_output_invalid", self.operation)
            remaining -= len(chunk)
            yield chunk
        self.context.check_deadline(self.deadline)
        if os.fstat(self.handle.fileno()).st_size != self.size:
            raise GitCommandError("git_output_invalid", self.operation)

    def records(self, separator: bytes, *, maximum: int | None = None) -> Iterator[bytes]:
        maximum = self.context.limits.max_capture_bytes if maximum is None else maximum
        pending = bytearray()
        for chunk in self.chunks():
            start = 0
            while True:
                end = chunk.find(separator, start)
                if end < 0:
                    pending.extend(chunk[start:])
                    if len(pending) > maximum:
                        raise GitCommandError("git_output_invalid", self.operation)
                    break
                pending.extend(chunk[start:end])
                if len(pending) > maximum:
                    raise GitCommandError("git_output_invalid", self.operation)
                yield bytes(pending)
                pending.clear()
                start = end + 1
        if pending:
            raise GitCommandError("git_output_invalid", self.operation)


def run_git(context: ScanContext, args: list[str], *, cwd: Path, text: bool = True,
            allow_nonzero: bool = False, deadline: float | None = None,
            input_bytes: bytes | None = None) -> str | bytes | None:
    # Small control output compatibility. Bodies use capture ranges directly.
    with capture_git(context, args, cwd=cwd, allow_nonzero=allow_nonzero,
                     deadline=deadline, input_bytes=input_bytes) as capture:
        if capture is None:
            return None
        output = b"".join(capture.chunks())
        return os.fsdecode(output) if text else output


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


def repo_root(context: ScanContext, work_dir: Path, *, deadline: float | None = None) -> Path:
    output = run_git(context, ["rev-parse", "--show-toplevel"], cwd=work_dir, deadline=deadline)
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


def is_inside_git_repo(context: ScanContext, work_dir: Path, *, deadline: float | None = None) -> bool:
    try:
        output = run_git(context,
            ["rev-parse", "--is-inside-work-tree"],
            cwd=work_dir,
            deadline=deadline,
        )
    except GitCommandError:
        if repository_marker_exists(work_dir):
            raise
        return False
    return isinstance(output, str) and output.strip() == "true"


def has_head(context: ScanContext, root: Path, *, deadline: float | None = None) -> bool:
    head = run_git(context,
        ["rev-parse", "--verify", "HEAD"],
        cwd=root,
        allow_nonzero=True,
        deadline=deadline,
    )
    if head is not None:
        return True
    branch = run_git(context, ["symbolic-ref", "--quiet", "HEAD"], cwd=root, deadline=deadline)
    if not isinstance(branch, str) or not branch.startswith("refs/heads/") or branch.count("\n") != 1:
        raise GitCommandError("git_head_invalid", "git_head")
    branch_exists = run_git(context,
        ["show-ref", "--verify", "--quiet", branch.rstrip("\n")],
        cwd=root,
        allow_nonzero=True,
        deadline=deadline,
    )
    if branch_exists is not None:
        raise GitCommandError("git_head_invalid", "git_head")
    return False


def collect_unmerged_files(context: ScanContext,
    root: Path, *, deadline: float | None = None,
) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    with capture_git(context, ["ls-files", "--unmerged", "-z", "--"], cwd=root,
                     deadline=deadline) as capture:
        for record in capture.records(b"\0"):
            source, path, _ = parse_index_record(
                record, allowed_stages={1, 2, 3}, operation="git_candidates")
            candidate = (source, path)
            if candidate in seen:
                raise GitCommandError("git_output_invalid", "git_candidates")
            seen.add(candidate)
            candidates.append(candidate)
            if len(candidates) > context.limits.max_objects:
                raise ScanLimitExceeded("snapshot_count_limit", "git_candidates",
                                        measured=len(candidates), limit=context.limits.max_objects)
    return candidates


def collect_files(context: ScanContext,
    root: Path, scope: str, root_has_head: bool, *, deadline: float | None = None,
) -> list[tuple[str, str]]:
    candidates = set(collect_unmerged_files(context, root, deadline=deadline))
    unmerged_paths = {path for _, path in candidates}
    diff_options = ["--name-only", "-z", "--no-ext-diff", "--no-color",
                    "--no-textconv", "--diff-filter=ACMRTUXB"]

    def add_paths(args: list[str], source: str) -> None:
        with capture_git(context, args, cwd=root, deadline=deadline) as capture:
            for raw_path in capture.records(b"\0"):
                if not raw_path:
                    continue
                path = os.fsdecode(raw_path)
                if source == CANDIDATE_STAGED and path in unmerged_paths:
                    continue
                actual_source = (CANDIDATE_UNMERGED_WORKTREE
                                 if source == CANDIDATE_WORKTREE and path in unmerged_paths
                                 else source)
                candidates.add((actual_source, path))
                if len(candidates) > context.limits.max_objects:
                    raise ScanLimitExceeded("snapshot_count_limit", "git_candidates",
                                            measured=len(candidates), limit=context.limits.max_objects)

    if scope in {"staged", "diff"}:
        add_paths(["diff", "--cached", *diff_options,
                   *(["HEAD"] if root_has_head else []), "--"], CANDIDATE_STAGED)
    if scope == "diff":
        add_paths(["diff", *diff_options, "--"], CANDIDATE_WORKTREE)
        add_paths(["ls-files", "-z", "--others", "--exclude-standard"], CANDIDATE_UNTRACKED)
    return sorted(candidates, key=lambda candidate: (candidate[1], candidate[0]))


def _is_reparse_point(details: os.stat_result) -> bool:
    attributes = getattr(details, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & flag)


def _validate_candidate_parts(path: str) -> tuple[str, ...]:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or not parsed.parts or any(part in {"", ".", ".."} for part in parsed.parts):
        raise ScanSecurityError("candidate_unsafe", "candidate_read")
    return parsed.parts


def parse_index_record(record: bytes, *, allowed_stages: set[int], operation: str,
                       canonical_path: bool = False) -> tuple[str, str, bytes]:
    header, separator, raw_path = record.partition(b"\t")
    match = re.fullmatch(rb"[0-7]{6} ([0-9a-f]{40}|[0-9a-f]{64}) ([0-3])", header)
    if not separator or not raw_path or match is None or int(match.group(2)) not in allowed_stages:
        raise GitCommandError("git_output_invalid", operation)
    path = os.fsdecode(raw_path)
    parts = _validate_candidate_parts(path)
    if canonical_path and "/".join(parts) != path:
        raise GitCommandError("git_output_invalid", operation)
    stage = int(match.group(2))
    source = CANDIDATE_STAGED if stage == 0 else CANDIDATE_UNMERGED_STAGES[stage - 1]
    return source, path, match.group(1)


def is_index_source(source: str) -> bool:
    return source == CANDIDATE_STAGED or source in CANDIDATE_UNMERGED_STAGES


@contextlib.contextmanager
def _worktree_descriptor(root: Path, path: str, *, allow_missing: bool = False) -> Iterator[int | None]:
    parts = _validate_candidate_parts(path)
    try:
        root_path = root.resolve(strict=True)
    except OSError as exc:
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    nonblocking = getattr(os, "O_NONBLOCK", 0)
    directory_flag = getattr(os, "O_DIRECTORY", 0)

    if os.open in os.supports_dir_fd and directory_flag:
        descriptors: list[int] = []
        opened = False
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
            descriptor = os.open(parts[-1], os.O_RDONLY | no_follow | nonblocking, dir_fd=current)
            descriptors.append(descriptor)
            opened = True
            yield descriptor
            return
        except (OSError, ValueError) as exc:
            if allow_missing and not opened and isinstance(exc, FileNotFoundError):
                yield None
                return
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
        descriptor = os.open(candidate, os.O_RDONLY | no_follow | nonblocking)
    except (OSError, ValueError) as exc:
        if allow_missing and isinstance(exc, FileNotFoundError):
            yield None
            return
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    try:
        yield descriptor
    except OSError as exc:
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    finally:
        os.close(descriptor)


class ScanBudget:
    def __init__(self, context: ScanContext):
        self.context = context
        self.deadline = context.deadline
        self.used_bytes = 0
        self.index_reserved: set[tuple[str, str]] = set()

    def remaining(self) -> int:
        self.context.check_deadline(self.deadline)
        return self.context.limits.max_candidate_bytes - self.used_bytes

    def charge(self, size: int, operation: str = "candidate_read") -> None:
        context = self.context
        self.context.check_deadline(self.deadline)
        if size > self.remaining():
            raise ScanLimitExceeded("total_bytes_limit", operation,
                                    measured=self.used_bytes + size, limit=context.limits.max_candidate_bytes)
        self.used_bytes += size

    def reserve_index(self, candidate: tuple[str, str], size: int) -> None:
        if candidate not in self.index_reserved:
            self.charge(size, "git_index")
            self.index_reserved.add(candidate)


class Snapshot:
    def __init__(self, candidate: tuple[str, str], capture: VerifiedCapture,
                 offset: int, byte_count: int):
        self.candidate = candidate
        self.capture = capture
        self.offset = offset
        self.byte_count = byte_count
        self.active = True
        self.classification = "binary"
        self.baseline_oid = None
        self.baseline_revision = None
        self.baseline_capture = None

    def chunks(self, chunk_bytes: int = 65536) -> Iterator[bytes]:
        if not self.active:
            raise ScanSecurityError("candidate_read_failed", "candidate_read")
        for chunk in self.capture.chunks(self.offset, self.byte_count, chunk_bytes):
            if not self.active:
                raise ScanSecurityError("candidate_read_failed", "candidate_read")
            yield chunk

    def classify(self) -> None:
        digest = hashlib.sha256()
        decoder = codecs.getincrementaldecoder("utf-8")("strict")
        valid = True
        nul = False
        for chunk in self.chunks():
            digest.update(chunk)
            nul = nul or b"\0" in chunk
            if valid:
                try:
                    decoder.decode(chunk, final=False)
                except UnicodeDecodeError:
                    valid = False
        if valid:
            try:
                decoder.decode(b"", final=True)
            except UnicodeDecodeError:
                valid = False
        self.digest = digest.digest()
        self.classification = ("text" if not nul and
                               (valid or Path(self.candidate[1]).suffix.lower() in TEXT_EXTENSIONS)
                               else "binary")


def resolve_index_candidates(context: ScanContext, root: Path, index_candidates: list[tuple[str, str]],
                             *, deadline: float | None = None) -> dict[tuple[str, str], bytes]:
    paths: list[str] = []
    for _, path in index_candidates:
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
            path_bytes = len(os.fsencode(paths[cursor])) * 2 + 3
            if cursor > start and argument_bytes + path_bytes > 8192:
                break
            argument_bytes += path_bytes
            cursor += 1
        batch_paths = paths[start:cursor]
        with capture_git(context,
            ["--literal-pathspecs", "ls-files", "--stage", "-z", "--", *batch_paths],
            cwd=root, deadline=deadline,
        ) as capture:
            if capture is None or not capture.size:
                raise GitCommandError("git_output_invalid", "git_index")
            for record in capture.records(b"\0"):
                source, path, oid = parse_index_record(
                    record, allowed_stages={0, 1, 2, 3}, operation="git_index", canonical_path=True)
                if path not in batch_paths:
                    # Literal pathspecs still expand directory descendants.
                    if any(path.startswith(parent + "/") for parent in batch_paths):
                        continue
                    raise GitCommandError("git_output_invalid", "git_index")
                candidate = (source, path)
                if candidate not in expected_candidates or candidate in resolved:
                    raise GitCommandError("git_output_invalid", "git_index")
                resolved[candidate] = oid
    if len(resolved) != len(index_candidates):
        raise GitCommandError("git_output_invalid", "git_index")
    return resolved


class SnapshotSource:
    """Own one index capture and one worktree spool in candidate order."""

    def __init__(self, root: Path, candidates: list[tuple[str, str]], budget: ScanBudget, *, diff_baselines: bool = False):
        context = budget.context
        self.root = root
        self.budget = budget
        self.objects: list[tuple[tuple[str, str], bytes, int, bytes]] = []
        self.cursor = 0
        self.batch_owner = contextlib.ExitStack()
        self.baseline_owner = contextlib.ExitStack()
        self.baseline_ranges = {}
        self.head_baselines = {}
        self.ranges: dict[tuple[str, str], tuple[VerifiedCapture, int, int]] = {}
        self.baselines = {}
        self.head_revision = None
        index_candidates = [candidate for candidate in candidates if is_index_source(candidate[0])]
        baseline_candidates = []
        if diff_baselines:
            revision = run_git(context, ["rev-parse", "--verify", "HEAD"], cwd=root, deadline=budget.deadline)
            if not isinstance(revision, str) or re.fullmatch(r"[0-9a-f]{40}\n|[0-9a-f]{64}\n", revision) is None:
                raise GitCommandError("git_output_invalid", "git_diff")
            self.head_revision = revision.strip()
            self.head_baselines = head_baseline_oids(context, root, self.head_revision,
                [path for source, path in candidates if source == CANDIDATE_STAGED])
            baseline_candidates = [(CANDIDATE_STAGED, path) for source, path in candidates
                                   if source == CANDIDATE_WORKTREE]
        required = list(dict.fromkeys([*index_candidates, *baseline_candidates]))
        resolved = resolve_index_candidates(context, root, required, deadline=budget.deadline) if required else {}
        self.baselines = {path: resolved[(CANDIDATE_STAGED, path)] for _, path in baseline_candidates}
        self._capture_baselines(context)
        if not index_candidates:
            return
        with capture_git(context, ["cat-file", "--batch-check"], cwd=root,
                         input_bytes=b"".join(resolved[c] + b"\n" for c in index_candidates),
                         deadline=budget.deadline) as capture:
            records = iter(capture.records(b"\n", maximum=96))
            for candidate in index_candidates:
                header = next(records, None)
                match = (re.fullmatch(rb"([0-9a-f]{40}|[0-9a-f]{64}) blob ([0-9]{1,20})", header)
                         if header is not None else None)
                if match is None or match.group(1) != resolved[candidate]:
                    raise GitCommandError("git_output_invalid", "git_index")
                size = int(match.group(2))
                budget.reserve_index(candidate, size)
                self.objects.append((candidate, match.group(1), size, header + b"\n"))
            if next(records, None) is not None:
                raise GitCommandError("git_output_invalid", "git_index")

    def _capture_baselines(self, context):
        oids = list(dict.fromkeys(oid for oid in [*self.head_baselines.values(), *self.baselines.values()] if oid))
        if not oids:
            return
        with capture_git(context, ["cat-file", "--batch-check"], cwd=self.root,
                         input_bytes=b"".join(oid + b"\n" for oid in oids), deadline=self.budget.deadline) as capture:
            rows = list(capture.records(b"\n", maximum=96))
        if len(rows) != len(oids):
            raise GitCommandError("git_output_invalid", "git_diff")
        entries = []
        total = 0
        for oid, row in zip(oids, rows):
            match = re.fullmatch(rb"([0-9a-f]{40}|[0-9a-f]{64}) blob ([0-9]{1,20})", row)
            if match is None or match.group(1) != oid:
                raise GitCommandError("git_output_invalid", "git_diff")
            size = int(match.group(2))
            header = row + b"\n"
            entries.append((oid, size, header))
            total += len(header) + size + 1
        # Larger baselines keep independent bounded capture in diff inputs.
        # Small repeated baselines share one stable protected capture.
        if total > context.limits.max_capture_bytes:
            return
        capture = self.baseline_owner.enter_context(capture_git(context, ["cat-file", "--batch"],
            cwd=self.root, input_bytes=b"".join(oid + b"\n" for oid in oids), deadline=self.budget.deadline))
        if capture.size != total:
            raise GitCommandError("git_output_invalid", "git_diff")
        offset = 0
        for oid, size, header in entries:
            if b"".join(capture.chunks(offset, len(header))) != header:
                raise GitCommandError("git_output_invalid", "git_diff")
            offset += len(header)
            if b"".join(capture.chunks(offset + size, 1)) != b"\n":
                raise GitCommandError("git_output_invalid", "git_diff")
            self.baseline_ranges[oid] = (capture, offset, size)
            offset += size + 1

    def finish(self):
        self.close()
        self.baseline_owner.close()
        self.baseline_ranges.clear()

    def close(self) -> None:
        self.batch_owner.close()
        self.ranges.clear()

    def _next_batch(self) -> None:
        context = self.budget.context
        self.close()
        start = self.cursor
        capture_bytes = 0
        while self.cursor < len(self.objects):
            _, _, size, header = self.objects[self.cursor]
            framed_size = len(header) + size + 1
            if capture_bytes + framed_size > context.limits.max_capture_bytes:
                break
            capture_bytes += framed_size
            self.cursor += 1
        batch = self.objects[start:self.cursor]
        if not batch:
            candidate, oid, size, _ = self.objects[self.cursor]
            self.cursor += 1
            capture = self.batch_owner.enter_context(capture_git(context,
                ["cat-file", "blob", oid.decode("ascii")], cwd=self.root, deadline=self.budget.deadline))
            if capture.size != size:
                raise GitCommandError("git_output_invalid", "git_index")
            self.ranges[candidate] = (capture, 0, size)
            return
        capture = self.batch_owner.enter_context(capture_git(context,
            ["cat-file", "--batch"], cwd=self.root,
            input_bytes=b"".join(oid + b"\n" for _, oid, _, _ in batch),
            deadline=self.budget.deadline))
        if capture.size != capture_bytes:
            raise GitCommandError("git_output_invalid", "git_index")
        offset = 0
        for candidate, _, size, header in batch:
            if b"".join(capture.chunks(offset, len(header))) != header:
                raise GitCommandError("git_output_invalid", "git_index")
            offset += len(header)
            if b"".join(capture.chunks(offset + size, 1)) != b"\n":
                raise GitCommandError("git_output_invalid", "git_index")
            self.ranges[candidate] = (capture, offset, size)
            offset += size + 1
        if offset != capture.size:
            raise GitCommandError("git_output_invalid", "git_index")

    @contextlib.contextmanager
    def acquire(self, candidate: tuple[str, str]) -> Iterator[Snapshot | None]:
        context = self.budget.context
        source, path = candidate
        snapshot = None
        spool_bytes = 0
        try:
            if is_index_source(source):
                if candidate not in self.ranges:
                    self._next_batch()
                snapshot = Snapshot(candidate, *self.ranges[candidate])
                snapshot.baseline_revision = self.head_revision
                snapshot.baseline_oid = self.head_baselines.get(path)
                snapshot.baseline_capture = self.baseline_ranges.get(snapshot.baseline_oid)
                snapshot.classify()
                yield snapshot
            else:
                with _worktree_descriptor(self.root, path,
                        allow_missing=source == CANDIDATE_UNMERGED_WORKTREE) as descriptor:
                    if descriptor is None:
                        yield None
                        return
                    details = os.fstat(descriptor)
                    if not stat.S_ISREG(details.st_mode) or _is_reparse_point(details):
                        raise ScanSecurityError("candidate_unsafe", "candidate_read")
                    remaining = self.budget.remaining()
                    if details.st_size > remaining:
                        raise ScanLimitExceeded("total_bytes_limit", "candidate_read",
                                                measured=self.budget.used_bytes + details.st_size,
                                                limit=context.limits.max_candidate_bytes)
                    with tempfile.TemporaryFile(mode="w+b") as spool:
                        _verify_private_capture(spool)
                        size = 0
                        ceiling = remaining
                        while True:
                            context.check_deadline(self.budget.deadline)
                            chunk = os.read(descriptor, min(65536, ceiling + 1 - size))
                            if not chunk:
                                break
                            size += len(chunk)
                            if size > ceiling:
                                raise ScanLimitExceeded("total_bytes_limit", "candidate_read",
                                                        measured=self.budget.used_bytes + len(chunk),
                                                        limit=context.limits.max_candidate_bytes)
                            self.budget.charge(len(chunk))
                            spool_bytes += len(chunk)
                            context.charge_temp(len(chunk))
                            spool.write(chunk)
                            after = os.fstat(descriptor)
                            if (after.st_size <= remaining and
                                    (details.st_size, details.st_mtime_ns) != (after.st_size, after.st_mtime_ns)):
                                raise ScanSecurityError("candidate_changed", "candidate_read")
                        spool.flush()
                        capture = VerifiedCapture(context, spool, size, self.budget.deadline, "candidate_read")
                        snapshot = Snapshot(candidate, capture, 0, size)
                        snapshot.baseline_oid = self.baselines.get(path)
                        snapshot.baseline_capture = self.baseline_ranges.get(snapshot.baseline_oid)
                        snapshot.classify()
                        yield snapshot
        except OSError as exc:
            raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
        finally:
            context.release_temp(spool_bytes)
            if snapshot is not None:
                snapshot.active = False
            if candidate in self.ranges:
                del self.ranges[candidate]
                if not self.ranges:
                    self.close()


@contextlib.contextmanager
def snapshot_source(root: Path, candidates: list[tuple[str, str]],
                    budget: ScanBudget, *, diff_baselines: bool = False) -> Iterator[SnapshotSource]:
    source = SnapshotSource.__new__(SnapshotSource)
    try:
        source.__init__(root, candidates, budget, diff_baselines=diff_baselines)
        yield source
    finally:
        source.finish()




@contextlib.contextmanager
def snapshot_diff_inputs(context: ScanContext, root: Path, path: str, source: str,
                         snapshot: Snapshot):
    """Lend private stable comparison files, never the original mutable path."""
    if source not in {CANDIDATE_STAGED, CANDIDATE_WORKTREE}:
        raise ScanSecurityError("candidate_unsafe", "git_diff")
    oid = snapshot.baseline_oid
    if oid is not None and (not isinstance(oid, bytes) or re.fullmatch(rb"[0-9a-f]{40}|[0-9a-f]{64}", oid) is None):
        raise GitCommandError("git_output_invalid", "git_diff")
    snapshot.baseline_oid = oid
    charged = 0
    try:
        with tempfile.TemporaryDirectory(prefix="scan-diff-") as directory:
            before = Path(directory) / "before"
            after = Path(directory) / "after"
            with contextlib.ExitStack() as resources:
                if snapshot.baseline_capture is not None:
                    capture, offset, size = snapshot.baseline_capture
                    baseline_chunks = capture.chunks(offset, size)
                elif oid is not None:
                    baseline = resources.enter_context(capture_git(context,
                        ["cat-file", "blob", oid.decode("ascii")], cwd=root, deadline=context.deadline))
                    baseline_chunks = baseline.chunks()
                else:
                    baseline_chunks = ()
                for destination, chunks in ((before, baseline_chunks),
                                            (after, snapshot.chunks())):
                    with destination.open("xb") as output:
                        os.chmod(destination, 0o600)
                        _verify_private_capture(output)
                        for chunk in chunks:
                            context.check_deadline()
                            charged += len(chunk)
                            context.charge_temp(len(chunk))
                            output.write(chunk)
                yield before, after
    except OSError as exc:
        raise ScanSecurityError("candidate_read_failed", "git_diff") from exc
    finally:
        context.release_temp(charged)


def head_baseline_oids(context, root, revision, paths):
    """Resolve relevant HEAD paths in bounded literal argument batches."""
    result = {path: None for path in paths}
    cursor = 0
    while cursor < len(paths):
        start = cursor
        used = 0
        while cursor < len(paths):
            cost = len(os.fsencode(paths[cursor])) * 2 + 3
            if cursor > start and used + cost > 8192:
                break
            used += cost
            cursor += 1
        selected = paths[start:cursor]
        seen = set()
        with capture_git(context, ["--literal-pathspecs", "ls-tree", "-z", revision, "--", *selected],
                         cwd=root, deadline=context.deadline) as capture:
            for record in capture.records(b"\0"):
                header, separator, raw_path = record.partition(b"\t")
                match = re.fullmatch(rb"[0-7]{6} blob ([0-9a-f]{40}|[0-9a-f]{64})", header)
                path = os.fsdecode(raw_path)
                if not separator or path not in selected or path in seen or match is None:
                    raise GitCommandError("git_output_invalid", "git_diff")
                seen.add(path)
                result[path] = match.group(1)
    return result
