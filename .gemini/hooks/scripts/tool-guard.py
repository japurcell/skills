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


TOOL_NAME_KEYS = ("tool_name", "toolName")
TOOL_INPUT_KEYS = ("tool_input", "toolInput", "toolArgs")
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

REPORT_BUILD = "5bde73f7111a7db8"


def inspection_incomplete(threats):
    return any(threat["category"] in {"input_limits", "inspection_failure"} for threat in threats)


def guard_attribution(*, security, audit, enforcement, profile, route, cause):
    # This helper is available before optional policy imports and takes explicit
    # route/profile values so bootstrap and input failures retain attribution.
    return (f" security_outcome={security}; audit_outcome={audit}; enforcement={enforcement}; build={REPORT_BUILD}; "
            f"profile={profile}; route={route}; cause={cause}.")
TOOL_PROFILE = "unsupported"
TOOL_ROUTE = "strict_fallback"
PROFILE_CAUSE = "unsupported_tool_profile"
MAX_GUARD_LOG_BYTES = 16384

try:
    from helpers.tool_guard_policy import (
        MAX_SCAN_TEXT,
        MAX_NATIVE_DATA_BYTES,
        MAX_NATIVE_PATCH_BYTES,
        MAX_COMMAND_SEGMENTS,
        MAX_COMMAND_TOKENS,
        MAX_STRUCTURED_DEPTH,
        MAX_STRUCTURED_NODES,
        MAX_STRUCTURED_STRINGS,
        MAX_TOOL_NAME_LENGTH,
        MAX_EXCERPT_LENGTH,
        REDACTED,
        KNOWN_TOOL_FIELDS,
        ScanLimitExceeded,
        R,
        _is_word_char,
        _find_word,
        _simple_match,
        _bounded_normalized_text,
        _command_segments,
        _ScanText,
        _executable_basename,
        _matches_protected_remove_target,
        _match_recursive_rm_target,
        _match_rm_env,
        _match_rm_git,
        _match_git_push,
        _sql_code_without_comments_or_literals,
        _match_delete_from,
        _match_pipe_chain,
        _match_data_upload,
        PATTERNS,
        RULE_DETAILS,
        NativeToolInput,
        _matches_native_schema,
        _parse_native_patch,
        _native_operation_threats,
        InspectionFailure,
        _ShellWord,
        _ShellCommand,
        _InspectionBudget,
        _shell_representation,
        _GUARD_TARGETS,
        _literal_search,
        _python_preflight,
        _python_inspection,
        _strict_threats,
        _python_threats,
        _inline_operand,
        _shell_threats,
        sanitize_tool_name,
        build_threats,
        build_input_threats,
        sanitize_excerpt,
        safe_excerpt_context,
        safe_git_push_match,
        build_action_excerpt,
        log_threat_metadata,
        build_block_reason,
        _normalize_allowlist_value,
        _has_forbidden_allowlist_separator,
        parse_allowlist,
        allowlist_contains,
        report_text,
        report_json_bytes,
    )
except Exception:
    emit_deny_response("Tool Guardian blocked execution due to an internal error."
                       + guard_attribution(security="incomplete", audit="not_attempted", enforcement="deny",
                                           profile="unavailable", route="bootstrap", cause="policy_unavailable"))


def read_tool_name(payload: dict) -> str:
    for key in TOOL_NAME_KEYS:
        value = payload.get(key)
        if value is not None:
            return str(value)
    return ""



def _read_tool_input_value(payload: dict) -> object:
    for key in TOOL_INPUT_KEYS:
        if key not in payload:
            continue
        value = payload.get(key)
        if value is None:
            return ""
        return value
    return ""



def read_tool_input(payload: dict) -> str:
    value = _read_tool_input_value(payload)
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))



