"""Render the Copilot and Gemini RTK automatic forwarders."""

from __future__ import annotations

from hooks.families.common import INPUT_PREAMBLE, INPUT_READER
from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


SHEBANG = "#!/usr/bin/env python3\n"
HEADER = "# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.\n"
ADAPTER_START = "# BEGIN PROVIDER ADAPTER\n"
ADAPTER_END = "# END PROVIDER ADAPTER\n"
_TARGET_PATHS = {
    "copilot": ".copilot/hooks/scripts/rtk-hook-copilot.py",
    "gemini": ".gemini/hooks/scripts/rtk-hook-gemini.py",
}
_COPILOT_ADAPTER = r'''RTK_PROVIDER = "copilot"


def normalize_rewritten(rewritten: dict) -> dict:
    top_decision = rewritten.get("permissionDecision")
    if isinstance(top_decision, str) and top_decision.strip().lower() == "ask":
        audit_log_event(SCRIPT_NAME, "Overriding top-level 'ask' decision to 'allow' for silent execution")
        rewritten["permissionDecision"] = "allow"

    hook_out = rewritten.get("hookSpecificOutput")
    if isinstance(hook_out, dict):
        nested_decision = hook_out.get("permissionDecision")
        if isinstance(nested_decision, str) and nested_decision.strip().lower() == "ask":
            audit_log_event(SCRIPT_NAME, "Overriding nested hookSpecificOutput 'ask' decision to 'allow' for silent execution")
            hook_out["permissionDecision"] = "allow"

    return rewritten


'''


_GEMINI_ADAPTER = r'''RTK_PROVIDER = "gemini"


def normalize_rewritten(rewritten: dict) -> dict:
    return rewritten


'''


_RUNTIME_SOURCE = r'''from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_log_event
from helpers.common import emit_json, sanitize_log_field


SCRIPT_NAME = Path(__file__).name
RTK_TIMEOUT_SECONDS = 1.0
INPUT_COMPLETION_IDLE_SECONDS = 0.5


def emit_noop() -> None:
    emit_json({})


def log_failure(reason: str) -> None:
    audit_log_event(SCRIPT_NAME, f"RTK rewrite fallback: {sanitize_log_field(reason)}")


def read_hook_input() -> tuple[bytes | None, dict | None, str | None]:
    try:
        raw, payload = collect_event_input("rtk")
        return raw, payload, None
    except (OSError, ValueError):
        return None, None, "invalid hook input JSON"


def forward_to_rtk(raw_input: bytes) -> tuple[dict | None, str | None]:
    rtk_bin = shutil.which("rtk") or "rtk"

    try:
        result = subprocess.run(
            [rtk_bin, "hook", RTK_PROVIDER],
            input=raw_input,
            capture_output=True,
            shell=False,
            timeout=RTK_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return None, "rtk command not found"
    except subprocess.TimeoutExpired:
        return None, f"rtk hook {RTK_PROVIDER} timed out after {RTK_TIMEOUT_SECONDS:.1f}s"
    except Exception as exc:  # noqa: BLE001 - safe fallback path
        return None, f"rtk hook invocation failed: {exc}"

    if result.returncode != 0:
        return None, f"rtk exited {result.returncode}"

    stdout_stripped = (result.stdout or b"").strip()
    if not stdout_stripped:
        return {}, None

    try:
        rewritten = json.loads(stdout_stripped.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "rtk returned invalid JSON"

    if not isinstance(rewritten, dict):
        return None, "rtk returned non-object JSON"

    return normalize_rewritten(rewritten), None


def main() -> int:
    raw_input, payload, input_failure = read_hook_input()

    if input_failure is not None or raw_input is None:
        log_failure(input_failure or "invalid hook input JSON")
        emit_noop()
        return 0

    rewritten, failure_reason = forward_to_rtk(raw_input)
    if failure_reason is not None:
        log_failure(failure_reason)
        emit_noop()
        return 0

    emit_json(rewritten)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _adapter_source(provider: Provider) -> str:
    if provider.name == "copilot":
        return _COPILOT_ADAPTER
    if provider.name == "gemini":
        return _GEMINI_ADAPTER
    raise ValueError(f"Unsupported RTK provider: {provider.name}")


def render(provider: Provider, target: GeneratedTarget) -> str:
    """Render one self-contained RTK provider forwarder."""
    if (
        target.family != "rtk"
        or target.provider != provider.name
        or target.output_path.as_posix() != _TARGET_PATHS.get(provider.name)
    ):
        raise ValueError(f"Unsupported RTK target/provider: {target.output_path}")
    future_import, runtime_body = _RUNTIME_SOURCE.split("\n", 1)
    return (
        SHEBANG
        + HEADER
        + future_import
        + "\n"
        + ADAPTER_START
        + _adapter_source(provider)
        + ADAPTER_END
        + runtime_body.replace("def read_hook_input()", INPUT_PREAMBLE + INPUT_READER + "def read_hook_input()", 1)
    )
