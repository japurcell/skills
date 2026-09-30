"""Serialize writers in Git-resolved per-worktree state."""

from contextlib import contextmanager
import os
import base64
from pathlib import Path
import stat
import uuid
import re

from .sources import AssetError, git, canonical, digest, read_json


def state_path(root, name):
    path = Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", name).decode().strip())
    if path.is_symlink() or (path.exists() and (not path.is_file() or path.stat().st_nlink != 1 or getattr(path.stat(), "st_file_attributes", 0) & 0x400)):
        raise AssetError("ASSET_RECORD_INVALID", "Unsafe installer state path.")
    return path


@contextmanager
def mutex(root):
    path = state_path(root, "agent-assets.mutex")
    fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    stream = os.fdopen(fd, "r+b")
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode) or os.fstat(fd).st_nlink != 1:
            raise AssetError("ASSET_RECORD_INVALID", "Unsafe installer mutex.")
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise AssetError("ASSET_CONFLICT", "Another installer is writing this worktree; retry after it finishes.", 1) from None
        yield
    finally:
        stream.close()


def observe(root, paths):
    from .core import inspect_destination, destination_parent
    result = {}
    for path in paths:
        inspect_destination(root, path)
        target = root / path
        if os.name != "posix":
            result[path] = (target.read_bytes(), target.stat().st_mode & 0o777) if target.exists() else None
            continue
        try:
            with destination_parent(target) as parent_fd:
                fd = os.open(target.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
                with os.fdopen(fd, "rb") as stream:
                    info = os.fstat(stream.fileno())
                    if not stat.S_ISREG(info.st_mode):
                        raise AssetError("ASSET_CONFLICT", "Unexpected destination type: " + path, 1)
                    result[path] = (stream.read(), info.st_mode & 0o777)
        except FileNotFoundError:
            result[path] = None
    return result


def pending(root):
    return state_path(root, "agent-assets-journal.json").exists()


def encode(value):
    if value is None:
        return None
    data, mode = value
    return {"bytes": base64.b64encode(data).decode("ascii"), "digest": digest(data), "mode": mode}


def decode(value):
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"bytes", "digest", "mode"} or type(value["mode"]) is not int or not 0 <= value["mode"] <= 0o777:
        raise AssetError("ASSET_INTERRUPTED", "Malformed interrupted-operation preimage.")
    try:
        data = base64.b64decode(value["bytes"], validate=True)
    except (ValueError, TypeError):
        raise AssetError("ASSET_INTERRUPTED", "Invalid interrupted-operation bytes.") from None
    if digest(data) != value["digest"]:
        raise AssetError("ASSET_INTERRUPTED", "Interrupted-operation digest mismatch.")
    return data, value["mode"]


def record_pair(states):
    from .core import validate_records
    names = (".agent-assets/selection.json", ".agent-assets/lock.json")
    if all(states.get(name) is None for name in names):
        return None
    if any(states.get(name) is None for name in names):
        raise AssetError("ASSET_INTERRUPTED", "Incomplete interrupted ownership records.")
    pair = tuple(read_json(states[name][0], "ASSET_INTERRUPTED") for name in names)
    validate_records(*pair)
    return pair


