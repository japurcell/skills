#!/usr/bin/env python3
# Generated from hooks/families/tool_guard.py by scripts/generate-hooks.py. Do not edit.

from __future__ import annotations

# BEGIN PROVIDER ADAPTER
import json
import os
import stat
import sys
import time
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

try:
    import msvcrt
except ImportError:
    msvcrt = None

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import emit_json, read_json_input  # noqa: E402


TOOL_PROVIDER = "gemini"


def emit_skip_allow_response() -> None:
    emit_json({"decision": "allow"})
    raise SystemExit(0)


def emit_allow_response(system_message: str | None = None) -> None:
    payload: dict[str, str] = {"decision": "allow"}
    if system_message:
        payload["systemMessage"] = system_message
    emit_json(payload)
    raise SystemExit(0)


def emit_deny_response(reason: str) -> None:
    emit_json({"decision": "deny", "reason": reason})
    raise SystemExit(0)
# END PROVIDER ADAPTER

REPORT_BUILD = "659adb2c9a3590d6"


def guard_attribution(*, security, audit, enforcement, profile, route, cause):
    # This helper is available before optional policy imports and takes explicit
    # route/profile values so bootstrap and input failures retain attribution.
    return (f" security_outcome={security}; audit_outcome={audit}; enforcement={enforcement}; build={REPORT_BUILD}; "
            f"profile={profile}; route={route}; cause={cause}.")


MAX_GUARD_LOG_BYTES = 16384

try:
    from helpers.common import InputLimitError
    from helpers.tool_guard_policy import (
        MAX_GUARD_INPUT_BYTES, MAX_GUARD_INPUT_MARKERS, ScanLimitExceeded,
        InspectionResult, inspect_tool, normal_enforcement, read_tool_name,
        read_tool_input, build_action_excerpt, build_block_reason,
        log_threat_metadata, sanitize_tool_name, parse_allowlist, allowlist_contains,
        report_text, report_json_bytes,
    )
except Exception:
    emit_deny_response("Tool Guardian blocked execution due to an internal error."
                       + guard_attribution(security="incomplete", audit="not_attempted", enforcement="deny",
                                           profile="unavailable", route="bootstrap", cause="policy_unavailable"))


def guard_report(event, mode, tool_name, result, enforcement, excerpt):
    """Retain bounded owned metadata, then serialize in the provider adapter."""
    threats = log_threat_metadata(result.findings)
    payload = {"timestamp": TIMESTAMP, "event": event, "mode": mode,
               "tool": sanitize_tool_name(tool_name), "build": REPORT_BUILD,
               "provider": TOOL_PROVIDER, "profile": result.profile,
               "route": result.route, "profile_cause": result.profile_cause,
               "cause": threats[0]["rule_id"] if threats else event,
               "security_outcome": result.security, "audit_outcome": "written",
               "inspection_outcome": "complete" if result.complete else "incomplete",
               "enforcement": enforcement, "omittedThreats": 0}
    if event == "threats_detected":
        payload.update(threat_count=len(threats), threats=threats, excerpt=report_text(excerpt))
    while report_json_bytes(payload) > MAX_GUARD_LOG_BYTES - 256 and threats:
        threats.pop()
        payload["omittedThreats"] += 1
    return payload


def record_guard(event, mode, tool_name, result, enforcement, excerpt):
    try:
        log_payload(guard_report(event, mode, tool_name, result, enforcement, excerpt))
    except Exception:
        # A failed audit cannot erase a security finding or allow a clean call.
        warning = enforcement == "allow" and result.findings and result.complete
        audit_enforcement = "allow" if warning else "deny"
        outcome = "warning" if warning else "blocked"
        reason = build_block_reason(tool_name, result.findings, excerpt, outcome) if result.findings else "Tool Guardian blocked: audit unavailable."
        reason += guard_attribution(security=result.security, audit="failed", enforcement=audit_enforcement,
                                    profile=result.profile, route=result.route, cause="audit_unavailable")
        if warning:
            emit_allow_response(reason)
        emit_deny_response(reason)


def attributed_reason(tool_name, result, excerpt, enforcement):
    outcome = "warning" if enforcement == "allow" else "blocked"
    cause = result.findings[0]["rule_id"] if result.findings else result.profile_cause
    return (build_block_reason(tool_name, result.findings, excerpt, outcome)
            + guard_attribution(security=result.security, audit="written", enforcement=enforcement,
                                profile=result.profile, route=result.route, cause=cause))


def input_failure_reason(reason, cause):
    return reason + guard_attribution(security="incomplete", audit="not_attempted", enforcement="deny",
                                     profile="unsupported", route="input_validation", cause=cause)


# BEGIN PROVIDER ADAPTER

LOG_LOCK_TIMEOUT_SECONDS = 1.0


def format_error(error: Exception) -> str:
    return type(error).__name__


