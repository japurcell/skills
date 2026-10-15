"""One bounded redacted scanner audit writer."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import stat
import time
from pathlib import Path
from .scan_types import (
    LOG_LOCK_POLL_SECONDS, LOG_LOCK_TIMEOUT_SECONDS, MAX_FILES, MAX_LOG_RECORD_BYTES,
    MAX_RETAINED_FINDINGS, ScanFailure, ScanLimitExceeded, ScanSecurityError, enforce_deadline,
)
from .scan_git import _is_reparse_point
from .scan_reporting import report_label, report_text, report_json_bytes

@dataclass(frozen=True)
class AuditPolicy:
    build: str
    provider: str
    action: str
    max_objects: int = MAX_FILES
    max_bytes: str | int = 1048576
    backups: str | int = 3

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


def append_scan_log(policy: AuditPolicy, **kwargs: object) -> None:
    try:
        _append_scan_log(policy, **kwargs)
    except ScanFailure:
        raise
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc


def _append_scan_log(
    policy: AuditPolicy, *,
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
    security_outcome: str | None = None,
    audit_outcome: str = "written",
    scan_result: dict | None = None,
) -> None:
    enforce_deadline(deadline)
    _ensure_secure_log_directory(log_path.parent)
    payload: dict[str, object] = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sessionId": report_label(session_id),
        "repoRoot": report_label(str(repo_root_path)),
        "mode": mode,
        "scope": scope,
        "status": status,
    }
    if status == "incomplete":
        # Incomplete records cannot carry payload-derived identifiers or paths.
        payload = {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "mode": mode, "scope": scope, "status": status, "action": policy.action}
        if diagnostic is not None:
            payload["diagnostic"] = diagnostic
    if note:
        payload["note"] = report_text(note, 512)
    payload.update(build=policy.build, provider=policy.provider,
                   profile="pending_snapshots_v1", route="pending_scan", action=policy.action,
                   cause=diagnostic["cause"] if diagnostic else status,
                   security_outcome=security_outcome or status, audit_outcome=audit_outcome,
                   inspection_outcome="incomplete" if status == "incomplete" else "complete",
                   enforcement="deny" if mode == "block" and status in {"findings", "incomplete"} else "allow")
    if scan_result is not None:
        payload["scanResult"] = scan_result
    if findings:
        payload["findings"] = findings[:MAX_RETAINED_FINDINGS]
    # Reserve structural/count metadata before retaining optional path labels.
    payload["omittedFindings"] = omitted_findings + max(0, len(findings) - MAX_RETAINED_FINDINGS)
    payload["findingsTruncated"] = findings_truncated
    payload["envFiles"] = []
    payload["omittedEnvFiles"] = len(env_files)
    retained_bytes = report_json_bytes(payload)
    for path in (env_files[:policy.max_objects] if status != "incomplete" else []):
        label = report_label(path)
        label_bytes = report_json_bytes(label) + 1
        if retained_bytes + label_bytes >= MAX_LOG_RECORD_BYTES - 128:
            break
        payload["envFiles"].append(label)
        payload["omittedEnvFiles"] -= 1
        retained_bytes += label_bytes
    while report_json_bytes(payload) >= MAX_LOG_RECORD_BYTES and payload.get("findings"):
        payload["findings"].pop()
        payload["omittedFindings"] += 1
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
            max_bytes = int(policy.max_bytes)
            backups = int(policy.backups)
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
