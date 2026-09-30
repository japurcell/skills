"""Public command parsing and output streams."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import sys
import subprocess

from .core import install, status
from .sources import AssetError, acquire
from .catalog import listing
from .providers import CLIENTS


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("install", help="Install selected committed skills and supporting assets into team, private, or personal native paths.", allow_abbrev=False)
    sub.add_argument("--repo", help="Target Git repository (defaults to the current Git root).")
    sub.add_argument("--preview", action="store_true", help="Plan changes without writing target files.")
    sub.add_argument("--adopt", action="store_true", help="Adopt only exact verified personal copies at the selected immutable revision.")
    sub.add_argument("--client", action="append", required=True, choices=CLIENTS)
    sub.add_argument("--asset", action="append", default=[])
    sub.add_argument("--bundle", action="append", default=[])
    sub.add_argument("--source", default=str(Path(__file__).resolve().parents[2]))
    refs = sub.add_mutually_exclusive_group()
    refs.add_argument("--branch")
    refs.add_argument("--revision")
    sub.add_argument("--format", choices=("human", "json"), default="human")
    sub = commands.add_parser("list", help="List committed catalog assets and dependency availability.", allow_abbrev=False)
    sub.add_argument("--client", action="append", default=[], choices=CLIENTS)
    sub.add_argument("--source", default=str(Path(__file__).resolve().parents[2]))
    refs = sub.add_mutually_exclusive_group()
    refs.add_argument("--branch")
    refs.add_argument("--revision")
    sub.add_argument("--format", choices=("human", "json"), default="human")
    for command in ("update", "restore"):
        sub = commands.add_parser(command, help="Update saved selection." if command == "update" else "Restore the exact recorded revision.", allow_abbrev=False)
        sub.add_argument("--repo")
        sub.add_argument("--preview", action="store_true")
        sub.add_argument("--format", choices=("human", "json"), default="human")
        refs = sub.add_mutually_exclusive_group()
        refs.add_argument("--branch")
        refs.add_argument("--revision")
    sub = commands.add_parser("status", help="Inspect recorded files offline; --check exits 1 on drift and never repairs.", allow_abbrev=False)
    sub.add_argument("--repo")
    sub.add_argument("--check", action="store_true")
    sub.add_argument("--format", choices=("human", "json"), default="human")
    for name, command in commands.choices.items():
        if name == "list":
            continue
        command.add_argument("--scope", choices=("repo", "user"), default="repo")
        command.add_argument("--mode", choices=("team", "local"), default="team",
                             help="Local mode refuses changes to tracked native files; no universal local-settings overlay is assumed.")
        command.add_argument("--codex-home", help="Explicit personal Codex home for agent outputs; repeat for lifecycle commands.")
        command.add_argument("--home", help="Personal destination home (requires --scope user).")
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
        if args.command == "status":
            report = status(args)
        elif args.command == "list":
            with acquire(args.source, args.branch, args.revision) as snapshot:
                catalog, _ = snapshot.catalog()
                report = listing(snapshot, catalog, sorted(set(args.client)))
        elif args.command == "install" and not args.asset and not args.bundle:
            raise AssetError("ASSET_SELECTION_INVALID", "Select at least one --asset or --bundle.")
        else:
            report = install(args)
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        elif args.command != "list":
            print(f"{args.command.title()} for {', '.join(report['selection']['clients'])} at {report['source']['commit']}: {report['changes']}")
            print(f"Requested assets: {', '.join(report['selection']['assets']) or '(none)'}; bundles: {', '.join(report['selection']['bundles']) or '(none)'}")
            print(f"Resolved assets: {', '.join(report['resolved_assets'])}")
            if args.command == "status":
                print("Verification: " + ("clean" if report["verification"]["passed"] else "drift"))
                for item in report["verification"]["drift"]:
                    print(item["destination"] + ": " + item["reason"])
            for warning in report["warnings"]:
                print("Warning: " + warning, file=sys.stderr)
        else:
            for asset_id, asset in report["assets"].items():
                print(f"{asset_id}: {'available' if asset['available'] else 'unavailable'}")
                print("  Required: " + (", ".join(asset["requires"]) or "(none)"))
                for problem in asset["missing"]:
                    print("  " + " -> ".join(problem["chain"]) + ": " + problem["reason"])
                for restriction in asset["restrictions"]:
                    print("  " + restriction["code"] + ": " + restriction["reason"])
        if args.command == "status" and args.check and not report["verification"]["passed"]:
            print("ASSET_DRIFT: Recorded installation differs; inspect verification.drift and resolve explicitly.", file=sys.stderr)
            return 1
        return 0
    except AssetError as error:
        return failure(error.code, str(error), error.exit_code)
    except subprocess.TimeoutExpired:
        return failure("ASSET_SOURCE_ERROR", "Git acquisition timed out; check source access and rerun.", 2)
    except (OSError, ValueError, KeyError, TypeError) as error:
        return failure("ASSET_INPUT_INVALID", "Invalid input or inaccessible file; check catalog, records, and directory permissions.", 2)
