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
    notification_type = stringify_value(payload.get("notification_type"))
    message = stringify_value(payload.get("message"))
    details_value = payload.get("details")
    details = "{}" if details_value is None else stringify_value(details_value)
    return (
        f"session_id: {session_id}, "
        f"notification_type: {notification_type}, "
        f"message: {message}, "
        f"details: {details}"
    )


if __name__ == "__main__":
    raise SystemExit(run_gemini_passive_log_hook(SCRIPT_NAME, build_message))
