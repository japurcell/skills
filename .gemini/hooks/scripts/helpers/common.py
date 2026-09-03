from __future__ import annotations

import codecs
import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Sequence


def _read_available_stdin_bytes(stdin_fd: int) -> bytes:
    if os.name == "nt":
        import ctypes
        import msvcrt

        chunks: list[bytes] = []
        pipe_handle = ctypes.c_void_p(msvcrt.get_osfhandle(stdin_fd))
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        while True:
            available = ctypes.c_ulong()
            if not kernel32.PeekNamedPipe(
                pipe_handle,
                None,
                0,
                None,
                ctypes.byref(available),
                None,
            ):
                return b""
            if available.value == 0:
                return b"".join(chunks)
            chunks.append(os.read(stdin_fd, min(available.value, 65536)))

    try:
        was_blocking = os.get_blocking(stdin_fd)
        os.set_blocking(stdin_fd, False)
    except OSError:
        return b""

    chunks = []
    try:
        while True:
            chunk = os.read(stdin_fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
    except BlockingIOError:
        pass
    finally:
        os.set_blocking(stdin_fd, was_blocking)
    return b"".join(chunks)


def _read_json_input_text() -> str:
    try:
        stdin_fd = sys.stdin.fileno()
    except (AttributeError, OSError):
        return sys.stdin.read()

    decoder = codecs.getincrementaldecoder("utf-8")()
    json_decoder = json.JSONDecoder()
    raw_input = ""

    while True:
        chunk = os.read(stdin_fd, 65536)
        if not chunk:
            return raw_input + decoder.decode(b"", final=True)

        raw_input += decoder.decode(chunk)
        try:
            start_index = len(raw_input) - len(raw_input.lstrip())
            json_decoder.raw_decode(raw_input, start_index)
        except json.JSONDecodeError:
            continue

        raw_input += decoder.decode(_read_available_stdin_bytes(stdin_fd))
        return raw_input + decoder.decode(b"", final=True)


def read_json_input() -> dict:
    try:
        payload = json.loads(_read_json_input_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
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
    import os
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
        elif os.path.exists(f"/{drive}"):
            return f"/{drive}{rest}"
        else:
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


def run_gemini_passive_log_hook(script_name: str, build_log_message_func) -> int:
    from .audit import audit_init, audit_log_passive_event

    def noop() -> None:
        emit_json({})
        raise SystemExit(0)

    try:
        input_payload = read_json_input()

        if not isinstance(input_payload, dict):
            noop()

        if not audit_init():
            noop()

        log_string = build_log_message_func(input_payload)

        if log_string and not audit_log_passive_event(script_name, log_string):
            noop()

        noop()
    except ValueError as exc:
        noop()
    except Exception as exc:  # noqa: BLE001
        noop()
    return 0
