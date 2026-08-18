#!/usr/bin/env python3

from __future__ import annotations

import sys


def main() -> int:
    sys.stderr.write("\a\n")
    sys.stderr.flush()
    sys.stdout.write("{}\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
