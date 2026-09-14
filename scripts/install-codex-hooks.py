#!/usr/bin/env python3

"""Install the maintained Codex hook group without disturbing user hooks."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


OWNED_POSIX_COMMAND = "python3 ~/.codex/hooks/load-required-skills.py"
OWNED_WINDOWS_COMMAND = 'py -3 "%USERPROFILE%\\.codex\\hooks\\load-required-skills.py"'


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge the maintained Codex required-skills hook into hooks.json."
    )
    parser.add_argument("--template", required=True, type=Path, help="Maintained hook JSON template.")
    parser.add_argument("--destination", required=True, type=Path, help="User-global hooks.json path.")
    return parser.parse_args()


def load_json_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"Unable to read {label}: {path}: {exc}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
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


def template_group(template: dict[str, Any]) -> dict[str, Any]:
    hooks = template.get("hooks")
    if not isinstance(hooks, dict):
        raise ValueError("Template hooks must be an object")
    groups = validate_groups(hooks.get("SessionStart"), "Template hooks.SessionStart")
    if len(groups) != 1:
        raise ValueError("Template hooks.SessionStart must contain exactly one group")
    return groups[0]


def is_owned_handler(handler: dict[str, Any]) -> bool:
    posix = handler.get("command")
    if isinstance(posix, str) and posix.strip() == OWNED_POSIX_COMMAND:
        return True

    windows = handler.get("commandWindows")
    return isinstance(windows, str) and windows.strip().casefold() == OWNED_WINDOWS_COMMAND.casefold()


def merged_config(existing: dict[str, Any], maintained_group: dict[str, Any]) -> dict[str, Any]:
    merged = json.loads(json.dumps(existing))
    hooks = merged.get("hooks")
    if hooks is None:
        hooks = {}
        merged["hooks"] = hooks
    if not isinstance(hooks, dict):
        raise ValueError("Existing hooks must be an object")

    session_start = hooks.get("SessionStart", [])
    groups = validate_groups(session_start, "Existing hooks.SessionStart")
    preserved_groups: list[dict[str, Any]] = []
    for group in groups:
        remaining_handlers = [handler for handler in group["hooks"] if not is_owned_handler(handler)]
        removed_owned_handler = len(remaining_handlers) != len(group["hooks"])
        if remaining_handlers or not removed_owned_handler:
            group["hooks"] = remaining_handlers
            preserved_groups.append(group)
    preserved_groups.append(maintained_group)
    hooks["SessionStart"] = preserved_groups
    return merged


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        try:
            directory_descriptor = os.open(path.parent, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if descriptor != -1:
            os.close(descriptor)
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    arguments = parse_arguments()
    try:
        template, _ = load_json_object(arguments.template, "template")
        maintained_group = template_group(template)
        if arguments.destination.is_symlink():
            raise ValueError(f"Destination must not be a symbolic link: {arguments.destination}")
        destination_exists = arguments.destination.exists()
        if destination_exists:
            existing, existing_bytes = load_json_object(arguments.destination, "destination")
        else:
            existing, existing_bytes = {}, b""
        merged = merged_config(existing, maintained_group)
        if destination_exists and merged == existing:
            os.chmod(arguments.destination, 0o600)
            return 0

        serialized = (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        if destination_exists:
            backup = arguments.destination.with_name("hooks.json.bak")
            if backup.is_symlink():
                raise ValueError(f"Backup must not be a symbolic link: {backup}")
            atomic_write(backup, existing_bytes)
        atomic_write(arguments.destination, serialized)
        return 0
    except (OSError, ValueError) as exc:
        print(f"Codex hook install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
