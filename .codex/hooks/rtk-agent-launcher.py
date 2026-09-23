#!/usr/bin/env python3
# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.
"""Launch the verified side-by-side RTK with child-only warning suppression."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


APPROVED_ASSET_DIGESTS = {
    "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321",
    "10345f57214b2f9a14f3de1ae1f4235f6eef0669dfed9ab1758a94601b7b829a",
    "4993afdf43a93d09dcce1bef0b0167464f96aa9e973fa5644ca244604a1846b8",
    "bf8a1d0e44afb28db9e88859e1f7668c56ecd074264f0c36637c4e07a0c2f1db",
    "636262ec8341455c09a3826329f90c92a57e2ef64d8761511eb123f1b84642d7",
}


def verified(binary: Path) -> bool:
    try:
        receipt = json.loads((binary.parent / "receipt.json").read_text(encoding="utf-8"))
        return (receipt.get("tag") == "dev-0.50.0-rc.451"
                and receipt.get("asset_sha256") in APPROVED_ASSET_DIGESTS
                and hashlib.sha256(binary.read_bytes()).hexdigest() == receipt.get("binary_sha256"))
    except (OSError, ValueError):
        return False


def main() -> int:
    binary = Path.home() / ".agents/rtk/dev-0.50.0-rc.451" / ("rtk.exe" if os.name == "nt" else "rtk")
    if not binary.is_file() or not verified(binary):
        print("Verified RTK prerelease is not installed", file=sys.stderr)
        return 127
    environment = os.environ.copy()
    environment["RTK_SUPPRESS_HOOK_WARNING"] = "1"
    try:
        return subprocess.call([str(binary), *sys.argv[1:]], env=environment)
    except OSError as error:
        print(f"Unable to start verified RTK prerelease: {error}", file=sys.stderr)
        return 127


if __name__ == "__main__":
    raise SystemExit(main())
