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
    build_block_reason,
    build_context,
    blocking_entries,
    ingest_skill_available,
    load_manifest,
    manifest_path_for_summary_root,
    reconcile_manifest,
    save_manifest,
    scan_sources,
)


SCRIPT_NAME = Path(__file__).name


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

def _repo_root(payload: dict[str, object]) -> Path:
    cwd = str(payload.get("cwd") or "")
    return Path(cwd) if cwd else Path.cwd()


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

        event_name = str(payload.get("hook_event_name") or "")
        if event_name and event_name not in {"BeforeAgent", "AfterModel"}:
            emit_json({})
            return 0
        if not event_name:
            event_name = "BeforeAgent"

        session_id = sanitize_log_field(str(payload.get("session_id") or ""))
        source_root = _source_root(payload)
        summary_root = _summary_root(payload)
        manifest_path = _manifest_path(summary_root)
        repo_root = _repo_root(payload)

        current_records = scan_sources(source_root, summary_root)
        manifest = load_manifest(manifest_path)
        report_entries, next_manifest = reconcile_manifest(manifest, current_records, summary_root)
        save_manifest(manifest_path, next_manifest)
        skill_available = ingest_skill_available(repo_root)

        if event_name == "AfterModel":
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
