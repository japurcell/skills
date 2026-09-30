"""Explicit catalog selection and required dependency closure."""

from __future__ import annotations

import re
import sys
from pathlib import PurePosixPath

from .sources import AssetError
from .providers import CLIENTS, SKILLS_ONLY
from .paths import safe_path


def validate(catalog):
    def invalid(message):
        raise AssetError("ASSET_CATALOG_INVALID", message)

    def strings(value, field, choices=None):
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value) or len(set(value)) != len(value):
            invalid(f"Catalog {field} must be a list of unique nonempty strings.")
        if choices is not None and any(item not in choices for item in value):
            invalid(f"Unsupported catalog {field} value.")

    if not isinstance(catalog.get("bundles"), dict):
        invalid("Catalog bundles must be an object.")
    all_paths = {}
    for asset_id, asset in catalog["assets"].items():
        if not re.fullmatch(r"(skill|agent|hook|reference|notice):[a-z0-9]+(?:-[a-z0-9]+)*", asset_id) or not isinstance(asset, dict):
            invalid("Invalid stable asset ID or asset object.")
        kind = asset_id.split(":")[0]
        name = asset_id.split(":")[1]
        if kind == "skill" and (name == "archive" or name.endswith("-workspace")):
            invalid(f"Historical or benchmark skill root is not distributable: {asset_id}.")
        if "source_root" in asset:
            source_root = safe_path(asset["source_root"])
            if kind != "skill" or source_root not in (f"skills/{name}", f".agents/skills/{name}"):
                invalid(f"Invalid maintained skill source_root: {asset_id}.")
        if asset.get("rendering") != kind:
            invalid(f"Invalid catalog rendering for {asset_id}.")
        for field in ("requires", "clients", "os", "runtime"):
            strings(asset.get(field), field, CLIENTS if field == "clients" else ("windows", "macos", "linux") if field == "os" else None)
        if any(not re.fullmatch(r"(skill|agent|hook|reference|notice):[a-z0-9]+(?:-[a-z0-9]+)*", dependency) for dependency in asset["requires"]):
            invalid(f"Invalid required asset ID: {asset_id}.")
        if "unavailable_reason" in asset and (not isinstance(asset["unavailable_reason"], str) or not asset["unavailable_reason"].strip()):
            invalid(f"Unavailable asset needs a reason: {asset_id}.")
        if not isinstance(asset.get("source_paths"), list):
            invalid(f"Catalog source_paths must be a list: {asset_id}.")
        paths = set()
        for spec in asset["source_paths"]:
            if not isinstance(spec, dict):
                invalid("Catalog source path must be an object.")
            path = safe_path(spec.get("path"))
            if path.casefold() in paths:
                invalid(f"Case-colliding output paths: {asset_id}.")
            paths.add(path.casefold())
            if path.casefold() in all_paths and all_paths[path.casefold()] != path:
                invalid(f"Case-colliding paths across assets: {path}.")
            all_paths[path.casefold()] = path
            if (spec.get("content"), spec.get("line_endings")) not in (("text", "lf"), ("text", "crlf"), ("binary", "none")):
                invalid(f"Invalid payload representation: {path}.")
            prefix = skill_source_root(asset_id, asset) + "/"
            if kind == "skill" and not path.startswith(prefix):
                invalid(f"Skill path is outside its declared root: {path}.")
            if kind == "skill" and set(PurePosixPath(path.removeprefix(prefix)).parts).intersection({"evals", "__pycache__", ".git", "outputs"}):
                invalid(f"Runtime state or evaluation output is not distributable: {path}.")
            if kind == "agent" and path != f"agents/{asset_id.split(':')[1]}.md":
                invalid(f"Agent path is outside its declared source: {path}.")
            if kind == "reference" and not path.startswith("references/"):
                invalid(f"Reference path is outside references/: {path}.")
            if kind == "notice" and path != "LICENSE":
                invalid(f"Unsupported notice path: {path}.")
        if kind == "skill" and not asset.get("unavailable_reason") and skill_source_root(asset_id, asset) + "/SKILL.md" not in {
            spec["path"] for spec in asset["source_paths"]
        }:
            invalid(f"Skill requires its declared SKILL.md entry point: {asset_id}.")
    for bundle, roots in catalog["bundles"].items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", bundle):
            invalid("Invalid bundle name.")
        strings(roots, "bundle roots")
        if not roots or any(root not in catalog["assets"] for root in roots):
            invalid(f"Bundle needs declared asset roots: {bundle}.")
    # Validate cycles even in entries that are not selected or have unavailable roots.
    visiting, visited = [], set()

    def visit(asset_id):
        if asset_id in visiting:
            invalid("Dependency cycle: " + " -> ".join([*visiting, asset_id]))
        if asset_id in visited or asset_id not in catalog["assets"]:
            return
        visiting.append(asset_id)
        for dependency in catalog["assets"][asset_id]["requires"]:
            visit(dependency)
        visiting.pop()
        visited.add(asset_id)

    for asset_id in catalog["assets"]:
        visit(asset_id)


def missing(catalog, roots):
    problems = []

    def visit(asset_id, chain):
        chain = [*chain, asset_id]
        asset = catalog["assets"].get(asset_id)
        reason = asset.get("unavailable_reason") if asset else "Required asset has no catalog entry."
        if reason:
            problems.append({"chain": chain, "reason": reason})
            return
        if asset_id in chain[:-1]:
            raise AssetError("ASSET_CATALOG_INVALID", "Dependency cycle: " + " -> ".join(chain))
        for dependency in asset["requires"]:
            visit(dependency, chain)

    for root in sorted(roots):
        visit(root, [])
    return problems


