#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import run_gemini_passive_log_hook, stringify_value  # noqa: E402

SCRIPT_NAME = Path(__file__).name


def build_message(payload: dict) -> str:
    session_id = stringify_value(payload.get("session_id"))
    timestamp = stringify_value(payload.get("timestamp"))
    hook_event_name = stringify_value(payload.get("hook_event_name"))
    transcript_path = stringify_value(payload.get("transcript_path"))
    cwd = stringify_value(payload.get("cwd"))
    return f"[{timestamp}] Transcript: {transcript_path}, Hook: {hook_event_name}, CWD: {cwd}, Session: {session_id}"


if __name__ == "__main__":
    raise SystemExit(run_gemini_passive_log_hook(SCRIPT_NAME, build_message))
