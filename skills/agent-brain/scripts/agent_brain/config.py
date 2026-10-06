"""Strict, standard-library validation for the bundled M1 configuration record."""

from __future__ import annotations

import json
import math
import uuid
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .metadata import _parse_fields
from .records import AgentBrainConfig, KnowledgeRoot, MappedUnit, StartupRead


class ConfigurationError(ValueError):
    """The selected configuration is unreadable or outside the M1 schema."""


def _reject_constant(value: str) -> None:
    raise ConfigurationError(f"non-finite JSON constant {value} is not supported")


def _finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ConfigurationError("JSON number exceeds the supported finite range")
    return parsed


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
        value = json.loads(source, object_pairs_hook=_unique_object, parse_constant=_reject_constant, parse_float=_finite_float)
    except ConfigurationError:
        raise
    except json.JSONDecodeError as exc:
        raise ConfigurationError(
            f"invalid JSON in {path}: {exc.msg} at line {exc.lineno} column {exc.colno}"
        ) from exc
    except (ValueError, OverflowError) as exc:
        raise ConfigurationError(f"unsupported JSON numeric value in {path}: {exc}") from exc

    root = _object(value, "configuration")
    required = {"schema_version", "repository_id", "knowledge_roots", "mapped_units", "startup"}
    optional = {"providers", "checks", "limits", "state_dir", "history_dir", "candidate_dir", "maintenance", "source_ingestion"}
    _keys(root, "configuration", required | (root.keys() & optional))
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
    mapping_selectors: set[tuple[str, str, str | None]] = set()
    for index, raw_unit in enumerate(units_value):
        field = f"mapped_units[{index}]"
        item = _object(raw_unit, field)
        missing = {"id", "path"} - item.keys()
        if missing:
            raise ConfigurationError(f"{field} is missing field(s): {', '.join(sorted(missing))}")
        unit_id = _uuid(item["id"], f"{field}.id")
        if unit_id in unit_ids:
            raise ConfigurationError(f"duplicate mapped unit id {unit_id}")
        unit_ids.add(unit_id)
        unit_path = _relative_path(item["path"], f"{field}.path")
        if not any(_is_under_root(unit_path, root.path) for root in roots):
            raise ConfigurationError(f"{field}.path must be under a declared knowledge root")

        if "unit" in item:
            _keys(item, field, {"id", "path", "unit"})
            if item["unit"] != "whole":
                raise ConfigurationError(f"{field}.unit must be whole")
            selector_type = "document"
            heading = None
            metadata: dict[str, Any] = {
                "kind": "policy", "status": "established", "applies": {},
                "requires": [], "evidence": {},
            }
        else:
            allowed = {"id", "path", "selector", "kind", "status", "applies", "requires", "evidence"}
            unknown = item.keys() - allowed
            required = {"id", "path", "selector", "kind", "status"}
            missing = required - item.keys()
            if missing:
                raise ConfigurationError(f"{field} is missing field(s): {', '.join(sorted(missing))}")
            if unknown:
                raise ConfigurationError(f"{field} has unknown field(s): {', '.join(sorted(unknown))}")
            selector = _object(item["selector"], f"{field}.selector")
            selector_type = _string(selector.get("type"), f"{field}.selector.type")
            if selector_type == "document":
                _keys(selector, f"{field}.selector", {"type"})
                heading = None
            elif selector_type == "section":
                _keys(selector, f"{field}.selector", {"type", "heading"})
                heading = _string(selector["heading"], f"{field}.selector.heading")
            else:
                raise ConfigurationError(f"{field}.selector.type must be document or section")
            try:
                metadata = _parse_fields(
                    {key: item[key] for key in ("kind", "status", "applies", "requires", "evidence")
                     if key in item},
                    is_defaults=True,
                )
            except ValueError as exc:
                raise ConfigurationError(f"{field}: {exc}") from exc
            if "kind" not in metadata or "status" not in metadata:
                raise ConfigurationError(f"{field} must define kind and status")
        key = (unit_path, selector_type, heading)
        if key in mapping_selectors:
            selector_label = "document" if heading is None else f"section {heading!r}"
            raise ConfigurationError(f"duplicate mapped {selector_label} in {unit_path!r}")
        mapping_selectors.add(key)

        normalized_applies = {name: tuple(metadata.get("applies", {}).get(name, ()))
                              for name in ("paths", "concepts", "actions", "dependencies", "providers", "runtimes")}
        units.append(MappedUnit(
            unit_id,
            unit_path,
            selector_type,  # type: ignore[arg-type]
            heading,
            metadata["kind"],  # type: ignore[arg-type]
            metadata["status"],  # type: ignore[arg-type]
            normalized_applies,
            tuple(metadata.get("requires", ())),
            metadata.get("evidence", {}),
        ))

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
        if unit_id in startup_ids:
            raise ConfigurationError(f"duplicate startup reference {unit_id}")
        startup_ids.add(unit_id)
        if item["loading_mode"] not in ("unit", "whole"):
            raise ConfigurationError(f"{field}.loading_mode must be unit or whole")
        startup.append(StartupRead(unit_id, item["loading_mode"]))  # type: ignore[arg-type]

    providers, checks, limits, state_dir = _lifecycle_fields(root)
    history_dir = _relative_path(root.get("history_dir", ".agents/context/history"), "history_dir")
    if history_dir == state_dir or history_dir.startswith(state_dir + "/") or state_dir.startswith(history_dir + "/"):
        raise ConfigurationError("portable history_dir must be separate from ignored runtime state_dir")
    candidate_dir = _relative_path(root.get("candidate_dir", ".agents/context/candidates"), "candidate_dir")
    if any(candidate_dir == path or candidate_dir.startswith(path + "/") or path.startswith(candidate_dir + "/")
           for path in (state_dir, history_dir)):
        raise ConfigurationError("candidate_dir must be separate from runtime state and inverse history")
    defaults = {"enabled": True, "interval_days": 7, "primary_limit": 5,
                "guidance_bytes": 32768, "retention_days": 30}
    maintenance = _object(root.get("maintenance", {}), "maintenance")
    _keys(maintenance, "maintenance", set(maintenance) & set(defaults))
    if "enabled" in maintenance and type(maintenance["enabled"]) is not bool:
        raise ConfigurationError("maintenance.enabled must be boolean")
    for field in ("interval_days", "primary_limit", "guidance_bytes", "retention_days"):
        if field in maintenance:
            maximum = {"interval_days": 366, "primary_limit": 5, "guidance_bytes": 32768, "retention_days": 36500}[field]
            _number(maintenance[field], "maintenance." + field, maximum, integer=True)
    if maintenance.get("retention_days", 30) < 30:
        raise ConfigurationError("maintenance.retention_days must be at least 30")
    ingestion = _object(root.get("source_ingestion", {"enabled": False}), "source_ingestion")
    enabled = ingestion.get("enabled")
    if type(enabled) is not bool:
        raise ConfigurationError("source_ingestion.enabled must be boolean")
    _keys(ingestion, "source_ingestion", {"enabled"} | ({"engine_path", "engine_revision", "bridge_path", "bridge_revision"} if enabled else set()))
    if enabled:
        for field in ("engine_path", "bridge_path"):
            _relative_path(ingestion[field], "source_ingestion." + field)
        for field in ("engine_revision", "bridge_revision"):
            value = ingestion[field]
            if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise ConfigurationError("source_ingestion." + field + " must be SHA-256")
    return AgentBrainConfig(
        schema_version=1,
        repository_id=repository_id,
        knowledge_roots=tuple(roots),
        mapped_units=tuple(units),
        startup=tuple(startup),
        providers=providers, checks=checks, limits=limits, state_dir=state_dir, history_dir=history_dir,
        candidate_dir=candidate_dir, maintenance=defaults | maintenance, source_ingestion=ingestion,
    )


