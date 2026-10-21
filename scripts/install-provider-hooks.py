#!/usr/bin/env python3
"""Merge maintained Copilot or Gemini settings without retiring installed user hooks."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

from file_io import atomic_write_bytes
from trusted_hook_launch import pin_provider_commands

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from hooks.registrations import (
    check_parent_directories,
    configuration_lock,
    preflight_status_path,
    reconcile,
    retire_assets,
    validate_status_asset,
    verify_unchanged,
)


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError("Configuration input must be a regular file")
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Invalid {label} JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return value, raw


def script_names(handler: dict[str, Any], provider: str) -> set[str]:
    keys = ("bash", "powershell") if provider == "copilot" else ("command",)
    names: set[str] = set()
    pattern = re.compile(rf"/\.{provider}/hooks/scripts/([\w.-]+\.py)(?=$|[\s\"'])")
    for key in keys:
        command = handler.get(key)
        if command is None:
            continue
        if not isinstance(command, str):
            raise ValueError(f"hook {key} must be a string")
        names.update(pattern.findall(command.replace("\\", "/")))
    return names


def validate_hooks(config: dict[str, Any], provider: str, label: str) -> dict[str, list[Any]]:
    hooks = config.get("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"{label} hooks must be an object")
    for event, entries in hooks.items():
        if provider == "gemini" and event == "disabled":
            if not isinstance(entries, list) or not all(isinstance(name, str) for name in entries):
                raise ValueError(f"{label} hooks.disabled must be a list of names")
            continue
        if not isinstance(entries, list):
            raise ValueError(f"{label} hooks.{event} must be a list")
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError(f"{label} hooks.{event}[{index}] must be an object")
            handlers = [entry] if provider == "copilot" else entry.get("hooks")
            if not isinstance(handlers, list):
                raise ValueError(f"{label} hooks.{event}[{index}].hooks must be a list")
            for handler in handlers:
                if not isinstance(handler, dict):
                    raise ValueError(f"{label} hooks.{event}[{index}] contains a non-object hook")
                names = script_names(handler, provider)
                retired = names & {"repository-state.py", "markdown-health.py"}
                if retired and len(names) != 1:
                    raise ValueError(f"{label} hooks.{event}[{index}] has ambiguous retired commands")
    return hooks


def merge_maps(existing: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    result = dict(existing)
    for key, value in template.items():
        old = result.get(key)
        result[key] = merge_maps(old, value) if isinstance(old, dict) and isinstance(value, dict) else value
    return result


def merge_hooks(existing: dict[str, Any], template: dict[str, Any], provider: str, home: Path) -> dict[str, Any]:
    current = validate_hooks(existing, provider, "Existing")
    maintained = validate_hooks(template, provider, "Template")
    result = merge_maps(existing, {key: value for key, value in template.items() if key != "hooks"})
    if provider == "copilot" and "disableAllHooks" in existing:
        result["disableAllHooks"] = existing["disableAllHooks"]
    directory = home / f".{provider}/hooks/scripts"
    result_hooks = reconcile(current, maintained, provider, directory)
    if current or maintained or "hooks" in existing or "hooks" in template:
        result["hooks"] = result_hooks
    return result



def atomic_write(path: Path, content: bytes, home: Path) -> None:
    check_parent_directories(home, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    check_parent_directories(home, path)
    atomic_write_bytes(path, content, suffix=".tmp", mode=0o600)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("copilot", "gemini"), required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--home", type=Path, required=True, help="Install home directory boundary.")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    try:
        template, _ = load_object(arguments.template, "template")
        validate_hooks(template, arguments.provider, "Template")
        home = Path(os.path.abspath(arguments.home))
        hook_directory = home / f".{arguments.provider}/hooks/scripts"
        pin_provider_commands(template, arguments.provider, home)
        destination = Path(os.path.abspath(arguments.destination))
        check_parent_directories(home, destination)
        if destination.is_symlink():
            raise ValueError(f"Destination must not be a symbolic link: {destination}")
        preflight_status_path(arguments.provider, template.get("hooks", {}), hook_directory)
        with configuration_lock(destination, arguments.check):
            exists = destination.exists()
            existing, old_bytes = load_object(destination, "existing") if exists else ({}, b"")
            merged = merge_hooks(existing, template, arguments.provider, home)
            if not arguments.check:
                validate_status_asset(arguments.provider, template.get("hooks", {}), hook_directory)
            if exists and merged == existing:
                info = destination.stat()
                needs_private_copy = info.st_nlink > 1 or (
                    os.name != "nt" and stat.S_IMODE(info.st_mode) != 0o600
                )
                if needs_private_copy and not arguments.check:
                    atomic_write(destination, old_bytes, home)
            else:
                backup = destination.with_name(destination.name + ".bak")
                if exists and backup.is_symlink():
                    raise ValueError(f"Backup must not be a symbolic link: {backup}")
                if not arguments.check:
                    verify_unchanged(destination, exists, old_bytes)
                    if exists:
                        atomic_write(backup, old_bytes, home)
                    atomic_write(destination, (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8"), home)
            if not arguments.check:
                retire_assets(arguments.provider, hook_directory)
            return 0
    except (OSError, ValueError) as exc:
        print(f"{arguments.provider.capitalize()} install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
