"""Generate standalone brain hooks; sharing occurs only at build time."""
from __future__ import annotations

from hooks.families.common import INPUT_READER, STANDARD_IMPORTS


RUNTIME = r'''
import argparse
import stat
import secrets
from contextlib import contextmanager, ExitStack
from urllib.parse import quote


class BrainError(ValueError):
    """A bounded diagnostic containing no untrusted file or payload content."""


def linked(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def windows_handle(path, access, sharing, creation, directory=False):
    """Open the entry itself; directory handles deny rename and reparse edits."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                   wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.GetFileInformationByHandleEx.argtypes = (wintypes.HANDLE, ctypes.c_int,
                                                   wintypes.LPVOID, wintypes.DWORD)
    kernel.GetFileInformationByHandleEx.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    # OPEN_REPARSE_POINT inspects the entry rather than its target.
    flags = 0x00200000 | (0x02000000 if directory else 0)
    handle = kernel.CreateFileW(str(path), access, sharing, None, creation, flags, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        attributes = (wintypes.DWORD * 2)()  # FILE_ATTRIBUTE_TAG_INFO, class 9
        if not kernel.GetFileInformationByHandleEx(handle, 9, attributes, ctypes.sizeof(attributes)):
            raise ctypes.WinError(ctypes.get_last_error())
        if attributes[0] & 0x400 or bool(attributes[0] & 0x10) != directory:
            raise BrainError("unsafe filesystem entry")
    except BaseException:
        kernel.CloseHandle(handle)
        raise
    return handle, kernel.CloseHandle


class Directory:
    """Pin a directory for descriptor-relative POSIX or replacement-denying Windows access."""

    def __init__(self, path, expected=None, parent=None):
        self.path = path
        self.stack = ExitStack()
        try:
            if os.name == "nt":
                paths = [path] if parent else [*reversed(path.parents), path]
                for item in paths:
                    # READ sharing only: other writers cannot rename or turn
                    # this directory into a junction while the handle is open.
                    handle, close = windows_handle(item, 0, 1, 3, directory=True)
                    self.stack.callback(close, handle)
                self.fd = None
                info = path.lstat()
            else:
                flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                if parent:
                    self.fd = os.open(path.name, flags, dir_fd=parent.fd)
                else:
                    descriptor = os.open(path.anchor, flags)
                    try:
                        for part in path.parts[1:]:
                            child = os.open(part, flags, dir_fd=descriptor)
                            os.close(descriptor)
                            descriptor = child
                        self.fd = descriptor
                    except BaseException:
                        os.close(descriptor)
                        raise
                self.stack.callback(os.close, self.fd)
                info = os.fstat(self.fd)
            if linked(info) or not stat.S_ISDIR(info.st_mode):
                raise BrainError("unsafe directory")
            if expected is not None and not os.path.samestat(expected, info):
                raise BrainError("directory changed")
        except BaseException:
            self.stack.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        return self.stack.__exit__(*exception)

    def stat(self, name):
        return (self.path / name).lstat() if self.fd is None else os.stat(name, dir_fd=self.fd, follow_symlinks=False)

    def regular(self, name):
        try:
            info = self.stat(name)
        except FileNotFoundError:
            return False
        if linked(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise BrainError("unsafe index destination")
        return True

    def open_file(self, name, flags):
        if self.fd is None:
            import msvcrt
            access = 0x80000000 | (0x40000000 if flags & os.O_RDWR or flags & os.O_WRONLY else 0)
            creation = 1 if flags & os.O_EXCL else 4 if flags & os.O_CREAT else 3
            handle, close = windows_handle(self.path / name, access, 3, creation)
            try:
                descriptor = msvcrt.open_osfhandle(handle, flags & (os.O_RDONLY | os.O_RDWR | os.O_WRONLY) | os.O_BINARY)
            except BaseException:
                close(handle)
                raise
        else:
            descriptor = os.open(name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=self.fd)
        info = os.fstat(descriptor)
        if linked(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            os.close(descriptor)
            raise BrainError("unsafe file")
        return descriptor

    def replace(self, source, destination):
        if self.fd is None:
            os.replace(self.path / source, self.path / destination)
        else:
            os.replace(source, destination, src_dir_fd=self.fd, dst_dir_fd=self.fd)

    def unlink(self, name):
        try:
            if self.fd is None:
                (self.path / name).unlink()
            else:
                os.unlink(name, dir_fd=self.fd)
        except FileNotFoundError:
            pass


def vault_for(payload):
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        return None
    current = Path(cwd).resolve(strict=True)
    if not current.is_dir():
        return None
    for directory in (current, *current.parents):
        vault = directory / "brain"
        try:
            info = vault.lstat()
        except FileNotFoundError:
            info = None
        if info is not None and stat.S_ISDIR(info.st_mode) and not linked(info):
            return vault, info
        if (directory / ".git").exists():
            return None
    return None


@contextmanager
def writer_lock(vault):
    vault.regular(".brain-index.lock")
    descriptor = vault.open_file(".brain-index.lock", os.O_CREAT | os.O_RDWR)
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
    pending = [((), ())]
    paths = []
    count = 0
    while pending:
        if time.monotonic() > deadline:
            raise BrainError("inventory budget exceeded")
        parts, identities = pending.pop()
        with ExitStack() as stack:
            directory = vault
            for part, identity in zip(parts, identities):
                if time.monotonic() > deadline:
                    raise BrainError("inventory budget exceeded")
                directory = stack.enter_context(Directory(directory.path / part, identity, directory))
            with os.scandir(directory.fd if directory.fd is not None else directory.path) as entries:
                for entry in entries:
                    count += 1
                    if count > 20000 or time.monotonic() > deadline:
                        raise BrainError("inventory budget exceeded")
                    info = entry.stat(follow_symlinks=False)
                    if linked(info):
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        pending.append(((*parts, entry.name), (*identities, info)))
                    elif stat.S_ISREG(info.st_mode) and entry.name.lower().endswith(".md"):
                        paths.append(Path(*parts, entry.name))
    for relative in sorted(paths):
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
    exists = vault.regular("index.md")
    previous = None
    if exists:
        with os.fdopen(vault.open_file("index.md", os.O_RDONLY), "rb") as stream:
            previous = stream.read(512 * 1024 + 1)
        if len(previous) > 512 * 1024:
            raise BrainError("existing index too large")
    if previous != content:
        name = ".brain-index-" + secrets.token_hex(12)
        descriptor = vault.open_file(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            vault.regular("index.md")
            vault.replace(name, "index.md")
        finally:
            vault.unlink(name)
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
            with Directory(*vault) as directory, writer_lock(directory):
                content = inventory(directory).decode("utf-8")
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
