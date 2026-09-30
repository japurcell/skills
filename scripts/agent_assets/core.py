"""Team installation and its ownership records."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import uuid

from .sources import AssetError, acquire, canonical, digest, git, read_json
from . import attributes


def safe_path(value: str) -> str:
    if not isinstance(value, str):
        raise AssetError("ASSET_CATALOG_INVALID", "Catalog paths must be strings.")
    path = PurePosixPath(value)
    reserved = r"^(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)"
    if path.is_absolute() or ".." in path.parts or "\\" in value or not path.parts or value != path.as_posix() or any(
        part.endswith((".", " ")) or re.match(reserved, part, re.IGNORECASE) or
        any(ord(c) < 32 or c in '<>:"|?*' for c in part) for part in path.parts
    ):
        raise AssetError("ASSET_CATALOG_INVALID", "Catalog path must be a safe relative path.")
    return path.as_posix()


def render(snapshot, catalog, assets, clients):
    files, inputs = {}, []
    for asset_id in assets:
        asset = catalog["assets"].get(asset_id)
        if not asset or asset.get("rendering") != "skill":
            raise AssetError("ASSET_DEPENDENCY_MISSING", f"Unavailable skill: {asset_id}", 1)
        if any(client not in asset["clients"] for client in clients):
            raise AssetError("ASSET_DEPENDENCY_MISSING", f"Skill is unavailable for a selected client: {asset_id}", 1)
        if asset.get("requires"):
            raise AssetError("ASSET_DEPENDENCY_MISSING", f"Required assets are unavailable: {asset_id}", 1)
        name = asset_id.removeprefix("skill:")
        names = [safe_path(spec["path"]).casefold() for spec in asset["source_paths"]]
        if len(set(names)) != len(names):
            raise AssetError("ASSET_CATALOG_INVALID", f"Case-colliding output paths: {asset_id}")
        for spec in asset["source_paths"]:
            path = safe_path(spec["path"])
            prefix = f"skills/{name}/"
            if not path.startswith(prefix):
                raise AssetError("ASSET_CATALOG_INVALID", f"Skill path is outside its declared root: {path}")
            data, executable = snapshot.read(path)
            inputs.append({"path": path, "type": "file", "executable": executable, "digest": digest(data)})
            content, endings = spec["content"], spec["line_endings"]
            if (content, endings) not in (("text", "lf"), ("text", "crlf"), ("binary", "none")):
                raise AssetError("ASSET_CATALOG_INVALID", f"Missing or invalid payload representation: {path}")
            if content == "text":
                data.decode("utf-8")
                data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                if endings == "crlf":
                    data = data.replace(b"\n", b"\r\n")
            destination = ".agents/" + path
            files[destination] = (data, 0o755 if executable else 0o644, asset_id, spec)
    return files, inputs


def write_atomic(path: Path, data: bytes, mode: int = 0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".agent-assets-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(data)
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def inspect_destination(root: Path, relative: str):
    path = root
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        path = path / part
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise AssetError("ASSET_CONFLICT", f"Linked destination refused: {relative}. Use an independent directory/file.", 1)
        expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected(info.st_mode):
            raise AssetError("ASSET_CONFLICT", f"Unexpected destination type: {relative}. Resolve it explicitly.", 1)


def read_records(selection_path: Path, lock_path: Path):
    if not selection_path.exists() or not lock_path.exists():
        raise AssetError("ASSET_RECORD_INVALID", "Both selection and lock records are required; restore the complete recorded installation.")
    selection = read_json(selection_path.read_bytes(), "ASSET_RECORD_INVALID")
    lock = read_json(lock_path.read_bytes(), "ASSET_RECORD_INVALID")
    if not isinstance(selection, dict) or not isinstance(lock, dict) or any(
        type(record.get("schema_version")) is not int or record["schema_version"] != 1 for record in (selection, lock)
    ) or type(lock.get("renderer_version")) is not int or lock["renderer_version"] != 1:
        raise AssetError("ASSET_RECORD_INVALID", "Unsupported record/renderer version; use the command checkout compatible with the recorded revision.")
    if selection.get("installation_id") != lock.get("installation_id") or lock.get("selection_digest") != digest(canonical(selection)):
        raise AssetError("ASSET_RECORD_INVALID", "Selection/lock identity or digest mismatch; restore agreeing records.")
    if not isinstance(lock.get("items"), list) or not isinstance(lock.get("attributes"), list):
        raise AssetError("ASSET_RECORD_INVALID", "Malformed ownership record; restore valid records before installing.")
    for entry in [*lock["items"], *lock["attributes"]]:
        if not isinstance(entry, dict) or not isinstance(entry.get("destination"), str):
            raise AssetError("ASSET_RECORD_INVALID", "Malformed owned destination in lock record.")
        safe_path(entry["destination"])
    return selection, lock


def install(args):
    root = Path(git(Path(args.repo or "."), "rev-parse", "--show-toplevel").decode().strip()).resolve()
    clients, assets = sorted(set(args.client)), sorted(set(args.asset))
    with acquire(args.source, args.branch, args.revision) as snapshot:
        catalog, catalog_bytes = snapshot.catalog()
        files, inputs = render(snapshot, catalog, assets, clients)
        for path in [*files, ".gitattributes", ".agent-assets/selection.json", ".agent-assets/lock.json"]:
            inspect_destination(root, path)
        if snapshot.source["kind"] == "local":
            selected_roots = [f"skills/{asset.removeprefix('skill:')}" for asset in assets]
            tracked = git(snapshot.repo, "ls-files", "-z", "--", "distribution/catalog.json", *selected_roots)
            inspected = sorted({"distribution/catalog.json", *[entry["path"] for entry in inputs],
                                *[path.decode("utf-8") for path in tracked.split(b"\0") if path]})
            source_attributes = attributes.observed(snapshot.repo, inspected)
            if any(values["filter"] not in ("unspecified", "unset") or values["working-tree-encoding"] not in ("unspecified", "unset")
                   for values in source_attributes.values()):
                raise AssetError("ASSET_SOURCE_INVALID", "Selected source uses unsupported content transforms; verification will not execute Git filters.")
            dirty = git(snapshot.repo, "status", "--porcelain=v1", "--untracked-files=all", "--",
                        "distribution/catalog.json", *selected_roots)
            if dirty:
                raise AssetError("ASSET_SOURCE_DIRTY", "Selected source paths have uncommitted changes; commit or restore them first.")
        source = {**snapshot.source, "commit": snapshot.commit,
                  "digest": digest(canonical([{"path": "distribution/catalog.json", "type": "file", "executable": snapshot.tree["distribution/catalog.json"][0] == "100755",
                                               "digest": digest(catalog_bytes)}, *sorted(inputs, key=lambda i: i["path"])]))}
        existing = None
        selection_path = root / ".agent-assets/selection.json"
        lock_path = root / ".agent-assets/lock.json"
        if selection_path.exists() or lock_path.exists():
            existing = read_records(selection_path, lock_path)
        installation_id = existing[0]["installation_id"] if existing else str(uuid.uuid4())
        selection = {"schema_version": 1, "installation_id": installation_id, "scope": "repo", "mode": "team",
                     "clients": clients, "assets": assets, "bundles": [], "source": snapshot.source}
        items = [{"destination": path, "type": "file", "mode": mode, "owners": [asset],
                  "baseline_digest": digest(data), "content": spec["content"], "line_endings": spec["line_endings"]}
                 for path, (data, mode, asset, spec) in sorted(files.items())]
        attribute_bytes, owned_attributes = attributes.plan(root, files, existing)
        lock = {"schema_version": 1, "renderer_version": 1, "installation_id": installation_id,
                "source": source, "assets": assets, "items": items, "selection_digest": digest(canonical(selection)),
                "attributes": owned_attributes}
        if existing:
            if existing != (selection, lock):
                raise AssetError("ASSET_CONFLICT", "Existing installation differs; use the lifecycle update command when available.", 1)
            for path, (data, mode, _, _) in files.items():
                target = root / path
                if not target.is_file() or target.read_bytes() != data or (os.name != "nt" and target.stat().st_mode & 0o777 != mode):
                    raise AssetError("ASSET_CONFLICT", f"Managed file changed: {path}. Restore recorded content and rerun.", 1)
            return {"schema_version": 1, "command": "install", "source": source, "selection": selection,
                    "changes": {"added": 0, "updated": 0, "retained": len(files), "removed": 0},
                    "conflicts": [], "warnings": ["Native client discovery and trust have not been verified."]}
        for path in files:
            if (root / path).exists():
                raise AssetError("ASSET_CONFLICT", f"Unowned destination already exists: {path}. Resolve it explicitly before installing.", 1)
        for path, (data, mode, _, _) in files.items():
            write_atomic(root / path, data, mode)
        if not (root / ".gitattributes").exists() or root.joinpath(".gitattributes").read_bytes() != attribute_bytes:
            write_atomic(root / ".gitattributes", attribute_bytes)
        write_atomic(root / ".agent-assets/selection.json", canonical(selection) + b"\n")
        write_atomic(root / ".agent-assets/lock.json", canonical(lock) + b"\n")
        return {"schema_version": 1, "command": "install", "source": source, "selection": selection,
                "changes": {"added": len(files), "updated": 0, "retained": 0, "removed": 0},
                "conflicts": [], "warnings": ["Native client discovery and trust have not been verified."]}
