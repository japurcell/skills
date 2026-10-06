"""Pinned immutable software inventory, explicit interpreters and shell commands."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import sqlite3
import stat
import subprocess
import sys

from . import __version__
from .state import LifecycleError

ADAPTER_VERSION = "native-1"
MANIFEST = "software.json"


def checked_absolute(path: Path, *, directory: bool = False) -> Path:
    if not path.is_absolute() or ".." in path.parts:
        raise LifecycleError("SOFTWARE_INVALID", "software paths must be explicit absolute paths")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink() or (current.exists() and getattr(current.lstat(), "st_file_attributes", 0) & 0x400):
            raise LifecycleError("SOFTWARE_INVALID", "linked or reparse software paths are ambiguous")
    if path.exists() and not (path.is_dir() if directory else path.is_file()):
        raise LifecycleError("SOFTWARE_INVALID", "software destination is not a regular file or directory")
    return path


def inventory(bundle: Path) -> dict[str, str]:
    checked_absolute(bundle, directory=True)
    result = {}
    for path in sorted(bundle.rglob("*")):
        relative = path.relative_to(bundle).as_posix()
        if "__pycache__" in path.parts or path.suffix == ".pyc" or relative == MANIFEST:
            continue
        checked_absolute(path, directory=path.is_dir())
        if path.is_file():
            if path.stat().st_size > 8 * 1024 * 1024 or len(result) >= 2000:
                raise LifecycleError("SOFTWARE_INVALID", "software inventory exceeds its bounded size")
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def inventory_revision(files: dict) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def compatible_interpreter(path: Path) -> dict:
    # Discovery resolves an executable link once; all launchers pin its actual target.
    path = path.resolve(strict=True)
    checked_absolute(path)
    program = "import json,sys,sqlite3; print(json.dumps({'python':list(sys.version_info[:3]),'sqlite':list(sqlite3.sqlite_version_info),'executable':sys.executable}))"
    try:
        result = subprocess.run([str(path), "-I", "-c", program], capture_output=True, text=True, timeout=5, check=True)
        record = json.loads(result.stdout)
        if tuple(record["python"]) < (3, 12) or tuple(record["sqlite"]) < (3, 15, 2):
            raise ValueError("unsupported runtime")
        record["executable"] = str(checked_absolute(Path(record["executable"]).resolve(strict=True)))
        return record
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        raise LifecycleError("RUNTIME_UNSUPPORTED", "select an existing Python 3.12+ interpreter with SQLite 3.15.2+; nothing is downloaded") from exc


def validate_software(pin: dict) -> dict:
    if set(pin) != {"bundle_path", "manifest_revision", "core_version", "adapter_version", "schema_version"}:
        raise LifecycleError("SOFTWARE_INVALID", "software pin has unsupported fields")
    bundle = checked_absolute(Path(pin["bundle_path"]), directory=True)
    manifest = checked_absolute(bundle / MANIFEST)
    from .lifecycle import read_json
    raw = manifest.read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin["manifest_revision"]:
        raise LifecycleError("SOFTWARE_UNAVAILABLE", "the exact pinned software manifest is unavailable; reinstall that reviewed bundle")
    record = read_json(raw.decode("utf-8"))
    if set(record) != {"schema_version", "core_version", "adapter_version", "inventory_revision", "files", "interpreter", "launcher", "bundle_path"}:
        raise LifecycleError("SOFTWARE_INVALID", "installed software manifest is malformed")
    for name in ("schema_version", "core_version", "adapter_version", "bundle_path"):
        if record[name] != pin[name]:
            raise LifecycleError("SOFTWARE_UNAVAILABLE", "the exact pinned core/adapter/schema bundle is unavailable")
    if record["core_version"] != __version__ or record["adapter_version"] != ADAPTER_VERSION or record["schema_version"] != 1:
        raise LifecycleError("SOFTWARE_UNAVAILABLE", "the requested pinned software versions are unavailable; no substitution is allowed")
    if any("__pycache__" in path.parts or path.suffix == ".pyc" for path in bundle.rglob("*")):
        raise LifecycleError("SOFTWARE_UNAVAILABLE", "unpinned installed bytecode is unavailable; restore the immutable bundle")
    if record["files"] != inventory(bundle) or record["inventory_revision"] != inventory_revision(record["files"]):
        raise LifecycleError("SOFTWARE_UNAVAILABLE", "installed immutable software bytes changed; restore the exact reviewed bundle")
    checked_absolute(Path(record["interpreter"]["executable"]))
    return record


def software_path(config, root: Path, path: str) -> Path:
    if Path(path).is_absolute():
        if not config.software:
            raise LifecycleError("SOFTWARE_INVALID", "external software must have an exact configured immutable pin")
        record = validate_software(config.software)
        target = checked_absolute(Path(path), directory=Path(path).is_dir())
        bundle = Path(record["bundle_path"])
        if target != bundle and not target.is_relative_to(bundle):
            raise LifecycleError("SOFTWARE_INVALID", "external path differs from the configured immutable bundle")
        return target
    from .state import local_path
    return local_path(root, path)


def command(argv: list[str], shell: str = "posix") -> str:
    if shell == "powershell":
        return "& " + " ".join("'" + word.replace("'", "''") + "'" for word in argv)
    if shell != "posix":
        raise LifecycleError("SHELL_UNSUPPORTED", "choose the supported posix or powershell command representation")
    return shlex.join(argv)


def command_words(source: str, shell: str) -> list[str]:
    if shell == "posix":
        from .native import literal_command_words
        return literal_command_words(source)
    # Accept only our literal PowerShell representation, never an evaluated expression.
    if not source.startswith("& ") or any(char in source for char in "\r\n"):
        raise ValueError("unsupported PowerShell invocation")
    words = []
    index = 2
    while index < len(source):
        if source[index] != "'":
            end = source.find(" ", index)
            end = len(source) if end == -1 else end
            word = source[index:end]
            if not word or any(not (char.isascii() and (char.isalnum() or char in "-_")) for char in word):
                raise ValueError("PowerShell arguments must be literal strings or simple option tokens")
            words.append(word)
            index = end + 1
            continue
        index += 1
        word = ""
        while index < len(source):
            if source[index:index + 2] == "''":
                word += "'"
                index += 2
            elif source[index] == "'":
                index += 1
                break
            else:
                word += source[index]
                index += 1
        else:
            raise ValueError("unclosed PowerShell literal")
        words.append(word)
        if index < len(source):
            if source[index] != " ":
                raise ValueError("PowerShell composition is unsupported")
            index += 1
    return words
