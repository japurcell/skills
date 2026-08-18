#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_log_event  # noqa: E402
from helpers.common import emit_json, read_json_input, sanitize_log_field  # noqa: E402
from helpers.source_ingest import (  # noqa: E402
    ManifestLock,
    blocking_entries,
    build_block_reason,
    build_context,
    ingest_skill_available,
    load_manifest,
    manifest_path_for_payload,
    reconcile_manifest,
    repo_root_for_payload,
    save_manifest,
    scan_sources,
    source_root_for_payload,
    summary_root_for_payload,
)


SCRIPT_NAME = Path(__file__).name


def log_event(message: str) -> None:
    try:
        audit_log_event(SCRIPT_NAME, message)
    except Exception:
        pass


def main() -> int:
    try:
        payload = read_json_input()
        if not isinstance(payload, dict):
            emit_json({})
            return 0

        if payload.get("stop_hook_active") or payload.get("stopHookActive"):
            emit_json({})
            return 0

        event_name = str(payload.get("hook_event_name") or "")
        if event_name and event_name not in {"BeforeAgent", "AfterAgent"}:
            emit_json({})
            return 0
        if not event_name:
            event_name = "BeforeAgent"

        session_id = sanitize_log_field(str(payload.get("session_id") or ""))
        source_root = source_root_for_payload(payload)
        summary_root = summary_root_for_payload(payload)
        manifest_path = manifest_path_for_payload(payload, summary_root)
        repo_root = repo_root_for_payload(payload)

        with ManifestLock(manifest_path):
            current_records = scan_sources(source_root, summary_root)
            manifest = load_manifest(manifest_path)
            report_entries, next_manifest = reconcile_manifest(manifest, current_records, summary_root)
            save_manifest(manifest_path, next_manifest)
        skill_available = ingest_skill_available(repo_root)

        if event_name == "AfterAgent":
            reason = build_block_reason(report_entries, skill_available)
            if not reason:
                emit_json({})
                return 0

            log_event(
                f"Message: blocked model response while ingest is pending, "
                f"Session: {session_id}, Findings: {len(blocking_entries(report_entries))}"
            )
            emit_json({"decision": "deny", "reason": reason})
            return 0

        context = build_context(report_entries, manifest_path, skill_available)
        if not context:
            emit_json({})
            return 0

        log_event(
            f"Message: injected pending ingest context before agent planning, "
            f"Session: {session_id}, Findings: {len(report_entries)}"
        )

        emit_json(
            {
                "hookSpecificOutput": {
                    "hookEventName": "BeforeAgent",
                    "additionalContext": context,
                },
                "suppressOutput": True,
            }
        )
        return 0
    except ValueError as exc:
        log_event(f"Error: {sanitize_log_field(str(exc))}")
        emit_json({})
    except Exception as exc:  # noqa: BLE001 - fail open on context-injection errors
        log_event(f"Error: Unexpected exception: {sanitize_log_field(str(exc))}")
        emit_json({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
