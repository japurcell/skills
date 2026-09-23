#!/usr/bin/env python3
# Generated from hooks/families/scan_secrets.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import stat
import sys
import threading
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


class GitCommandError(RuntimeError):
    pass


class ScanSecurityError(RuntimeError):
    pass


class ScanLimitExceeded(ScanSecurityError):
    pass


def enforce_deadline(deadline: float | None) -> None:
    if deadline is not None and time.monotonic() >= deadline:
        raise ScanLimitExceeded("secret scan exceeds the time limit")


def noop() -> None:
    emit_json({})
    raise SystemExit(0)


def warn_and_noop(message: str) -> None:
    print(message, file=sys.stderr)
    noop()
# BEGIN PROVIDER ADAPTER
def emit_block_denial(reason: str) -> None:
    if HOOK_EVENT != "PreToolUse":
        emit_json({"decision": "block", "reason": reason})
    else:
        emit_json({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            },
        })
# END PROVIDER ADAPTER


def read_payload(mode: str) -> dict | None:
    payload: dict | None = None
    try:
        payload = read_json_input()
    except Exception as exc:
        if mode == "block":
            reason = f"{SCRIPT_NAME}: {exc}"
            print(reason, file=sys.stderr)
            emit_block_denial(reason)
            return None
        warn_and_noop(f"{SCRIPT_NAME}: {exc}")

    if not isinstance(payload, dict):
        if mode == "block":
            reason = f"{SCRIPT_NAME}: invalid JSON input."
            print(reason, file=sys.stderr)
            emit_block_denial(reason)
            return None
        warn_and_noop(f"{SCRIPT_NAME}: invalid JSON input; skipping hook.")

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
) -> str | bytes | None:
    import subprocess

    now = time.monotonic()
    command_deadline = now + 5.0
    if deadline is not None:
        command_deadline = min(command_deadline, deadline)
    if command_deadline <= now:
        raise ScanLimitExceeded("secret scan exceeds the time limit")

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = ""
    env["GIT_LITERAL_PATHSPECS"] = "1"
    popen_options: dict[str, object] = {
        "cwd": str(cwd),
        "env": env,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "posix":
        popen_options["start_new_session"] = True

    try:
        process = subprocess.Popen(["git", *args], **popen_options)
    except OSError as exc:
        raise GitCommandError("unable to execute Git") from exc

    assert process.stdout is not None
    output = bytearray()
    read_errors: list[BaseException] = []

    def read_stdout() -> None:
        try:
            while len(output) <= MAX_GIT_OUTPUT_BYTES:
                remaining = MAX_GIT_OUTPUT_BYTES + 1 - len(output)
                chunk = process.stdout.read(min(65536, remaining))
                if not chunk:
                    return
                output.extend(chunk)
        except BaseException as exc:  # noqa: BLE001
            read_errors.append(exc)
        finally:
            try:
                process.stdout.close()
            except OSError:
                pass

    reader = threading.Thread(target=read_stdout, daemon=True)
    reader.start()
    reader.join(max(0.0, command_deadline - time.monotonic()))

    if reader.is_alive():
        _stop_git_process(process, subprocess)
        try:
            process.stdout.close()
        except OSError:
            pass
        reader.join(0.5)
        raise ScanLimitExceeded("Git command exceeds the scanner time limit")
    if read_errors:
        _stop_git_process(process, subprocess)
        raise GitCommandError("unable to read Git output") from read_errors[0]
    if len(output) > MAX_GIT_OUTPUT_BYTES:
        _stop_git_process(process, subprocess)
        raise ScanLimitExceeded("Git output exceeds the scanner limit")

    try:
        return_code = process.wait(timeout=max(0.0, command_deadline - time.monotonic()))
    except subprocess.TimeoutExpired as exc:
        _stop_git_process(process, subprocess)
        raise ScanLimitExceeded("Git command exceeds the scanner time limit") from exc

    if return_code != 0:
        if allow_nonzero:
            return None
        raise GitCommandError(f"Git command failed with exit {return_code}")

    raw_output = bytes(output)
    return os.fsdecode(raw_output) if text else raw_output


def _stop_git_process(process: object, subprocess_module: object) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
    except (OSError, ProcessLookupError):
        pass
    try:
        process.wait(timeout=0.25)
        return
    except subprocess_module.TimeoutExpired:
        pass
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except (OSError, ProcessLookupError):
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
        raise ScanSecurityError("unable to inspect repository boundary") from exc

    for directory in (current, *current.parents):
        try:
            (directory / ".git").lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ScanSecurityError("unable to inspect repository marker") from exc
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
    return run_git(
        ["rev-parse", "--verify", "HEAD"],
        cwd=root,
        allow_nonzero=True,
        deadline=deadline,
    ) is not None


def decode_nul_paths(output: bytes) -> list[str]:
    if not output:
        return []
    if not output.endswith(b"\0"):
        raise GitCommandError("Git returned malformed NUL-delimited paths")
    return [os.fsdecode(path) for path in output[:-1].split(b"\0") if path]


def collect_files(
    root: Path,
    scope: str,
    root_has_head: bool,
    *,
    deadline: float | None = None,
) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
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
                (CANDIDATE_WORKTREE, path) for path in decode_nul_paths(output)
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
        raise ScanLimitExceeded("modified file count exceeds the scanner limit")
    return unique_candidates


def _is_reparse_point(details: os.stat_result) -> bool:
    attributes = getattr(details, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & flag)


def _validate_candidate_parts(path: str) -> tuple[str, ...]:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or not parsed.parts or any(part in {"", ".", ".."} for part in parsed.parts):
        raise ScanSecurityError("candidate path escapes the repository")
    return parsed.parts


def _read_bounded_descriptor(descriptor: int) -> bytes:
    details = os.fstat(descriptor)
    if not stat.S_ISREG(details.st_mode) or _is_reparse_point(details):
        raise ScanSecurityError("candidate must be a regular file")
    if details.st_size > MAX_FILE_BYTES:
        raise ScanLimitExceeded("candidate file exceeds the scanner limit")

    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, min(65536, MAX_FILE_BYTES + 1 - total))
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        total += len(chunk)
        if total > MAX_FILE_BYTES:
            raise ScanLimitExceeded("candidate file exceeds the scanner limit")


