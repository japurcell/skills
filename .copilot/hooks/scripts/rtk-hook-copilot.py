#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from helpers.audit import audit_log_event
from helpers.common import emit_json, sanitize_log_field


SCRIPT_NAME = Path(__file__).name
RTK_TIMEOUT_SECONDS = 1.0


def emit_noop() -> None:
    emit_json({})


def log_failure(reason: str) -> None:
    audit_log_event(SCRIPT_NAME, f"RTK rewrite fallback: {sanitize_log_field(reason)}")


def forward_to_rtk(raw_input: str) -> tuple[dict | None, str | None]:
    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        return None, "invalid hook input JSON"

    if not isinstance(payload, dict):
        return None, "invalid hook input JSON"

    try:
        result = subprocess.run(
            ["rtk", "hook", "copilot"],
            input=raw_input,
            capture_output=True,
            text=True,
            shell=False,
            timeout=RTK_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return None, "rtk command not found"
    except subprocess.TimeoutExpired:
        return None, f"rtk hook copilot timed out after {RTK_TIMEOUT_SECONDS:.1f}s"
    except Exception as exc:  # noqa: BLE001 - safe fallback path
        return None, f"rtk hook invocation failed: {exc}"

    if result.returncode != 0:
        stderr = sanitize_log_field(result.stderr)
        return None, f"rtk exited {result.returncode}: {stderr}"

    try:
        rewritten = json.loads(result.stdout or "")
    except json.JSONDecodeError:
        return None, "rtk returned invalid JSON"

    if not isinstance(rewritten, dict):
        return None, "rtk returned non-object JSON"

    return rewritten, None


def main() -> int:
    raw_input = sys.stdin.read()

    rewritten, failure_reason = forward_to_rtk(raw_input)
    if failure_reason is not None:
        log_failure(failure_reason)
        emit_noop()
        return 0

    sys.stdout.write(json.dumps(rewritten, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.write("\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
