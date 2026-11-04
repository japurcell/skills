#!/usr/bin/env python3
# Generated from hooks/families/common.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations

import json
import os
import re
import sys
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn, Sequence

if TYPE_CHECKING:
    import subprocess


INPUT_COMPLETION_IDLE_SECONDS = 0.5
INPUT_COMPLETION_TOTAL_SECONDS = 2.0
# Six-byte JSON escapes for 256 KiB of native data, plus 512 KiB of metadata.
INPUT_MAX_BYTES = 2 * 1024 * 1024
INPUT_MAX_DEPTH = 64


def _stdin_is_ready(stdin_fd: int, timeout: float = 0) -> bool:
    if os.name != "nt":
        import select

        return bool(select.select([stdin_fd], [], [], timeout)[0])

    import ctypes
    import msvcrt

    deadline = time.monotonic() + timeout
    pipe_handle = ctypes.c_void_p(msvcrt.get_osfhandle(stdin_fd))
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    while True:
        available = ctypes.c_ulong()
        if kernel32.PeekNamedPipe(
            pipe_handle, None, 0, None, ctypes.byref(available), None,
        ):
            if available.value:
                return True
        else:
            error = ctypes.get_last_error()
            # A broken pipe is readable EOF; regular-file stdin needs no wait.
            if error == 109 or kernel32.GetFileType(pipe_handle) == 1:
                return True
            raise OSError(error, "Hook stdin readiness failed")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(0.01, remaining))


class InputLimitError(ValueError):
    def __init__(self, rule_id: str, limit: int, measured: int, unit: str):
        self.rule_id, self.limit, self.measured, self.unit = rule_id, limit, measured, unit
        super().__init__(rule_id)


def _read_stdin_chunk(stdin_fd: int, max_bytes: int, timeout: float) -> bytes | None:
    if os.name == "nt":
        # Pre-3.12 Windows pipes require PeekNamedPipe, not POSIX flags.
        return os.read(stdin_fd, max_bytes) if _stdin_is_ready(stdin_fd, timeout) else None

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


def _read_available_stdin_bytes(
    stdin_fd: int,
    max_bytes: int = INPUT_MAX_BYTES,
    deadline: float | None = None,
    *, initial_bytes: int = 0,
) -> bytes:
    if deadline is None:
        deadline = time.monotonic() + INPUT_COMPLETION_TOTAL_SECONDS
    chunks: list[bytes] = []
    total = 0
    while True:
        if time.monotonic() >= deadline:
            raise ValueError("Invalid hook input: input deadline exceeded")
        chunk = _read_stdin_chunk(stdin_fd, min(65536, max_bytes - total + 1), 0)
        if chunk is None:
            break
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise InputLimitError("raw_input_bytes", max_bytes + initial_bytes, total + initial_bytes, "bytes")
        chunks.append(chunk)
    return b"".join(chunks)


def _read_json_input_text(*, max_bytes: int = INPUT_MAX_BYTES, max_markers: int | None = None) -> str:
    try:
        stdin_fd = sys.stdin.fileno()
    except (AttributeError, OSError):
        # Runtime hooks require descriptor readiness to bound blocking reads.
        raise ValueError("Invalid hook input: stdin readiness unavailable") from None

    deadline = time.monotonic() + INPUT_COMPLETION_TOTAL_SECONDS
    chunks: list[bytes] = []
    total = markers = 0
    stack: list[int] = []
    started = False
    in_string = False
    escaped = False
    complete = False

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("Invalid hook input: input deadline exceeded")
        chunk = _read_stdin_chunk(stdin_fd, min(65536, max_bytes - total + 1),
                                  min(INPUT_COMPLETION_IDLE_SECONDS, remaining))
        if chunk is None:
            raise ValueError("Invalid hook input: malformed or incomplete JSON")
        if not chunk:
            return b"".join(chunks).decode("utf-8")
        total += len(chunk)
        if total > max_bytes:
            raise InputLimitError("raw_input_bytes", max_bytes, total, "bytes")
        chunks.append(chunk)

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

        if time.monotonic() >= deadline:
            raise ValueError("Invalid hook input: input deadline exceeded")
        if complete:
            trailing = _read_available_stdin_bytes(stdin_fd, max_bytes - total, deadline, initial_bytes=total)
            if trailing.strip(b" \t\r\n"):
                raise ValueError("Invalid hook input: trailing data")
            chunks.append(trailing)
            return b"".join(chunks).decode("utf-8")


def read_json_input(*, max_bytes: int = INPUT_MAX_BYTES, max_markers: int | None = None) -> dict:
    try:
        payload = json.loads(_read_json_input_text(max_bytes=max_bytes, max_markers=max_markers))
    except InputLimitError:
        raise
    except (ValueError, OSError) as exc:
        raise ValueError("Invalid hook input: expected a JSON object") from exc

    if not isinstance(payload, dict):
        raise ValueError("Invalid hook input: expected a JSON object")

    try:
        from .observability import begin_hook_capture

        begin_hook_capture(payload)
    except Exception:
        pass

    return payload


def emit_json(payload: dict) -> None:
    try:
        sys.stdout.buffer.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()
    except Exception:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        sys.stdout.write("\n")
        sys.stdout.flush()

    try:
        from .observability import complete_hook_capture

        complete_hook_capture(payload)
    except Exception:
        pass