def validate_journal(journal):
    from .core import owned_destination
    if not isinstance(journal, dict) or type(journal.get("schema_version")) is not int or journal["schema_version"] != 1 or not isinstance(journal.get("entries"), list):
        raise AssetError("ASSET_INTERRUPTED", "Unsupported interrupted-operation journal.")
    operation_id = journal.get("operation_id")
    if not isinstance(operation_id, str) or not re.fullmatch("[0-9a-f]{32}", operation_id):
        raise AssetError("ASSET_INTERRUPTED", "Invalid interrupted operation identity.")
    before, after = {}, {}
    for entry in journal["entries"]:
        if not isinstance(entry, dict) or set(entry) != {"destination", "before", "after"}:
            raise AssetError("ASSET_INTERRUPTED", "Invalid interrupted-operation entry.")
        path = entry["destination"]
        if path not in (".gitattributes", ".agent-assets/selection.json", ".agent-assets/lock.json"):
            owned_destination(path)
        if path in before:
            raise AssetError("ASSET_INTERRUPTED", "Duplicate interrupted destination.")
        before[path], after[path] = decode(entry["before"]), decode(entry["after"])
    old, new = record_pair(before), record_pair(after)
    if not new or (old and old[0]["installation_id"] != new[0]["installation_id"]):
        raise AssetError("ASSET_INTERRUPTED", "Interrupted ownership identity mismatch.")
    for states, pair in ((before, old), (after, new)):
        items = {item["destination"]: item for item in pair[1]["items"]} if pair else {}
        for path, value in states.items():
            if path in (".gitattributes", ".agent-assets/selection.json", ".agent-assets/lock.json") or value is None:
                continue
            item = items.get(path)
            from . import configuration
            if path in configuration.PATHS.values():
                if item and (item["type"] != "configuration" or not configuration.entries_match(value[0], item["entries"]) or (os.name != "nt" and value[1] != item["mode"])):
                    raise AssetError("ASSET_INTERRUPTED", "Interrupted configuration is not authorized by its ownership baseline.")
                continue
            if not item or digest(value[0]) != item["baseline_digest"] or (os.name != "nt" and value[1] != item["mode"]):
                raise AssetError("ASSET_INTERRUPTED", "Interrupted payload is not authorized by its ownership baseline.")
    from . import configuration
    for path in configuration.PATHS.values():
        if path not in before:
            continue
        unrelated_configs = []
        for states, pair in ((before, old), (after, new)):
            item = next((item for item in pair[1]["items"] if item["destination"] == path), None) if pair else None
            data = states[path][0] if states[path] else None
            unowned = configuration.without_owned(data, item["entries"]) if item and data is not None else configuration.parse(data)
            if path == configuration.PATHS["copilot"] and type(unowned.get("version")) is int and unowned["version"] == 1:
                unowned.pop("version")
            unrelated_configs.append(unowned)
        if unrelated_configs[0] != unrelated_configs[1]:
            raise AssetError("ASSET_INTERRUPTED", "Interrupted configuration changes unowned settings.")
    def unrelated(states, pair):
        value = states.get(".gitattributes")
        data = value[0] if value else b""
        for entry in pair[1]["attributes"] if pair else []:
            line = ('"' + entry["destination"] + '" ' + " ".join(entry["values"]) + "\n").encode()
            if data.count(line) != 1:
                raise AssetError("ASSET_INTERRUPTED", "Ambiguous interrupted checkout ownership.")
            data = data.replace(line, b"")
        for marker in (b"# agent-assets begin\n", b"# agent-assets end\n"):
            data = data.replace(marker, b"")
        return data.rstrip(b"\n")
    if unrelated(before, old) != unrelated(after, new):
        raise AssetError("ASSET_INTERRUPTED", "Interrupted attributes modify unowned rules.")
    directories = journal.get("created_directories")
    if not isinstance(directories, list) or len(set(directories)) != len(directories):
        raise AssetError("ASSET_INTERRUPTED", "Invalid interrupted directory list.")
    allowed = {parent.as_posix() for path in after for parent in Path(path).parents if parent != Path(".")}
    if any(not isinstance(path, str) or path not in allowed for path in directories):
        raise AssetError("ASSET_INTERRUPTED", "Unsafe interrupted directory.")
    identities = journal.get("directory_identities")
    if not isinstance(identities, dict) or set(identities) != allowed | {"."}:
        raise AssetError("ASSET_INTERRUPTED", "Invalid interrupted directory identities.")
    if any(value is not None and (not isinstance(value, list) or len(value) != 2
            or any(type(number) is not int or number < 0 for number in value)) for value in identities.values()):
        raise AssetError("ASSET_INTERRUPTED", "Invalid interrupted directory identity.")
    if any(value is None and name not in directories for name, value in identities.items()):
        raise AssetError("ASSET_INTERRUPTED", "Missing interrupted parent authority.")
    return before, after


def staging_path(path, operation_id):
    return Path(path).parent / (".agent-assets-" + operation_id + "-" + digest(path.encode())[:20])


def inspect_staging(root, journal, before, after):
    from .core import inspect_destination
    found = []
    for path in before:
        staging = staging_path(path, journal["operation_id"])
        inspect_destination(root, staging.as_posix())
        target = root / staging
        if target.exists():
            data = target.read_bytes()
            expected = [value[0] for value in (before[path], after[path]) if value is not None]
            if not any(value.startswith(data) for value in expected) or target.stat().st_nlink != 1:
                raise AssetError("ASSET_INTERRUPTED", "Ambiguous interrupted staging bytes: " + staging.as_posix())
            found.append((target, (data, target.stat().st_mode & 0o777)))
    return found


def require_mutation_support():
    if os.name != "posix":
        raise AssetError("ASSET_PLATFORM_UNSUPPORTED", "Native Windows writes/recovery await verified parent-handle support; read-only status and preview remain available.")


def check_directories(root, journal):
    from .core import directory_identity
    for name, expected in journal["directory_identities"].items():
        try:
            current = directory_identity(root / name)
        except FileNotFoundError:
            if name in journal["created_directories"]:
                continue
            raise AssetError("ASSET_INTERRUPTED", "Interrupted destination parent is missing: " + name) from None
        except OSError:
            raise AssetError("ASSET_INTERRUPTED", "Interrupted destination parent is unsafe: " + name) from None
        if current != expected:
            raise AssetError("ASSET_INTERRUPTED", "Interrupted destination parent identity changed: " + name)


def recover(root):
    try:
        _recover(root)
    except AssetError as error:
        if error.exit_code == 1:
            raise AssetError("ASSET_INTERRUPTED", "Cannot safely recover the pending operation: " + str(error)) from None
        raise


