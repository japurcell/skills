#!/usr/bin/env python3
"""Merge maintained Copilot or Gemini settings without retiring installed user hooks."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
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


def merge_hooks(existing: dict[str, Any], template: dict[str, Any], provider: str) -> dict[str, Any]:
    current = validate_hooks(existing, provider, "Existing")
    maintained = validate_hooks(template, provider, "Template")
    result = merge_maps(existing, {key: value for key, value in template.items() if key != "hooks"})
    result_hooks = dict(current)
    for event, entries in maintained.items():
        managed_names = {
            name
            for entry in entries
            for handler in ([entry] if provider == "copilot" else entry["hooks"])
            for name in script_names(handler, provider)
        }
        preserved: list[Any] = []
        for entry in current.get(event, []):
            if provider == "copilot":
                if not (script_names(entry, provider) & managed_names):
                    preserved.append(entry)
                continue
            remaining = [
                handler for handler in entry["hooks"]
                if not (script_names(handler, provider) & managed_names)
            ]
            if remaining or not entry["hooks"]:
                preserved.append({**entry, "hooks": remaining})
        result_hooks[event] = [*preserved, *entries]
    if current or maintained or "hooks" in existing or "hooks" in template:
        result["hooks"] = result_hooks
    return result


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if descriptor != -1:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("copilot", "gemini"), required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    try:
        template, _ = load_object(arguments.template, "template")
        destination = arguments.destination
        if destination.is_symlink():
            raise ValueError(f"Destination must not be a symbolic link: {destination}")
        exists = destination.exists()
        existing, old_bytes = load_object(destination, "existing") if exists else ({}, b"")
        merged = merge_hooks(existing, template, arguments.provider)
        if exists and merged == existing:
            if not arguments.check:
                os.chmod(destination, 0o600)
            return 0
        backup = destination.with_name(destination.name + ".bak")
        if exists and backup.is_symlink():
            raise ValueError(f"Backup must not be a symbolic link: {backup}")
        if arguments.check:
            return 0
        if exists:
            atomic_write(backup, old_bytes)
        atomic_write(destination, (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        return 0
    except (OSError, ValueError) as exc:
        print(f"{arguments.provider.capitalize()} install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
