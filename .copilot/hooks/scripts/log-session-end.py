#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from helpers.audit import audit_log_event
from helpers.common import read_json_input


SCRIPT_NAME = Path(__file__).name


def main() -> int:
    payload = read_json_input()
    session_id = str(payload.get("sessionId") or payload.get("session_id") or "")
    timestamp = str(payload.get("timestamp") or "")
    reason = str(payload.get("reason") or "")

    audit_log_event(
        SCRIPT_NAME,
        f"[{timestamp}] Session: {session_id}, Reason: {reason}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
