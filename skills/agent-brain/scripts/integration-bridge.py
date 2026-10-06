#!/usr/bin/env python3
"""Internal normalized event entrypoint for configured integrations."""
import sys

sys.dont_write_bytecode = True

from agent_brain.lifecycle import bridge_main

if __name__ == "__main__":
    raise SystemExit(bridge_main())
