#!/usr/bin/env python3
# Generated from hooks/families/brain.py by scripts/generate-hooks.py. Do not edit.
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
            raise ValueError("Invalid hook input: raw byte limit exceeded")
        chunks.append(chunk)
    return b"".join(chunks)


def _read_json_input_text() -> str:
    try:
        stdin_fd = sys.stdin.fileno()
    except (AttributeError, OSError):
        # Runtime hooks require descriptor readiness to bound blocking reads.
        raise ValueError("Invalid hook input: stdin readiness unavailable") from None

    deadline = time.monotonic() + INPUT_COMPLETION_TOTAL_SECONDS
    chunks: list[bytes] = []
    total = 0
    stack: list[int] = []
    started = False
    in_string = False
    escaped = False
    complete = False

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("Invalid hook input: input deadline exceeded")
        chunk = _read_stdin_chunk(stdin_fd, min(65536, INPUT_MAX_BYTES - total + 1),
                                  min(INPUT_COMPLETION_IDLE_SECONDS, remaining))
        if chunk is None:
            raise ValueError("Invalid hook input: malformed or incomplete JSON")
        if not chunk:
            return b"".join(chunks).decode("utf-8")
        total += len(chunk)
        if total > INPUT_MAX_BYTES:
            raise ValueError("Invalid hook input: raw byte limit exceeded")
        chunks.append(chunk)

        # Scan structural markers once in C, skipping ordinary UTF-8 bytes.
        # json.loads remains the full syntax authority after bounded collection.
        cursor = 0
        for match in re.finditer(rb'["\\\[\]{}]', chunk):
            position = match.start()
            byte = chunk[position]
            if not started:
                if byte != 123 or chunk[cursor:position].strip(b" \t\r\n"):
                    raise ValueError("Invalid hook input: expected a JSON object")
                started = True
            if in_string:
                if escaped and position == cursor:
                    escaped = False
                else:
                    # Ordinary bytes between markers already consumed an escape.
                    escaped = byte == 92
                    if byte == 34:
                        in_string = False
            elif byte == 34:
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
            cursor = position + 1
        if not started and chunk[cursor:].strip(b" \t\r\n"):
            raise ValueError("Invalid hook input: expected a JSON object")
        if escaped and cursor < len(chunk):
            # Only a terminal backslash carries its escape into the next chunk.
            escaped = False

        if time.monotonic() >= deadline:
            raise ValueError("Invalid hook input: input deadline exceeded")
        if complete:
            trailing = _read_available_stdin_bytes(stdin_fd, INPUT_MAX_BYTES - total, deadline)
            if trailing.strip(b" \t\r\n"):
                raise ValueError("Invalid hook input: trailing data")
            chunks.append(trailing)
            return b"".join(chunks).decode("utf-8")

INJECT = False

import argparse
import stat
import tempfile
from contextlib import contextmanager
from urllib.parse import quote


class BrainError(ValueError):
    """A bounded diagnostic containing no untrusted file or payload content."""


