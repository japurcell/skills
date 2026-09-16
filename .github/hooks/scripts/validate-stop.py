#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import emit_json, read_json_input


MAX_STOP_OUTPUT_BYTES = 8192
TRUNCATION_MARKER = "\n\n[Reason truncated.]"
MAX_REASON_PREFIX_BYTES = 512
VALIDATORS = (
    SCRIPT_DIR / "inject-auto-ingest-context.py",
    SCRIPT_DIR / "lint-okf.py",
)


def _compact_json_bytes(payload: Mapping[str, object]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _serialized_response_size(reason: str) -> int:
    return len(_compact_json_bytes({"decision": "block", "reason": reason}))


def _truncate_utf8(text: str, max_bytes: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[:max_bytes].decode("utf-8", errors="ignore")


def _bounded_combined_block(reasons: list[str]) -> str:
    combined = "\n\n".join(reasons)
    if _serialized_response_size(combined) < MAX_STOP_OUTPUT_BYTES:
        return combined

    truncated = "\n\n".join(_truncate_utf8(reason, MAX_REASON_PREFIX_BYTES) for reason in reasons)
    bounded = truncated + TRUNCATION_MARKER
    while _serialized_response_size(bounded) >= MAX_STOP_OUTPUT_BYTES and truncated:
        truncated = _truncate_utf8(truncated, max(0, len(truncated.encode("utf-8")) - 1))
        bounded = truncated + TRUNCATION_MARKER
    return bounded


def _block_reason(response: object, validator: Path) -> str | None:
    if not isinstance(response, Mapping):
        raise ValueError(f"{validator.name} returned a non-object response")

    decision = response.get("decision")
    if decision == "allow":
        return None
    if decision == "block" and isinstance(response.get("reason"), str) and response["reason"].strip():
        return response["reason"]
    raise ValueError(f"{validator.name} returned an invalid stop response")


def _run_validator(validator: Path, payload: str) -> str | None:
    completed = subprocess.run(
        [sys.executable, str(validator)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(f"{validator.name} exited {completed.returncode}")
    return _block_reason(json.loads(completed.stdout), validator)


def main() -> int:
    reasons: list[str] = []

    try:
        payload = json.dumps(read_json_input(), ensure_ascii=False, separators=(",", ":"))
        for validator in VALIDATORS:
            reason = _run_validator(validator, payload)
            if reason:
                reasons.append(reason)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError):
        reasons.append("Copilot stop validation failed. Run the source-ingest and OKF validators directly, then retry.")

    response: dict[str, str]
    if reasons:
        response = {"decision": "block", "reason": _bounded_combined_block(reasons)}
    else:
        response = {"decision": "allow"}
    emit_json(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
