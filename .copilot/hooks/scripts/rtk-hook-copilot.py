#!/usr/bin/env python3
# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations
# BEGIN PROVIDER ADAPTER
RTK_PROVIDER = "copilot"


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


# END PROVIDER ADAPTER

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


INPUT_COMPLETION_IDLE_SECONDS = 0.5
INPUT_COMPLETION_TOTAL_SECONDS = 2.0
# Six-byte JSON escapes for 256 KiB of native data, plus 512 KiB of metadata.
INPUT_MAX_BYTES = 2 * 1024 * 1024
INPUT_MAX_DEPTH = 64


def _stdin_is_ready(stdin_fd: int, timeout: float = 0, *, eof_ready: bool = True) -> bool:
    if os.name != "nt":
        import select

        return bool(select.select([stdin_fd], [], [], timeout)[0])

    deadline = time.monotonic() + timeout
    while True:
        available = windows_pipe_bytes_available(stdin_fd)
        if available or (available is None and eof_ready):
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(0.01, remaining))


def windows_pipe_bytes_available(stdin_fd: int) -> int | None:
    import ctypes
    import msvcrt

    pipe_handle = ctypes.c_void_p(msvcrt.get_osfhandle(stdin_fd))
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    available = ctypes.c_ulong()
    if kernel32.PeekNamedPipe(pipe_handle, None, 0, None, ctypes.byref(available), None):
        return available.value
    error = ctypes.get_last_error()
    if error == 109 or kernel32.GetFileType(pipe_handle) == 1:
        return None
    raise OSError(error, "Hook stdin readiness failed")

class InputLimitError(ValueError):
    def __init__(self, rule_id: str, limit: int, measured: int, unit: str):
        self.rule_id, self.limit, self.measured, self.unit = rule_id, limit, measured, unit
        super().__init__(rule_id)


def _read_stdin_chunk(stdin_fd: int, max_bytes: int, timeout: float, *, eof_ready: bool = True) -> bytes | None:
    if os.name == "nt":
        return os.read(stdin_fd, max_bytes) if _stdin_is_ready(stdin_fd, timeout, eof_ready=eof_ready) else None
    blocking = os.get_blocking(stdin_fd)
    try:
        os.set_blocking(stdin_fd, False)
        try:
            return os.read(stdin_fd, max_bytes)
        except BlockingIOError:
            if not _stdin_is_ready(stdin_fd, timeout):
                return None
            return os.read(stdin_fd, max_bytes)
    finally:
        os.set_blocking(stdin_fd, blocking)


def _bounded_completion(max_markers):
    markers = 0
    stack = []
    started = in_string = escaped = complete = False
    chunk = yield False
    while True:
        # Scan structural markers once in C, skipping ordinary UTF-8 bytes.
        # json.loads remains the full syntax authority after bounded collection.
        cursor = 1 if in_string and escaped else 0
        escaped = False
        marker_pattern = re.compile(rb'(?:\\[\s\S])+|["\\\[\]{},:]')
        # Batch escape runs and ordinary spans between them inside strings.
        # Keep contiguous Unicode and byte-pair runs on their direct C paths.
        string_pattern = re.compile(
            rb'\\(?:u[0-9a-fA-F]{4}(?:\\u[0-9a-fA-F]{4})*'
            rb'|[\s\S](?:\\[\s\S])*)(?:[^"\\]+\\[\s\S](?:\\[\s\S])*)*|["\\]'
        )
        while (match := (string_pattern if in_string else marker_pattern).search(chunk, cursor)) is not None:
            position = match.start()
            byte = chunk[position]
            if not started:
                if byte != 123 or chunk[cursor:position].strip(b" \t\r\n"):
                    raise ValueError("Invalid hook input: expected a JSON object")
                started = True
            if in_string:
                escaped = byte == 92 and match.end() - position == 1
                if byte == 34:
                    in_string = False
            else:
                markers += 1
                if max_markers is not None and markers > max_markers:
                    raise InputLimitError("raw_structural_markers", max_markers, markers, "markers")
                if byte == 34:
                    in_string = True
                elif byte in (123, 91):
                    stack.append(byte)
                    if len(stack) > INPUT_MAX_DEPTH:
                        raise ValueError("Invalid hook input: nesting limit exceeded")
                elif byte in (125, 93):
                    if not stack or stack.pop() != (123 if byte == 125 else 91):
                        raise ValueError("Invalid hook input: malformed JSON")
                    complete = not stack
                    if complete:
                        if chunk[position + 1:].strip(b" \t\r\n"):
                            raise ValueError("Invalid hook input: trailing data")
                        break
            cursor = match.end()
        if not started and chunk[cursor:].strip(b" \t\r\n"):
            raise ValueError("Invalid hook input: expected a JSON object")
        if escaped and cursor < len(chunk):
            # Only a terminal backslash carries its escape into the next chunk.
            escaped = False

        chunk = yield complete


