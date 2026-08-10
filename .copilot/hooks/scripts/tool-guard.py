#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_log_event  # noqa: E402
from helpers.common import emit_json, read_json_input, sanitize_log_field  # noqa: E402


SCRIPT_NAME = Path(__file__).name


def R(*codes: int) -> str:
    return "".join(chr(code) for code in codes)


def _is_word_char(char: str) -> bool:
    return char.isalnum() or char == "_"


def _find_word(lower_text: str, word: str, start: int = 0) -> int:
    index = lower_text.find(word, start)
    while index != -1:
        before = lower_text[index - 1] if index > 0 else ""
        after_index = index + len(word)
        after = lower_text[after_index] if after_index < len(lower_text) else ""
        if not _is_word_char(before) and not _is_word_char(after):
            return index
        index = lower_text.find(word, index + 1)
    return -1


def _simple_match(*codes: int):
    needle = R(*codes)

    def matcher(text: str, lower_text: str) -> str | None:
        index = lower_text.find(needle)
        if index == -1:
            return None
        return text[index : index + len(needle)]

    return matcher


def _match_rm_env(text: str, lower_text: str) -> str | None:
    commands = (R(114, 109), R(100, 101, 108), R(117, 110, 108, 105, 110, 107))
    suffix = R(46, 101, 110, 118)
    for command in commands:
        index = _find_word(lower_text, command)
        if index == -1:
            continue
        end = lower_text.find(suffix, index + len(command))
        if end != -1:
            return text[index : end + len(suffix)]
    return None


def _match_rm_git(text: str, lower_text: str) -> str | None:
    commands = (R(114, 109), R(100, 101, 108), R(117, 110, 108, 105, 110, 107))
    suffix = R(46, 103, 105, 116)
    for command in commands:
        index = _find_word(lower_text, command)
        if index == -1:
            continue
        end = lower_text.find(suffix, index + len(command))
        if end == -1:
            continue
        after = end + len(suffix)
        if after == len(lower_text) or not _is_word_char(lower_text[after]):
            return text[index:after]
    return None


def _match_git_push(*prefix_codes: int):
    prefix = R(*prefix_codes)
    main = R(109, 97, 105, 110)
    master = R(109, 97, 115, 116, 101, 114)

    def matcher(text: str, lower_text: str) -> str | None:
        index = lower_text.find(prefix)
        if index == -1:
            return None
        tail = lower_text[index + len(prefix) :]
        branch_index = tail.find(main)
        branch_len = len(main)
        if branch_index == -1:
            branch_index = tail.find(master)
            branch_len = len(master)
        if branch_index == -1:
            return None
        return text[index : index + len(prefix) + branch_index + branch_len]

    return matcher


def _match_delete_from(text: str, lower_text: str) -> str | None:
    prefix = R(100, 101, 108, 101, 116, 101, 32, 102, 114, 111, 109, 32)
    index = lower_text.find(prefix)
    if index == -1:
        return None
    semicolon = lower_text.find(";", index + len(prefix))
    if semicolon == -1:
        return None
    if R(119, 104, 101, 114, 101) in lower_text[index:semicolon]:
        return None
    return text[index : semicolon + 1]


def _match_pipe_chain(*codes: int):
    first, second = (R(*codes[0]), R(*codes[1]))

    def matcher(text: str, lower_text: str) -> str | None:
        index = lower_text.find(first)
        if index == -1:
            return None
        pipe = lower_text.find(R(124), index + len(first))
        if pipe == -1:
            return None
        tail = lower_text.find(second, pipe + 1)
        if tail == -1:
            return None
        return text[index : tail + len(second)]

    return matcher


def _match_data_upload(text: str, lower_text: str) -> str | None:
    curl = R(99, 117, 114, 108)
    data = R(45, 45, 100, 97, 116, 97)
    at_sign = R(64)
    index = lower_text.find(curl)
    if index == -1:
        return None
    marker = lower_text.find(data, index + len(curl))
    if marker == -1:
        return None
    end = lower_text.find(at_sign, marker + len(data))
    if end == -1:
        return None
    return text[index : end + 1]


