#!/usr/bin/env python3
"""Authenticate a selected factory release before executing selected JavaScript.

Python 3.11+ standard library only. `verify` creates no installation state.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import errno
import hashlib
import json
import lzma
import os
from pathlib import Path
import re
import signal
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import uuid
import zipfile


MIB = 1024 * 1024
NODE = {
    "darwin-arm64": ("https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz", "654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628"),
    "linux-x64": ("https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz", "6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6"),
    "win32-x64": ("https://nodejs.org/download/release/v24.22.1/node-v24.22.1-win-x64.zip", "d2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5"),
}
WINDOWS_HELPER_SHA = "f46ba4a408f8618d5e186ce29cf47bdac3411b67356136d79da4a0ed0c35ec44"
LOCK_SHA = "bea7cfb5a835aba203893966dde3e964418b12c69f8680e53a65b3603b9467d6"
MODULES = (
    "accounting", "adapters/codex", "adapters/copilot", "adapters/fake", "adapters/types",
    "agents", "build", "capture", "clearance", "cli", "dashboard", "execution-control", "installation-bindings", "installed-bindings",
    "install", "install-candidate", "install-entry", "install-publication", "install-publication-state", "learning", "lifecycle", "maintenance", "maintenance-entry", "native/notification-transport", "native/notifications",
    "native/process", "notifications", "placement", "profiles", "redaction", "release", "schema", "store",
    "workflow", "workspace",
)
WEB = ("app.js", "index.html", "style.css")
TEMPLATES = (
    "agents.json", "package.json", "prompts/audit.md", "prompts/implementation.md", "prompts/planning.md",
    "prompts/recipe.md", "prompts/review.md", "workflows/audit.ts", "workflows/change.ts",
    "workflows/evaluate.ts", "workflows/learn.ts",
)
OMIT = {"bin/corepack": "../lib/node_modules/corepack/dist/corepack.js", "bin/npm": "../lib/node_modules/npm/bin/npm-cli.js", "bin/npx": "../lib/node_modules/npm/bin/npx-cli.js"}
HEX = re.compile(r"[0-9a-f]{64}\Z")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?\Z")
BAD_PART = re.compile(r"^(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)", re.I)


def refuse(message: str):
    raise ValueError(message)


def require_private_file_mode():
    if not callable(getattr(os, "fchmod", None)):
        refuse("private stage requires os.fchmod")


def fields(value, required, optional=frozenset()):
    if not isinstance(value, dict) or required - value.keys() or value.keys() - required - optional:
        refuse("unknown or missing descriptor field")
    return value


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            refuse("duplicate JSON field")
        result[key] = value
    return result


def json_bytes(data: bytes):
    return json.loads(data.decode("utf-8"), object_pairs_hook=pairs)


def safe_name(value, allow_node_modules=False):
    if not isinstance(value, str) or not value or len(value.encode("utf-8", "surrogatepass")) > 4096 or value.count("/") > 63 or value.startswith("/") or "\\" in value or any(ord(c) < 32 or c in '<>:"|?*' for c in value):
        refuse("unsafe path")
    for part in value.split("/"):
        if not part or len(part.encode("utf-8", "surrogatepass")) > 255 or part in (".", "..") or (part.lower() == "node_modules" and not allow_node_modules) or part.endswith((".", " ")) or BAD_PART.match(part):
            refuse("unsafe path")
    return value


def canonical(path: str, directory: bool):
    if not isinstance(path, str) or len(path.encode("utf-8", "surrogatepass")) > 4096 or path.count("/") > 64 or any(len(part.encode("utf-8", "surrogatepass")) > 255 for part in path.split("/")):
        refuse("source path length or depth limit exceeded")
    value = Path(path)
    if not value.is_absolute() or os.path.normpath(path) != path:
        refuse("canonical absolute source path required")
    current = Path(value.anchor)
    for part in value.parts[1:]:
        current /= part
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or (current != value and not stat.S_ISDIR(info.st_mode)):
            refuse("linked or non-directory source component")
    info = value.lstat()
    if (directory and not stat.S_ISDIR(info.st_mode)) or (not directory and not stat.S_ISREG(info.st_mode)) or str(value.resolve()) != path:
        refuse("canonical source type required")
    return value


def provider_selection(path: str):
    """Bounded structural gate before selected JavaScript; fixed errors disclose no source paths."""
    try:
        if not isinstance(path, str) or len(path.encode("utf-8")) > 512:
            refuse("invalid provider selector path")
        descriptor = canonical(path, False)
        observed = descriptor.lstat()
        if observed.st_nlink != 1 or not 1 <= observed.st_size <= 4096:
            refuse("invalid provider selector file")
        fd = os.open(descriptor, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            before = os.fstat(fd)
            data = os.read(fd, 4097)
            after = os.fstat(fd)
        finally:
            os.close(fd)
        if len(data) != before.st_size or file_id(before) != file_id(after) or file_id(after) != file_id(descriptor.lstat()):
            refuse("changed provider selector file")
        providers = json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                               parse_constant=lambda _: refuse("invalid provider JSON constant"))
        pending = [(providers, 0)]
        while pending:
            value, depth = pending.pop()
            if depth > 3:
                refuse("deep provider descriptor")
            if isinstance(value, dict):
                pending.extend((item, depth + 1) for item in value.values())
            elif isinstance(value, list):
                pending.extend((item, depth + 1) for item in value)
        fields(providers, set(), {"codex", "copilot"})
        for name, value in providers.items():
            required = {"executable", "modes"} if name == "codex" else {"packageRoot", "manifestFile", "modes"}
            fields(value, required)
            modes = value["modes"]
            allowed = {"read-only", "workspace-write"} if name == "codex" else {"read-only"}
            if not isinstance(modes, list) or not 1 <= len(modes) <= len(allowed) or any(type(mode) is not str or mode not in allowed for mode in modes) or len(set(modes)) != len(modes):
                refuse("unsupported provider mode")
            for field in required - {"modes"}:
                selected = value[field]
                if not isinstance(selected, str) or len(selected.encode("utf-8")) > 512 or selected.count("/") > 32:
                    refuse("invalid provider source path")
                canonical(selected, field == "packageRoot")
        return descriptor, providers, file_id(observed), hashlib.sha256(data).hexdigest()
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
        refuse("provider selection refused")


def file_id(info):
    return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def inventory(root: Path, allow_node_modules=False):
    found = {}
    folded = set()
    def visit(directory, prefix=""):
        for item in os.scandir(directory):
            name = f"{prefix}/{item.name}" if prefix else item.name
            safe_name(name, allow_node_modules=allow_node_modules)
            if name.lower() in folded:
                refuse("case-insensitive path collision")
            folded.add(name.lower())
            info = item.stat(follow_symlinks=False)
            if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                refuse("linked or special bundle entry")
            found[name] = file_id(info)
            if stat.S_ISDIR(info.st_mode):
                visit(item.path, name)
    visit(root)
    return found


class PrivateStage:
    """Records exact new inodes and removes only those same regular files/directories."""
    def __init__(self):
        require_private_file_mode()
        temp_root = Path(tempfile.gettempdir()).resolve()
        if "factory" in temp_root.parts or len(str(temp_root)) > 160:
            refuse("temporary stage root refused")
        self.root = Path(tempfile.mkdtemp(prefix="factory-install-verify-", dir=temp_root))
        self.owned = {"": self._id(self.root)}
        self.preserved = False

    @staticmethod
    def _id(path):
        info = path.lstat()
        return info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode)

    def check(self, name):
        if self._id(self.root / name) != self.owned[name]:
            refuse("temporary stage ownership changed")

    def mkdir(self, name):
        if not name or name == ".":
            self.check("")
            return self.root
        safe_name(name, allow_node_modules=True)
        parent = Path(name).parent.as_posix()
        self.mkdir(parent)
        path = self.root / name
        if name not in self.owned:
            path.mkdir(mode=0o700)
            path.chmod(0o700)
            self.owned[name] = self._id(path)
        self.check(name)
        if not path.is_dir():
            refuse("temporary path is not a directory")
        return path

    def create(self, name, executable=False):
        require_private_file_mode()
        safe_name(name, allow_node_modules=True)
        self.mkdir(Path(name).parent.as_posix())
        path = self.root / name
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o700 if executable else 0o600)
        try:
            info = os.fstat(fd)
            self.owned[name] = info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode)
            os.fchmod(fd, 0o700 if executable else 0o600)
            return os.fdopen(fd, "wb")
        except BaseException as error:
            try:
                os.close(fd)
            except OSError as close_error:
                if close_error.errno != errno.EBADF:
                    self.preserved = True
                    refuse("private stage descriptor closure uncertain")
            if name not in self.owned:
                self.preserved = True
                refuse("private stage file identity uncertain")
            if isinstance(error, (OSError, AttributeError)):
                refuse("private stage file setup refused")
            raise

    def cleanup(self):
        errors = []
        for name in sorted(self.owned, key=lambda x: (x.count("/"), x), reverse=True):
            path = self.root / name
            try:
                self.check(name)
                if stat.S_ISDIR(path.lstat().st_mode):
                    path.rmdir()
                else:
                    path.unlink()
            except (OSError, ValueError) as error:
                errors.append(str(error))
        if errors:
            refuse("temporary stage cleanup refused: " + errors[0])


@contextmanager
def private_stage():
    stage = PrivateStage()
    try:
        yield stage
    finally:
        if not stage.preserved:
            stage.cleanup()


def copy_checked(source, stage, destination, maximum, size=None, sha=None, executable=False):
    fd = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum or (size is not None and size != before.st_size):
            refuse("source size mismatch or non-regular file")
        digest = hashlib.sha256()
        count = 0
        with stage.create(destination, executable) as output:
            while True:
                chunk = os.read(fd, min(64 * 1024, maximum + 1 - count))
                if not chunk:
                    break
                count += len(chunk)
                if count > maximum:
                    refuse("source size limit exceeded")
                digest.update(chunk)
                output.write(chunk)
        after = os.fstat(fd)
        if file_id(before) != file_id(after) or source.lstat().st_ino != before.st_ino or count != before.st_size:
            refuse("source changed during read")
        measured = digest.hexdigest()
        if sha is not None and measured != sha:
            refuse("changed file hash")
        return count, measured
    finally:
        os.close(fd)


def required_files(platform):
    result = {"package.json", "toolchain/package.json", "toolchain/package-lock.json"}
    result.update(f"dist/{stem}.{suffix}" for stem in MODULES for suffix in ("js", "js.map", "d.ts"))
    result.update(f"dist/web/{name}" for name in WEB)
    result.update(f"templates/{name}" for name in TEMPLATES)
    if platform == "win32-x64":
        result.add("native/windows-notify.exe")
    return result


def authenticate_bundle(bundle, selected_sha, stage):
    if not isinstance(selected_sha, str) or not HEX.fullmatch(selected_sha):
        refuse("external manifest SHA256 required")
    canonical(str(bundle), True)
    root_id = file_id(bundle.lstat())
    before = inventory(bundle)
    length, _ = copy_checked(bundle / "release-manifest.json", stage, "bundle/release-manifest.json", MIB, sha=selected_sha)
    if not length:
        refuse("empty release manifest")
    manifest = fields(json_bytes((stage.root / "bundle/release-manifest.json").read_bytes()), {"schema", "version", "platform", "node", "files"}, {"windowsHelper"})
    platform = manifest["platform"]
    if type(manifest["schema"]) is not int or manifest["schema"] != 2 or platform not in NODE:
        refuse("unsupported release manifest")
    if not isinstance(manifest["version"], str) or len(manifest["version"]) > 128 or not VERSION.fullmatch(manifest["version"]):
        refuse("invalid release version")
    node = fields(manifest["node"], {"version", "url", "sha256"})
    if node != {"version": "v24.22.1", "url": NODE[platform][0], "sha256": NODE[platform][1]}:
        refuse("unqualified Node asset")
    if platform == "win32-x64":
        helper = fields(manifest.get("windowsHelper"), {"path", "sha256", "qualificationRun"})
        if helper != {"path": "native/windows-notify.exe", "sha256": WINDOWS_HELPER_SHA, "qualificationRun": "39808257041"}:
            refuse("unqualified Windows helper")
    elif "windowsHelper" in manifest:
        refuse("unexpected Windows helper")
    entries = manifest["files"]
    if not isinstance(entries, list) or len(entries) > 4096:
        refuse("invalid manifest file inventory")
    names, folded, total = [], set(), 0
    for raw in entries:
        entry = fields(raw, {"path", "bytes", "sha256"})
        name = safe_name(entry["path"])
        if name == "release-manifest.json" or name in names or name.lower() in folded:
            refuse("duplicate or case-colliding manifest file")
        names.append(name)
        folded.add(name.lower())
        size = entry["bytes"]
        if type(size) is not int or size < 0 or size > 32 * MIB or not isinstance(entry["sha256"], str) or not HEX.fullmatch(entry["sha256"]):
            refuse("invalid file size or hash limit")
        total += size
        if total > 256 * MIB:
            refuse("release payload size limit exceeded")
    if names != sorted(names) or set(names) != required_files(platform):
        refuse("incomplete or unsorted release payload")
    expected_dirs = set()
    for name in names:
        parent = Path(name).parent
        while parent.as_posix() != ".":
            expected_dirs.add(parent.as_posix())
            parent = parent.parent
    if set(before) != set(names) | expected_dirs | {"release-manifest.json"}:
        refuse("missing or unowned release file or directory")
    for name in expected_dirs:
        if not stat.S_ISDIR(before[name][2]):
            refuse("non-directory release parent")
    for entry in entries:
        name = entry["path"]
        if not stat.S_ISREG(before[name][2]):
            refuse("non-regular release file")
        copy_checked(bundle / name, stage, f"bundle/{name}", 32 * MIB, entry["bytes"], entry["sha256"])
    if next(item for item in entries if item["path"] == "toolchain/package-lock.json")["sha256"] != LOCK_SHA:
        refuse("unapproved factory toolchain lock")
    canonical(str(bundle), True)
    if file_id(bundle.lstat()) != root_id or inventory(bundle) != before:
        refuse("bundle source changed during authentication")
    return manifest


def archive_name(raw, platform):
    top = f"node-v24.22.1-{'win-x64' if platform == 'win32-x64' else platform}"
    if raw in (top, top + "/"):
        return ""
    if not raw.startswith(top + "/"):
        refuse("archive member outside selected root")
    return safe_name(raw[len(top) + 1:].removesuffix("/"), allow_node_modules=True)


def preflight_tar_headers(archive):
    """Bound physical TAR extensions before tarfile's recursive PAX parser runs."""
    physical = extension_run = expanded = metadata = 0
    with lzma.open(archive, "rb") as source:
        while True:
            header = source.read(512)
            if len(header) != 512:
                refuse("truncated TAR header")
            if header == bytes(512):
                break
            physical += 1
            if physical > 16384:
                refuse("TAR physical header limit exceeded")
            size_field = header[124:136]
            try:
                if size_field[0] & 0x80:
                    size = int.from_bytes(bytes([size_field[0] & 0x7f]) + size_field[1:], "big")
                else:
                    size = int(size_field.strip(b" \0") or b"0", 8)
            except ValueError:
                refuse("invalid TAR physical header")
            if size > 256 * MIB:
                refuse("TAR physical payload limit exceeded")
            kind = header[156:157]
            if kind in (b"g", b"x", b"L", b"K"):
                extension_run += 1
                metadata += size
                if extension_run > 64 or metadata > 16 * MIB:
                    refuse("TAR extension limit exceeded")
            else:
                extension_run = 0
            expanded += (size + 511) // 512 * 512
            if expanded > 272 * MIB:
                refuse("TAR physical expansion limit exceeded")
            remaining = (size + 511) // 512 * 512
            while remaining:
                chunk = source.read(min(64 * 1024, remaining))
                if not chunk:
                    refuse("truncated TAR physical payload")
                remaining -= len(chunk)