def linked(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def regular(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    if linked(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise BrainError("unsafe index destination")
    return True


def vault_for(payload):
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        return None
    current = Path(cwd).resolve(strict=True)
    if not current.is_dir():
        return None
    for directory in (current, *current.parents):
        vault = directory / "brain"
        if vault.is_dir() and not linked(vault.lstat()):
            return vault
        if (directory / ".git").exists():
            return None
    return None


@contextmanager
def writer_lock(vault):
    path = vault / ".brain-index.lock"
    regular(path)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    locked = False
    try:
        info = os.fstat(descriptor)
        if linked(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise BrainError("unsafe lock")
        if info.st_size == 0:
            os.write(descriptor, b"0")
        os.lseek(descriptor, 0, os.SEEK_SET)
        deadline = time.monotonic() + 0.3
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise BrainError("index writer busy") from None
                time.sleep(0.01)
        yield
    finally:
        if locked:
            if os.name == "nt":
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def inventory(vault):
    deadline = time.monotonic() + 2
    groups = {}
    pending = [vault]
    paths = []
    count = 0
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                count += 1
                if count > 20000 or time.monotonic() > deadline:
                    raise BrainError("inventory budget exceeded")
                info = entry.stat(follow_symlinks=False)
                if linked(info):
                    continue
                if stat.S_ISDIR(info.st_mode):
                    pending.append(Path(entry.path))
                elif stat.S_ISREG(info.st_mode) and entry.name.lower().endswith(".md"):
                    paths.append(Path(entry.path))
    for path in sorted(paths):
        relative = path.relative_to(vault)
        if relative.as_posix() == "index.md":
            continue
        groups.setdefault(relative.parent.as_posix(), []).append(relative.as_posix())
    lines = ["# Brain"]
    for group, notes in sorted(groups.items()):
        lines.extend(["", "## " + ("Root" if group == "." else group), ""])
        for note in notes:
            stem = note[:-3]
            if any(character in stem for character in "[]#|^\\\r\n"):
                label = re.sub(r"([\\\[\]])", r"\\\1", stem).replace("\n", " ").replace("\r", " ")
                lines.append("- [" + label + "](<" + quote(note, safe="/") + ">)")
            else:
                lines.append("- [[" + stem + "]]")
    content = ("\n".join(lines) + "\n").encode("utf-8")
    if len(content) > 512 * 1024 or time.monotonic() > deadline:
        raise BrainError("inventory budget exceeded")
    index = vault / "index.md"
    exists = regular(index)
    previous = None
    if exists:
        with index.open("rb") as stream:
            previous = stream.read(512 * 1024 + 1)
        if len(previous) > 512 * 1024:
            raise BrainError("existing index too large")
    if previous != content:
        descriptor, name = tempfile.mkstemp(prefix=".brain-index-", dir=vault)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            regular(index)
            os.replace(name, index)
        finally:
            Path(name).unlink(missing_ok=True)
    return content


def main():
    if sys.version_info < (3, 12):
        print("brain: Python 3.12 or newer is required", file=sys.stderr)
        sys.stdout.buffer.write(b"{}\n")
        return 0
    parser = argparse.ArgumentParser(description="Maintain the brain Markdown inventory.")
    parser.add_argument("--provider", choices=("copilot", "codex", "gemini"), required=True)
    arguments = parser.parse_args()
    result = {}
    try:
        payload = json.loads(_read_json_input_text())
        if not isinstance(payload, dict):
            raise ValueError("expected object")
        event = payload.get("hook_event_name", payload.get("hookEventName"))
        source = payload.get("source")
        allowed_sources = {"startup", "resume", "new"} if arguments.provider == "copilot" else {"startup", "resume", "clear"}
        if arguments.provider == "codex":
            allowed_sources |= {"compact", "fork"}
        admitted = not INJECT or (event in (None, "SessionStart", "sessionStart")
                                  and isinstance(source, str) and source in allowed_sources)
        if not INJECT:
            if arguments.provider == "codex":
                admitted = event in (None, "PostToolUse")
            elif arguments.provider == "copilot":
                response = payload.get("toolResult", payload.get("tool_result"))
                admitted = (event in (None, "postToolUse", "PostToolUse")
                            and isinstance(response, dict)
                            and response.get("resultType", response.get("result_type")) == "success")
            else:
                response = payload.get("tool_response")
                admitted = (event in (None, "AfterTool") and isinstance(response, dict)
                            and not response.get("error"))
        vault = vault_for(payload) if admitted else None
        if vault is not None:
            with writer_lock(vault):
                content = inventory(vault).decode("utf-8")
            if INJECT:
                if len(content.encode("utf-8")) > 24000:
                    content = "Brain index is too large for startup context. Read brain/index.md to find relevant notes.\n"
                if arguments.provider == "copilot":
                    result = {"additionalContext": content}
                else:
                    specific = {"additionalContext": content}
                    if arguments.provider == "codex":
                        specific["hookEventName"] = "SessionStart"
                    result = {"hookSpecificOutput": specific}
                if event is not None:
                    message = "inject-brain: pass; index loaded"
                    if arguments.provider == "copilot":
                        sys.stdout.buffer.write((json.dumps({"type": "progress", "message": message}) + "\n").encode("utf-8"))
                    else:
                        result["systemMessage"] = message
    except BrainError as error:
        print("brain: " + str(error) + "; previous index preserved", file=sys.stderr)
    except (OSError, ValueError):
        print("brain: invalid input or inaccessible vault; previous index preserved", file=sys.stderr)
    sys.stdout.buffer.write((json.dumps(result, ensure_ascii=False) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
