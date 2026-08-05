#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_init, audit_log_event  # noqa: E402
from helpers.common import emit_json, read_json_input, sanitize_log_field  # noqa: E402
from helpers.source_ingest import (  # noqa: E402
    build_context,
    load_manifest,
    manifest_path_for_summary_root,
    reconcile_manifest,
    save_manifest,
    scan_sources,
)


SCRIPT_NAME = Path(__file__).name


def hard_stop(reason: str) -> None:
    message = reason.strip() or "Hook failed"
    print(f"Hook hard stop: {message}", file=sys.stderr)
    emit_json({"continue": False, "stopReason": message, "suppressOutput": True})
    raise SystemExit(0)


def _source_root(payload: dict[str, object]) -> Path:
    override = os.environ.get("AGENTS_SOURCE_SCAN_DIR")
    if override:
        return Path(override)
    cwd = str(payload.get("cwd") or "")
    return Path(cwd) / ".agents/sources" if cwd else Path.cwd() / ".agents/sources"


def _summary_root(payload: dict[str, object]) -> Path:
    override = os.environ.get("AGENTS_SOURCE_SUMMARY_DIR")
    if override:
        return Path(override)
    cwd = str(payload.get("cwd") or "")
    return Path(cwd) / ".agents/memory/sources" if cwd else Path.cwd() / ".agents/memory/sources"


def _manifest_path(summary_root: Path) -> Path:
    override = os.environ.get("AGENTS_SOURCE_MANIFEST_PATH")
    if override:
        return Path(override)
    return manifest_path_for_summary_root(summary_root)


def _is_startup_only(payload: dict[str, object]) -> bool:
    return str(payload.get("hook_event_name") or "") == "SessionStart" and str(payload.get("source") or "") == "startup"


def main() -> int:
    try:
        input_payload = read_json_input()
        if not isinstance(input_payload, dict):
            emit_json({})
            return 0

        if not _is_startup_only(input_payload):
            emit_json({})
            return 0

        session_id = str(input_payload.get("session_id") or "")
        timestamp = str(input_payload.get("timestamp") or "")
        cwd = str(input_payload.get("cwd") or "")

        if not audit_init():
            hard_stop("audit_init failed")

        safe_session_id = sanitize_log_field(session_id)
        safe_timestamp = sanitize_log_field(timestamp)
        safe_cwd = sanitize_log_field(cwd)

        if not audit_log_event(
            SCRIPT_NAME,
            f"[{safe_timestamp}] Hook: SessionStart(startup), CWD: {safe_cwd}, Session: {safe_session_id}",
        ):
            hard_stop("Failed to write initial audit event")

        source_root = _source_root(input_payload)
        summary_root = _summary_root(input_payload)
        manifest_path = _manifest_path(summary_root)

        current_records = scan_sources(source_root, summary_root)
        manifest = load_manifest(manifest_path)
        report_entries, next_manifest = reconcile_manifest(manifest, current_records, summary_root)
        save_manifest(manifest_path, next_manifest)

        context = build_context(report_entries, manifest_path)
        if not context:
            emit_json({})
            return 0

        emit_json(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                },
                "suppressOutput": True,
            }
        )
        return 0
    except ValueError as exc:
        hard_stop(str(exc))
    except Exception as exc:  # noqa: BLE001 - top-level fallback
        print(f"{SCRIPT_NAME}: Unexpected auto-ingest scan exception: {exc}", file=sys.stderr)
        emit_json({})
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
