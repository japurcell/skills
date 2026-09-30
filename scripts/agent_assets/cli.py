"""Public command parsing and output streams."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import sys
import subprocess

from .core import install
from .sources import AssetError


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("install", help="Install committed skill files into a team repository.", allow_abbrev=False)
    sub.add_argument("--repo", help="Target Git repository (defaults to the current Git root).")
    sub.add_argument("--client", action="append", required=True, choices=("codex",))
    sub.add_argument("--asset", action="append", required=True)
    sub.add_argument("--source", default=str(Path(__file__).resolve().parents[2]))
    refs = sub.add_mutually_exclusive_group()
    refs.add_argument("--branch")
    refs.add_argument("--revision")
    sub.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)
    def failure(code, message, exit_code):
        print(f"{code}: {message}", file=sys.stderr)
        if args.format == "json":
            print(json.dumps({"schema_version": 1, "command": args.command, "source": None, "selection": None,
                              "changes": {"added": 0, "updated": 0, "retained": 0, "removed": 0},
                              "conflicts": [{"code": code, "message": message}] if exit_code == 1 else [],
                              "warnings": [] if exit_code == 1 else [{"code": code, "message": message}]}, sort_keys=True))
        return exit_code
    try:
        report = install(args)
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        else:
            print(f"Installed for {', '.join(args.client)} at {report['source']['commit']}: {report['changes']}")
        return 0
    except AssetError as error:
        return failure(error.code, str(error), error.exit_code)
    except subprocess.TimeoutExpired:
        return failure("ASSET_SOURCE_ERROR", "Git acquisition timed out; check source access and rerun.", 2)
    except (OSError, ValueError, KeyError, TypeError) as error:
        return failure("ASSET_INPUT_INVALID", "Invalid input or inaccessible file; check catalog, records, and directory permissions.", 2)
