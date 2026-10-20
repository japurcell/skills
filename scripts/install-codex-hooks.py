#!/usr/bin/env python3

"""Install maintained Codex hook handlers without disturbing user hooks."""

from __future__ import annotations

import argparse
import json
import os
import sys
import stat
from pathlib import Path
from typing import Any

from file_io import atomic_write_bytes
from trusted_hook_launch import PINNED_HOOK_FILES, trusted_command, template_commands, hook_arguments

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from hooks.registrations import (
    DESIRED,
    RETIRED,
    check_parent_directories,
    configuration_lock,
    preflight_status_path,
    reconcile,
    retire_assets,
    validate_status_asset,
    verify_unchanged,
    unique_object,
)


MAINTAINED_HOOK_FILES = tuple(sorted({name for names in DESIRED["codex"].values() for name in names}))
RETIRED_RTK_HOOK_FILES = ("rtk-explicit-codex.py", "rtk-agent-launcher.py")
MAINTAINED_POSIX_COMMANDS = {template_commands("codex", name)["command"] for name in MAINTAINED_HOOK_FILES}
OWNED_HOOK_FILES = MAINTAINED_HOOK_FILES + RETIRED_RTK_HOOK_FILES + ("scan-secrets.py",)
OWNED_POSIX_COMMANDS = {f"python3 ~/.codex/hooks/{name}" for name in OWNED_HOOK_FILES}
OWNED_WINDOWS_COMMANDS = {
    f'py -3 "%USERPROFILE%\\.codex\\hooks\\{name}"'.casefold() for name in OWNED_HOOK_FILES
}
MAINTAINED_EVENTS = ("SessionStart", "PreToolUse", "PostToolUse", "Stop")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge maintained Codex handlers into hooks.json."
    )
    parser.add_argument("--template", required=True, type=Path, help="Maintained hook JSON template.")
    parser.add_argument("--destination", required=True, type=Path, help="User-global hooks.json path.")
    parser.add_argument("--check", action="store_true", help="Validate the merge without writing files.")
    return parser.parse_args()


def load_json_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError("Configuration input must be a regular file")
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"Unable to read {label}: {path}: {exc}") from exc
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label.capitalize()} must contain a JSON object: {path}")
    return value, raw


def validate_groups(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    groups: list[dict[str, Any]] = []
    for index, group in enumerate(value):
        if not isinstance(group, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            raise ValueError(f"{label}[{index}].hooks must be a list")
        for handler_index, handler in enumerate(handlers):
            if not isinstance(handler, dict):
                raise ValueError(f"{label}[{index}].hooks[{handler_index}] must be an object")
        groups.append(group)
    return groups


def template_groups(template: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    hooks = template.get("hooks")
    if not isinstance(hooks, dict):
        raise ValueError("Template hooks must be an object")
    if not hooks or not set(hooks).issubset(MAINTAINED_EVENTS):
        raise ValueError("Template must contain maintained Codex events")
    result = {}
    for event in hooks:
        groups = validate_groups(hooks[event], f"Template hooks.{event}")
        if not groups:
            raise ValueError(f"Template hooks.{event} must contain a group")
        seen: set[str] = set()
        for group in groups:
            if not group["hooks"]:
                raise ValueError(f"Template hooks.{event} contains an empty group")
            for handler in group["hooks"]:
                posix = handler.get("command")
                windows = handler.get("commandWindows")
                if not isinstance(posix, str) or posix not in MAINTAINED_POSIX_COMMANDS:
                    raise ValueError(f"Template hooks.{event} contains an unowned command")
                filename = next(name for name in MAINTAINED_HOOK_FILES if template_commands("codex", name)["command"] == posix)
                if windows != template_commands("codex", filename)["commandWindows"]:
                    raise ValueError(f"Template hooks.{event} has mismatched hook commands")
                if posix in seen:
                    raise ValueError(f"Template repeats maintained handler: {posix}")
                seen.add(posix)
        result[event] = groups
    return result


def merged_config(existing: dict[str, Any], maintained: dict[str, list[dict[str, Any]]], hook_directory: Path) -> dict[str, Any]:
    merged = json.loads(json.dumps(existing))
    hooks = merged.get("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("Existing hooks must be an object")
    for event in set(maintained) | set(RETIRED["codex"]):
        validate_groups(hooks.get(event, []), f"Existing hooks.{event}")
    merged["hooks"] = reconcile(hooks, maintained, "codex", hook_directory)
    return merged


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(path, content, suffix=".tmp", mode=0o600)
    try:
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def main() -> int:
    arguments = parse_arguments()
    try:
        template, _ = load_json_object(arguments.template, "template")
        maintained = template_groups(template)
        hook_directory = arguments.destination.absolute().parent / "hooks"
        for groups in maintained.values():
            for group in groups:
                for handler in group["hooks"]:
                    for filename in PINNED_HOOK_FILES:
                        if handler["command"] == template_commands("codex", filename)["command"]:
                            handler["command"] = trusted_command(hook_directory / filename, "posix", extra=hook_arguments(filename, "codex"))
                            handler["commandWindows"] = trusted_command(hook_directory / filename, "windows", extra=hook_arguments(filename, "codex"))
        check_parent_directories(arguments.destination.absolute().parent, arguments.destination.absolute())
        if arguments.destination.is_symlink():
            raise ValueError(f"Destination must not be a symbolic link: {arguments.destination}")
        preflight_status_path("codex", maintained, hook_directory)
        with configuration_lock(arguments.destination, arguments.check):
            destination_exists = arguments.destination.exists()
            if destination_exists:
                existing, existing_bytes = load_json_object(arguments.destination, "destination")
            else:
                existing, existing_bytes = {}, b""
            merged = merged_config(existing, maintained, hook_directory)
            if not arguments.check:
                validate_status_asset("codex", maintained, hook_directory)
            if destination_exists and merged == existing:
                info = arguments.destination.stat()
                if not arguments.check and (info.st_nlink > 1 or (os.name != "nt" and stat.S_IMODE(info.st_mode) != 0o600)):
                    atomic_write(arguments.destination, existing_bytes)
                if not arguments.check:
                    retire_assets("codex", hook_directory)
                return 0

            if destination_exists:
                backup = arguments.destination.with_name("hooks.json.bak")
                if backup.is_symlink():
                    raise ValueError(f"Backup must not be a symbolic link: {backup}")
            if arguments.check:
                return 0
            serialized = (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            verify_unchanged(arguments.destination, destination_exists, existing_bytes)
            if destination_exists:
                atomic_write(backup, existing_bytes)
            atomic_write(arguments.destination, serialized)
            retire_assets("codex", hook_directory)
            return 0
    except (OSError, ValueError) as exc:
        print(f"Codex hook install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