def collect_event_input(mode, *, max_bytes=None, max_markers=None):
    """Collect one event, retaining its bytes and applying the caller's policy."""
    import codecs

    try:
        fd = sys.stdin.fileno()
    except (AttributeError, OSError):
        if mode == "bounded":
            raise ValueError("Invalid hook input: stdin readiness unavailable") from None
        raise
    deadline = time.monotonic() + INPUT_COMPLETION_TOTAL_SECONDS if mode == "bounded" else None
    raw = bytearray()
    bounded = _bounded_completion(max_markers) if mode == "bounded" else None
    if bounded is not None:
        next(bounded)
    decoder = codecs.getincrementaldecoder("utf-8")() if mode == "rtk" else None
    text = ""
    parser = json.JSONDecoder()
    end = 0
    payload = None
    complete = False
    while True:
        remaining = deadline - time.monotonic() if deadline is not None else INPUT_COMPLETION_IDLE_SECONDS
        if remaining <= 0:
            raise ValueError("Invalid hook input: input deadline exceeded")
        size = 65536 if mode == "bounded" else (8192 if mode == "rtk" else 4096)
        if max_bytes is not None:
            size = min(size, max_bytes - len(raw) + 1)
        chunk = _read_stdin_chunk(fd, size, min(INPUT_COMPLETION_IDLE_SECONDS, remaining), eof_ready=mode != "codex")
        if chunk is None:
            raise ValueError("Invalid hook input: malformed or incomplete JSON")
        if not chunk:
            if mode == "bounded":
                return bytes(raw), None
            raise ValueError("Invalid hook input: incomplete JSON")
        raw.extend(chunk)
        if max_bytes is not None and len(raw) > max_bytes:
            if mode == "bounded":
                raise InputLimitError("raw_input_bytes", max_bytes, len(raw), "bytes")
            raise ValueError("Hook input exceeds the maximum size")
        if mode == "bounded":
            complete = bounded.send(chunk)
        else:
            try:
                text = text + decoder.decode(chunk, final=False) if decoder else raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                if mode == "codex" and exc.reason == "unexpected end of data":
                    continue
                raise ValueError("Invalid hook input: expected UTF-8 JSON") from exc
            try:
                start = len(text) - len(text.lstrip())
                payload, end = parser.raw_decode(text, start)
                complete = True
            except json.JSONDecodeError:
                continue
            if mode == "rtk" and not isinstance(payload, dict):
                raise ValueError("invalid hook input JSON")
        if deadline is not None and time.monotonic() >= deadline:
            raise ValueError("Invalid hook input: input deadline exceeded")
        if not complete:
            continue
        while True:
            if deadline is not None and time.monotonic() >= deadline:
                raise ValueError("Invalid hook input: input deadline exceeded")
            size = 65536 if mode == "bounded" else (8192 if mode == "rtk" else 4096)
            if max_bytes is not None:
                size = min(size, max_bytes - len(raw) + 1)
            extra = _read_stdin_chunk(fd, size, 0, eof_ready=mode != "codex")
            if not extra:
                break
            raw.extend(extra)
            if max_bytes is not None and len(raw) > max_bytes:
                if mode == "bounded":
                    raise InputLimitError("raw_input_bytes", max_bytes, len(raw), "bytes")
                raise ValueError("Hook input exceeds the maximum size")
            if mode == "bounded":
                if extra.strip(b" \t\r\n"):
                    raise ValueError("Invalid hook input: trailing data")
            elif mode == "rtk":
                try:
                    text += decoder.decode(extra, final=False)
                except UnicodeDecodeError as exc:
                    raise ValueError("Invalid hook input: expected UTF-8 JSON") from exc
        if mode != "bounded":
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError("Invalid hook input: expected UTF-8 JSON") from exc
            if mode == "codex":
                payload, end = parser.raw_decode(text, start)
            if text[end:].strip():
                raise ValueError("Invalid hook input: trailing data")
        return bytes(raw), payload


def _read_json_input_text(*, max_bytes: int = INPUT_MAX_BYTES, max_markers: int | None = None) -> str:
    raw, _ = collect_event_input("bounded", max_bytes=max_bytes, max_markers=max_markers)
    return raw.decode("utf-8")

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
