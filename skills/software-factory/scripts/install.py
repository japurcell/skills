#!/usr/bin/env python3
"""Authenticate a selected factory release before executing selected JavaScript.

Python 3.11+ standard library only. `verify` creates no installation state.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import threading
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
    "agents", "build", "capture", "clearance", "cli", "dashboard", "execution-control", "installation-bindings",
    "learning", "lifecycle", "maintenance", "native/notification-transport", "native/notifications",
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
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value or any(ord(c) < 32 or c in '<>:"|?*' for c in value):
        refuse("unsafe path")
    for part in value.split("/"):
        if not part or part in (".", "..") or (part.lower() == "node_modules" and not allow_node_modules) or part.endswith((".", " ")) or BAD_PART.match(part):
            refuse("unsafe path")
    return value


def canonical(path: str, directory: bool):
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


def file_id(info):
    return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def inventory(root: Path):
    found = {}
    folded = set()
    def visit(directory, prefix=""):
        for item in os.scandir(directory):
            name = f"{prefix}/{item.name}" if prefix else item.name
            safe_name(name)
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
        temp_root = Path(tempfile.gettempdir()).resolve()
        if "factory" in temp_root.parts:
            refuse("temporary stage must be outside factory")
        self.root = Path(tempfile.mkdtemp(prefix="factory-install-verify-", dir=temp_root))
        self.owned = {"": self._id(self.root)}

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
        safe_name(name, allow_node_modules=True)
        self.mkdir(Path(name).parent.as_posix())
        path = self.root / name
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o700 if executable else 0o600)
        os.fchmod(fd, 0o700 if executable else 0o600)
        self.owned[name] = self._id(path)
        return os.fdopen(fd, "wb")

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
    rows = archive_rows(archive, platform)
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
        with tarfile.open(archive, "r:xz") as source:
            for name, kind, size, item in rows:
                if name and kind == "file":
                    with source.extractfile(item) as data:
                        extract_file(data, stage, f"node/{name}", size, name == "bin/node")
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


def bounded_child(command):
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={"PATH": os.defpath, "HOME": tempfile.gettempdir()})
    outputs = [bytearray(), bytearray()]
    overflow = threading.Event()
    def drain(stream, output):
        while chunk := stream.read(4096):
            if len(output) + len(chunk) > 16 * 1024:
                overflow.set()
                process.kill()
                return
            output.extend(chunk)
    threads = [threading.Thread(target=drain, args=(stream, outputs[i]), daemon=True) for i, stream in enumerate((process.stdout, process.stderr))]
    for thread in threads:
        thread.start()
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        refuse("semantic validator timeout")
    for thread in threads:
        thread.join(timeout=2)
    if overflow.is_set():
        refuse("semantic validator output limit exceeded")
    if process.returncode or outputs[1] or len(outputs[0]) > 2048:
        refuse("semantic selection validation refused")
    return bytes(outputs[0])


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

    def revalidate_sources(self):
        """Required before a later candidate binds the original selection."""
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
def prepare_install_selection(bundle_root: str, manifest_sha256: str, node_archive: str):
    """Reusable authenticated preparation scope for the later installer."""
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
        program = "import {validateInstallSelection} from " + json.dumps(entry.as_uri()) + ";const s=validateInstallSelection({bundleRoot:process.argv[1],manifestSha256:process.argv[2],nodeArchivePath:process.argv[3]});process.stdout.write(JSON.stringify({version:s.bundle.version,platform:s.bundle.platform,manifestSha256:s.bundle.manifestSha256,nodeSha256:s.node.sha256}));"
        output = bounded_child([str(executable), "--input-type=module", "-e", program, str(stage.root / "bundle"), manifest_sha256, str(stage.root / "selected-node-archive")])
        semantic = fields(json_bytes(output), {"version", "platform", "manifestSha256", "nodeSha256"})
        if semantic != {"version": manifest["version"], "platform": platform, "manifestSha256": manifest_sha256, "nodeSha256": NODE[platform][1]}:
            refuse("semantic selection receipt mismatch")
        receipt = {"schema": 1, "version": manifest["version"], "platform": platform, "manifestSha256": manifest_sha256, "nodeSha256": NODE[platform][1], "nodeArchiveBytes": archive_size, "bundleFiles": len(manifest["files"]), "archiveMembers": extraction["members"], "omittedLinks": extraction["omittedLinks"]}
        yield PreparedSelection(bundle, archive, stage.root / "bundle", stage.root / "selected-node-archive", stage.root / "node", manifest_sha256, receipt, source_bundle_identity, source_bundle_inventory, source_archive_identity)


def main():
    if sys.version_info < (3, 11):
        refuse("Python 3.11 or newer required")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify", help="Authenticate selected local bytes without installing")
    verify.add_argument("--bundle-root", required=True)
    verify.add_argument("--manifest-sha256", required=True)
    verify.add_argument("--node-archive", required=True)
    args = parser.parse_args()
    with prepare_install_selection(args.bundle_root, args.manifest_sha256, args.node_archive) as prepared:
        print(json.dumps(prepared.receipt, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, UnicodeError, tarfile.TarError, zipfile.BadZipFile) as error:
        print(f"install bootstrap: {error}", file=sys.stderr)
        raise SystemExit(1)