def resolve(catalog, assets, bundles):
    for asset_id in assets:
        if asset_id not in catalog["assets"]:
            raise AssetError("ASSET_SELECTION_INVALID", f"Unknown requested asset: {asset_id}. Use list to choose an asset ID.")
    roots = set(assets)
    for bundle in bundles:
        if bundle not in catalog["bundles"]:
            raise AssetError("ASSET_SELECTION_INVALID", f"Unknown bundle: {bundle}")
        roots.update(catalog["bundles"][bundle])
    problems = missing(catalog, roots)
    if problems:
        raise AssetError("ASSET_DEPENDENCY_MISSING", "; ".join(
            " -> ".join(problem["chain"]) + ": " + problem["reason"] for problem in problems), 1)
    resolved, visiting = set(), []

    def visit(asset_id):
        if asset_id in visiting:
            raise AssetError("ASSET_CATALOG_INVALID", "Dependency cycle: " + " -> ".join([*visiting, asset_id]))
        if asset_id in resolved:
            return
        asset = catalog["assets"].get(asset_id)
        if asset is None:
            raise AssetError("ASSET_DEPENDENCY_MISSING", "Missing required asset: " + " -> ".join([*visiting, asset_id]), 1)
        visiting.append(asset_id)
        for dependency in asset["requires"]:
            visit(dependency)
        visiting.pop()
        resolved.add(asset_id)

    for root in sorted(roots):
        visit(root)
    return sorted(resolved)


def listing(snapshot, catalog, clients):
    assets = {}
    for asset_id, asset in sorted(catalog["assets"].items()):
        if clients and any(client not in asset["clients"] for client in clients):
            continue
        problems = missing(catalog, [asset_id])
        resolved = resolve(catalog, [asset_id], []) if not problems else []
        restrictions = installation_restrictions(catalog, resolved, clients)
        assets[asset_id] = {**asset, "available": not problems, "missing": problems,
                            "resolved_assets": resolved, "installable": not problems and not restrictions,
                            "restrictions": restrictions}
    bundles = {}
    for name, roots in sorted(catalog["bundles"].items()):
        problems = missing(catalog, roots)
        resolved = resolve(catalog, roots, []) if not problems else []
        restrictions = installation_restrictions(catalog, resolved, clients)
        bundles[name] = {"assets": roots, "available": not problems, "missing": problems,
                         "resolved_assets": resolved, "installable": not problems and not restrictions,
                         "restrictions": restrictions}
    return {"schema_version": 1, "command": "list", "source": {**snapshot.source, "commit": snapshot.commit},
            "selection": {"clients": clients}, "assets": assets, "bundles": catalog["bundles"], "bundle_details": bundles,
            "changes": {"added": 0, "updated": 0, "retained": 0, "removed": 0}, "conflicts": [],
            "warnings": ["No repository-safe instruction fragments are currently cataloged; personal instructions and settings are not distributed."]}


def installation_restrictions(catalog, assets, clients):
    problems = []
    system = "windows" if sys.platform == "win32" else "macos" if sys.platform == "darwin" else "linux"
    for asset_id in assets:
        asset = catalog["assets"][asset_id]
        if asset["os"] and system not in asset["os"]:
            problems.append({"code": "ASSET_PLATFORM_UNSUPPORTED", "asset": asset_id,
                             "reason": "Asset does not support this operating system: " + system})
        elif asset["rendering"] in ("agent", "hook") and SKILLS_ONLY.intersection(clients):
            problems.append({"code": "ASSET_CLIENT_UNSUPPORTED", "asset": asset_id,
                             "reason": "Claude Code, Cursor, and OpenCode initially support skills only."})
        elif any(client not in asset["clients"] for client in clients):
            problems.append({"code": "ASSET_CLIENT_UNSUPPORTED", "asset": asset_id,
                             "reason": "Asset is unavailable for a selected client."})
        elif asset["rendering"] in ("agent", "hook") and not asset["source_paths"]:
            problems.append({"code": "ASSET_RENDERER_UNAVAILABLE", "asset": asset_id,
                             "reason": "Native asset has no declared maintained sources; no files were installed."})
    return problems


def validate_runtime_files(snapshot, catalog, assets):
    runtime_suffixes = {".py", ".sh", ".ps1", ".js", ".mjs", ".cjs", ".ts", ".bat", ".cmd", ".exe", ".dll"}
    for asset_id in assets:
        if not asset_id.startswith("skill:"):
            continue
        root = skill_source_root(asset_id, catalog["assets"][asset_id]) + "/"
        declared = {spec["path"] for spec in catalog["assets"][asset_id]["source_paths"]}
        for path, entry in snapshot.tree.items():
            relative = path.removeprefix(root)
            if not path.startswith(root) or set(PurePosixPath(relative).parts).intersection({"evals", "__pycache__"}):
                continue
            if path not in declared and (entry[0] == "100755" or PurePosixPath(path).suffix.lower() in runtime_suffixes):
                raise AssetError("ASSET_CATALOG_INVALID", f"Undeclared runtime file: {path}. Declare required source files before selecting this skill.")


def skill_source_root(asset_id, asset):
    return asset.get("source_root", f"skills/{asset_id.split(':')[1]}")
