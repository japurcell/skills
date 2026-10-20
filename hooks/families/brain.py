"""Generate standalone brain hooks; sharing occurs only at build time."""
from __future__ import annotations

from hooks.families.common import INPUT_READER, STANDARD_IMPORTS


RUNTIME = r'''
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
'''


def render(provider, target):
    return ("#!/usr/bin/env python3\n"
            "# Generated from hooks/families/brain.py by scripts/generate-hooks.py. Do not edit.\n"
            + STANDARD_IMPORTS + INPUT_READER
            + "INJECT = " + repr(target.output_path.name == "inject-brain.py") + "\n"
            + RUNTIME)