PATTERNS = [
    ("destructive_file_ops", "critical", _simple_match(114, 109, 32, 45, 114, 102, 32, 47), "Use targeted removals."),
    ("destructive_file_ops", "critical", _simple_match(114, 109, 32, 45, 114, 102, 32, 126), "Use targeted removals."),
    ("destructive_file_ops", "critical", _simple_match(114, 109, 32, 45, 114, 102, 32, 46), "Use targeted removals."),
    ("destructive_file_ops", "critical", _simple_match(114, 109, 32, 45, 114, 102, 32, 46, 46), "Avoid recursive parent removal."),
    ("destructive_file_ops", "critical", _match_rm_env, "Back up sensitive files first."),
    ("destructive_file_ops", "critical", _match_rm_git, "Never delete repository metadata."),
    ("destructive_git_ops", "critical", _match_git_push(103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 45, 102, 111, 114, 99, 101), "Use a safer push strategy."),
    ("destructive_git_ops", "critical", _match_git_push(103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 102), "Use a safer push strategy."),
    ("destructive_git_ops", "high", _simple_match(103, 105, 116, 32, 114, 101, 115, 101, 116, 32, 45, 45, 104, 97, 114, 100), "Prefer a softer reset path."),
    ("destructive_git_ops", "high", _simple_match(103, 105, 116, 32, 99, 108, 101, 97, 110, 32, 45, 102, 100), "Preview deletions first."),
    ("database_destruction", "critical", _simple_match(100, 114, 111, 112, 32, 116, 97, 98, 108, 101), "Preserve the schema instead."),
    ("database_destruction", "critical", _simple_match(100, 114, 111, 112, 32, 100, 97, 116, 97, 98, 97, 115, 101), "Back up before removing."),
    ("database_destruction", "critical", _simple_match(116, 114, 117, 110, 99, 97, 116, 101), "Preserve the schema instead."),
    ("database_destruction", "high", _match_delete_from, "Add a filter clause."),
    ("permission_abuse", "high", _simple_match(99, 104, 109, 111, 100, 32, 45, 114, 32, 55, 55, 55), "Use narrower permissions."),
    ("permission_abuse", "high", _simple_match(99, 104, 109, 111, 100, 32, 55, 55, 55), "Use narrower permissions."),
    ("network_exfiltration", "critical", _match_pipe_chain((99, 117, 114, 108), (98, 97, 115, 104)), "Review downloads before execution."),
    ("network_exfiltration", "critical", _match_pipe_chain((119, 103, 101, 116), (115, 104)), "Review downloads before execution."),
    ("network_exfiltration", "high", _match_data_upload, "Review outbound data before sending."),
    ("system_danger", "high", _simple_match(115, 117, 100, 111, 32), "Use least privilege."),
    ("system_danger", "high", _simple_match(110, 112, 109, 32, 112, 117, 98, 108, 105, 115, 104), "Dry-run publication first."),
]


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


def parse_allowlist_csv(raw_allowlist: str | None) -> list[str]:
    if not raw_allowlist:
        return []
    return [entry.strip() for entry in raw_allowlist.split(",") if entry.strip()]


def allowlist_contains(text: str, entries: list[str]) -> bool:
    return any(entry in text for entry in entries)


def read_tool_name(payload: dict) -> str:
    for key in ("toolName", "tool_name"):
        value = payload.get(key)
        if value is not None:
            return str(value)
    return ""


def read_tool_input(payload: dict) -> str:
    for key in ("toolArgs", "toolInput", "tool_input"):
        if key not in payload:
            continue
        value = payload.get(key)
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return ""


def build_threats(tool_text: str) -> list[dict[str, str]]:
    lower_tool_text = tool_text.lower()
    threats: list[dict[str, str]] = []
    for category, severity, matcher, suggestion in PATTERNS:
        match = matcher(tool_text, lower_tool_text)
        if match:
            threats.append(
                {
                    "category": category,
                    "severity": severity,
                    "match": match,
                    "suggestion": suggestion,
                }
            )
    return threats


def build_block_reason(tool_name: str, threats: list[dict[str, str]]) -> str:
    summary = [f"{threat['category']}/{threat['severity']} matched '{threat['match']}'" for threat in threats[:3]]
    joined = "; ".join(summary)
    return (
        f"Tool Guardian blocked {tool_name or 'tool invocation'}. {joined}. "
        "Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
    )


def log_payload(event: str, mode: str, tool_name: str, threat_count: int = 0, threats: list[dict[str, str]] | None = None) -> None:
    payload: dict[str, object] = {
        "timestamp": TIMESTAMP,
        "event": event,
        "mode": mode,
        "tool": tool_name,
    }
    if event == "threats_detected":
        payload["threat_count"] = threat_count
        payload["threats"] = threats or []

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


def main() -> int:
    global TIMESTAMP, LOG_FILE, LOCK_FILE

    if os.environ.get("SKIP_TOOL_GUARD") == "true":
        emit_skip_allow_response()

    TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    LOG_FILE = os.environ.get(
        "TOOL_GUARD_LOG_DIR",
        str(Path.home() / ".copilot" / "hooks" / "tool-guardian" / "guard.log"),
    )
    LOCK_FILE = f"{LOG_FILE}.lock"
    mode = os.environ.get("GUARD_MODE", "block")
    if mode not in {"warn", "block"}:
        mode = "block"

    try:
        payload = read_json_input()
    except ValueError:
        emit_deny_response("Tool Guardian skipped: invalid hook input JSON.")
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        print(f"Tool Guardian failed to read input: {sanitize_log_field(exc)}", file=sys.stderr)
        emit_deny_response("Tool Guardian skipped: unexpected exception.")

    if not isinstance(payload, dict):
        emit_deny_response("Tool Guardian skipped: invalid hook input JSON.")

    tool_name = read_tool_name(payload)
    tool_text = f"{tool_name} {read_tool_input(payload)}"
    allowlist = parse_allowlist_csv(os.environ.get("TOOL_GUARD_ALLOWLIST"))

    if allowlist and allowlist_contains(tool_text, allowlist):
        log_payload("guard_skipped", mode, tool_name)
        emit_allow_response()

    threats = build_threats(tool_text)
    if not threats:
        log_payload("guard_passed", mode, tool_name)
        emit_allow_response()

    log_payload("threats_detected", mode, tool_name, len(threats), threats)
    if mode == "warn":
        emit_allow_response(f"⚠️ Tool Guardian warning: {build_block_reason(tool_name, threats)}")

    emit_deny_response(build_block_reason(tool_name, threats))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        print(f"Tool Guardian failed unexpectedly: {sanitize_log_field(exc)}", file=sys.stderr)
        emit_deny_response("Tool Guardian blocked execution due to an internal error.")