def _native_shell_shape(tool_name: str, value: dict) -> NativeToolInput | None:
    """Only proven inert fields leave inspection; execution context stays strict."""
    metadata: list[str] = []
    numeric: tuple[str, ...] = ()
    if TOOL_PROVIDER == "codex" and tool_name in {"exec_command", "functions.exec_command"}:
        key = "cmd"
        optional = {"max_output_tokens": int, "yield_time_ms": int, "workdir": str,
                    "shell": str, "login": bool, "tty": bool, "justification": str,
                    "sandbox_permissions": str, "prefix_rule": list}
        numeric = ("max_output_tokens", "yield_time_ms")
    elif TOOL_PROVIDER == "codex" and tool_name == "Bash":
        key, optional = "command", {}
    elif TOOL_PROVIDER == "copilot" and tool_name == "bash":
        key = "command"
        optional = {"description": str, "initial_wait": int, "mode": str, "detach": bool}
        numeric = ("initial_wait",)
    elif TOOL_PROVIDER == "gemini" and tool_name == "run_shell_command":
        key = "command"
        optional = {"description": str, "dir_path": str, "is_background": bool,
                    "delay_ms": int, "additional_permissions": dict}
        numeric = ("delay_ms",)
    else:
        return None
    if not _matches_native_schema(value, {key: str}, optional):
        return None
    # Booleans are not integers here. Finite bounded counters cannot carry code.
    if any(not 0 <= value[field] <= 2147483647 for field in numeric if field in value):
        return None
    if "shell" in value and value["shell"] not in {
        "bash", "sh", "zsh", "/bin/bash", "/bin/sh", "/bin/zsh",
        "/usr/bin/bash", "/usr/bin/sh", "/usr/bin/zsh",
    }:
        return None
    if "sandbox_permissions" in value and value["sandbox_permissions"] not in {
        "use_default", "require_escalated",
    }:
        return None
    if "mode" in value and value["mode"] not in {"sync", "async"}:
        return None
    for field in ("workdir", "dir_path"):
        if field in value:
            metadata.append(value[field])
    if "prefix_rule" in value:
        prefix = value["prefix_rule"]
        if len(prefix) > MAX_STRUCTURED_NODES or any(type(item) is not str for item in prefix):
            return None
        metadata.extend(prefix)
    if "additional_permissions" in value:
        permissions = value["additional_permissions"]
        if not _matches_native_schema(permissions, {}, {"network": bool, "fileSystem": dict}):
            return None
        if "fileSystem" in permissions:
            filesystem = permissions["fileSystem"]
            if not _matches_native_schema(filesystem, {}, {"read": list, "write": list}):
                return None
            for paths in filesystem.values():
                if len(paths) > MAX_STRUCTURED_NODES or any(type(path) is not str for path in paths):
                    return None
                metadata.extend(paths)
    return NativeToolInput("shell", tuple(metadata), (value[key],))



