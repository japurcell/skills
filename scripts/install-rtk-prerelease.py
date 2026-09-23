#!/usr/bin/env python3
"""Install a checksum-verified RTK prerelease beside the user's stable RTK."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import stat
import sys
import tarfile
import tempfile
import urllib.request
import zipfile


TAG = "dev-0.50.0-rc.451"
BASE = f"https://github.com/rtk-ai/rtk/releases/download/{TAG}"
# Official release checksums.txt, also corroborated by GitHub asset digests.
ASSETS = {
    ("Darwin", "arm64"): ("rtk-aarch64-apple-darwin.tar.gz", "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321"),
    ("Darwin", "x86_64"): ("rtk-x86_64-apple-darwin.tar.gz", "10345f57214b2f9a14f3de1ae1f4235f6eef0669dfed9ab1758a94601b7b829a"),
    ("Linux", "aarch64"): ("rtk-aarch64-unknown-linux-gnu.tar.gz", "4993afdf43a93d09dcce1bef0b0167464f96aa9e973fa5644ca244604a1846b8"),
    ("Linux", "x86_64"): ("rtk-x86_64-unknown-linux-musl.tar.gz", "bf8a1d0e44afb28db9e88859e1f7668c56ecd074264f0c36637c4e07a0c2f1db"),
    ("Windows", "AMD64"): ("rtk-x86_64-pc-windows-msvc.zip", "636262ec8341455c09a3826329f90c92a57e2ef64d8761511eb123f1b84642d7"),
}
MAX_ARCHIVE_BYTES = 32 * 1024 * 1024


def archive_bytes(name: str, supplied: Path | None) -> bytes:
    if supplied is not None:
        with supplied.open("rb") as stream:
            return stream.read(MAX_ARCHIVE_BYTES + 1)
    with urllib.request.urlopen(f"{BASE}/{name}", timeout=20) as response:
        data = response.read(MAX_ARCHIVE_BYTES + 1)
    return data


def executable_bytes(name: str, archive: bytes) -> bytes:
    member = "rtk.exe" if name.endswith(".zip") else "rtk"
    if name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            matches = [item for item in bundle.infolist() if item.filename == member and not item.is_dir()]
            if len(matches) != 1 or matches[0].file_size > MAX_ARCHIVE_BYTES:
                raise ValueError("RTK executable missing or oversized in archive")
            return bundle.read(matches[0])
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        matches = [item for item in bundle.getmembers() if item.name == member and item.isfile()]
        if len(matches) != 1 or matches[0].size > MAX_ARCHIVE_BYTES:
            raise ValueError("RTK executable missing or oversized in archive")
        stream = bundle.extractfile(matches[0])
        if stream is None:
            raise ValueError("RTK executable could not be read")
        return stream.read()


def install(home: Path, system: str, machine: str, supplied: Path | None) -> Path:
    asset = ASSETS.get((system, machine))
    if asset is None:
        raise ValueError(f"No verified RTK asset for {system}/{machine}")
    name, digest = asset
    archive = archive_bytes(name, supplied)
    if len(archive) > MAX_ARCHIVE_BYTES or hashlib.sha256(archive).hexdigest() != digest:
        raise ValueError(f"RTK archive checksum mismatch for {name}")
    binary = executable_bytes(name, archive)
    destination = home / ".agents" / "rtk" / TAG
    for parent in (home, home / ".agents", home / ".agents" / "rtk", destination):
        if parent.is_symlink():
            raise ValueError("RTK destination must not contain symbolic links")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / ("rtk.exe" if system == "Windows" else "rtk")
    receipt = destination / "receipt.json"
    if target.is_symlink() or receipt.is_symlink():
        raise ValueError("RTK destination must not be a symbolic link")
    descriptor, temporary_name = tempfile.mkstemp(prefix=".rtk-stage-", dir=destination)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(binary)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        os.replace(temporary, target)
        receipt.write_text(json.dumps({"tag": TAG, "asset": name, "asset_sha256": digest, "binary_sha256": hashlib.sha256(binary).hexdigest()}) + "\n", encoding="utf-8")
    finally:
        temporary.unlink(missing_ok=True)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--platform", choices=["darwin-arm64", "darwin-x86_64", "linux-aarch64", "linux-x86_64", "windows-amd64"])
    args = parser.parse_args()
    systems = {
        "darwin-arm64": ("Darwin", "arm64"), "darwin-x86_64": ("Darwin", "x86_64"),
        "linux-aarch64": ("Linux", "aarch64"), "linux-x86_64": ("Linux", "x86_64"),
        "windows-amd64": ("Windows", "AMD64"),
    }
    system, machine = systems[args.platform] if args.platform else (platform.system(), platform.machine())
    try:
        target = install(args.home, system, machine, args.archive)
    except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as error:
        print(f"RTK prerelease install failed: {error}", file=sys.stderr)
        return 1
    print(f"Installed verified {TAG} at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