def _read_worktree_candidate(root: Path, path: str) -> bytes:
    parts = _validate_candidate_parts(path)
    root_path = root.resolve(strict=True)
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
                    raise ScanSecurityError("candidate path contains a link")
                current = os.open(
                    component,
                    os.O_RDONLY | directory_flag | no_follow,
                    dir_fd=current,
                )
                descriptors.append(current)
            details = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
                raise ScanSecurityError("candidate path contains a link")
            descriptor = os.open(parts[-1], os.O_RDONLY | no_follow, dir_fd=current)
            descriptors.append(descriptor)
            return _read_bounded_descriptor(descriptor)
        except (OSError, ValueError) as exc:
            if isinstance(exc, ScanSecurityError):
                raise
            raise ScanSecurityError("unable to open candidate safely") from exc
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
                raise ScanSecurityError("candidate path contains a link")
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root_path)
        descriptor = os.open(candidate, os.O_RDONLY | no_follow)
    except (OSError, ValueError) as exc:
        if isinstance(exc, ScanSecurityError):
            raise
        raise ScanSecurityError("unable to open candidate safely") from exc
    try:
        return _read_bounded_descriptor(descriptor)
    finally:
        os.close(descriptor)


def read_candidate_bytes(
    root: Path,
    path: str,
    source: str,
    *,
    deadline: float | None = None,
) -> bytes:
    if source == CANDIDATE_STAGED:
        _validate_candidate_parts(path)
        index_object = f":./{path}"
        size_output = run_git(
            ["cat-file", "-s", index_object],
            cwd=root,
            text=False,
            deadline=deadline,
        )
        if not isinstance(size_output, bytes):
            raise GitCommandError("Git returned an invalid staged size")
        try:
            size = int(size_output.strip())
        except ValueError as exc:
            raise GitCommandError("Git returned an invalid staged size") from exc
        if size < 0 or size > MAX_FILE_BYTES:
            raise ScanLimitExceeded("candidate file exceeds the scanner limit")
        output = run_git(
            ["show", "--no-textconv", index_object],
            cwd=root,
            text=False,
            deadline=deadline,
        )
        if not isinstance(output, bytes) or len(output) != size:
            raise GitCommandError("Git returned invalid staged content")
        return output

    return _read_worktree_candidate(root, path)


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
        raise ScanSecurityError("unsupported diff candidate source")
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
            raise GitCommandError("Git returned malformed unified diff output")
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
        raise ScanSecurityError("required log path is missing") from None
    except OSError as exc:
        raise ScanSecurityError("unable to inspect log path") from exc
    if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
        raise ScanSecurityError("log paths must not be links or reparse points")
    return details


def _ensure_secure_log_directory(directory: Path) -> None:
    try:
        directory.mkdir(parents=True, mode=0o700, exist_ok=True)
        details = _assert_safe_log_path(directory, allow_missing=False)
        if details is None or not stat.S_ISDIR(details.st_mode):
            raise ScanSecurityError("log parent must be a directory")
        os.chmod(directory, 0o700)
    except ScanSecurityError:
        raise
    except OSError as exc:
        raise ScanSecurityError("unable to secure log directory") from exc


