#!/usr/bin/env -S python3 -I -S -B
"""Thin repository installation entrypoint; scan_cli owns parsing and policy."""
import os
from pathlib import Path
import runpy
import sys

if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
    os.execv(sys.executable, [sys.executable, "-I", "-S", "-B", os.path.abspath(__file__), *sys.argv[1:]])

entry = Path(__file__).resolve().with_name("scan-secrets.py")
arguments = sys.argv[1:]
# Top-level help/noargs/version retain the authoritative root's read-only path.
if arguments and arguments[0] not in {"hooks", "help", "--help", "-h", "--version"}:
    arguments.insert(0, "hooks")
sys.argv = [str(entry), *arguments]
runpy.run_path(str(entry), run_name="__main__")
