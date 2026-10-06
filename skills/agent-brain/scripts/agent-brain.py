#!/usr/bin/env python3
"""Source-checkout entrypoint for the agent-brain CLI."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

sys.dont_write_bytecode = True

from agent_brain.cli import main


if __name__ == "__main__":
    if sys.argv[1:2] == ["--native-foreground"]:
        from agent_brain.native import main as native_main
        raise SystemExit(native_main(["foreground", *sys.argv[2:]]))
    raise SystemExit(main())