def _native_tool_shape(tool_name: str, value: object) -> NativeToolInput | None:
    if not isinstance(value, dict) or len(value) > MAX_STRUCTURED_NODES:
        return None
    shell = _native_shell_shape(tool_name, value)
    if shell is not None:
        return shell
    if TOOL_PROVIDER == "codex" and tool_name == "apply_patch" and _matches_native_schema(value, {"command": str}):
        return NativeToolInput("patch", (), (value["command"],))
    if TOOL_PROVIDER == "gemini":
        if tool_name == "write_file" and _matches_native_schema(value, {"file_path": str, "content": str}):
            return NativeToolInput("write", (value["file_path"],), (value["content"],))
        if tool_name == "replace" and _matches_native_schema(value, {"file_path": str, "instruction": str, "old_string": str, "new_string": str}, {"allow_multiple": bool}):
            return NativeToolInput("edit", (value["file_path"], value["instruction"]), (value["old_string"], value["new_string"]))
        if tool_name == "grep_search" and _matches_native_schema(value, {"pattern": str}, {"path": str, "include": str}):
            return NativeToolInput("search", tuple(value.get(key, "") for key in ("path", "include")), (value["pattern"],))
    if TOOL_PROVIDER == "copilot":
        if tool_name == "create" and _matches_native_schema(value, {"path": str, "file_text": str}):
            return NativeToolInput("write", (value["path"],), (value["file_text"],))
        if tool_name == "edit" and _matches_native_schema(value, {"path": str, "old_str": str, "new_str": str}):
            return NativeToolInput("edit", (value["path"],), (value["old_str"], value["new_str"]))
        if tool_name in {"grep", "rg"}:
            # Observed CLI arguments, not a guessed complete provider schema.
            pattern_keys = value.keys() & {"pattern", "query"}
            if len(pattern_keys) != 1 or (tool_name == "rg" and "query" in value):
                return None
            pattern_key = next(iter(pattern_keys))
            fields = {"path": str, "paths": (str, list), "output_mode": str, "head_limit": int,
                      "n": (bool, int), "C": int, "case_sensitive": bool} if tool_name == "grep" else {
                          "paths": (str, list), "output_mode": str, "head_limit": int, "glob": str,
                          "-n": bool, "-i": bool, "-A": int, "-C": int, "n": int}
            if not value.keys() <= fields.keys() | {pattern_key} or type(value[pattern_key]) is not str:
                return None
            if "path" in value and "paths" in value:
                return None
            for key, child in value.items():
                if key == pattern_key:
                    continue
                allowed_types = fields[key] if isinstance(fields[key], tuple) else (fields[key],)
                if type(child) not in allowed_types or (type(child) is list and (
                    len(child) > MAX_STRUCTURED_NODES or any(type(item) is not str for item in child)
                )):
                    return None
            return NativeToolInput("search", (), tuple(child for child in value.values() if isinstance(child, str)))
    return None



def read_tool_scan_inputs(payload: dict) -> tuple[str, ...] | NativeToolInput:
    global TOOL_PROFILE, TOOL_ROUTE, PROFILE_CAUSE
    value = _read_tool_input_value(payload)
    tool_name = read_tool_name(payload)
    if isinstance(value, str):
        # Copilot's native patch transport is raw text in the primary fields.
        # Alternate input/name fields and serialized objects remain strict.
        if TOOL_PROVIDER == "copilot" and payload.get("toolName") == "apply_patch" and type(payload.get("toolArgs")) is str:
            native = NativeToolInput("patch", (), (value,))
        else:
            return (value,)
    else:
        native = _native_tool_shape(tool_name, value)
    if native:
        TOOL_PROFILE = native.kind + "_v1"
        PROFILE_CAUSE = "recognized_profile"
    elif tool_name.casefold() in KNOWN_TOOL_FIELDS:
        PROFILE_CAUSE = "native_profile_rejected"
    byte_limit = MAX_SCAN_TEXT
    if native and native.kind == "patch":
        byte_limit = MAX_NATIVE_PATCH_BYTES
    elif native and native.kind != "shell":
        byte_limit = MAX_NATIVE_DATA_BYTES
    known_fields = KNOWN_TOOL_FIELDS.get(tool_name.casefold(), frozenset())
    stack = [iter(((value, 0, "tool input"),))]
    strings: list[str] = []
    node_count = 0
    total_string_bytes = 0
    keys: list[str] = []

    def dictionary_children(mapping, depth):
        for key, child in mapping.items():
            keys.append(key)
            field = f"{tool_name.casefold()}.{key}" if depth == 0 and key in known_fields and isinstance(child, str) else "tool input"
            yield child, depth + 1, field

    def sequence_children(sequence, depth):
        for child in sequence:
            yield child, depth + 1, "tool input"

    while stack:
        try:
            current, depth, field = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
        node_count += 1
        if node_count > MAX_STRUCTURED_NODES:
            raise ScanLimitExceeded("structured_nodes", MAX_STRUCTURED_NODES, node_count, "nodes")
        if depth > MAX_STRUCTURED_DEPTH:
            raise ScanLimitExceeded("structured_depth", MAX_STRUCTURED_DEPTH, depth, "levels")
        if isinstance(current, str):
            strings.append(current)
            current_bytes = len(current.encode("utf-8"))
            total_string_bytes += current_bytes
            if len(strings) > MAX_STRUCTURED_STRINGS:
                raise ScanLimitExceeded("structured_strings", MAX_STRUCTURED_STRINGS, len(strings), "strings")
            if total_string_bytes > byte_limit:
                source = field if current_bytes > byte_limit else "tool input"
                raise ScanLimitExceeded("structured_bytes", byte_limit, total_string_bytes, "bytes", source)
        elif isinstance(current, dict):
            stack.append(dictionary_children(current, depth))
        elif isinstance(current, (list, tuple)):
            stack.append(sequence_children(current, depth))

    key_bytes = sum(len(key.encode("utf-8")) for key in keys)
    if native:
        aggregate_bytes = total_string_bytes + key_bytes
        if aggregate_bytes > byte_limit:
            raise ScanLimitExceeded("structured_bytes", byte_limit, aggregate_bytes, "bytes")
        if native.kind == "patch":
            native = _parse_native_patch(native.data[0])
        if native is not None:
            TOOL_PROFILE, TOOL_ROUTE, PROFILE_CAUSE = native.kind + "_v1", "native", "recognized_profile"
            return native
        TOOL_PROFILE, PROFILE_CAUSE = "unsupported", "native_profile_rejected"
        if isinstance(value, str):
            return (value,)
        if total_string_bytes > MAX_SCAN_TEXT:
            raise ScanLimitExceeded("structured_bytes", MAX_SCAN_TEXT, total_string_bytes, "bytes")
    elif key_bytes > MAX_SCAN_TEXT:
        raise ScanLimitExceeded("structured_bytes", MAX_SCAN_TEXT, key_bytes, "bytes")
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return tuple(strings) + tuple(keys) + (serialized,)


