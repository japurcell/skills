#!/usr/bin/env -S python3 -I -S -B
"""Isolated source entrypoint for explicit secret checkpoints."""
from __future__ import annotations

import os
import sys

if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
    os.execv(sys.executable, [sys.executable, "-I", "-S", "-B", os.path.abspath(__file__), *sys.argv[1:]])

import importlib.util
from pathlib import Path
import types

ENTRY = Path(__file__).resolve()
RUNTIME = ENTRY.parent.parent / "hooks" / "runtime"
PACKAGE = "_scan_checkpoint"
package = types.ModuleType(PACKAGE)
package.__path__ = []
sys.modules[PACKAGE] = package


def load(name, source=None):
    spec = importlib.util.spec_from_file_location(PACKAGE + "." + name, RUNTIME / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    source = (RUNTIME / (name + ".py")).read_bytes() if source is None else source
    exec(compile(source, str(RUNTIME / (name + ".py")), "exec"), module.__dict__)
    load.sources[name] = source
    return module


load.sources = {}


try:
    cli = load("scan_cli")
except Exception:
    # The parser itself is unavailable. Do not expose import paths or errors.
    if "--json" in sys.argv[1:]:
        try:
            if next((item for item in sys.argv[1:] if item in {"check", "status", "help"}), None) == "status":
                os.write(1, b'{"schema":"scan_secrets_status_v1","historical":true,"authorizes_publication":false,"last_scan":null,"outcome":"unavailable","reason":"runtime_unavailable","phase":"initialization","recovery":"Restore the scanner runtime."}\n')
            else:
                os.write(1, b'{"schema":"scan_secrets_check_v1","outcome":"incomplete","coverage_complete":false,"reason":"runtime_unavailable","phase":"initialization","recovery":"Restore the scanner runtime."}\n')
        except BrokenPipeError:
            pass
    elif next((item for item in sys.argv[1:] if item in {"check", "status", "help"}), None) == "status":
        os.write(2, b"scan-secrets: last scan unavailable; saved time and scope unavailable; runtime_unavailable. Restore the scanner runtime.\n")
    else:
        os.write(2, b"scan-secrets: runtime_unavailable. Restore the scanner runtime.\n")
    raise SystemExit(2)
raise SystemExit(cli.main(sys.argv[1:], load=load, runtime=RUNTIME, entry=ENTRY))
