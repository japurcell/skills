#!/usr/bin/env python3
"""Validate stable RTK and safely enable its missing-hook warning suppression."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib

MINIMUM_VERSION = (0, 50, 0)
RETIRED_FILES = {
    ".copilot/hooks/scripts/rtk-explicit-copilot.py": "c399c6b18ea635f344a29e13570dc121ab15736b0f96e39c245fe57388a64b02",
    ".gemini/hooks/scripts/rtk-explicit-gemini.py": "e9f3aa3855b39c0f23cc6f25c8f7b203576a0e36b22de128c336109e2e558e2a",
    ".codex/hooks/rtk-explicit-codex.py": "f55706b439c0b922d67795f312bc232946edf07ee9c33b466425e37344f42566",
    ".copilot/hooks/scripts/rtk-agent-launcher.py": "d6d6a01e83ef4fa53b4b36a14c30f41788334ec0490b914dcb1edb9b9fec9bf3",
    ".gemini/hooks/scripts/rtk-agent-launcher.py": "d6d6a01e83ef4fa53b4b36a14c30f41788334ec0490b914dcb1edb9b9fec9bf3",
    ".codex/hooks/rtk-agent-launcher.py": "d6d6a01e83ef4fa53b4b36a14c30f41788334ec0490b914dcb1edb9b9fec9bf3",
}
ASSET_DIGESTS = {
    "rtk-aarch64-apple-darwin.tar.gz": "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321",
    "rtk-x86_64-apple-darwin.tar.gz": "10345f57214b2f9a14f3de1ae1f4235f6eef0669dfed9ab1758a94601b7b829a",
    "rtk-aarch64-unknown-linux-gnu.tar.gz": "4993afdf43a93d09dcce1bef0b0167464f96aa9e973fa5644ca244604a1846b8",
    "rtk-x86_64-unknown-linux-musl.tar.gz": "bf8a1d0e44afb28db9e88859e1f7668c56ecd074264f0c36637c4e07a0c2f1db",
    "rtk-x86_64-pc-windows-msvc.zip": "636262ec8341455c09a3826329f90c92a57e2ef64d8761511eb123f1b84642d7",
}


def regular_destination(path: Path) -> None:
    for entry in (path, *path.parents):
        try:
            info = entry.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Refusing linked RTK destination: {entry}")
        if entry == path and not stat.S_ISREG(info.st_mode):
            raise ValueError(f"RTK destination must be a regular file: {path}")


def regular_directory(path: Path) -> None:
    for entry in (path, *path.parents):
        info = entry.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Refusing linked RTK directory: {entry}")
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"RTK directory is not a directory: {entry}")


def stable_rtk() -> None:
    executable = shutil.which("rtk")
    guidance = "Install or upgrade Rust Token Killer to stable RTK 0.50.0 or newer, then rerun the installer."
    if not executable:
        raise ValueError(f"RTK is missing. {guidance}")
    try:
        result = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError(f"RTK version could not be checked. {guidance}") from error
    match = re.fullmatch(r"rtk (\d+)\.(\d+)\.(\d+)(?:\+[\w.-]+)?\s*", result.stdout)
    if result.returncode or not match or tuple(map(int, match.groups())) < MINIMUM_VERSION:
        raise ValueError(f"RTK does not meet the stable version prerequisite. {guidance}")


def config_path(home: Path, platform: str) -> Path:
    if platform == "darwin":
        return home / "Library/Application Support/rtk/config.toml"
    if platform == "win32":
        appdata = os.environ.get("APPDATA")
        if not appdata or not Path(appdata).is_absolute():
            raise ValueError("Windows RTK setup requires an absolute APPDATA directory.")
        return Path(appdata).resolve() / "rtk/config.toml"
    if platform == "linux":
        return home / ".config/rtk/config.toml"
    raise ValueError(f"Unsupported RTK platform: {platform}")


def updated_config(original: bytes) -> bytes:
    try:
        text = original.decode("utf-8")
        current = tomllib.loads(text)
    except (UnicodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError("Malformed RTK TOML; repair config.toml before installing.") from error
    hooks = current.get("hooks", {})
    if not isinstance(hooks, dict) or ("suppress_hook_warning" in hooks and type(hooks["suppress_hook_warning"]) is not bool):
        raise ValueError("RTK hooks.suppress_hook_warning must be a TOML boolean.")
    if hooks.get("suppress_hook_warning") is True:
        return original
    expected = copy.deepcopy(current)
    expected.setdefault("hooks", {})["suppress_hook_warning"] = True
    newline = "\r\n" if "\r\n" in text else "\n"
    candidates = []
    # A full semantic comparison below makes apparent headers/keys inside strings
    # harmless. Unusual dotted/inline representations fail safely for manual edit.
    if "suppress_hook_warning" in hooks:
        pattern = r"(?m)^([ \t]*suppress_hook_warning[ \t]*=[ \t]*)false([ \t]*(?:#[^\r\n]*)?\r?$)"
        for match in re.finditer(pattern, text):
            candidates.append(text[:match.start()] + match.group(1) + "true" + match.group(2) + text[match.end():])
    else:
        pattern = r"(?m)^[ \t]*\[hooks\][ \t]*(?:#[^\r\n]*)?(?:\r?\n|$)"
        for match in re.finditer(pattern, text):
            prefix = text[:match.end()]
            candidates.append(prefix + ("" if prefix.endswith("\n") else newline) + "suppress_hook_warning = true" + newline + text[match.end():])
        if "hooks" not in current:
            candidates.append(text + ("" if not text or text.endswith("\n") else newline) + "[hooks]" + newline + "suppress_hook_warning = true" + newline)
    valid = []
    for candidate in candidates:
        try:
            if tomllib.loads(candidate) == expected:
                valid.append(candidate)
        except tomllib.TOMLDecodeError:
            continue
    if len(valid) != 1:
        raise ValueError("Ambiguous RTK TOML layout; set [hooks] suppress_hook_warning = true manually, then rerun.")
    return valid[0].encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    regular_destination(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def retire_owned(home: Path) -> None:
    for relative, expected in RETIRED_FILES.items():
        path = home / relative
        if not path.exists() and not path.is_symlink():
            continue
        try:
            regular_destination(path)
            if file_digest(path) == expected:
                path.unlink()
            else:
                print(f"RTK migration left modified file for manual review: {path}", file=sys.stderr)
        except (OSError, ValueError) as error:
            print(f"RTK migration left file for manual review: {path}: {error}", file=sys.stderr)

    bundle = home / ".agents/rtk/dev-0.50.0-rc.451"
    if not bundle.exists() and not bundle.is_symlink():
        return
    try:
        regular_directory(bundle.parent)
        if bundle.is_symlink() or not bundle.is_dir():
            raise ValueError("not a regular directory")
        names = {entry.name for entry in bundle.iterdir()}
        if names not in ({"rtk", "receipt.json"}, {"rtk.exe", "receipt.json"}):
            raise ValueError("unexpected bundle contents")
        binary = bundle / ("rtk.exe" if "rtk.exe" in names else "rtk")
        receipt_path = bundle / "receipt.json"
        regular_destination(binary)
        regular_destination(receipt_path)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if (not isinstance(receipt, dict) or receipt.get("tag") != "dev-0.50.0-rc.451"
                or not isinstance(receipt.get("asset"), str)
                or receipt.get("asset_sha256") != ASSET_DIGESTS.get(receipt.get("asset"))
                or receipt.get("binary_sha256") != file_digest(binary)):
            raise ValueError("receipt verification failed")
        binary.unlink()
        receipt_path.unlink()
        bundle.rmdir()
    except (OSError, ValueError) as error:
        print(f"RTK migration left prerelease bundle for manual review: {bundle}: {error}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--platform", choices=("darwin", "linux", "win32"), default=sys.platform)
    parser.add_argument("--check", action="store_true", help="Validate without changing any installed file.")
    args = parser.parse_args()
    try:
        stable_rtk()
        home = args.home.resolve()
        path = config_path(home, args.platform)
        regular_destination(path)
        original = path.read_bytes() if path.exists() else b""
        updated = updated_config(original)
        if updated != original:
            backup = path.with_suffix(".toml.bak")
            regular_destination(backup)
            if path.exists() and backup.exists():
                raise ValueError(f"RTK backup already exists; preserve it and review manually: {backup}")
            if not args.check:
                if path.exists():
                    descriptor = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(descriptor, "wb") as stream:
                        stream.write(original)
                        stream.flush()
                        os.fsync(stream.fileno())
                atomic_write(path, updated)
        if not args.check:
            retire_owned(home)
        return 0
    except (OSError, ValueError) as error:
        print(f"RTK setup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