def configure_log() -> None:
    global TIMESTAMP, LOG_FILE
    log_dir = os.environ.get("TOOL_GUARD_LOG_DIR", os.path.expanduser("~/.gemini/hooks/tool-guardian"))
    LOG_FILE = f"{log_dir}/guard.log"
    TIMESTAMP = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _open_owner_only_no_follow(path: str, flags: int) -> int:
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags | no_follow, 0o600)
    try:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode):
            raise OSError(f"Log path is not a regular file: {path}")
        if not no_follow:
            path_details = os.stat(path, follow_symlinks=False)
            if not stat.S_ISREG(path_details.st_mode) or (
                path_details.st_dev,
                path_details.st_ino,
            ) != (details.st_dev, details.st_ino):
                raise OSError(f"Refusing linked or replaced log path: {path}")
        if hasattr(os, "fchmod"):
            os.fchmod(descriptor, 0o600)
        else:
            os.chmod(path, 0o600, follow_symlinks=False)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _acquire_log_lock(lock_path: str) -> int:
    descriptor = _open_owner_only_no_follow(lock_path, os.O_CREAT | os.O_RDWR)
    deadline = time.monotonic() + LOG_LOCK_TIMEOUT_SECONDS
    if fcntl is not None:
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return descriptor
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    os.close(descriptor)
                    raise TimeoutError(f"Timed out waiting for Tool Guardian log lock: {lock_path}") from None
                time.sleep(0.01)
    if msvcrt is not None:
        if os.fstat(descriptor).st_size == 0:
            os.write(descriptor, b"0")
            os.fsync(descriptor)
        while True:
            try:
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                return descriptor
            except OSError:
                if time.monotonic() >= deadline:
                    os.close(descriptor)
                    raise TimeoutError(f"Timed out waiting for Tool Guardian log lock: {lock_path}") from None
                time.sleep(0.01)
    os.close(descriptor)
    raise OSError("No supported Tool Guardian log locking primitive is available")


def _release_log_lock(descriptor: int) -> None:
    try:
        if fcntl is not None:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        elif msvcrt is not None:
            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
    finally:
        os.close(descriptor)


def append_log(log_file: str, payload: dict) -> None:
    parent = os.path.dirname(log_file)
    if parent:
        os.makedirs(parent, mode=0o700, exist_ok=True)

    lock_descriptor = _acquire_log_lock(f"{log_file}.lock")
    try:
        descriptor = _open_owner_only_no_follow(log_file, os.O_APPEND | os.O_CREAT | os.O_WRONLY)
        try:
            handle = os.fdopen(descriptor, "a", encoding="utf-8")
        except BaseException:
            os.close(descriptor)
            raise
        with handle:
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        _release_log_lock(lock_descriptor)


def log_payload(payload: dict) -> None:
    append_log(LOG_FILE, payload)

# END PROVIDER ADAPTER


def main() -> int:
    if os.environ.get("SKIP_TOOL_GUARD") == "true":
        emit_skip_allow_response()

    configure_log()
    mode = os.environ.get("GUARD_MODE", "block")
    if mode not in {"warn", "block"}:
        mode = "block"

    try:
        payload = read_json_input(max_bytes=MAX_GUARD_INPUT_BYTES, max_markers=MAX_GUARD_INPUT_MARKERS)
    except InputLimitError as limit:
        threat = ScanLimitExceeded(limit.rule_id, limit.limit, limit.measured, limit.unit).threat()
        reason = build_block_reason("", [threat], "command omitted", "blocked")
        emit_deny_response(input_failure_reason(reason, limit.rule_id))
    except ValueError:
        emit_deny_response(input_failure_reason("Tool Guardian skipped: invalid hook input JSON.", "input_invalid"))
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        print(f"Tool Guardian failed to read input: {format_error(exc)}", file=sys.stderr)
        emit_deny_response(input_failure_reason("Tool Guardian skipped: unexpected exception.", "input_read_failed"))

    if not isinstance(payload, dict):
        emit_deny_response(input_failure_reason("Tool Guardian skipped: invalid hook input JSON.", "input_invalid"))

    tool_name = read_tool_name(payload, TOOL_PROVIDER)
    result = inspect_tool(payload, TOOL_PROVIDER)
    allowlist = parse_allowlist(os.environ.get("TOOL_GUARD_ALLOWLIST")) if result.complete else []
    if allowlist and allowlist_contains(tool_name, read_tool_input(payload, TOOL_PROVIDER), allowlist):
        # Allowlist skips have always audited as clean; audit failure still denies.
        result = InspectionResult(result.profile, result.route, result.profile_cause)
        event = "guard_skipped"
    else:
        event = "threats_detected" if result.findings else "guard_passed"
    enforcement = normal_enforcement(result, mode)
    excerpt = build_action_excerpt(result.findings) if result.complete else "command omitted"
    record_guard(event, mode, tool_name, result, enforcement, excerpt)
    if enforcement == "deny":
        emit_deny_response(attributed_reason(tool_name, result, excerpt, enforcement))
    if result.findings:
        emit_allow_response(attributed_reason(tool_name, result, excerpt, enforcement))
    emit_allow_response()



if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - intentional fail-closed safety net
        print(f"Tool Guardian failed unexpectedly: {format_error(exc)}", file=sys.stderr)
        emit_deny_response(input_failure_reason("Tool Guardian blocked execution due to an internal error.", "internal_error"))