def _recover(root):
    from .core import write_atomic, unlink_owned, prune_empty, authenticate_ownership
    require_mutation_support()
    path = state_path(root, "agent-assets-journal.json")
    if not path.exists():
        return
    with mutex(root):
        journal_bytes = path.read_bytes()
        journal_mode = path.stat().st_mode & 0o777
        journal = read_json(journal_bytes, "ASSET_INTERRUPTED")
        before, after = validate_journal(journal)
        check_directories(root, journal)
        for states in (before, after):
            recorded = record_pair(states)
            if recorded:
                authenticate_ownership(recorded)
        current = observe(root, before)
        for name, value in current.items():
            if value not in (before[name], after[name]):
                raise AssetError("ASSET_INTERRUPTED", "External edits prevent safe recovery: " + name + ". Resolve the interrupted operation explicitly.")
        staging_files = inspect_staging(root, journal, before, after)
        for staged, expected in staging_files:
            unlink_owned(staged, expected)
        for name, value in before.items():
            if current[name] == value:
                continue
            if observe(root, [name])[name] != current[name]:
                raise AssetError("ASSET_INTERRUPTED", "Concurrent edit during recovery: " + name)
            if value is None:
                unlink_owned(root / name, current[name])
            else:
                write_atomic(root / name, *value, expected=current[name],
                             staging=root / staging_path(name, journal["operation_id"]))
            if observe(root, [name])[name] != value:
                raise AssetError("ASSET_INTERRUPTED", "Recovery verification failed: " + name)
        check_directories(root, journal)
        for name in sorted(journal["created_directories"], key=lambda v: len(Path(v).parts), reverse=True):
            prune_empty(root / name)
        unlink_owned(path, (journal_bytes, journal_mode))


def apply(root, writes, removals, observations, recheck):
    from .core import write_atomic, unlink_owned, prune_empty, directory_identity
    require_mutation_support()
    with mutex(root):
        if pending(root):
            raise AssetError("ASSET_INTERRUPTED", "A pending interrupted operation appeared; retry to recover it.")
        if observe(root, observations) != observations:
            raise AssetError("ASSET_CONFLICT", "Target changed during planning; inspect it and rerun.", 1)
        recheck()
        paths = set(writes) | set(removals) | {".agent-assets/selection.json", ".agent-assets/lock.json", ".gitattributes"}
        entries = []
        directories = set()
        for path in sorted(paths):
            before = observations[path]
            after = None if path in removals else writes.get(path, before)
            entries.append({"destination": path, "before": encode(before), "after": encode(after)})
            for parent in Path(path).parents:
                if parent != Path(".") and not (root / parent).exists():
                    directories.add(parent.as_posix())
        directory_names = {parent.as_posix() for path in paths for parent in Path(path).parents}
        identities = {}
        for name in sorted(directory_names):
            try:
                identities[name] = directory_identity(root / name)
            except FileNotFoundError:
                identities[name] = None
        journal = {"schema_version": 1, "operation_id": uuid.uuid4().hex, "entries": entries,
                   "created_directories": sorted(directories), "directory_identities": identities}
        validate_journal(journal)
        journal_path = state_path(root, "agent-assets-journal.json")
        journal_bytes = canonical(journal) + b"\n"
        write_atomic(journal_path, journal_bytes, 0o600)
        def bind_created(parent_fd, created):
            nonlocal journal_bytes
            created_names = {path.relative_to(root).as_posix() for path in created}
            changed = False
            for name in created_names:
                if name not in directories or identities[name] is not None:
                    raise AssetError("ASSET_INTERRUPTED", "Unexpected created destination parent: " + name)
                identities[name] = directory_identity(root / name)
                changed = True
            if changed:
                updated = canonical(journal) + b"\n"
                write_atomic(journal_path, updated, 0o600, expected=(journal_bytes, 0o600))
                journal_bytes = updated
            check_directories(root, journal)
        for path in removals:
            check_directories(root, journal)
            if observe(root, [path])[path] != observations[path]:
                raise AssetError("ASSET_INTERRUPTED", "Concurrent edit during removal: " + path)
            unlink_owned(root / path, observations[path])
        for path, (data, mode) in writes.items():
            if observe(root, [path])[path] != observations[path]:
                raise AssetError("ASSET_INTERRUPTED", "Concurrent edit during replacement: " + path)
            write_atomic(root / path, data, mode, expected=observations[path], parent_check=bind_created,
                         staging=root / staging_path(path, journal["operation_id"]))
            if observe(root, [path])[path] != (data, mode):
                raise AssetError("ASSET_INTERRUPTED", "Replacement verification failed: " + path)
        check_directories(root, journal)
        expected = {entry["destination"]: decode(entry["after"]) for entry in entries}
        if observe(root, expected) != expected:
            raise AssetError("ASSET_INTERRUPTED", "Target changed before transaction completion.")
        unlink_owned(journal_path, (journal_bytes, 0o600))
        for path in removals:
            parent = (root / path).parent
            while parent != root:
                if not prune_empty(parent):
                    break
                parent = parent.parent