def _open_secure_regular(path: Path, flags: int) -> int:
    _assert_safe_log_path(path)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    binary = getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags | no_follow | binary, 0o600)
    except OSError as exc:
        raise ScanSecurityError("unable to open log path safely") from exc
    try:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode) or _is_reparse_point(details):
            raise ScanSecurityError("log path must be a regular file")
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
        raise ScanSecurityError("invalid log rotation limits")
    if incoming_bytes < 1 or incoming_bytes > MAX_LOG_RECORD_BYTES:
        raise ScanLimitExceeded("scan-log record exceeds the size limit")
    if incoming_bytes > max_bytes:
        raise ScanLimitExceeded("scan-log record exceeds the configured rotation size")
    details = _assert_safe_log_path(log_path)
    if details is None:
        return
    if not stat.S_ISREG(details.st_mode):
        raise ScanSecurityError("scan log must be a regular file")
    if details.st_size + incoming_bytes <= max_bytes:
        return

    paths = [log_path.with_name(f"{log_path.name}.{index}") for index in range(1, backups + 2)]
    for path in paths:
        details = _assert_safe_log_path(path)
        if details is not None and not stat.S_ISREG(details.st_mode):
            raise ScanSecurityError("rotated scan log must be a regular file")

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
        raise ScanSecurityError("unable to rotate scan log safely") from exc


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
    enforce_deadline(lock_deadline)
    if fcntl_module is not None:
        while True:
            enforce_deadline(lock_deadline)
            try:
                fcntl_module.flock(lock_fd, fcntl_module.LOCK_EX | fcntl_module.LOCK_NB)
                return "posix"
            except (BlockingIOError, OSError) as exc:
                if time.monotonic() >= lock_deadline:
                    raise ScanLimitExceeded("timed out waiting for scan-log lock") from exc
                time.sleep(LOG_LOCK_POLL_SECONDS)
    if msvcrt_module is not None:
        if os.fstat(lock_fd).st_size == 0:
            os.write(lock_fd, b"\0")
        while True:
            enforce_deadline(lock_deadline)
            try:
                os.lseek(lock_fd, 0, os.SEEK_SET)
                msvcrt_module.locking(lock_fd, msvcrt_module.LK_NBLCK, 1)
                return "windows"
            except OSError as exc:
                if time.monotonic() >= lock_deadline:
                    raise ScanLimitExceeded("timed out waiting for scan-log lock") from exc
                time.sleep(LOG_LOCK_POLL_SECONDS)
    raise ScanSecurityError("no supported scan-log lock is available")


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


def append_scan_log(
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
        raise ScanLimitExceeded("scan-log record exceeds the size limit")

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
        rotate_scan_log(
            log_path,
            len(record),
            int(os.environ.get("AUDIT_LOG_MAX_BYTES", "1048576")),
            int(os.environ.get("AUDIT_LOG_MAX_BACKUPS", "3")),
        )
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


def emit_output(findings_count: int, log_path: Path) -> None:
    if findings_count > 0:
        emit_json({"systemMessage": f"Potential secrets detected in modified files. See {log_path}."})
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
        raise ScanLimitExceeded("secret scan exceeds the time limit")
    if total_bytes > MAX_TOTAL_BYTES:
        raise ScanLimitExceeded("secret scan exceeds the total-byte limit")


def handle_unexpected_exception(_exc: Exception) -> int:
    mode = normalized_mode_from_env()
    reason = f"{SCRIPT_NAME}: unexpected scanner error."
    print(reason, file=sys.stderr)
    if mode == "block":
        emit_block_denial(reason)
        return 0
    emit_json({})
    return 0
# BEGIN PROVIDER ADAPTER
SESSION_ID_KEYS = ("session_id",)
DEFAULT_SECRETS_LOG_PATH = Path.home() / ".codex" / "hooks" / "secrets"
HOOK_EVENT = ""


def resolve_work_dir(payload: dict) -> Path:
    global HOOK_EVENT
    HOOK_EVENT = payload.get("hook_event_name", "")
    return Path(str(payload.get("cwd") or Path.cwd()))


def findings_denial_reason(scan_log: Path) -> str:
    return f"{SCRIPT_NAME}: potential secrets detected. See {scan_log}."
# END PROVIDER ADAPTER


def main() -> int:
    scan_started = time.monotonic()
    scan_deadline = scan_started + MAX_SCAN_SECONDS
    mode = normalized_mode_from_env()

    if not git_available():
        reason = f"{SCRIPT_NAME}: required command not found: git"
        if mode == "block":
            emit_block_denial(reason)
            return 0
        warn_and_noop(reason)

    if not audit_init():
        reason = f"{SCRIPT_NAME}: failed to initialize audit logging."
        if mode == "block":
            emit_block_denial(reason)
            return 0
        warn_and_noop(f"{reason[:-1]}; skipping hook.")

    payload = read_payload(mode)
    if payload is None:
        return 0
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
    work_dir = resolve_work_dir(payload)

    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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
        emit_output(0, scan_log)
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
        emit_output(0, scan_log)
        return 0

    root = repo_root(work_dir, deadline=scan_deadline)
    root_has_head = has_head(root, deadline=scan_deadline)
    candidates = collect_files(root, scope, root_has_head, deadline=scan_deadline)

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

    for source, path in candidates:
        enforce_scan_budget(scan_started, total_bytes)
        raw_bytes = read_candidate_bytes(root, path, source, deadline=scan_deadline)
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
        elif scope == "staged" or not root_has_head or source == CANDIDATE_UNTRACKED:
            candidate_lines = enumerate_file_lines(raw_bytes.decode("utf-8", errors="replace"))
        else:
            candidate_lines = emit_diff_added_lines(
                root,
                path,
                source,
                root_has_head=root_has_head,
                deadline=scan_deadline,
            )

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
        emit_output(0, scan_log)
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