def archive_rows(archive, platform):
    rows = []
    expanded = 0
    if platform == "win32-x64":
        with archive.open("rb") as raw:
            raw.seek(0, os.SEEK_END)
            archive_size = raw.tell()
            raw.seek(max(0, archive_size - 65_557))
            tail = raw.read()
        eocd = tail.rfind(b"PK\x05\x06")
        if eocd < 0 or eocd + 22 > len(tail):
            refuse("ZIP end record missing")
        _, disk, central_disk, disk_entries, entries, central_size, central_offset, comment_size = struct.unpack_from("<4s4H2LH", tail, eocd)
        if disk or central_disk or disk_entries != entries or entries == 0xFFFF or entries > 8192 or eocd + 22 + comment_size != len(tail) or central_offset + central_size > archive_size:
            refuse("ZIP member count or central directory refused")
        with zipfile.ZipFile(archive) as source:
            if len(source.infolist()) != entries:
                refuse("archive member count limit exceeded")
            for item in source.infolist():
                name = archive_name(item.filename, platform)
                kind = stat.S_IFMT(item.external_attr >> 16)
                if item.flag_bits & 1 or item.external_attr & 0x400 or kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                    refuse("ZIP link, reparse, encrypted or special member")
                directory = item.is_dir()
                if (directory and kind == stat.S_IFREG) or (not directory and kind == stat.S_IFDIR):
                    refuse("ZIP type mismatch")
                if not directory:
                    if item.file_size > 128 * MIB:
                        refuse("archive member size limit exceeded")
                    expanded += item.file_size
                    if expanded > 256 * MIB:
                        refuse("archive expanded size limit exceeded")
                rows.append((name, "dir" if directory else "file", item.file_size, item))
    else:
        preflight_tar_headers(archive)
        with tarfile.open(archive, "r:xz") as source:
            for item in source:
                if len(rows) >= 8192:
                    refuse("archive member count limit exceeded")
                name = archive_name(item.name, platform)
                if item.isdir():
                    kind = "dir"
                elif item.isfile():
                    kind = "file"
                elif item.issym() and name in OMIT and item.linkname == OMIT[name]:
                    kind = "omit"
                else:
                    refuse("unexpected archive link or special member")
                if kind == "file":
                    if item.size > 128 * MIB:
                        refuse("archive member size limit exceeded")
                    expanded += item.size
                    if expanded > 256 * MIB:
                        refuse("archive expanded size limit exceeded")
                rows.append((name, kind, item.size, item))
    return rows


