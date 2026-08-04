#!/usr/bin/env python3

from __future__ import annotations

import json
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


def _field_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def main() -> int:
    try:
        input_payload = read_json_input()

        if not isinstance(input_payload, dict):
            noop()

        if not audit_init():
            noop()

        session_id = _field_text(input_payload.get("session_id"))
        timestamp = _field_text(input_payload.get("timestamp"))
        prompt = _field_text(input_payload.get("prompt"))
        stop_hook_active = _field_text(input_payload.get("stop_hook_active"))

        if not audit_log_passive_event(
            SCRIPT_NAME,
            f"[{timestamp}] Prompt: {prompt}, Stop Hook Active: {stop_hook_active}, Session: {session_id}",
        ):
            noop()

        noop()
    except ValueError as exc:
        print(f"{SCRIPT_NAME}: {exc}", file=sys.stderr)
        noop()
    except Exception as exc:
        print(f"{SCRIPT_NAME}: unexpected error: {exc}", file=sys.stderr)
        noop()


if __name__ == "__main__":
    raise SystemExit(main())
