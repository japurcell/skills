"""Team installation and its ownership records."""

from __future__ import annotations

import os
import re
from urllib.parse import urlsplit
from pathlib import Path, PurePosixPath
import stat
import uuid
from contextlib import contextmanager

from .sources import AssetError, acquire, canonical, digest, git, read_json
from . import attributes, transaction
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


@contextmanager
def destination_parent(path: Path, *, create=False, created=None):
    if os.name != "posix":
        raise AssetError("ASSET_PLATFORM_UNSUPPORTED", "Safe filesystem mutation requires POSIX directory descriptors; native Windows writes await verified parent-handle support.")
    parent_fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        traversed = Path("/")
        for part in path.parent.parts[1:]:
            traversed /= part
            try:
                child_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
            except FileNotFoundError:
                if not create:
                    raise
                try:
                    os.mkdir(part, mode=0o755, dir_fd=parent_fd)
                    if created is not None:
                        created.append(traversed)
                except FileExistsError:
                    pass
                child_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = child_fd
        yield parent_fd
    finally:
        os.close(parent_fd)


def directory_identity(path):
    with destination_parent(path / ".agent-assets-identity") as fd:
        info = os.fstat(fd)
        return [info.st_dev, info.st_ino]


def confirm_parent(path, parent_fd):
    info = os.fstat(parent_fd)
    try:
        visible = directory_identity(path.parent)
    except OSError:
        visible = None
    if visible != [info.st_dev, info.st_ino]:
        raise AssetError("ASSET_INTERRUPTED", "Destination parent changed during mutation: " + path.name)


def read_at(parent_fd, name):
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
    except FileNotFoundError:
        return None, None
    except OSError:
        raise AssetError("ASSET_INTERRUPTED", "Destination changed during mutation: " + name) from None
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise AssetError("ASSET_INTERRUPTED", "Destination is not a regular file: " + name)
        value = (stream.read(), info.st_mode & 0o777)
    visible = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    identity = (info.st_dev, info.st_ino)
    if (visible.st_dev, visible.st_ino) != identity:
        raise AssetError("ASSET_INTERRUPTED", "Destination changed while reading: " + name)
    return value, identity