def extract_node_archive(archive: str | Path, platform: str, stage: PrivateStage):
    """Public hostile-input seam; production verify pins the archive before calling."""
    if platform not in NODE:
        refuse("unqualified platform")
    archive = Path(archive)
    info = archive.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > 128 * MIB:
        refuse("archive type or size limit exceeded")
    try:
        rows = archive_rows(archive, platform)
    except (RecursionError, lzma.LZMAError):
        refuse("TAR parser limit or corruption refused")
    seen, folded, kinds, omitted, total = set(), set(), {}, set(), 0
    root_seen = False
    for name, kind, size, _ in rows:
        if not name:
            if root_seen or kind != "dir":
                refuse("missing, duplicate or non-directory archive root")
            root_seen = True
            continue
        if name in seen or name.lower() in folded:
            refuse("duplicate or case-colliding archive member")
        seen.add(name)
        folded.add(name.lower())
        kinds[name] = kind
        if kind == "omit":
            omitted.add(name)
        elif kind == "file":
            if size > 128 * MIB:
                refuse("archive member size limit exceeded")
            total += size
            if total > 256 * MIB:
                refuse("archive expanded size limit exceeded")
    ancestor_names = {}
    for name in seen:
        for parent in Path(name).parents:
            if parent.as_posix() == ".":
                break
            parent_name = parent.as_posix()
            prior = ancestor_names.setdefault(parent_name.lower(), parent_name)
            if prior != parent_name:
                refuse("case-colliding archive parent")
            if parent_name in kinds and kinds[parent_name] != "dir":
                refuse("archive parent is not a directory")
    for name in seen:
        if name.lower() in ancestor_names and ancestor_names[name.lower()] != name:
            refuse("case-colliding archive member and parent")
    if not root_seen:
        refuse("missing archive root")
    for name, kind, _, _ in rows:
        if name and kind == "dir":
            stage.mkdir(f"node/{name}")
    if platform == "win32-x64":
        with zipfile.ZipFile(archive) as source:
            for name, kind, size, item in rows:
                if name and kind == "file":
                    with source.open(item) as data:
                        extract_file(data, stage, f"node/{name}", size, name == "node.exe")
    else:
        try:
            with tarfile.open(archive, "r:xz") as source:
                for name, kind, size, item in rows:
                    if name and kind == "file":
                        with source.extractfile(item) as data:
                            extract_file(data, stage, f"node/{name}", size, name == "bin/node")
        except (RecursionError, lzma.LZMAError):
            refuse("TAR parser limit or corruption refused")
    return {"members": len(rows), "expandedBytes": total, "omittedLinks": sorted(omitted)}


