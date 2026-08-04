#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_init, audit_log_passive_event  # noqa: E402
from helpers.common import emit_json, read_json_input  # noqa: E402


SCRIPT_NAME = Path(__file__).name


def noop() -> None:
    emit_json({})
    raise SystemExit(0)


def main() -> int:
    try:
        payload = read_json_input()
    except ValueError as exc:
        print(f"{SCRIPT_NAME}: {exc}", file=sys.stderr)
        noop()

    if not isinstance(payload, dict):
        noop()

    if not audit_init():
        noop()

    session_id = str(payload.get("session_id") or "")
    timestamp = str(payload.get("timestamp") or "")
    hook_event_name = str(payload.get("hook_event_name") or "")
    reason = str(payload.get("reason") or "")

    if not audit_log_passive_event(
        SCRIPT_NAME,
        f"[{timestamp}] Reason: {reason}, Hook: {hook_event_name}, Session: {session_id}",
    ):
        noop()

    noop()


if __name__ == "__main__":
    raise SystemExit(main())