def write_atomic(path: Path, data: bytes, mode: int = 0o644, *, staging: Path | None = None,
                 expected=None, parent_check=None):
    # Open each ancestor without following links and pin the final parent.
    # Verify its visible identity and the original entry before replacement.
    created = []
    with destination_parent(path, create=True, created=created) as parent_fd:
        confirm_parent(path, parent_fd)
        before, before_identity = read_at(parent_fd, path.name)
        if before != expected:
            raise AssetError("ASSET_INTERRUPTED", "Destination changed before staging: " + path.name)
        if parent_check:
            parent_check(parent_fd, created)
        name = staging.name if staging else ".agent-assets-" + uuid.uuid4().hex
        temporary_inode = None
        try:
            fd = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=parent_fd)
            temporary_inode = os.fstat(fd).st_ino
            with os.fdopen(fd, "wb") as output:
                output.write(data)
                output.flush()
                os.fchmod(output.fileno(), mode)
                os.fsync(output.fileno())
            confirm_parent(path, parent_fd)
            current, current_identity = read_at(parent_fd, path.name)
            if current != before or current_identity != before_identity:
                raise AssetError("ASSET_INTERRUPTED", "Concurrent change prevents replacement: " + path.name)
            os.replace(name, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            os.fsync(parent_fd)
            confirm_parent(path, parent_fd)
            after, after_identity = read_at(parent_fd, path.name)
            if after != (data, mode) or after_identity[1] != temporary_inode:
                raise AssetError("ASSET_INTERRUPTED", "Replacement verification failed: " + path.name)
        finally:
            try:
                if temporary_inode is not None and os.stat(name, dir_fd=parent_fd, follow_symlinks=False).st_ino == temporary_inode:
                    os.unlink(name, dir_fd=parent_fd)
            except FileNotFoundError:
                pass


def unlink_owned(path, expected):
    with destination_parent(path) as parent_fd:
        confirm_parent(path, parent_fd)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            current = (stream.read(), info.st_mode & 0o777)
        observed = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if current != expected or (observed.st_dev, observed.st_ino) != (info.st_dev, info.st_ino):
            raise AssetError("ASSET_INTERRUPTED", "Concurrent change prevents removal: " + path.name)
        os.unlink(path.name, dir_fd=parent_fd)
        confirm_parent(path, parent_fd)


def prune_empty(path):
    try:
        with destination_parent(path) as parent_fd:
            os.rmdir(path.name, dir_fd=parent_fd)
        return True
    except OSError:
        return False


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


def read_records(selection_path: Path, lock_path: Path, *, check_agreement=True):
    if not selection_path.exists() or not lock_path.exists():
        raise AssetError("ASSET_RECORD_INVALID", "Both selection and lock records are required; restore the complete recorded installation.")
    selection = read_json(selection_path.read_bytes(), "ASSET_RECORD_INVALID")
    lock = read_json(lock_path.read_bytes(), "ASSET_RECORD_INVALID")
    validate_records(selection, lock, check_agreement=check_agreement)
    return selection, lock


def owned_destination(path):
    try:
        safe_path(path)
    except AssetError:
        raise AssetError("ASSET_RECORD_INVALID", "Unsafe owned destination.") from None
    roots = (".agents/skills/", ".claude/skills/", ".agents/references/", ".claude/references/", ".agent-assets/notices/")
    if not path.startswith(roots) or any(part.casefold() in (".git", ".agent-assets") for part in PurePosixPath(path).parts[1:]):
        raise AssetError("ASSET_RECORD_INVALID", "Owned destination is outside supported payload roots.")
    return path


def records_agree(selection, lock):
    return (selection["installation_id"] == lock["installation_id"]
            and lock["selection_digest"] == digest(canonical(selection))
            and selection["source"] == {key: lock["source"][key] for key in ("kind", "location", "policy")})


def validate_records(selection, lock, *, check_agreement=True):
    def invalid(message):
        raise AssetError("ASSET_RECORD_INVALID", message)
    def sha(value, length=64):
        return isinstance(value, str) and re.fullmatch("[0-9a-f]{%d}" % length, value)
    def names(value):
        return isinstance(value, list) and all(isinstance(v, str) and v for v in value) and value == sorted(set(value))
    if not isinstance(selection, dict) or not isinstance(lock, dict) or any(
        type(record.get("schema_version")) is not int or record["schema_version"] != 1 for record in (selection, lock)
    ) or type(lock.get("renderer_version")) is not int or lock["renderer_version"] != 1:
        revision = lock.get("source", {}).get("commit", "unknown") if isinstance(lock, dict) and isinstance(lock.get("source"), dict) else "unknown"
        invalid("Unsupported record/renderer version at " + str(revision) + "; use the compatible command checkout.")
    for record in (selection, lock):
        if not isinstance(record.get("installation_id"), str) or not re.fullmatch(r"[0-9a-f-]{36}", record["installation_id"]):
            invalid("Invalid installation identity.")
        source = record.get("source")
        if not isinstance(source, dict) or source.get("kind") not in ("local", "git") or not isinstance(source.get("location"), str):
            invalid("Invalid source identity.")
        location = source["location"]
        url = urlsplit(location)
        if not location or any(ord(c) < 32 for c in location) or url.password or url.query or url.fragment or (url.username and url.scheme != "ssh"):
            invalid("Unsafe recorded source location.")
        if source["kind"] == "local" and not Path(location).is_absolute():
            invalid("Local source must be absolute.")
        if source["kind"] == "git" and (url.scheme not in ("https", "ssh", "file") and not re.fullmatch(r"[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+:[^\s]+", location)):
            invalid("Unsupported recorded source URL.")
        policy = source.get("policy")
        if not isinstance(policy, dict) or policy.get("kind") not in ("branch", "revision") or not isinstance(policy.get("value"), str) or not policy["value"] or policy["value"].startswith("-") or any(ord(c) < 32 for c in policy["value"]):
            invalid("Invalid source policy.")
    if selection.get("scope") != "repo" or selection.get("mode") != "team" or any(not names(selection.get(key)) for key in ("clients", "assets", "bundles")):
        invalid("Invalid or unsupported selection scope.")
    from .providers import CLIENTS
    if not selection["clients"] or not set(selection["clients"]).issubset(CLIENTS) or not names(lock.get("assets")):
        invalid("Invalid selection clients/assets.")
    if not sha(lock.get("selection_digest")) or not sha(lock["source"].get("digest")) or not (sha(lock["source"].get("commit"), 40) or sha(lock["source"].get("commit"), 64)):
        invalid("Invalid recorded commit or digest.")
    if check_agreement and not records_agree(selection, lock):
        invalid("Selection/lock identity or digest mismatch; restore agreeing records.")
    if not isinstance(lock.get("items"), list) or not isinstance(lock.get("attributes"), list):
        invalid("Malformed ownership record.")
    destinations = set()
    for item in lock["items"]:
        if not isinstance(item, dict):
            invalid("Invalid file record.")
        path = owned_destination(item.get("destination"))
        if path.casefold() in destinations:
            invalid("Duplicate/case-colliding ownership.")
        destinations.add(path.casefold())
        if item.get("type") != "file" or type(item.get("mode")) is not int or item["mode"] not in (0o644, 0o755) or not sha(item.get("baseline_digest")) or not names(item.get("owners")) or not item["owners"] or not set(item["owners"]).issubset(lock["assets"]):
            invalid("Invalid file baseline, mode or owners.")
        if (item.get("content"), item.get("line_endings")) not in (("text", "lf"), ("text", "crlf"), ("binary", "none")):
            invalid("Invalid payload representation.")
        origin = item.get("origin_commit", lock["source"]["commit"])
        if not (sha(origin, 40) or sha(origin, 64)):
            invalid("Invalid item origin commit.")
    attribute_paths = set()
    for entry in lock["attributes"]:
        if not isinstance(entry, dict):
            invalid("Invalid attribute entry.")
        path = owned_destination(entry.get("destination"))
        if path.casefold() not in destinations or path.casefold() in attribute_paths or entry.get("values") not in (["-text"], ["text", "eol=lf"], ["text", "eol=crlf"]):
            invalid("Invalid attribute ownership.")
        attribute_paths.add(path.casefold())


def source_digest(snapshot, catalog_bytes, inputs):
    return digest(canonical([{"path": "distribution/catalog.json", "type": "file",
                              "executable": snapshot.tree["distribution/catalog.json"][0] == "100755",
                              "digest": digest(catalog_bytes)}, *sorted(inputs, key=lambda item: item["path"])]))


def authenticate_ownership(existing):
    """Prove saved ownership against immutable source, never directory membership."""
    selection, lock = existing
    with acquire(selection["source"]["location"], None, lock["source"]["commit"]) as snapshot:
        catalog, catalog_bytes = snapshot.catalog()
        assets = resolve(catalog, selection["assets"], selection["bundles"])
        files, inputs = render(snapshot, catalog, assets, selection["clients"])
        old = {item["destination"]: item for item in lock["items"]}
        if (snapshot.commit != lock["source"]["commit"] or assets != lock["assets"]
                or source_digest(snapshot, catalog_bytes, inputs) != lock["source"]["digest"]
                or set(old) != set(files)):
            raise AssetError("ASSET_SOURCE_MISMATCH", "Recorded ownership differs from its immutable source; restore authentic records before changing files.")
        for path, (data, mode, owners, spec) in files.items():
            item = old[path]
            expected = (digest(data), mode, owners, spec["content"], spec["line_endings"])
            actual = (item["baseline_digest"], item["mode"], item["owners"], item["content"], item["line_endings"])
            if actual != expected:
                raise AssetError("ASSET_SOURCE_MISMATCH", "Recorded baseline differs from its immutable source: " + path)
    origins = sorted({item.get("origin_commit", lock["source"]["commit"]) for item in lock["items"]})
    for origin in origins:
        if origin == lock["source"]["commit"]:
            continue
        with acquire(selection["source"]["location"], None, origin) as snapshot:
            catalog, _ = snapshot.catalog()
            for item in lock["items"]:
                if item.get("origin_commit", lock["source"]["commit"]) != origin:
                    continue
                owners = item["owners"]
                if any(owner not in catalog["assets"] for owner in owners):
                    raise AssetError("ASSET_SOURCE_MISMATCH", "Recorded origin lacks its owner: " + item["destination"])
                clients = sorted(set.intersection(*(set(catalog["assets"][owner]["clients"]) for owner in owners)))
                files, _ = render(snapshot, catalog, owners, clients)
                value = files.get(item["destination"])
                if value is None:
                    raise AssetError("ASSET_SOURCE_MISMATCH", "Recorded origin lacks its payload: " + item["destination"])
                data, mode, rendered_owners, spec = value
                expected = (digest(data), mode, rendered_owners, spec["content"], spec["line_endings"])
                actual = (item["baseline_digest"], item["mode"], owners, item["content"], item["line_endings"])
                if actual != expected:
                    raise AssetError("ASSET_SOURCE_MISMATCH", "Recorded origin differs from its retained baseline: " + item["destination"])


def install(args):
    root = Path(git(Path(args.repo or "."), "rev-parse", "--show-toplevel").decode().strip()).resolve()
    # A later renderer may have installed another scope. Until that ownership
    # schema is supported, refusing is the only safe reconciliation strategy.
    for path in (".agent-assets/local/selection.json", ".agent-assets/local/lock.json"):
        inspect_destination(root, path)
        if (root / path).exists():
            raise AssetError("ASSET_RECORD_INVALID", "Local ownership records require a compatible command checkout; team pruning cannot ignore them.")
    if transaction.pending(root):
        if args.preview:
            raise AssetError("ASSET_INTERRUPTED", "Interrupted operation pending; rerun a write command to recover before preview.")
        transaction.recover(root)
    selection_path = root / ".agent-assets/selection.json"
    lock_path = root / ".agent-assets/lock.json"
    for path in (".agent-assets/selection.json", ".agent-assets/lock.json", ".gitattributes"):
        inspect_destination(root, path)
    existing = read_records(selection_path, lock_path) if selection_path.exists() or lock_path.exists() else None
    observed_paths = [".agent-assets/selection.json", ".agent-assets/lock.json", ".gitattributes"]
    if existing:
        observed_paths.extend(item["destination"] for item in existing[1]["items"])
    observations = transaction.observe(root, observed_paths)
    if existing:
        authenticate_ownership(existing)
    if args.command != "install":
        if not existing:
            raise AssetError("ASSET_RECORD_INVALID", "No recorded installation; install a selection first.")
        saved, previous = existing
        args.client, args.asset, args.bundle = saved["clients"], saved["assets"], saved["bundles"]
        args.source = saved["source"]["location"]
        if args.command == "restore":
            if args.branch or args.revision:
                raise AssetError("ASSET_SELECTION_INVALID", "Restore uses the recorded commit; use update to change policy.")
            args.revision = previous["source"]["commit"]
        elif not args.branch and not args.revision:
            policy = saved["source"]["policy"]
            if policy["kind"] == "branch":
                args.branch = policy["value"]
            else:
                args.revision = policy["value"]
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
        observations.update(transaction.observe(root, [path for path in files if path not in observations]))
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
                  "digest": source_digest(snapshot, catalog_bytes, inputs)}
        if args.command == "restore":
            if source["commit"] != existing[1]["source"]["commit"] or source["digest"] != existing[1]["source"]["digest"]:
                raise AssetError("ASSET_SOURCE_MISMATCH", "Recorded source digest does not match; use the compatible command checkout and exact recorded source.")
            source = existing[1]["source"]
        runtime = sorted({requirement for asset in assets for requirement in catalog["assets"][asset]["runtime"]})
        warnings = ["Native client discovery and trust have not been verified."]
        if runtime:
            warnings.append("Runtime requirements must be supplied by the consumer: " + ", ".join(runtime))
        installation_id = existing[0]["installation_id"] if existing else str(uuid.uuid4())
        selection = {"schema_version": 1, "installation_id": installation_id, "scope": "repo", "mode": "team",
                     "clients": clients, "assets": requested, "bundles": bundles, "source": existing[0]["source"] if args.command == "restore" else snapshot.source}
        items = [{"destination": path, "type": "file", "mode": mode, "owners": owners,
                  "baseline_digest": digest(data), "origin_commit": snapshot.commit, "content": spec["content"], "line_endings": spec["line_endings"]}
                 for path, (data, mode, owners, spec) in sorted(files.items())]
        if args.command == "restore":
            old = {item["destination"]: item for item in existing[1]["items"]}
            compared = ("type", "mode", "owners", "baseline_digest", "content", "line_endings")
            if set(old) != set(files) or any(any(item[key] != old[item["destination"]][key] for key in compared) for item in items):
                raise AssetError("ASSET_SOURCE_MISMATCH", "Recorded rendered payload differs from the exact source; use the compatible command checkout.")
        attribute_bytes, owned_attributes = attributes.plan(root, files, existing)
        lock = {"schema_version": 1, "renderer_version": 1, "installation_id": installation_id,
                "source": source, "assets": assets, "items": items, "selection_digest": digest(canonical(selection)),
                "attributes": owned_attributes}
        changes = {"added": 0, "updated": 0, "retained": 0, "removed": 0}
        old_items = {item["destination"]: item for item in existing[1]["items"]} if existing else {}
        writes = {}
        for item in items:
            path = item["destination"]
            data, mode, _, _ = files[path]
            target = root / path
            previous = old_items.get(path)
            current = (digest(target.read_bytes()), target.stat().st_mode & 0o777) if target.exists() else None
            desired = (digest(data), mode)
            baseline = (previous["baseline_digest"], previous["mode"]) if previous else None
            if os.name == "nt":
                current = (current[0], mode) if current else None
                baseline = (baseline[0], mode) if baseline else None
            if previous is None and current is not None:
                raise AssetError("ASSET_CONFLICT", f"Unowned destination already exists: {path}. Resolve it explicitly.", 1)
            compared = ("type", "mode", "owners", "baseline_digest", "content", "line_endings")
            if previous and all(item[key] == previous[key] for key in compared):
                item["origin_commit"] = previous.get("origin_commit", existing[1]["source"]["commit"])
            if current == desired:
                changes["retained"] += 1
            elif previous and desired == baseline and current is not None:
                changes["retained"] += 1
                warnings.append("Retained local edit: " + path)
            elif current is not None and current != baseline:
                raise AssetError("ASSET_CONFLICT", f"Managed file changed: {path}. Restore baseline or maintain edits upstream and rerun.", 1)
            else:
                writes[path] = (data, mode)
                changes["updated" if previous else "added"] += 1
        removals = []
        for path, previous in old_items.items():
            if path in files:
                continue
            inspect_destination(root, path)
            target = root / path
            if target.exists():
                if digest(target.read_bytes()) != previous["baseline_digest"] or (os.name != "nt" and target.stat().st_mode & 0o777 != previous["mode"]):
                    raise AssetError("ASSET_CONFLICT", f"Edited obsolete managed file: {path}. Resolve the edit before removing it.", 1)
                removals.append(path)
            changes["removed"] += 1
        validate_records(selection, lock)
        for path, data in ((".gitattributes", attribute_bytes),
                           (".agent-assets/selection.json", canonical(selection) + b"\n"),
                           (".agent-assets/lock.json", canonical(lock) + b"\n")):
            if not (root / path).exists() or (root / path).read_bytes() != data:
                writes[path] = (data, 0o644)
        if not args.preview and (writes or removals):
            transaction.apply(root, writes, removals, observations, lambda: attributes.plan(root, files, existing))
        return {"schema_version": 1, "command": args.command, "source": source, "selection": selection,
                "resolved_assets": assets, "changes": changes, "conflicts": [], "warnings": warnings}


