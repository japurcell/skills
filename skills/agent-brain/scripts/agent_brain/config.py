"""Strict, standard-library validation for the bundled M1 configuration record."""

from __future__ import annotations

import json
import uuid
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .records import AgentBrainConfig, KnowledgeRoot, MappedUnit, StartupRead


class ConfigurationError(ValueError):
    """The selected configuration is unreadable or outside the M1 schema."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigurationError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f"{field} must be a JSON object")
    return value


def _keys(value: dict[str, Any], field: str, expected: set[str]) -> None:
    missing = expected - value.keys()
    unknown = value.keys() - expected
    if missing:
        raise ConfigurationError(f"{field} is missing field(s): {', '.join(sorted(missing))}")
    if unknown:
        raise ConfigurationError(f"{field} has unknown field(s): {', '.join(sorted(unknown))}")


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{field} must be a non-empty string")
    return value


def _relative_path(value: Any, field: str, *, allow_dot: bool = False) -> str:
    value = _string(value, field)
    if allow_dot and value == ".":
        return "."
    if "\\" in value or "\x00" in value:
        raise ConfigurationError(f"{field} must use repository-relative POSIX separators")
    if any(part in (".", "..") for part in value.split("/")):
        raise ConfigurationError(f"{field} must not contain dot segments")
    path = PurePosixPath(value)
    if path.is_absolute() or PureWindowsPath(value).drive or ".." in path.parts:
        raise ConfigurationError(f"{field} must stay within the repository")
    if len(path.parts) == 0:
        raise ConfigurationError(f"{field} must not be empty")
    return path.as_posix()


def _uuid(value: Any, field: str) -> str:
    raw = _string(value, field)
    try:
        parsed = uuid.UUID(raw)
    except (ValueError, AttributeError) as exc:
        raise ConfigurationError(f"{field} must be a UUID") from exc
    if str(parsed) != raw.lower():
        raise ConfigurationError(f"{field} must use canonical UUID formatting")
    return raw.lower()


def load_config(path: Path) -> AgentBrainConfig:
    try:
        source = path.read_bytes().decode("utf-8")
    except FileNotFoundError as exc:
        raise ConfigurationError(f"configuration file not found: {path}") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigurationError(f"cannot read configuration {path}: {exc}") from exc

    try:
        value = json.loads(source, object_pairs_hook=_unique_object)
    except ConfigurationError:
        raise
    except json.JSONDecodeError as exc:
        raise ConfigurationError(
            f"invalid JSON in {path}: {exc.msg} at line {exc.lineno} column {exc.colno}"
        ) from exc

    root = _object(value, "configuration")
    _keys(
        root,
        "configuration",
        {"schema_version", "repository_id", "knowledge_roots", "mapped_units", "startup"},
    )
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise ConfigurationError("configuration schema_version must be 1")
    repository_id = _uuid(root["repository_id"], "repository_id")

    roots_value = root["knowledge_roots"]
    if not isinstance(roots_value, list) or not roots_value:
        raise ConfigurationError("knowledge_roots must be a non-empty array")
    roots: list[KnowledgeRoot] = []
    root_paths: set[str] = set()
    for index, raw_root in enumerate(roots_value):
        field = f"knowledge_roots[{index}]"
        item = _object(raw_root, field)
        _keys(item, field, {"path", "ownership"})
        root_path = _relative_path(item["path"], f"{field}.path", allow_dot=True)
        ownership = _string(item["ownership"], f"{field}.ownership")
        if ownership not in ("read_only", "agent_brain"):
            raise ConfigurationError(f"{field}.ownership must be read_only or agent_brain")
        if root_path in root_paths:
            raise ConfigurationError(f"duplicate knowledge root path {root_path!r}")
        root_paths.add(root_path)
        roots.append(KnowledgeRoot(root_path, ownership))

    units_value = root["mapped_units"]
    if not isinstance(units_value, list) or not units_value:
        raise ConfigurationError("mapped_units must be a non-empty array")
    units: list[MappedUnit] = []
    unit_ids: set[str] = set()
    unit_paths: set[str] = set()
    for index, raw_unit in enumerate(units_value):
        field = f"mapped_units[{index}]"
        item = _object(raw_unit, field)
        _keys(item, field, {"id", "path", "unit"})
        unit_id = _uuid(item["id"], f"{field}.id")
        if unit_id in unit_ids:
            raise ConfigurationError(f"duplicate mapped unit id {unit_id}")
        unit_ids.add(unit_id)
        unit_path = _relative_path(item["path"], f"{field}.path")
        if unit_path in unit_paths:
            raise ConfigurationError(f"duplicate whole-artifact path {unit_path!r}")
        unit_paths.add(unit_path)
        if item["unit"] != "whole":
            raise ConfigurationError(f"{field}.unit must be whole in this CLI")
        if not any(_is_under_root(unit_path, root.path) for root in roots):
            raise ConfigurationError(f"{field}.path must be under a declared knowledge root")
        units.append(MappedUnit(unit_id, unit_path, "whole"))

    startup_value = root["startup"]
    if not isinstance(startup_value, list) or not startup_value:
        raise ConfigurationError("startup must be a non-empty array")
    startup: list[StartupRead] = []
    startup_ids: set[str] = set()
    for index, raw_read in enumerate(startup_value):
        field = f"startup[{index}]"
        item = _object(raw_read, field)
        _keys(item, field, {"id", "loading_mode"})
        unit_id = _uuid(item["id"], f"{field}.id")
        if unit_id not in unit_ids:
            raise ConfigurationError(f"{field}.id references an unknown mapped unit {unit_id}")
        if unit_id in startup_ids:
            raise ConfigurationError(f"duplicate startup reference {unit_id}")
        startup_ids.add(unit_id)
        if item["loading_mode"] != "whole":
            raise ConfigurationError(f"{field}.loading_mode must be whole in this CLI")
        startup.append(StartupRead(unit_id, "whole"))

    return AgentBrainConfig(
        schema_version=1,
        repository_id=repository_id,
        knowledge_roots=tuple(roots),
        mapped_units=tuple(units),
        startup=tuple(startup),
    )


def _is_under_root(path: str, root: str) -> bool:
    candidate = PurePosixPath(path)
    root_path = PurePosixPath(root)
    return root == "." or candidate.is_relative_to(root_path)
