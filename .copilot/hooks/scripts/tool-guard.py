#!/usr/bin/env python3
# Generated from hooks/families/tool_guard.py by scripts/generate-hooks.py. Do not edit.

from __future__ import annotations

# BEGIN PROVIDER ADAPTER
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_log_event  # noqa: E402
from helpers.common import emit_json, read_json_input  # noqa: E402


SCRIPT_NAME = Path(__file__).name
TOOL_NAME_KEYS = ("toolName", "tool_name")
TOOL_INPUT_KEYS = ("toolArgs", "toolInput", "tool_input")
TOOL_PROVIDER = "copilot"


def emit_skip_allow_response() -> None:
    emit_json(
        {
            "continue": True,
            "permissionDecision": "allow",
            "hookSpecificOutput": {"permissionDecision": "allow"},
        }
    )
    raise SystemExit(0)


def emit_allow_response(system_message: str | None = None) -> None:
    payload = {
        "continue": True,
        "permissionDecision": "allow",
        "hookSpecificOutput": {"permissionDecision": "allow"},
    }
    if system_message:
        payload["systemMessage"] = system_message
    emit_json(payload)
    raise SystemExit(0)


def emit_deny_response(reason: str) -> None:
    emit_json(
        {
            "continue": True,
            "permissionDecision": "deny",
            "hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": reason},
            "permissionDecisionReason": reason,
        }
    )
    raise SystemExit(0)
# END PROVIDER ADAPTER

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
    )
except Exception:
    emit_deny_response("Tool Guardian blocked execution due to an internal error.")


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



def _native_tool_shape(tool_name: str, value: object) -> NativeToolInput | None:
    if not isinstance(value, dict) or len(value) > MAX_STRUCTURED_NODES:
        return None
    shell_tools = {"codex": {"Bash", "exec_command", "functions.exec_command"}, "copilot": {"bash"}, "gemini": {"run_shell_command"}}
    if tool_name in shell_tools.get(TOOL_PROVIDER, set()):
        key = "cmd" if tool_name in {"exec_command", "functions.exec_command"} else "command"
        if _matches_native_schema(value, {key: str}):
            return NativeToolInput("shell", (), (value[key],))
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
            return native
        if isinstance(value, str):
            return (value,)
        if total_string_bytes > MAX_SCAN_TEXT:
            raise ScanLimitExceeded("structured_bytes", MAX_SCAN_TEXT, total_string_bytes, "bytes")
    elif key_bytes > MAX_SCAN_TEXT:
        raise ScanLimitExceeded("structured_bytes", MAX_SCAN_TEXT, key_bytes, "bytes")
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return tuple(strings) + tuple(keys) + (serialized,)


# BEGIN PROVIDER ADAPTER

def format_error(error: Exception) -> str:
    return type(error).__name__


def configure_log() -> None:
    global TIMESTAMP, LOG_FILE, LOCK_FILE
    TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    LOG_FILE = os.environ.get(
        "TOOL_GUARD_LOG_DIR",
        str(Path.home() / ".copilot" / "hooks" / "tool-guardian" / "guard.log"),
    )
    LOCK_FILE = f"{LOG_FILE}.lock"


def log_payload(event: str, mode: str, tool_name: str, threat_count: int = 0, threats: list[dict[str, str]] | None = None, excerpt: str | None = None) -> None:
    payload: dict[str, object] = {
        "timestamp": TIMESTAMP,
        "event": event,
        "mode": mode,
        "tool": sanitize_tool_name(tool_name),
    }
    if event == "threats_detected":
        payload["threat_count"] = threat_count
        payload["threats"] = threats or []
        payload["excerpt"] = excerpt or "command omitted"

    old_audit_log = os.environ.get("AUDIT_LOG")
    old_audit_lock = os.environ.get("AUDIT_LOCK")
    try:
        os.environ["AUDIT_LOG"] = LOG_FILE
        os.environ["AUDIT_LOCK"] = LOCK_FILE
        audit_log_event(SCRIPT_NAME, json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    finally:
        if old_audit_log is None:
            os.environ.pop("AUDIT_LOG", None)
        else:
            os.environ["AUDIT_LOG"] = old_audit_log
        if old_audit_lock is None:
            os.environ.pop("AUDIT_LOCK", None)
        else:
            os.environ["AUDIT_LOCK"] = old_audit_lock
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
        emit_deny_response("Tool Guardian skipped: invalid hook input JSON.")
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        print(f"Tool Guardian failed to read input: {format_error(exc)}", file=sys.stderr)
        emit_deny_response("Tool Guardian skipped: unexpected exception.")

    if not isinstance(payload, dict):
        emit_deny_response("Tool Guardian skipped: invalid hook input JSON.")

    tool_name = read_tool_name(payload)
    try:
        tool_scan_inputs = read_tool_scan_inputs(payload)
        threats = build_input_threats(tool_name, tool_scan_inputs)
    except ScanLimitExceeded as limit:
        threats = [limit.threat()]
    except UnicodeError:
        threats = [{"category": "inspection_failure", "severity": "critical", "rule_id": "inspection_failure", "cause": "tool input cannot be encoded as UTF-8 for inspection"}]
    if any(threat["category"] in {"input_limits", "inspection_failure"} for threat in threats):
        excerpt = "command omitted"
        log_payload("threats_detected", mode, tool_name, len(threats), log_threat_metadata(threats), excerpt)
        emit_deny_response(build_block_reason(tool_name, threats, excerpt, "blocked"))

    tool_input = read_tool_input(payload)
    allowlist = parse_allowlist(os.environ.get("TOOL_GUARD_ALLOWLIST"))

    if allowlist and allowlist_contains(tool_name, tool_input, allowlist):
        log_payload("guard_skipped", mode, tool_name)
        emit_allow_response()

    if not threats:
        log_payload("guard_passed", mode, tool_name)
        emit_allow_response()

    excerpt = build_action_excerpt(tool_input, threats)
    log_payload("threats_detected", mode, tool_name, len(threats), log_threat_metadata(threats), excerpt)
    if mode == "warn":
        emit_allow_response(build_block_reason(tool_name, threats, excerpt, "warning"))

    emit_deny_response(build_block_reason(tool_name, threats, excerpt, "blocked"))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - intentional fail-closed safety net
        print(f"Tool Guardian failed unexpectedly: {format_error(exc)}", file=sys.stderr)
        emit_deny_response("Tool Guardian blocked execution due to an internal error.")
