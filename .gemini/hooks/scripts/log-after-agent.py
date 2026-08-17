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
    prompt = stringify_value(payload.get("prompt"))
    stop_hook_active = stringify_value(payload.get("stop_hook_active"))
    return f"[{timestamp}] Prompt: {prompt}, Stop Hook Active: {stop_hook_active}, Session: {session_id}"


if __name__ == "__main__":
    raise SystemExit(run_gemini_passive_log_hook(SCRIPT_NAME, build_message))