def _is_under_root(path: str, root: str) -> bool:
    candidate = PurePosixPath(path)
    root_path = PurePosixPath(root)
    return root == "." or candidate.is_relative_to(root_path)


LIFECYCLE_EVENTS = (
    "startup", "task", "scope", "checkpoint", "resume", "context_lost", "recover",
    "pause", "cancel", "child_start", "child_stop",
)
BUILTIN_CHECKS = ("guidance", "review_sources")


def _number(value: Any, field: str, maximum: float, *, integer: bool = False) -> float | int:
    if type(value) not in (int, float) or not 0 < value <= maximum:
        raise ConfigurationError(f"{field} must be greater than zero and at most {maximum}")
    if integer and type(value) is not int:
        raise ConfigurationError(f"{field} must be an integer")
    return value


def _strings(value: Any, field: str, *, nonempty: bool = True) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ConfigurationError(f"{field} must be {'a non-empty' if nonempty else 'an'} array")
    items = [_string(item, field) for item in value]
    if len(items) != len(set(items)):
        raise ConfigurationError(f"{field} must not contain duplicate values")
    return items


def _lifecycle_fields(root: dict[str, Any]) -> tuple[dict, dict, dict, str]:
    providers = _object(root.get("providers", {}), "providers")
    for provider_id, provider in providers.items():
        _string(provider_id, "integration id")
        item = _object(provider, f"providers.{provider_id}")
        _keys(item, f"providers.{provider_id}", {
            "enabled", "kind", "core_version", "adapter_version", "schema_version",
            "certification_id", "support_record", "events", "max_attempts",
        })
        if type(item["enabled"]) is not bool or item["kind"] not in ("native", "protocol_fixture"):
            raise ConfigurationError("provider enabled must be boolean and kind must be native or protocol_fixture")
        for field in ("core_version", "adapter_version"):
            _string(item[field], field)
        if type(item["schema_version"]) is not int or item["schema_version"] != 1:
            raise ConfigurationError("provider schema_version must be 1")
        if _uuid(item["certification_id"], "certification_id") != item["certification_id"]:
            raise ConfigurationError("certification_id must use lowercase canonical UUID formatting")
        _relative_path(item["support_record"], "support_record")
        events = _strings(item["events"], "provider events")
        if set(events) - set(LIFECYCLE_EVENTS):
            raise ConfigurationError("provider events contain an unsupported event")
        _number(item["max_attempts"], "provider max_attempts", 3, integer=True)

    checks = _object(root.get("checks", {"required": list(BUILTIN_CHECKS), "trusted": []}), "checks")
    _keys(checks, "checks", {"required", "trusted"})
    required = _strings(checks["required"], "checks.required")
    if not set(BUILTIN_CHECKS).issubset(required):
        raise ConfigurationError("checks.required must include guidance and review_sources")
    if not isinstance(checks["trusted"], list):
        raise ConfigurationError("checks.trusted must be an array")
    checker_ids = set(BUILTIN_CHECKS)
    for checker in checks["trusted"]:
        item = _object(checker, "trusted checker")
        _keys(item, "trusted checker", {"id", "argv", "timeout_seconds"})
        checker_id = _string(item["id"], "checker id")
        if checker_id in checker_ids:
            raise ConfigurationError("checker IDs must be unique and not shadow built-ins")
        checker_ids.add(checker_id)
        if not isinstance(item["argv"], list) or not item["argv"]:
            raise ConfigurationError("checker argv must be a non-empty array")
        for argument in item["argv"]:
            _string(argument, "checker argument")
            if "\x00" in argument:
                raise ConfigurationError("checker argument contains NUL")
        _number(item["timeout_seconds"], "checker timeout_seconds", 60)
    if set(required) - checker_ids:
        raise ConfigurationError("required check is not a built-in or explicitly trusted checker ID")

    defaults = {"lease_seconds": 1800, "contention_seconds": 2, "max_attempts": 3, "check_timeout_seconds": 60}
    limits = _object(root.get("limits", {}), "limits")
    if limits.keys() - defaults.keys():
        raise ConfigurationError("limits contains an unsupported field")
    for field, value in limits.items():
        _number(value, f"limits.{field}", defaults[field], integer=field == "max_attempts")
    limits = defaults | limits
    state_dir = _relative_path(root.get("state_dir", ".agents/context/state"), "state_dir")
    if not state_dir.startswith(".agents/context/") or state_dir == ".agents/context/":
        raise ConfigurationError("state_dir must be local under .agents/context/")
    return providers, checks, limits, state_dir