def guard_report(payload):
    """Retain bounded owned metadata, then serialize in the provider adapter."""
    security = "findings" if payload.get("threat_count") else "clean"
    threats = payload.get("threats", [])
    incomplete = inspection_incomplete(threats)
    if incomplete:
        security = "incomplete"
    payload.update(build=REPORT_BUILD, provider=TOOL_PROVIDER, profile=TOOL_PROFILE,
                   route=TOOL_ROUTE, profile_cause=PROFILE_CAUSE,
                   cause=threats[0]["rule_id"] if threats else payload["event"],
                   security_outcome=security, audit_outcome="written",
                   inspection_outcome="incomplete" if incomplete else "complete",
                   enforcement="deny" if incomplete or (security == "findings" and payload["mode"] == "block") else "allow",
                   omittedThreats=0)
    payload["tool"] = report_text(payload["tool"])
    if "excerpt" in payload:
        payload["excerpt"] = report_text(payload["excerpt"])
    while report_json_bytes(payload) > MAX_GUARD_LOG_BYTES - 256 and threats:
        threats.pop()
        payload["omittedThreats"] += 1
    return payload


def record_guard(event, mode, tool_name, threats=None, excerpt="command omitted"):
    threats = threats or []
    try:
        log_payload(event, mode, tool_name, len(threats), log_threat_metadata(threats), excerpt)
    except Exception:
        # A failed audit cannot erase a security finding or allow a clean call.
        incomplete = inspection_incomplete(threats)
        warning = mode == "warn" and threats and not incomplete
        outcome = "warning" if warning else "blocked"
        reason = build_block_reason(tool_name, threats, excerpt, outcome) if threats else "Tool Guardian blocked: audit unavailable."
        reason += guard_attribution(security="incomplete" if incomplete else "findings" if threats else "clean",
                                    audit="failed", enforcement="allow" if warning else "deny",
                                    profile=TOOL_PROFILE, route=TOOL_ROUTE, cause="audit_unavailable")
        if warning:
            emit_allow_response(reason)
        emit_deny_response(reason)


def attributed_reason(tool_name, threats, excerpt, outcome):
    incomplete = inspection_incomplete(threats)
    cause = threats[0]["rule_id"] if threats else PROFILE_CAUSE
    return (build_block_reason(tool_name, threats, excerpt, outcome)
            + guard_attribution(security="incomplete" if incomplete else "findings", audit="written",
                                enforcement="allow" if outcome == "warning" else "deny",
                                profile=TOOL_PROFILE, route=TOOL_ROUTE, cause=cause))


