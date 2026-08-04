#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from helpers.audit import audit_log_event
from helpers.common import (
    emit_json,
    first_present,
    nested_present,
    read_json_input,
    sanitize_log_field,
    stringify_value,
)


SCRIPT_NAME = Path(__file__).name


def log_event(message: str) -> None:
    try:
        audit_log_event(SCRIPT_NAME, message)
    except Exception:
        pass


def fail_safe(reason: str) -> None:
    safe_reason = sanitize_log_field(reason).strip() or "Hook failed"
    print(f"{SCRIPT_NAME}: {safe_reason}", file=sys.stderr)
    log_event(f"Error: {safe_reason}")
    emit_json({})


def main() -> int:
    try:
        payload = read_json_input()
        session_id = stringify_value(first_present(payload, "sessionId", "session_id"))
        timestamp = stringify_value(first_present(payload, "timestamp"))
        error_message = stringify_value(nested_present(payload, "error", "message"))
        error_name = stringify_value(nested_present(payload, "error", "name"))
        error_stack = stringify_value(nested_present(payload, "error", "stack"))
        error_context = stringify_value(first_present(payload, "errorContext", "error_context"))
        recoverable = stringify_value(first_present(payload, "recoverable"))
        log_event(
            f"[{timestamp}] Session: {session_id}, "
            f"Error Message: {error_message}, "
            f"Error Name: {error_name}, "
            f"Error Stack: {error_stack}, "
            f"Error Context: {error_context}, "
            f"Recoverable: {recoverable}"
        )
        emit_json({})
        return 0
    except ValueError as exc:
        fail_safe(str(exc))
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        fail_safe(f"Unexpected exception: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
