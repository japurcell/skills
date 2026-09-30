"""Team installation and its ownership records."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
import uuid

from .sources import AssetError, acquire, canonical, digest, git, read_json
from . import attributes
from .catalog import resolve, installation_restrictions, validate_runtime_files, skill_source_root
from .providers import skill_roots
from .paths import safe_path




def render(snapshot, catalog, assets, clients):
    files, inputs = {}, []
    for asset_id in assets:
        asset = catalog["assets"].get(asset_id)
        if not asset or asset.get("rendering") not in ("skill", "reference", "notice"):
            raise AssetError("ASSET_RENDERER_UNAVAILABLE", f"Unavailable rendering: {asset_id}", 1)
        if any(client not in asset["clients"] for client in clients):
            raise AssetError("ASSET_DEPENDENCY_MISSING", f"Skill is unavailable for a selected client: {asset_id}", 1)
        name = asset_id.removeprefix("skill:")
        names = [safe_path(spec["path"]).casefold() for spec in asset["source_paths"]]
        if len(set(names)) != len(names):
            raise AssetError("ASSET_CATALOG_INVALID", f"Case-colliding output paths: {asset_id}")
        for spec in asset["source_paths"]:
            path = safe_path(spec["path"])
            prefix = skill_source_root(asset_id, asset) + "/"
            if asset["rendering"] == "skill" and not path.startswith(prefix):
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
            roots = [".agent-assets/notices"] if asset["rendering"] == "notice" else skill_roots(clients)
            for root in roots:
                if asset["rendering"] == "notice":
                    destination = root + "/" + path
                elif asset["rendering"] == "reference":
                    destination = root.removesuffix("/skills") + "/" + path
                else:
                    destination = root + "/" + name + "/" + path.removeprefix(prefix)
                mode = 0o755 if executable else 0o644
                owners = [asset_id]
                if destination in files:
                    previous_data, previous_mode, previous_owners, previous_spec = files[destination]
                    if (previous_data, previous_mode, previous_spec) != (data, mode, spec):
                        raise AssetError("ASSET_CATALOG_INVALID", f"Conflicting declared output: {destination}.")
                    owners = sorted(set([*previous_owners, asset_id]))
                files[destination] = (data, mode, owners, spec)
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
    clients, requested, bundles = sorted(set(args.client)), sorted(set(args.asset)), sorted(set(args.bundle))
    with acquire(args.source, args.branch, args.revision) as snapshot:
        catalog, catalog_bytes = snapshot.catalog()
        assets = resolve(catalog, requested, bundles)
        restrictions = installation_restrictions(catalog, assets, clients)
        if restrictions:
            first = restrictions[0]
            raise AssetError(first["code"], first["asset"] + ": " + first["reason"], 1)
        validate_runtime_files(snapshot, catalog, assets)
        files, inputs = render(snapshot, catalog, assets, clients)
        for path in [*files, ".gitattributes", ".agent-assets/selection.json", ".agent-assets/lock.json"]:
            inspect_destination(root, path)
        if snapshot.source["kind"] == "local":
            selected_roots = [skill_source_root(asset, catalog["assets"][asset]) for asset in assets if asset.startswith("skill:")]
            selected_roots.extend(entry["path"] for entry in inputs if not entry["path"].startswith("skills/"))
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
        runtime = sorted({requirement for asset in assets for requirement in catalog["assets"][asset]["runtime"]})
        warnings = ["Native client discovery and trust have not been verified."]
        if runtime:
            warnings.append("Runtime requirements must be supplied by the consumer: " + ", ".join(runtime))
        existing = None
        selection_path = root / ".agent-assets/selection.json"
        lock_path = root / ".agent-assets/lock.json"
        if selection_path.exists() or lock_path.exists():
            existing = read_records(selection_path, lock_path)
        installation_id = existing[0]["installation_id"] if existing else str(uuid.uuid4())
        selection = {"schema_version": 1, "installation_id": installation_id, "scope": "repo", "mode": "team",
                     "clients": clients, "assets": requested, "bundles": bundles, "source": snapshot.source}
        items = [{"destination": path, "type": "file", "mode": mode, "owners": owners,
                  "baseline_digest": digest(data), "content": spec["content"], "line_endings": spec["line_endings"]}
                 for path, (data, mode, owners, spec) in sorted(files.items())]
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
                    "resolved_assets": assets,
                    "changes": {"added": 0, "updated": 0, "retained": len(files), "removed": 0},
                    "conflicts": [], "warnings": warnings}
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
                "resolved_assets": assets,
                "changes": {"added": len(files), "updated": 0, "retained": 0, "removed": 0},
                "conflicts": [], "warnings": warnings}
