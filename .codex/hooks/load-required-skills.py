#!/usr/bin/env python3

from __future__ import annotations

import json
import os
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


def input_is_ready(file_descriptor: int, timeout: float = 0) -> bool:
    if os.name != "nt":
        return bool(select.select([file_descriptor], [], [], timeout)[0])

    import ctypes
    import msvcrt

    deadline = time.monotonic() + timeout
    handle = msvcrt.get_osfhandle(file_descriptor)
    while True:
        available = ctypes.c_ulong(0)
        if ctypes.windll.kernel32.PeekNamedPipe(
            handle, None, 0, None, ctypes.byref(available), None
        ) and available.value:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.01)


def read_json_input() -> object:
    decoder = json.JSONDecoder()
    file_descriptor = sys.stdin.buffer.fileno()
    raw = bytearray()
    while True:
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("Hook input exceeds the maximum size")
        if not input_is_ready(file_descriptor, INPUT_COMPLETION_IDLE_SECONDS):
            raise ValueError("Invalid hook input: malformed or incomplete JSON")
        chunk = os.read(file_descriptor, 4096)
        if not chunk:
            raise ValueError("Invalid hook input: incomplete JSON")
        raw.extend(chunk)
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("Hook input exceeds the maximum size")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            if exc.reason == "unexpected end of data":
                continue
            raise ValueError("Invalid hook input: expected UTF-8 JSON") from exc

        start = len(text) - len(text.lstrip())
        try:
            payload, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError as exc:
            if not input_is_ready(file_descriptor, INPUT_COMPLETION_IDLE_SECONDS):
                raise ValueError("Invalid hook input: malformed or incomplete JSON") from exc
            continue

        while input_is_ready(file_descriptor):
            extra = os.read(file_descriptor, 4096)
            if not extra:
                break
            raw.extend(extra)
            if len(raw) > MAX_INPUT_BYTES:
                raise ValueError("Hook input exceeds the maximum size")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Invalid hook input: expected UTF-8 JSON") from exc
        payload, end = decoder.raw_decode(text, start)
        if text[end:].strip():
            raise ValueError("Invalid hook input: trailing data")
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
    emit_json({"continue": False, "stopReason": safe_reason, "systemMessage": "Required skill context was NOT loaded."})
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
            "systemMessage": f"Required skill context loaded from {len(loaded_paths)} file(s).",
            "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context},
        })
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return failure(str(exc), event, source, session_id)
    except Exception as exc:  # noqa: BLE001 - a hook must return a parseable decision.
        return failure(f"Unexpected required-skill hook error: {exc}", event, source, session_id)


if __name__ == "__main__":
    raise SystemExit(main())
