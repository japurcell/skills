#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from helpers.audit import audit_log_event
from helpers.common import emit_json, read_json_input, sanitize_log_field


SCRIPT_NAME = Path(__file__).name


def R(*codes: int) -> str:
    return "".join(chr(code) for code in codes)


PATTERNS = [
    ("destructive_file_ops", "critical", R(114, 109, 32, 45, 114, 102, 32, 47), "Narrow the deletion scope."),
    ("destructive_file_ops", "critical", R(114, 109, 32, 45, 114, 102, 32, 126), "Narrow the deletion scope."),
    ("destructive_file_ops", "critical", R(114, 109, 32, 45, 114, 102, 32, 92, 46), "Narrow the deletion scope."),
    ("destructive_file_ops", "critical", R(114, 109, 32, 45, 114, 102, 32, 92, 46, 92, 46), "Avoid recursive parent removal."),
    ("destructive_file_ops", "critical", R(92, 98, 40, 114, 109, 124, 100, 101, 108, 124, 117, 110, 108, 105, 110, 107, 41, 92, 98, 46, 42, 92, 46, 101, 110, 118), "Move sensitive files aside before deleting."),
    ("destructive_file_ops", "critical", R(92, 98, 40, 114, 109, 124, 100, 101, 108, 124, 117, 110, 108, 105, 110, 107, 41, 92, 98, 46, 42, 92, 46, 103, 105, 116, 40, 91, 94, 65, 45, 90, 97, 45, 122, 48, 45, 57, 95, 93, 124, 36, 41), "Avoid deleting repository metadata."),
    ("destructive_git_ops", "critical", R(103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 45, 102, 111, 114, 99, 101, 46, 42, 40, 109, 97, 105, 110, 124, 109, 97, 115, 116, 101, 114, 41), "Use a safer push strategy."),
    ("destructive_git_ops", "critical", R(103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 102, 46, 42, 40, 109, 97, 105, 110, 124, 109, 97, 115, 116, 101, 114, 41), "Use a safer push strategy."),
    ("destructive_git_ops", "high", R(103, 105, 116, 32, 114, 101, 115, 101, 116, 32, 45, 45, 104, 97, 114, 100), "Prefer a softer reset path."),
    ("destructive_git_ops", "high", R(103, 105, 116, 32, 99, 108, 101, 97, 110, 32, 45, 102, 100), "Preview deletions first."),
    ("database_destruction", "critical", R(68, 82, 79, 80, 32, 84, 65, 66, 76, 69), "Use a schema-preserving change path."),
    ("database_destruction", "critical", R(68, 82, 79, 80, 32, 68, 65, 84, 65, 66, 65, 83, 69), "Back up before removing."),
    ("database_destruction", "critical", R(84, 82, 85, 78, 67, 65, 84, 69), "Use a schema-preserving change path."),
    ("database_destruction", "high", R(68, 69, 76, 69, 84, 69, 32, 70, 82, 79, 77, 32, 91, 65, 45, 90, 97, 45, 122, 95, 93, 43, 32, 42, 59), "Add a filter clause."),
    ("permission_abuse", "high", R(99, 104, 109, 111, 100, 32, 45, 82, 32, 55, 55, 55), "Use narrower permissions."),
    ("permission_abuse", "high", R(99, 104, 109, 111, 100, 32, 55, 55, 55), "Use narrower permissions."),
    ("network_exfiltration", "critical", R(99, 117, 114, 108, 46, 42, 92, 124, 46, 42, 98, 97, 115, 104), "Review downloads before execution."),
    ("network_exfiltration", "critical", R(119, 103, 101, 116, 46, 42, 92, 124, 46, 42, 115, 104), "Review downloads before execution."),
    ("network_exfiltration", "high", R(99, 117, 114, 108, 46, 42, 45, 45, 100, 97, 116, 97, 46, 42, 64), "Review outbound data before sending."),
    ("system_danger", "high", R(115, 117, 100, 111, 32), "Use least privilege."),
    ("system_danger", "high", R(110, 112, 109, 32, 112, 117, 98, 108, 105, 115, 104), "Dry-run the publication step."),
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
    threats: list[dict[str, str]] = []
    for category, severity, regex, suggestion in PATTERNS:
        match = re.search(regex, tool_text, flags=re.IGNORECASE)
        if match:
            threats.append(
                {
                    "category": category,
                    "severity": severity,
                    "match": match.group(0),
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
        emit_allow_response("Tool Guardian skipped: invalid hook input JSON.")
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        print(f"Tool Guardian failed to read input: {sanitize_log_field(exc)}", file=sys.stderr)
        emit_allow_response("Tool Guardian skipped: unexpected exception.")

    if not isinstance(payload, dict):
        emit_allow_response("Tool Guardian skipped: invalid hook input JSON.")

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
        emit_allow_response()

    emit_deny_response(build_block_reason(tool_name, threats))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        print(f"Tool Guardian failed unexpectedly: {sanitize_log_field(exc)}", file=sys.stderr)
        emit_allow_response("Tool Guardian skipped: unexpected exception.")
