#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    payload = sys.stdin.buffer.read()
    if not payload.startswith(b"{") or not payload.rstrip().endswith(b"}"):
        sys.stdout.buffer.write(b"{}\n")
        return 0

    try:
        result = subprocess.run(["rtk", "hook", "gemini"], input=payload, capture_output=True, check=False)
    except Exception:
        sys.stdout.buffer.write(b"{}\n")
        return 0

    if result.returncode != 0 or not result.stdout.startswith(b"{"):
        sys.stdout.buffer.write(b"{}\n")
        return 0

    sys.stdout.buffer.write(result.stdout if result.stdout.endswith(b"\n") else result.stdout + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