def input_failure_reason(reason, cause):
    return reason + guard_attribution(security="incomplete", audit="not_attempted", enforcement="deny",
                                     profile="unsupported", route="input_validation", cause=cause)


def guard_log_payload(event, mode, tool_name, timestamp, threat_count=0, threats=None, excerpt=None):
    payload = {"timestamp": timestamp, "event": event, "mode": mode,
               "tool": sanitize_tool_name(tool_name)}
    if event == "threats_detected":
        payload["threat_count"] = threat_count
        payload["threats"] = threats or []
        payload["excerpt"] = excerpt or "command omitted"
    return guard_report(payload)


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


def append_log(
    log_file: str,
    event: str,
    mode: str,
    tool_name: str,
    timestamp: str,
    threat_count: int = 0,
    threats: list[dict[str, str]] | None = None,
    excerpt: str | None = None,
) -> None:
    parent = os.path.dirname(log_file)
    if parent:
        os.makedirs(parent, mode=0o700, exist_ok=True)

    payload = guard_log_payload(event, mode, tool_name, timestamp, threat_count, threats, excerpt)

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


def log_payload(event: str, mode: str, tool_name: str, threat_count: int = 0, threats: list[dict[str, str]] | None = None, excerpt: str | None = None) -> None:
    append_log(LOG_FILE, event, mode, tool_name, TIMESTAMP, threat_count, threats, excerpt)
# END PROVIDER ADAPTER


def main() -> int:
    if os.environ.get("SKIP_TOOL_GUARD") == "true":
        emit_skip_allow_response()

    configure_log()
    mode = os.environ.get("GUARD_MODE", "block")
    if mode not in {"warn", "block"}:
        mode = "block"

    try:
        payload = read_json_input()
    except ValueError:
        emit_deny_response(input_failure_reason("Tool Guardian skipped: invalid hook input JSON.", "input_invalid"))
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        print(f"Tool Guardian failed to read input: {format_error(exc)}", file=sys.stderr)
        emit_deny_response(input_failure_reason("Tool Guardian skipped: unexpected exception.", "input_read_failed"))

    if not isinstance(payload, dict):
        emit_deny_response(input_failure_reason("Tool Guardian skipped: invalid hook input JSON.", "input_invalid"))

    tool_name = read_tool_name(payload)
    try:
        tool_scan_inputs = read_tool_scan_inputs(payload)
        threats = build_input_threats(tool_name, tool_scan_inputs)
    except ScanLimitExceeded as limit:
        threats = [limit.threat()]
    except UnicodeError:
        threats = [{"category": "inspection_failure", "severity": "critical", "rule_id": "inspection_failure", "cause": "tool input cannot be encoded as UTF-8 for inspection"}]
    if inspection_incomplete(threats):
        excerpt = "command omitted"
        record_guard("threats_detected", mode, tool_name, threats, excerpt)
        emit_deny_response(attributed_reason(tool_name, threats, excerpt, "blocked"))

    tool_input = read_tool_input(payload)
    allowlist = parse_allowlist(os.environ.get("TOOL_GUARD_ALLOWLIST"))

    if allowlist and allowlist_contains(tool_name, tool_input, allowlist):
        record_guard("guard_skipped", mode, tool_name)
        emit_allow_response()

    if not threats:
        record_guard("guard_passed", mode, tool_name)
        emit_allow_response()

    excerpt = build_action_excerpt(tool_input, threats)
    record_guard("threats_detected", mode, tool_name, threats, excerpt)
    if mode == "warn":
        emit_allow_response(attributed_reason(tool_name, threats, excerpt, "warning"))

    emit_deny_response(attributed_reason(tool_name, threats, excerpt, "blocked"))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - intentional fail-closed safety net
        print(f"Tool Guardian failed unexpectedly: {format_error(exc)}", file=sys.stderr)
        emit_deny_response(input_failure_reason("Tool Guardian blocked execution due to an internal error.", "internal_error"))
