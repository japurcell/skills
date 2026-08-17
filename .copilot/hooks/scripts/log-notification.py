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
    title = stringify_value(first_present(payload, "title"))
    message = stringify_value(first_present(payload, "message"))
    notification_type = stringify_value(first_present(payload, "notificationType", "notification_type"))
    return (
        f"[{timestamp}] Session: {session_id}, "
        f"Title: {title}, "
        f"Message: {message}, "
        f"Notification Type: {notification_type}"
    )


if __name__ == "__main__":
    raise SystemExit(run_passive_log_hook(SCRIPT_NAME, build_message))