def extract_file(data, stage, name, size, executable):
    remaining = size
    with stage.create(name, executable) as output:
        while remaining:
            chunk = data.read(min(64 * 1024, remaining))
            if not chunk:
                refuse("truncated archive member")
            output.write(chunk)
            remaining -= len(chunk)
        if data.read(1):
            refuse("archive member exceeds declared size")


def bounded_child(command, stage=None, timeout_seconds=30):
    """Require direct exit, both pipe EOFs and original POSIX group absence."""
    deadline = time.monotonic() + timeout_seconds
    cleanup_window = min(2, max(0.1, timeout_seconds / 4))
    run_deadline = deadline - cleanup_window
    outputs = [bytearray(), bytearray()]
    overflow = threading.Event()
    errors = threading.Event()
    done = [threading.Event(), threading.Event()]
    threads = []
    closure_confirmed = False
    expected_refusal = False

    def drain(stream, output, finished):
        try:
            while chunk := stream.read(4096):
                if len(output) + len(chunk) > 16 * 1024:
                    overflow.set()
                elif not overflow.is_set():
                    output.extend(chunk)
        except OSError:
            errors.set()
        finally:
            finished.set()

    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env={"PATH": os.defpath, "HOME": tempfile.gettempdir()}, start_new_session=os.name == "posix")
    try:
        for i, stream in enumerate((process.stdout, process.stderr)):
            thread = threading.Thread(target=drain, args=(stream, outputs[i], done[i]), name=f"factory-install-drain-{i}", daemon=True)
            threads.append(thread)
            thread.start()
        while not all(finished.is_set() for finished in done) and not overflow.is_set() and not errors.is_set() and time.monotonic() < run_deadline:
            try:
                unfinished = next(finished for finished in done if not finished.is_set())
            except StopIteration:
                # Both pipes completed after the loop condition was checked.
                break
            unfinished.wait(min(0.02, max(0, run_deadline - time.monotonic())))
        if not all(finished.is_set() for finished in done) or overflow.is_set() or errors.is_set():
            expected_refusal = True
            refuse("validator pipe closure or output limit refused")
        try:
            process.wait(timeout=max(0, run_deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            expected_refusal = True
            raise
        for thread in threads:
            thread.join(timeout=max(0, deadline - time.monotonic()))
        if any(thread.is_alive() for thread in threads):
            expected_refusal = True
            refuse("validator drain thread closure uncertain")
        if os.name == "posix":
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                pass
            else:
                expected_refusal = True
                refuse("validator original process group remains")
        else:
            expected_refusal = True
            refuse("validator descendant closure unsupported")
        closure_confirmed = True
        if process.returncode or outputs[1] or len(outputs[0]) > 2048:
            refuse("semantic selection validation refused")
        return bytes(outputs[0])
    except BaseException as error:
        if closure_confirmed:
            raise
        if stage is not None:
            stage.preserved = True
        # Keep the leader unreaped until signaling this invocation's own group.
        # A blocked group signal falls back only to the directly owned PID.
        shutdown_deadline = min(deadline, time.monotonic() + cleanup_window)
        if process.returncode is None:
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except BaseException:
                    try:
                        os.kill(process.pid, signal.SIGKILL)
                    except BaseException:
                        pass
            else:
                try:
                    process.kill()
                except BaseException:
                    pass
            try:
                process.wait(timeout=max(0, shutdown_deadline - time.monotonic()))
            except BaseException:
                pass
        for thread in threads:
            try:
                thread.join(timeout=max(0, shutdown_deadline - time.monotonic()))
            except BaseException:
                pass
        for i, stream in enumerate((process.stdout, process.stderr)):
            if i >= len(threads) or not threads[i].is_alive():
                try:
                    stream.close()
                except BaseException:
                    pass
        if stage is not None:
            message = f"validator closure uncertain; private stage preserved at {stage.root}"
        else:
            message = "validator closure uncertain"
        if expected_refusal:
            raise ValueError(message) from error
        raise RuntimeError(message) from error
    finally:
        if closure_confirmed:
            process.stdout.close()
            process.stderr.close()


def authenticate_snapshot(bundle, selected_sha):
    data = (bundle / "release-manifest.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != selected_sha:
        refuse("changed temporary manifest")
    manifest = json_bytes(data)
    for entry in manifest["files"]:
        path = bundle / entry["path"]
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(64 * 1024):
                digest.update(chunk)
        if digest.hexdigest() != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            refuse("changed temporary bundle file")


@dataclass(frozen=True)
class PreparedSelection:
    source_bundle_root: Path
    source_node_archive: Path
    snapshot_bundle_root: Path
    snapshot_node_archive: Path
    extracted_node_root: Path
    manifest_sha256: str
    receipt: dict
    source_bundle_identity: tuple
    source_bundle_inventory: tuple
    source_archive_identity: tuple
    providers: dict
    provider_descriptor: Path | None
    provider_descriptor_identity: tuple | None
    provider_descriptor_sha256: str | None
    stage: PrivateStage

    def revalidate_sources(self):
        """Required before a later candidate binds the original selection."""
        if self.provider_descriptor is not None:
            _, providers, identity, digest = provider_selection(str(self.provider_descriptor))
            if providers != self.providers or identity != self.provider_descriptor_identity or digest != self.provider_descriptor_sha256:
                refuse("provider selection refused")
        canonical(str(self.source_bundle_root), True)
        canonical(str(self.source_node_archive), False)
        if file_id(self.source_bundle_root.lstat()) != self.source_bundle_identity or tuple(sorted(inventory(self.source_bundle_root).items())) != self.source_bundle_inventory or file_id(self.source_node_archive.lstat()) != self.source_archive_identity:
            refuse("selected source identity changed")
        with private_stage() as check:
            authenticate_bundle(self.source_bundle_root, self.manifest_sha256, check)
            copy_checked(self.source_node_archive, check, "selected-node-archive", 128 * MIB, sha=self.receipt["nodeSha256"])
        if file_id(self.source_bundle_root.lstat()) != self.source_bundle_identity or tuple(sorted(inventory(self.source_bundle_root).items())) != self.source_bundle_inventory or file_id(self.source_node_archive.lstat()) != self.source_archive_identity:
            refuse("selected source changed during revalidation")


@contextmanager
def prepare_install_selection(bundle_root: str, manifest_sha256: str, node_archive: str, providers_path: str | None = None):
    """Reusable authenticated preparation scope for the later installer."""
    descriptor, providers, descriptor_identity, descriptor_sha = provider_selection(providers_path) if providers_path is not None else (None, {}, None, None)
    bundle = canonical(bundle_root, True)
    archive = canonical(node_archive, False)
    with private_stage() as stage:
        manifest = authenticate_bundle(bundle, manifest_sha256, stage)
        source_bundle_identity = file_id(bundle.lstat())
        source_bundle_inventory = tuple(sorted(inventory(bundle).items()))
        source_archive_identity = file_id(archive.lstat())
        platform = manifest["platform"]
        archive_size, _ = copy_checked(archive, stage, "selected-node-archive", 128 * MIB, sha=NODE[platform][1])
        extraction = extract_node_archive(stage.root / "selected-node-archive", platform, stage)
        if platform != "win32-x64" and extraction["omittedLinks"] != sorted(OMIT):
            refuse("incomplete Node convenience link omission table")
        executable = stage.root / "node" / ("node.exe" if platform == "win32-x64" else "bin/node")
        if not executable.is_file() or executable.is_symlink():
            refuse("verified Node executable missing")
        authenticate_snapshot(stage.root / "bundle", manifest_sha256)
        entry = stage.root / "bundle/dist/installation-bindings.js"
        selected_file = "-"
        if providers:
            selected_file = str(stage.root / "selected-providers.json")
            with stage.create("selected-providers.json") as output:
                output.write((json.dumps(providers, separators=(",", ":"), sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
                output.flush()
                os.fsync(output.fileno())
        program = "import {readFileSync} from 'node:fs';import {validateInstallSelection} from " + json.dumps(entry.as_uri()) + ";const p=process.argv[4]==='-'?undefined:JSON.parse(readFileSync(process.argv[4],'utf8'));const s=validateInstallSelection({bundleRoot:process.argv[1],manifestSha256:process.argv[2],nodeArchivePath:process.argv[3],...(p?{providers:p}:{})});process.stdout.write(JSON.stringify({version:s.bundle.version,platform:s.bundle.platform,manifestSha256:s.bundle.manifestSha256,nodeSha256:s.node.sha256}));"
        output = bounded_child([str(executable), "--input-type=module", "-e", program, str(stage.root / "bundle"), manifest_sha256, str(stage.root / "selected-node-archive"), selected_file], stage)
        semantic = fields(json_bytes(output), {"version", "platform", "manifestSha256", "nodeSha256"})
        if semantic != {"version": manifest["version"], "platform": platform, "manifestSha256": manifest_sha256, "nodeSha256": NODE[platform][1]}:
            refuse("semantic selection receipt mismatch")
        receipt = {"schema": 1, "version": manifest["version"], "platform": platform, "manifestSha256": manifest_sha256, "nodeSha256": NODE[platform][1], "nodeArchiveBytes": archive_size, "bundleFiles": len(manifest["files"]), "archiveMembers": extraction["members"], "omittedLinks": extraction["omittedLinks"]}
        yield PreparedSelection(bundle, archive, stage.root / "bundle", stage.root / "selected-node-archive", stage.root / "node", manifest_sha256, receipt, source_bundle_identity, source_bundle_inventory, source_archive_identity, providers, descriptor, descriptor_identity, descriptor_sha, stage)


def extracted_node_tree(root: Path, platform: str):
    """Canonical byte-and-mode tree digest agreed with install-candidate.ts."""
    canonical(str(root), True)
    original = file_id(root.lstat())
    rows = []
    folded = set()
    regular_bytes = 0

    def visit(directory: Path, prefix=""):
        nonlocal regular_bytes
        for item in os.scandir(directory):
            name = f"{prefix}/{item.name}" if prefix else item.name
            safe_name(name, allow_node_modules=True)
            if len(name.encode("utf-8")) > 512 or len(name.split("/")) > 32 or name.lower() in folded:
                refuse("extracted Node path bound or collision")
            folded.add(name.lower())
            info = item.stat(follow_symlinks=False)
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISDIR(info.st_mode):
                if mode != 0o700:
                    refuse("extracted Node directory mode changed")
                rows.append((name, "D", mode, 0, None))
                visit(Path(item.path), name)
            elif stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1 or mode != (0o700 if name in ("bin/node", "node.exe") else 0o600):
                    refuse("extracted Node file link or mode changed")
                if info.st_size > 128 * MIB:
                    refuse("extracted Node file exceeds bound")
                regular_bytes += info.st_size
                if regular_bytes > 512 * MIB:
                    refuse("extracted Node bytes exceed bound")
                digest = hashlib.sha256()
                fd = os.open(item.path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                try:
                    before = os.fstat(fd)
                    if file_id(before) != file_id(info):
                        refuse("extracted Node file identity changed")
                    remaining = before.st_size
                    while remaining:
                        chunk = os.read(fd, min(64 * 1024, remaining))
                        if not chunk:
                            refuse("extracted Node file truncated")
                        digest.update(chunk)
                        remaining -= len(chunk)
                    if file_id(os.fstat(fd)) != file_id(before) or file_id(Path(item.path).lstat()) != file_id(before):
                        refuse("extracted Node file changed during read")
                finally:
                    os.close(fd)
                rows.append((name, "F", mode, info.st_size, digest.digest()))
            else:
                refuse("linked or special extracted Node entry")
            if len(rows) > 8192:
                refuse("extracted Node entries exceed bound")

    visit(root)
    digest = hashlib.sha256(b"factory-node-tree-v1\0")
    for name, kind, mode, size, file_digest in sorted(rows, key=lambda row: row[0].encode("utf-8")):
        if kind == "D":
            digest.update(b"D\0" + name.encode("utf-8") + b"\0" + format(mode, "o").encode() + b"\0")
        else:
            digest.update(b"F\0" + name.encode("utf-8") + b"\0" + str(size).encode() + b"\0" + format(mode, "o").encode() + b"\0" + file_digest)
    if file_id(root.lstat()) != original:
        refuse("extracted Node root changed")
    return {"schema": 1, "digest": digest.hexdigest(), "entries": len(rows), "regularBytes": regular_bytes,
            "omittedLinks": [] if platform == "win32-x64" else sorted(OMIT)}


def private_npm_inputs(stage: PrivateStage, offline: bool, seed: str | None):
    for name in ("npm", "npm/cache", "npm/home"):
        stage.mkdir(name)
    for name in ("npm/user.npmrc", "npm/global.npmrc"):
        with stage.create(name) as output:
            output.flush()
            os.fsync(output.fileno())
    seeded = {}
    if seed is None:
        return seeded
    if not offline:
        refuse("offline cache seed requires --offline")
    cache = canonical(seed, True)
    source = cache / "_cacache"
    canonical(str(source), True)
    count = 0
    total = 0
    folded = set()

    def visit(directory: Path, prefix=""):
        nonlocal count, total
        for item in sorted(os.scandir(directory), key=lambda entry: entry.name.encode("utf-8")):
            name = f"{prefix}/{item.name}" if prefix else item.name
            safe_name(name, allow_node_modules=True)
            if len(name.encode("utf-8")) > 512 or len(name.split("/")) > 32 or name.lower() in folded:
                refuse("offline cache path bound or collision")
            folded.add(name.lower())
            count += 1
            if count > 4096:
                refuse("offline cache entry bound exceeded")
            info = item.stat(follow_symlinks=False)
            destination = f"npm/cache/_cacache/{name}"
            if stat.S_ISDIR(info.st_mode):
                stage.mkdir(destination)
                visit(Path(item.path), name)
            elif stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1 or info.st_size > 64 * MIB:
                    refuse("offline cache link or file bound refused")
                total += info.st_size
                if total > 128 * MIB:
                    refuse("offline cache bytes exceed bound")
                size, digest = copy_checked(Path(item.path), stage, destination, 64 * MIB, size=info.st_size)
                if file_id(Path(item.path).lstat()) != file_id(info) or size != info.st_size:
                    refuse("offline cache source changed")
                seeded[destination] = (stage.owned[destination], size, digest)
            else:
                refuse("linked or special offline cache entry")

    stage.mkdir("npm/cache/_cacache")
    visit(source)
    return seeded


def adopt_npm_outputs(stage: PrivateStage, seeded: dict):
    """After known process-group closure, admit only bounded private cache/home outputs."""
    count = 0
    total = 0
    folded = set()

    def visit(directory: Path, prefix: str):
        nonlocal count, total
        for item in os.scandir(directory):
            relative = f"{prefix}/{item.name}"
            name = relative[len("npm/"):]
            safe_name(name, allow_node_modules=True)
            if len(name.encode("utf-8")) > 512 or len(name.split("/")) > 32 or name.lower() in folded:
                refuse("post-npm cache path bound or collision")
            folded.add(name.lower())
            count += 1
            if count > 8192:
                refuse("post-npm cache entry bound exceeded")
            info = item.stat(follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                if relative not in stage.owned:
                    stage.owned[relative] = stage._id(Path(item.path))
                else:
                    stage.check(relative)
                visit(Path(item.path), relative)
            elif stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1 or info.st_size > 64 * MIB:
                    refuse("post-npm cache link or file bound refused")
                total += info.st_size
                if total > 256 * MIB:
                    refuse("post-npm cache bytes exceed bound")
                if relative not in stage.owned:
                    stage.owned[relative] = stage._id(Path(item.path))
                else:
                    stage.check(relative)
                if relative in seeded:
                    original_id, size, digest = seeded[relative]
                    if stage.owned[relative] != original_id or info.st_size != size or hashlib.sha256(Path(item.path).read_bytes()).hexdigest() != digest:
                        refuse("seeded offline cache changed")
            else:
                refuse("post-npm linked or special entry")

    visit(stage.root / "npm/cache", "npm/cache")
    visit(stage.root / "npm/home", "npm/home")
    for name in ("npm/user.npmrc", "npm/global.npmrc"):
        stage.check(name)
        if (stage.root / name).stat().st_size != 0:
            refuse("private npm configuration changed")
    # A full owned-tree preflight prevents an unregistered sidecar from causing partial cleanup.
    actual = set(inventory(stage.root, allow_node_modules=True))
    if actual != set(stage.owned) - {""}:
        refuse("unowned private stage content after preparation")
    for name in stage.owned:
        stage.check(name)


def prepare_candidate(prepared: PreparedSelection, repository: str, offline: bool, seed: str | None, handoff=False):
    stage = prepared.stage
    stage.check("")
    canonical(repository, True)
    seeded = private_npm_inputs(stage, offline, seed)
    node_tree = extracted_node_tree(prepared.extracted_node_root, prepared.receipt["platform"])
    request = {"schema": 1, "requestId": str(uuid.uuid4()),
               "repository": repository, "npm": {"offline": offline}, "stageRoot": str(stage.root),
               "stageIdentity": f"{stage.root.lstat().st_dev}:{stage.root.lstat().st_ino}",
               "source": {"bundleRoot": str(prepared.source_bundle_root), "manifestSha256": prepared.manifest_sha256,
                          "nodeArchivePath": str(prepared.source_node_archive),
                          **({"providers": prepared.providers} if prepared.providers else {})},
               "snapshot": {"bundleRoot": str(prepared.snapshot_bundle_root), "nodeArchivePath": str(prepared.snapshot_node_archive),
                            "extractedNodeRoot": str(prepared.extracted_node_root), "nodeTree": node_tree}}
    data = (json.dumps(request, separators=(",", ":"), sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    if len(data) > 64 * 1024:
        refuse("private prepare request exceeds bound")
    with stage.create("preparer-request.json") as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())
    prepared.revalidate_sources()
    stage.check("")
    entry = prepared.snapshot_bundle_root / "dist/install-entry.js"
    executable = prepared.extracted_node_root / ("node.exe" if prepared.receipt["platform"] == "win32-x64" else "bin/node")
    try:
        command = [str(executable), str(entry), "--request", str(stage.root / "preparer-request.json")]
        if handoff:
            command.append("--handoff")
        response = bounded_child(command, stage,
                                 timeout_seconds=300)
        required = {"operationId", "repositoryId", "claimId", "stagePath", "candidateDigest"}
        if handoff:
            required.update({"ticketPath", "stageDigest"})
        result = fields(json_bytes(response), required)
        if any(not isinstance(result[key], str) or not result[key] for key in result):
            refuse("invalid candidate preparation receipt")
        prepared.revalidate_sources()
        if extracted_node_tree(prepared.extracted_node_root, prepared.receipt["platform"]) != node_tree:
            refuse("private extracted Node changed after preparation")
        adopt_npm_outputs(stage, seeded)
        stage.check("")
        return result
    except BaseException:
        stage.preserved = True
        raise


def publish_candidate(prepared: dict):
    """Issue the private post-wait receipt and run only the staged Node in foreground."""
    stage = canonical(prepared["stagePath"], True)
    ticket_path = canonical(prepared["ticketPath"], False)
    if ticket_path != stage / "handoff-ticket.json" or ticket_path.stat().st_size > 8192:
        refuse("private handoff ticket path or bound invalid")
    ticket = fields(json_bytes(ticket_path.read_bytes()), {"version", "operationId", "repositoryId", "root", "commonDir",
        "claimId", "token", "stagePath", "stageIdentity", "stageDigest", "nonce", "release", "selectionDigest",
        "targetReleaseSha256", "artifactDigests", "targetSchema", "exitReceiptPath", "candidate"})
    if ticket["version"] != 1 or ticket["operationId"] != prepared["operationId"] or ticket["claimId"] != prepared["claimId"] or ticket["stagePath"] != str(stage) or ticket["stageDigest"] != prepared["stageDigest"]:
        refuse("private handoff ticket differs from preparer receipt")
    nonce = ticket["nonce"]
    if not isinstance(nonce, str) or str(uuid.UUID(nonce)) != nonce:
        refuse("private handoff nonce invalid")
    exit_path = stage / f"handoff-exit-{nonce}.json"
    if ticket["exitReceiptPath"] != str(exit_path):
        refuse("private handoff exit path differs")
    exit_receipt = {"version": 1, "operationId": prepared["operationId"], "claimId": prepared["claimId"],
                    "stageDigest": prepared["stageDigest"], "nonce": nonce}
    data = (json.dumps(exit_receipt, separators=(",", ":"), sort_keys=True) + "\n").encode()
    fd = os.open(exit_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "wb") as output:
        os.fchmod(output.fileno(), 0o600)
        output.write(data)
        output.flush()
        os.fsync(output.fileno())
    if exit_path.read_bytes() != data:
        refuse("post-wait receipt changed")
    directory_fd = os.open(stage, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    platform = "win32-x64" if os.name == "nt" else None
    executable = canonical(str(stage / "payload" / ("node.exe" if platform else "node")), False)
    entry = canonical(str(stage / "payload/dist/maintenance-entry.js"), False)
    owned = snapshot_completed_stage(stage)
    result = fields(json_bytes(bounded_child([str(executable), str(entry), "--ticket", str(ticket_path)],
                                             timeout_seconds=300)), {"state", "operationId", "repositoryId"})
    if result != {"state": "ready", "operationId": prepared["operationId"], "repositoryId": prepared["repositoryId"]}:
        refuse("staged controller completion differs")
    cleanup_completed_stage(stage, owned)
    return result


def snapshot_completed_stage(stage: Path):
    """Capture only the private operation stage, including every payload and sidecar."""
    if os.name != "posix":
        refuse("Windows stage cleanup ownership requires native qualification")
    root = stage.lstat()
    if not stat.S_ISDIR(root.st_mode) or stat.S_ISLNK(root.st_mode):
        refuse("completed stage root changed")
    found = inventory(stage)
    if len(found) > 576:
        refuse("completed stage inventory exceeds bound")
    rows = {"": (stage_directory_identity(root), None)}
    total = 0
    for name, observed in found.items():
        path = stage / name
        info = path.lstat()
        if file_id(info) != observed:
            refuse("completed stage entry changed")
        if stat.S_ISDIR(info.st_mode):
            rows[name] = (stage_directory_identity(info), None)
            continue
        if info.st_nlink != 1 or info.st_size > 256 * MIB:
            refuse("completed stage file link or bound refused")
        total += info.st_size
        if total > 256 * MIB:
            refuse("completed stage bytes exceed bound")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            if file_id(os.fstat(descriptor)) != observed:
                refuse("completed stage descriptor identity changed")
            digest = hashlib.sha256()
            with os.fdopen(descriptor, "rb", closefd=False) as source:
                while chunk := source.read(65536):
                    digest.update(chunk)
            if file_id(os.fstat(descriptor)) != observed:
                refuse("completed stage file changed while reading")
            rows[name] = (observed, digest.hexdigest())
        finally:
            os.close(descriptor)
    if stage_directory_identity(stage.lstat()) != rows[""][0]:
        refuse("completed stage root changed")
    return rows


def stage_directory_identity(info):
    return info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode), info.st_mode & 0o777


def cleanup_completed_stage(stage: Path, owned):
    if snapshot_completed_stage(stage) != owned:
        refuse("completed stage changed; retained for inspection")
    for name in sorted((name for name in owned if name), key=lambda item: (item.count("/"), item), reverse=True):
        path = stage / name
        observed = path.lstat()
        actual = stage_directory_identity(observed) if owned[name][1] is None else file_id(observed)
        if actual != owned[name][0]:
            refuse("completed stage changed during cleanup")
        if owned[name][1] is None:
            path.rmdir()
        else:
            path.unlink()
    if stage_directory_identity(stage.lstat()) != owned[""][0]:
        refuse("completed stage root changed during cleanup")
    stage.rmdir()
    directory_fd = os.open(stage.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def main():
    if sys.version_info < (3, 11):
        refuse("Python 3.11 or newer required")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify", help="Authenticate selected local bytes without installing")
    verify.add_argument("--bundle-root", required=True)
    verify.add_argument("--manifest-sha256", required=True)
    verify.add_argument("--node-archive", required=True)
    verify.add_argument("--providers", help="Canonical local JSON file with selected qualified external providers")
    prepare = sub.add_parser("prepare", help="Prepare an incomplete, candidate-bound install without publication")
    prepare.add_argument("--repository", required=True)
    prepare.add_argument("--bundle-root", required=True)
    prepare.add_argument("--manifest-sha256", required=True)
    prepare.add_argument("--node-archive", required=True)
    prepare.add_argument("--offline", action="store_true")
    prepare.add_argument("--offline-cache-seed")
    prepare.add_argument("--providers", help="Canonical local JSON file with selected qualified external providers")
    install = sub.add_parser("install", help="Publish a foreground first install from authenticated selected bytes")
    install.add_argument("--repository", required=True)
    install.add_argument("--bundle-root", required=True)
    install.add_argument("--manifest-sha256", required=True)
    install.add_argument("--node-archive", required=True)
    install.add_argument("--offline", action="store_true")
    install.add_argument("--offline-cache-seed")
    install.add_argument("--providers", help="Canonical local JSON file with selected qualified external providers")
    args = parser.parse_args()
    if args.command in ("prepare", "install") and args.offline_cache_seed and not args.offline:
        refuse("offline cache seed requires --offline")
    with prepare_install_selection(args.bundle_root, args.manifest_sha256, args.node_archive, args.providers) as prepared:
        if args.command == "verify":
            result = prepared.receipt
        else:
            result = prepare_candidate(prepared, args.repository, args.offline, args.offline_cache_seed,
                                       handoff=args.command == "install")
    if args.command == "install":
        result = publish_candidate(result)
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, UnicodeError, tarfile.TarError, zipfile.BadZipFile) as error:
        detail = str(error).replace("\r", " ").replace("\n", " ")[:300]
        print(f"install bootstrap: {detail}", file=sys.stderr)
        raise SystemExit(1)
