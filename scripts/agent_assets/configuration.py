"""Semantic ownership of native hook registrations, preserving unrelated settings."""

from copy import deepcopy
import tomllib

from .sources import AssetError, canonical, digest, read_json

PATHS = {"codex": ".codex/hooks.json", "copilot": ".github/hooks/agent-assets.json", "gemini": ".gemini/settings.json"}


def parse(data):
    value = read_json(data, "ASSET_CONFIG_INVALID") if data is not None else {}
    if not isinstance(value, dict) or not isinstance(value.get("hooks", {}), dict):
        raise AssetError("ASSET_CONFIG_INVALID", "Native hook configuration must contain an object.")
    if any(not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries)
           for entries in value.get("hooks", {}).values()):
        raise AssetError("ASSET_CONFIG_INVALID", "Native hook events must contain object arrays.")
    for entries in value.get("hooks", {}).values():
        for entry in entries:
            if "hooks" in entry and (not isinstance(entry["hooks"], list) or any(not isinstance(handler, dict) for handler in entry["hooks"])):
                raise AssetError("ASSET_CONFIG_INVALID", "Native hook groups must contain handler objects.")
    return value


def entries_match(data, owned):
    value = parse(data)
    return (all(key in value and canonical(value[key]) == canonical(expected) for key, expected in owned.items() if key != "hooks")
            and all(sum(canonical(candidate) == canonical(entry) for candidate in value.get("hooks", {}).get(event, [])) == 1
                    for event, entries in owned["hooks"].items() for entry in entries))


def without_owned(data, owned):
    value = deepcopy(parse(data))
    if any(key not in value or canonical(value[key]) != canonical(expected) for key, expected in owned.items() if key != "hooks"):
        raise AssetError("ASSET_CONFLICT", "Managed native configuration metadata was edited or removed.", 1)
    hooks = value.get("hooks", {})
    for event, entries in owned.get("hooks", {}).items():
        for entry in entries:
            matches = [index for index, candidate in enumerate(hooks.get(event, [])) if canonical(candidate) == canonical(entry)]
            if len(matches) != 1:
                raise AssetError("ASSET_CONFLICT", "Managed native hook entry was edited, removed, or duplicated.", 1)
            del hooks[event][matches[0]]
        if not hooks.get(event):
            hooks.pop(event, None)
    if not hooks:
        value.pop("hooks", None)
    return value


def commands(entry):
    result = {entry[key] for key in ("command", "commandWindows", "bash", "powershell") if isinstance(entry.get(key), str)}
    for child in entry.get("hooks", []):
        if isinstance(child, dict):
            result.update(commands(child))
    return result


def merge(current, old, desired):
    value = without_owned(current, old) if old else parse(current)
    hook_map = value.setdefault("hooks", {})
    new_commands = set().union(*(commands(entry) for entries in desired["hooks"].values() for entry in entries))
    if any(commands(entry) & new_commands for entries in hook_map.values() for entry in entries):
        raise AssetError("ASSET_CONFLICT", "Unowned or duplicate registration invokes a selected managed hook.", 1)
    for event, entries in desired["hooks"].items():
        hook_map.setdefault(event, []).extend(deepcopy(entries))
    if "version" in desired:
        if canonical(value.get("version", desired["version"])) != canonical(desired["version"]):
            raise AssetError("ASSET_CONFIG_INVALID", "Unsupported native hook configuration version.")
        value["version"] = desired["version"]
    if not hook_map:
        value.pop("hooks", None)
    return canonical(value) + b"\n"


def preflight(root, clients, inspect, *, hooks=True):
    if "codex" in clients:
        path = ".codex/config.toml"
        inspect(root, path)
        target = root / path
        if target.exists():
            try:
                value = tomllib.loads(target.read_text(encoding="utf-8"))
            except (ValueError, UnicodeError) as error:
                raise AssetError("ASSET_CONFIG_INVALID", "Invalid native Codex TOML: " + str(error)) from None
            if hooks and "hooks" in value:
                raise AssetError("ASSET_CONFLICT", "Codex inline hooks already exist in this layer; reconcile them before installing hooks.json.", 1)


def validate_item(item):
    owned = item.get("entries")
    if item["destination"] not in PATHS.values() or not isinstance(owned, dict) or set(owned) - {"hooks", "version"} or "hooks" not in owned:
        raise AssetError("ASSET_RECORD_INVALID", "Invalid native configuration ownership.")
    parse(canonical(owned))
    if digest(canonical(owned) + b"\n") != item["baseline_digest"]:
        raise AssetError("ASSET_RECORD_INVALID", "Configuration entry digest mismatch.")
