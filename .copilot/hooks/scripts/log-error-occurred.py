#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from helpers.common import (
    first_present,
    nested_present,
    run_passive_log_hook,
    stringify_value,
)

SCRIPT_NAME = Path(__file__).name


def build_message(payload: dict) -> str:
    session_id = stringify_value(first_present(payload, "sessionId", "session_id"))
    timestamp = stringify_value(first_present(payload, "timestamp"))
    error_message = stringify_value(nested_present(payload, "error", "message"))
    error_name = stringify_value(nested_present(payload, "error", "name"))
    error_stack = stringify_value(nested_present(payload, "error", "stack"))
    error_context = stringify_value(first_present(payload, "errorContext", "error_context"))
    recoverable = stringify_value(first_present(payload, "recoverable"))
    return (
        f"[{timestamp}] Session: {session_id}, "
        f"Error Message: {error_message}, "
        f"Error Name: {error_name}, "
        f"Error Stack: {error_stack}, "
        f"Error Context: {error_context}, "
        f"Recoverable: {recoverable}"
    )


if __name__ == "__main__":
    raise SystemExit(run_passive_log_hook(SCRIPT_NAME, build_message))
