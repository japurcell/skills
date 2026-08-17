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
    tool_name = stringify_value(first_present(payload, "toolName", "tool_name"))
    tool_args = stringify_value(first_present(payload, "toolArgs", "tool_input"))
    error_message = stringify_value(first_present(payload, "error"))
    return (
        f"[{timestamp}] Session: {session_id}, "
        f"Tool: {tool_name}, "
        f"Args: {tool_args}, "
        f"Error: {error_message}"
    )


if __name__ == "__main__":
    raise SystemExit(run_passive_log_hook(SCRIPT_NAME, build_message))
