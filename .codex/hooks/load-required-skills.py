#!/usr/bin/env python3
# Generated from hooks/families/required_skills.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations

import json
import os
import re
import select
import stat
import sys
import time
from pathlib import Path, PureWindowsPath


required_skill_files = ["caveman/SKILL.md"]
max_context_bytes = 20_000
MAX_INPUT_BYTES = 1_000_000
MAX_SKILL_FILE_BYTES = 1_000_000
INPUT_COMPLETION_IDLE_SECONDS = 0.5
SUPPORTED_SOURCES = {"startup", "resume", "clear", "compact"}


def emit_json(payload: dict) -> None:
    sys.stdout.buffer.write(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
    )
    sys.stdout.buffer.flush()


def sanitize(value: object) -> str:
    safe = str(value).encode("utf-8", errors="replace").decode("utf-8")
    return safe.replace("\n", " ").replace("\r", " ").replace("\x00", " ")[:200]


def is_link_or_reparse_point(path: Path) -> bool:
    try:
        path_stat = os.lstat(path)
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(path_stat.st_mode):
        return True
    is_junction = getattr(path, "is_junction", None)
    if is_junction is not None and is_junction():
        return True
    file_attributes = getattr(path_stat, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and file_attributes & reparse_flag)


def audit(event: str, source: str, session_id: str, detail: str) -> None:
    directory_descriptor = -1
    try:
        audit_dir = Path.home() / ".codex" / "hooks" / "logs"
        audit_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
        if is_link_or_reparse_point(audit_dir):
            raise OSError("audit directory must not be a link or reparse point")
        audit_path = audit_dir / "audit.log"
        if is_link_or_reparse_point(audit_path):
            raise OSError("audit file must not be a link or reparse point")

        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW

        if os.name != "nt" and hasattr(os, "O_DIRECTORY") and hasattr(os, "O_NOFOLLOW"):
            directory_descriptor = os.open(
                audit_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            )
            os.fchmod(directory_descriptor, 0o700)
            descriptor = os.open("audit.log", flags, 0o600, dir_fd=directory_descriptor)
        else:
            os.chmod(audit_dir, 0o700)
            descriptor = os.open(audit_path, flags, 0o600)
        try:
            if hasattr(os, "fchmod"):
                os.fchmod(descriptor, 0o600)
            line = (
                f"event={sanitize(event)} source={sanitize(source)} "
                f"session={sanitize(session_id)} detail={sanitize(detail)}\n"
            )
            os.write(descriptor, line.encode("utf-8"))
        finally:
            os.close(descriptor)
    except OSError as exc:
        print(f"Warning: required-skill audit unavailable: {sanitize(exc)}", file=sys.stderr)
    finally:
        if directory_descriptor != -1:
            os.close(directory_descriptor)


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

def read_json_input() -> object:
    _, payload = collect_event_input("codex", max_bytes=MAX_INPUT_BYTES)
    return payload


def strip_yaml_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0] == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line == "---":
                return "\n".join(lines[index + 1:]).strip()
    return text.strip()


def resolve_skill_path(skill_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute() or PureWindowsPath(raw_path).is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Required skill path is not a safe relative path: {raw_path}")
    resolved_root = skill_root.resolve()
    resolved_skill = (resolved_root / candidate).resolve()
    try:
        resolved_skill.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Required skill path escapes the skills directory: {raw_path}") from exc
    return resolved_skill


def load_context(skill_root: Path) -> tuple[str, list[str]]:
    context_parts: list[str] = []
    loaded_paths: list[str] = []
    for raw_path in required_skill_files:
        if not isinstance(raw_path, str):
            raise ValueError("Required skill path must be text")
        skill_path = resolve_skill_path(skill_root, raw_path)
        if not skill_path.exists() or not skill_path.is_file():
            raise ValueError(f"Required skill file not found: {raw_path}")
        if not stat.S_IMODE(skill_path.stat().st_mode) & 0o444:
            raise ValueError(f"Required skill file not readable: {raw_path}")
        try:
            with skill_path.open("rb") as handle:
                raw_content = handle.read(MAX_SKILL_FILE_BYTES + 1)
            if len(raw_content) > MAX_SKILL_FILE_BYTES:
                raise ValueError(f"Required skill file exceeds the maximum size: {raw_path}")
            body = strip_yaml_frontmatter(raw_content.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ValueError(f"Required skill file is not valid UTF-8: {raw_path}") from exc
        except OSError as exc:
            raise ValueError(f"Failed to read required skill file: {raw_path}") from exc
        context_parts.append(f"BEGIN REQUIRED SKILL: {raw_path}\n{body}\nEND REQUIRED SKILL: {raw_path}")
        loaded_paths.append(raw_path)

    context = "Required skill context loaded.\n\n" + "\n\n".join(context_parts)
    if len(context.encode("utf-8")) > max_context_bytes:
        raise ValueError("Required skill context exceeds the maximum size")
    return context, loaded_paths


def failure(reason: str, event: str, source: str, session_id: str) -> int:
    safe_reason = sanitize(reason) or "Required skill hook failed"
    audit(event, source, session_id, f"failure:{safe_reason}")
    emit_json({"continue": False, "stopReason": f"load-required-skills: blocked; {safe_reason}"})
    return 0


def main() -> int:
    event = ""
    source = ""
    session_id = ""
    try:
        payload = read_json_input()
        if not isinstance(payload, dict):
            raise ValueError("Invalid hook input: expected a JSON object")
        event = str(payload.get("hook_event_name", ""))
        source = str(payload.get("source", ""))
        session_id = str(payload.get("session_id", payload.get("sessionId", "")))
        if event != "SessionStart":
            raise ValueError(f"Unsupported hook event: {event or '(missing)'}")
        if source not in SUPPORTED_SOURCES:
            raise ValueError(f"Unsupported SessionStart source: {source or '(missing)'}")

        context, loaded_paths = load_context(Path.home() / ".agents" / "skills")
        for loaded_path in loaded_paths:
            audit(event, source, session_id, f"loaded:{loaded_path}")
        emit_json({
            "systemMessage": f"load-required-skills: pass; {len(loaded_paths)} skill {'file' if len(loaded_paths) == 1 else 'files'}",
            "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context},
        })
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return failure(str(exc), event, source, session_id)
    except Exception as exc:  # noqa: BLE001 - a hook must return a parseable decision.
        return failure(f"Unexpected required-skill hook error: {exc}", event, source, session_id)


if __name__ == "__main__":
    raise SystemExit(main())