def status(args):
    root = Path(git(Path(args.repo or "."), "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if transaction.pending(root):
        raise AssetError("ASSET_INTERRUPTED", "Interrupted operation pending; status never recovers it.")
    for path in (".agent-assets/selection.json", ".agent-assets/lock.json"):
        inspect_destination(root, path)
    selection, lock = read_records(root / ".agent-assets/selection.json", root / ".agent-assets/lock.json", check_agreement=False)
    drift = []
    if not records_agree(selection, lock):
        drift.append({"code": "ASSET_DRIFT", "destination": ".agent-assets/selection.json", "reason": "selection/lock disagreement"})
    try:
        inspect_destination(root, ".gitattributes")
        attributes.verify(root, lock)
    except AssetError as error:
        drift.append({"code": "ASSET_DRIFT", "destination": ".gitattributes", "reason": str(error)})
    for item in lock["items"]:
        path = item["destination"]
        try:
            inspect_destination(root, path)
            target = root / path
            if not target.exists():
                reason = "missing"
            elif digest(target.read_bytes()) != item["baseline_digest"] or (os.name != "nt" and target.stat().st_mode & 0o777 != item["mode"]):
                reason = "modified"
            else:
                continue
        except AssetError:
            reason = "unexpected file type"
        drift.append({"code": "ASSET_DRIFT", "destination": path, "reason": reason})
    return {"schema_version": 1, "command": "status", "source": lock["source"], "selection": selection,
            "resolved_assets": lock["assets"], "changes": {"added": 0, "updated": 0, "removed": 0, "retained": len(lock["items"])},
            "conflicts": [], "warnings": ["Offline content verification does not establish source freshness or native trust."],
            "verification": {"passed": not drift, "drift": drift}}
