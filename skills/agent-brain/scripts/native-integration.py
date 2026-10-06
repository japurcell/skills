#!/usr/bin/env python3
"""Validated native integration and opaque foreground continuation boundary."""
import sys

sys.dont_write_bytecode = True
from agent_brain.native import main

if __name__ == "__main__":
    raise SystemExit(main())
