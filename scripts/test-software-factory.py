#!/usr/bin/env python3
"""Build and run software-factory checks without installing dependencies or browsers."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", default="all", choices=(
        "all", "fixtures", "store", "lifecycle", "adapters", "workflows", "web",
        "notifications", "learning", "maintenance", "qualification",
    ))
    args, filters = parser.parse_known_args()
    package = Path(__file__).resolve().parents[1] / "packages" / "software-factory"
    npm = shutil.which("npm")
    if npm is None:
        print("software-factory: npm missing; install the qualified development runtime explicitly", file=sys.stderr)
        return 1
    if not (package / "node_modules/typescript/bin/tsc").is_file():
        print("software-factory: dependencies missing; explicitly run npm ci in packages/software-factory", file=sys.stderr)
        return 1
    for script, arguments in (("typecheck", []), ("build", []), (f"test:{args.suite}", filters)):
        result = subprocess.run([npm, "run", script, "--", *arguments], cwd=package, stdin=subprocess.DEVNULL)
        if result.returncode:
            return result.returncode if result.returncode > 0 else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
