#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_log_event
from helpers.auto_ingest import (
    ManifestLock,
    build_context,
    ingest_skill_available,
    load_manifest,
    manifest_path,
    reconcile_manifest,
    scan_sources,
    save_manifest,
    source_root,
    summary_root,
)
from helpers.common import emit_json, first_present, read_json_input, sanitize_log_field, stringify_value


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
    try:
        audit_log_event(SCRIPT_NAME, message)
    except Exception:
        pass


def fail_safe(reason: str, event_name: str = "") -> None:
    safe_reason = sanitize_log_field(reason).strip() or "Hook failed"
    print(f"{SCRIPT_NAME}: {safe_reason}", file=sys.stderr)
    log_event(f"Error: {safe_reason}")
    emit_json(build_output(f"Auto-ingest source scan failed.\n\nReason: {safe_reason}", event_name))


def _repo_root(payload: dict[str, object]) -> Path:
    env_override = os.environ.get("COPILOT_AUTO_INGEST_REPO_ROOT")
    if env_override:
        return Path(env_override)

    cwd = stringify_value(first_present(payload, "cwd", "workingDirectory", "working_directory"))
    if cwd:
        return Path(cwd)

    return Path.cwd()
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

        root = _repo_root(payload)
        sources_dir = source_root(root)
        summaries_dir = summary_root(root)
        manifest_file = manifest_path(summaries_dir)

        with ManifestLock(manifest_file):
            current_sources = scan_sources(sources_dir, summaries_dir)
            previous_manifest = load_manifest(manifest_file)
            report_entries, next_manifest = reconcile_manifest(previous_manifest, current_sources, summaries_dir)
            save_manifest(manifest_file, next_manifest)

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

        emit_json(build_output(message, event_name))
        return 0
    except ValueError as exc:
        fail_safe(str(exc), "")
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        fail_safe(f"Unexpected exception: {exc}", "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
