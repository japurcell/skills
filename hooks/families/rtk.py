"""Render the RTK forwarders with their explicit provider adapters."""

from __future__ import annotations

from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


SHEBANG = "#!/usr/bin/env python3\n"
HEADER = "# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.\n"
ADAPTER_START = "# BEGIN PROVIDER ADAPTER\n"
ADAPTER_END = "# END PROVIDER ADAPTER\n"


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

import codecs
import io
import json
import os
import select
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
from helpers.observability import begin_hook_capture


SCRIPT_NAME = Path(__file__).name
RTK_TIMEOUT_SECONDS = 1.0
INPUT_COMPLETION_IDLE_SECONDS = 0.5


def emit_noop() -> None:
    emit_json({})


def log_failure(reason: str) -> None:
    audit_log_event(SCRIPT_NAME, f"RTK rewrite fallback: {sanitize_log_field(reason)}")


def windows_pipe_bytes_available(file_descriptor: int) -> int | None:
    """Return queued pipe bytes, or None when the pipe is closed."""
    import ctypes
    import ctypes.wintypes
    import msvcrt

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.PeekNamedPipe.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.c_void_p,
        ctypes.wintypes.DWORD,
        ctypes.POINTER(ctypes.wintypes.DWORD),
        ctypes.POINTER(ctypes.wintypes.DWORD),
        ctypes.POINTER(ctypes.wintypes.DWORD),
    ]
    kernel32.PeekNamedPipe.restype = ctypes.wintypes.BOOL
    available = ctypes.wintypes.DWORD()
    handle = msvcrt.get_osfhandle(file_descriptor)
    if kernel32.PeekNamedPipe(handle, None, 0, None, ctypes.byref(available), None):
        return available.value
    return None


def wait_for_stdin(file_descriptor: int, timeout: float) -> bool:
    if os.name != "nt":
        return bool(select.select([file_descriptor], [], [], timeout)[0])

    deadline = time.monotonic() + timeout
    while True:
        available = windows_pipe_bytes_available(file_descriptor)
        if available is None or available:
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(remaining, 0.01))


def read_stdin_bytes(file_descriptor: int) -> bytes:
    if os.name == "nt":
        available = windows_pipe_bytes_available(file_descriptor)
        return os.read(file_descriptor, available or 1)
    return os.read(file_descriptor, io.DEFAULT_BUFFER_SIZE)


def read_hook_input() -> tuple[bytes | None, dict | None, str | None]:
    file_descriptor = sys.stdin.fileno()
    raw_input = bytearray()
    decoded_input = ""
    utf8_decoder = codecs.getincrementaldecoder("utf-8")()
    json_decoder = json.JSONDecoder()
    idle_deadline = time.monotonic() + INPUT_COMPLETION_IDLE_SECONDS

    while True:
        timeout = max(0.0, idle_deadline - time.monotonic())
        if not wait_for_stdin(file_descriptor, timeout):
            return None, None, "invalid hook input JSON"

        try:
            chunk = read_stdin_bytes(file_descriptor)
        except OSError:
            return None, None, "invalid hook input JSON"

        if not chunk:
            return None, None, "invalid hook input JSON"

        raw_input.extend(chunk)
        try:
            decoded_input += utf8_decoder.decode(chunk, final=False)
        except UnicodeDecodeError:
            return None, None, "invalid hook input JSON"

        try:
            start = len(decoded_input) - len(decoded_input.lstrip())
            payload, end = json_decoder.raw_decode(decoded_input, start)
        except json.JSONDecodeError:
            idle_deadline = time.monotonic() + INPUT_COMPLETION_IDLE_SECONDS
            continue

        if not isinstance(payload, dict):
            return None, None, "invalid hook input JSON"

        while wait_for_stdin(file_descriptor, 0.0):
            try:
                buffered = read_stdin_bytes(file_descriptor)
            except OSError:
                return None, None, "invalid hook input JSON"
            if not buffered:
                break
            raw_input.extend(buffered)
            try:
                decoded_input += utf8_decoder.decode(buffered, final=False)
            except UnicodeDecodeError:
                return None, None, "invalid hook input JSON"

        trailing_input = decoded_input[end:]
        if utf8_decoder.getstate()[0] or (trailing_input and not trailing_input.isspace()):
            return None, None, "invalid hook input JSON"
        return bytes(raw_input), payload, None


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
    begin_hook_capture(payload or {})

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
        or provider.name not in {"copilot", "gemini"}
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
        + runtime_body
    )
