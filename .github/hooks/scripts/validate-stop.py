#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATORS = (
    SCRIPT_DIR / "inject-auto-ingest-context.py",
    SCRIPT_DIR / "lint-okf.py",
)


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
    payload = sys.stdin.read()
    reasons: list[str] = []

    try:
        for validator in VALIDATORS:
            reason = _run_validator(validator, payload)
            if reason:
                reasons.append(reason)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError):
        reasons.append("Copilot stop validation failed. Run the source-ingest and OKF validators directly, then retry.")

    response: dict[str, str]
    if reasons:
        response = {"decision": "block", "reason": "\n\n".join(reasons)}
    else:
        response = {"decision": "allow"}
    sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
