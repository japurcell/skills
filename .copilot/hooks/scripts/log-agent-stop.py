#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from helpers.common import (
    first_present,
    run_passive_log_hook,
    stringify_value,
)

SCRIPT_NAME = Path(__file__).name


def build_message(payload: dict) -> str:
    session_id = stringify_value(first_present(payload, "sessionId", "session_id"))
    timestamp = stringify_value(first_present(payload, "timestamp"))
    transcript_path = stringify_value(first_present(payload, "transcriptPath", "transcript_path"))
    stop_reason = stringify_value(first_present(payload, "stopReason", "stop_reason"))
    return (
        f"[{timestamp}] Session: {session_id}, "
        f"Transcript: {transcript_path}, "
        f"Stop Reason: {stop_reason}"
    )


if __name__ == "__main__":
    raise SystemExit(run_passive_log_hook(SCRIPT_NAME, build_message))
