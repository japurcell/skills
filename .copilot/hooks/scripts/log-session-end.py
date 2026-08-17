#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from helpers.common import run_passive_log_hook

SCRIPT_NAME = Path(__file__).name


def build_message(payload: dict) -> str:
    session_id = str(payload.get("sessionId") or payload.get("session_id") or "")
    timestamp = str(payload.get("timestamp") or "")
    reason = str(payload.get("reason") or "")
    return f"[{timestamp}] Session: {session_id}, Reason: {reason}"


if __name__ == "__main__":
    raise SystemExit(run_passive_log_hook(SCRIPT_NAME, build_message))