def sanitize_log_field(value: object) -> str:
    return str(value or "").translate({ord("\r"): " ", ord("\n"): " ", ord("\t"): " "})


def first_present(payload: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return ""


def nested_present(payload: Mapping[str, Any], *keys: str) -> Any:
    current: Any = payload

    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return ""
        current = current[key]

    return current if current is not None else ""


def convert_windows_path_to_posix(path_str: str) -> str:
    if not path_str:
        return ""
    if os.name == "nt":
        return path_str.replace("/", "\\")

    if len(path_str) >= 2 and path_str[1] == ":" and path_str[0].isalpha():
        drive = path_str[0].lower()
        rest = path_str[2:].replace("\\", "/")
        if not rest.startswith("/"):
            rest = "/" + rest

        if os.path.exists(f"/mnt/{drive}"):
            return f"/mnt/{drive}{rest}"
        if os.path.exists(f"/{drive}"):
            return f"/{drive}{rest}"
        return f"/mnt/{drive}{rest}"

    if "\\" in path_str:
        return path_str.replace("\\", "/")

    return path_str


def stringify_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, (dict, list, bool, int, float)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def trim_ws(value: str) -> str:
    return value.strip()


def resolve_skill_file_path(skill_file: str, skills_dir: str, home: str | None) -> str:
    if not skill_file:
        raise ValueError("Skill file path is empty")

    normalized = skill_file
    if os.name != "nt" and len(skill_file) >= 2 and skill_file[1] == ":" and skill_file[0].isalpha():
        normalized = convert_windows_path_to_posix(skill_file)

    if normalized.startswith("~/"):
        if not home:
            raise ValueError("Cannot expand ~/: HOME is not set")
        return str(Path(home, normalized[2:]))

    path = Path(normalized)
    if not path.is_absolute():
        return str(Path(skills_dir, path))

    return str(path)


def merge_env_skill_files(raw: str | None, skills_dir: str, home: str | None) -> list[str]:
    if not raw:
        return []

    import os
    import re

    if os.name == "nt":
        parts = re.split(r"[\r\n,;]", raw)
    else:
        parts = re.split(r"[\r\n,;]|(?<!\b[a-zA-Z]):", raw)

    resolved: list[str] = []

    for part in parts:
        item = trim_ws(part)
        if not item:
            continue

        resolved_path = resolve_skill_file_path(item, skills_dir, home)
        if resolved_path not in resolved:
            resolved.append(resolved_path)

    return resolved


def strip_yaml_frontmatter(text: str) -> str:
    lines = text.splitlines()
    body: list[str] = []
    in_header = False
    first_line = True

    for line in lines:
        if first_line:
            first_line = False
            if line == "---":
                in_header = True
                continue

        if in_header:
            if line == "---":
                in_header = False
            continue

        body.append(line)

    return "\n".join(body)


def parse_skill_context(skill_file: Path) -> str:
    return strip_yaml_frontmatter(skill_file.read_text(encoding="utf-8"))


def load_required_skill_context(raw_skill_file: str, fail: Callable[[str], NoReturn]) -> str:
    # Leave failure decisions and audit requirements to the provider.
    skill_path = Path(raw_skill_file)
    if not skill_path.exists() or not skill_path.is_file():
        fail(f"Required skill file not found: {raw_skill_file}")
    if not os.access(skill_path, os.R_OK):
        fail(f"Required skill file not readable: {raw_skill_file}")
    try:
        skill_context = parse_skill_context(skill_path)
    except OSError as exc:
        fail(f"Failed to read skill file: {raw_skill_file} ({exc})")
    return (f"<!-- BEGIN REQUIRED SKILL: {raw_skill_file} -->\n"
            f"{skill_context}\n"
            f"<!-- END REQUIRED SKILL: {raw_skill_file} -->")


def repository_root_from_payload(payload: dict[str, object], override_environment: str) -> Path:
    override = os.environ.get(override_environment)
    if override:
        return Path(override)
    cwd = stringify_value(first_present(payload, "cwd", "workingDirectory", "working_directory"))
    return Path(convert_windows_path_to_posix(cwd)) if cwd else Path.cwd()


def run_command(
    args: Sequence[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    check: bool = False,
    capture_output: bool = False,
    text: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    if isinstance(args, (str, bytes)):
        raise TypeError("run_command requires a sequence of arguments; shell execution is disabled")

    import subprocess

    return subprocess.run(
        list(args),
        cwd=cwd,
        env=env,
        check=check,
        capture_output=capture_output,
        text=text,
        timeout=timeout,
        shell=False,
    )


def run_passive_log_hook(script_name: str, build_log_message_func) -> int:
    from .audit import audit_log_event

    def log_event(message: str) -> None:
        try:
            audit_log_event(script_name, message)
        except Exception:
            pass

    def fail_safe(reason: str) -> None:
        safe_reason = sanitize_log_field(reason).strip() or "Hook failed"
        log_event(f"Error: {safe_reason}")
        emit_json({})

    try:
        payload = read_json_input()
        log_message = build_log_message_func(payload)
        if log_message:
            log_event(log_message)
        emit_json({})
        return 0
    except ValueError as exc:
        fail_safe(str(exc))
    except Exception as exc:  # noqa: BLE001
        fail_safe(f"Unexpected exception: {exc}")
    return 0
