#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_init, audit_log_passive_event  # noqa: E402
from helpers.common import emit_json, read_json_input  # noqa: E402


SCRIPT_NAME = Path(__file__).name


def noop() -> None:
    emit_json({})
    raise SystemExit(0)


def main() -> int:
    try:
        input_payload = read_json_input()
    except ValueError as exc:
        print(f"{SCRIPT_NAME}: {exc}", file=sys.stderr)
        noop()

    if not isinstance(input_payload, dict):
        noop()

    if not audit_init():
        noop()

    session_id = str(input_payload.get("session_id") or "")
    timestamp = str(input_payload.get("timestamp") or "")
    hook_event_name = str(input_payload.get("hook_event_name") or "")
    transcript_path = str(input_payload.get("transcript_path") or "")
    cwd = str(input_payload.get("cwd") or "")

    if not audit_log_passive_event(
        SCRIPT_NAME,
        f"[{timestamp}] Transcript: {transcript_path}, Hook: {hook_event_name}, CWD: {cwd}, Session: {session_id}",
    ):
        noop()

    noop()


if __name__ == "__main__":
    raise SystemExit(main())

