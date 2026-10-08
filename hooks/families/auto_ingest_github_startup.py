#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import best_effort_audit_event
from helpers.auto_ingest import (
    build_context,
    ingest_skill_available,
    manifest_path,
    scan_and_reconcile,
    source_root,
    summary_root,
)
from helpers.common import emit_json, first_present, read_json_input, sanitize_log_field, stringify_value, repository_root_from_payload


SCRIPT_NAME = Path(__file__).name


def build_output(message: str, event_name: str) -> dict:
    payload = {
        "additionalContext": message,
    }

    if event_name == "SessionStart":
        payload["hookSpecificOutput"] = {
            "hookEventName": event_name,
            "additionalContext": message,
        }

    return payload


def log_event(message: str) -> None:
    best_effort_audit_event(SCRIPT_NAME, message)


def fail_safe(reason: str, event_name: str = "") -> None:
    safe_reason = sanitize_log_field(reason).strip() or "Hook failed"
    print(f"{SCRIPT_NAME}: {safe_reason}", file=sys.stderr)
    log_event(f"Error: {safe_reason}")
    if event_name in {"", "SessionStart"}:
        emit_json({"type": "progress", "message": "auto-ingest-source: incomplete"})
    emit_json(build_output(f"Auto-ingest source scan failed.\n\nReason: {safe_reason}", event_name))



def main() -> int:
    try:
        payload = read_json_input()
        if not isinstance(payload, dict):
            fail_safe("Invalid hook input: expected a JSON object")
            return 0

        event_name = stringify_value(
            first_present(payload, "hook_event_name", "hookEventName", "sourceEventName", "source_event_name")
        )
        if event_name and event_name != "SessionStart":
            emit_json({})
            return 0

        root = repository_root_from_payload(payload, "COPILOT_AUTO_INGEST_REPO_ROOT")
        sources_dir = source_root(root)
        summaries_dir = summary_root(root)
        manifest_file = manifest_path(summaries_dir)

        current_sources, report_entries = scan_and_reconcile(sources_dir, summaries_dir, manifest_file)

        message = build_context(report_entries, manifest_file, ingest_skill_available(root))
        session_id = sanitize_log_field(stringify_value(first_present(payload, "sessionId", "session_id")))

        if not message.strip():
            if not current_sources:
                log_event(
                    f"Message: auto-ingest scan complete, Event: {event_name or 'SessionStart'}, "
                    f"Session: {session_id}, Findings: 0, no context injected (no sources found)"
                )
            else:
                log_event(
                    f"Message: auto-ingest scan complete, Event: {event_name or 'SessionStart'}, "
                    f"Session: {session_id}, Findings: 0, no context injected (all summaries up to date)"
                )
            emit_json({"type": "progress", "message": "auto-ingest-source: pass; 0 pending sources"})
            emit_json({})
            return 0

        log_event(
            f"Message: auto-ingest scan complete, Event: {event_name or 'SessionStart'}, "
            f"Session: {session_id}, Findings: {len(report_entries)}, context injected"
        )
        for entry in report_entries:
            state = sanitize_log_field(str(entry.get("state") or ""))
            reason = sanitize_log_field(str(entry.get("reason") or ""))
            source_path = sanitize_log_field(str(entry.get("source_path") or ""))
            log_event(f"Finding: state={state}, reason={reason}, path={source_path}, Session: {session_id}")

        count = len(report_entries)
        emit_json({"type": "progress", "message": f"auto-ingest-source: changed; {count} pending {'source' if count == 1 else 'sources'}"})
        emit_json(build_output(message, event_name))
        return 0
    except ValueError as exc:
        fail_safe(str(exc), "")
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        fail_safe(f"Unexpected exception: {exc}", "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
