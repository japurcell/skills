"""POSIX repository ownership, held-directory writes and cooperating locks.

The Git lock covers cooperating config writers. A direct editor replacing the
config during promotion is outside this protocol, not an atomic CAS guarantee.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path
import re
import stat

from .scan_private import Directory, decoded, encoded
from .scan_repo_install import HOOKS, LIMITS, fail, identity
from .scan_types import ScanContext, ScanLimits

OWNER_SCHEMA = "scan_secrets_repository_owner_v1"
MANIFEST = "repository-installation.json"
KEYS = {"schema", "version", "phase", "repository", "scope", "config", "previous_value", "installed_value", "before", "after",
        "build", "interpreter", "git", "git_identity", "data", "budget_file", "hooks", "files", "bindings", "before_value", "selection", "config_lock", "original_effective", "config_absent"}
PHASES = {"prepared", "active", "retiring", "retired"}
MAX_FILES = 128
OWNER_MAX_BYTES = LIMITS["file_bytes"]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def context():
    return ScanContext(ScanLimits(max_seconds=20, max_capture_bytes=1048576,
        max_capture_total_bytes=16777216, max_temp_bytes=16777216))


def read(snapshot, path, *, missing=False, maximum=1048576):
    with snapshot.reader.open_selected(path, missing=missing) as descriptor:
        if descriptor is None:
            return None
        info = os.fstat(descriptor)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid not in {0, os.getuid()}
                or info.st_mode & 0o022):
            fail("installation_file_untrusted", 3, "ownership")
        raw = snapshot.reader.read(path, descriptor=descriptor, maximum=maximum)
        return raw


def owner(raw, base, repository):
    if len(raw) > OWNER_MAX_BYTES:
        fail("installation_ownership_limit", 3, "preparation", "The complete repository ownership manifest exceeds its supported byte limit. Choose shorter repository/runtime/original-hook locations before retrying; no gates were activated.", measured=len(raw), limit=OWNER_MAX_BYTES, unit="bytes")
    try:
        value = decoded(raw)
        if type(value) is not dict:
            raise ValueError
        if value.get("schema") != OWNER_SCHEMA:
            fail("installation_ownership_unsupported", 3, "ownership")
        if value.keys() != KEYS or type(value["installed_value"]) is not str:
            raise ValueError
        if base is None:
            base = Path(value["installed_value"]).parent
        if (value.keys() != KEYS or type(value["version"]) is not int or value["version"] != 1
                or value["phase"] not in PHASES or value["repository"] != {key: str(repository[key]) for key in ("root", "gitdir", "common")}
                or base.parent != repository["gitdir"] / "scan-secrets/installations" or re.fullmatch(r"[0-9a-f]{32}", base.name) is None
                or value["installed_value"] != str(base / "hooks") or value["scope"] not in {"repository", "worktree"}
                or value["config"] != str(repository["gitdir"] / "config.worktree" if value["scope"] == "worktree" else repository["common"] / "config")
                or type(value["files"]) is not dict or not 1 <= len(value["files"]) <= MAX_FILES
                or type(value["hooks"]) is not list or len(value["hooks"]) != len(HOOKS)
                or {item["name"] for item in value["hooks"]} != set(HOOKS)
                or type(value["bindings"]) is not list or len(value["bindings"]) > 32
                or value["previous_value"] is not None and type(value["previous_value"]) is not str):
            raise ValueError
        if (type(value["config_absent"]) is not bool or type(value["original_effective"]) is not str
                or value["before_value"] is not None and type(value["before_value"]) is not str
                or type(value["selection"]) is not dict or value["selection"].keys() != {"destinations", "lfs", "endpoint", "budget_file", "data", "interpreter", "git", "original_effective"}
                or value["config_lock"] is not None and (type(value["config_lock"]) is not list or len(value["config_lock"]) != 7 or any(type(n) is not int for n in value["config_lock"]))
                or value["phase"] in {"active", "retired"} and value["config_lock"] is not None):
            raise ValueError
        from .scan_repo_install import path_value
        original_directory = path_value(value["original_effective"])
        for key in ("previous_value", "before_value"):
            if value[key] is not None:
                path_value(value[key])
        for key in ("interpreter", "git", "data"):
            if type(value[key]) is not str or not Path(value[key]).is_absolute() or any(ord(c) < 32 for c in value[key]):
                raise ValueError
        for key in ("build", "before", "after"):
            if type(value[key]) is not str or re.fullmatch(r"[0-9a-f]{64}", value[key]) is None:
                raise ValueError
        for name, record in value["files"].items():
            if (not isinstance(name, str) or Path(name).is_absolute() or any(part in {".", ".."} for part in name.split("/"))
                    or len(Path(name).parts) > 5 or type(record) is not dict or record.keys() != {"sha256", "identity"}
                    or re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) is None
                    or type(record["identity"]) is not list or len(record["identity"]) != 7
                    or any(type(n) is not int for n in record["identity"])):
                raise ValueError
        for hook in value["hooks"]:
            from .scan_repo_install import RECEIVE_HOOKS
            cwd = repository["gitdir"] if hook["name"] in RECEIVE_HOOKS else repository["root"]
            expected_path = Path(os.path.abspath((original_directory if original_directory.is_absolute() else cwd / original_directory) / hook["name"]))
            if (hook["path"] != str(expected_path) or hook["cwd"] != str(cwd) or type(hook) is not dict or hook.keys() != {"name", "path", "cwd", "state", "executable", "identity", "sha256"}
                    or not Path(hook["path"]).is_absolute() or Path(hook["path"]).name != hook["name"]
                    or Path(hook["path"]).is_relative_to(base) or hook["state"] not in {"present", "absent"}
                    or type(hook["executable"]) is not bool):
                raise ValueError
        for name in value["bindings"]:
            if type(name) is not str or name not in value["files"] or re.fullmatch(r"bindings/[0-9]+\.json", name) is None:
                raise ValueError
        required = {"backups/config.before", "backups/config.after", "backups/config.original", "bundle/scripts/scan-secrets.py", "bundle/hooks/runtime/scan_cli.py",
                    *("hooks/" + name for name in HOOKS), *value["bindings"]}
        if not required <= value["files"].keys():
            raise ValueError
        return value
    except (ValueError, TypeError, KeyError, RecursionError, UnicodeError):
        fail("installation_ownership_invalid", 3, "ownership",
             "Preserve and review the repository ownership manifest; no restoration was attempted.")


def validate(snapshot, base, value, *, originals=True, missing_helpers=False):
    snapshot.trusted_location(base)
    if stat.S_IMODE(base.lstat().st_mode) != 0o700 or base.lstat().st_uid != os.getuid():
        fail("installation_ownership_invalid", 3, "ownership")
    inventory = set()
    expected = set(value["files"]) | {MANIFEST}
    for name in list(expected):
        expected.update(str(parent) for parent in Path(name).parents if str(parent) != ".")
    with contextlib.ExitStack() as resources:
        directory = Directory(base, snapshot.context, resources)
        def visit(selected, prefix=""):
            with os.scandir(selected.descriptor) as entries:
                for entry in entries:
                    snapshot.context.check_deadline()
                    name = prefix + entry.name
                    inventory.add(name)
                    if name not in expected or len(inventory) > MAX_FILES + 16:
                        fail("installation_owned_inventory_drift", 3, "ownership",
                             "Preserve added or missing repository-owned files and backups for review.")
                    info = entry.stat(follow_symlinks=False)
                    if (stat.S_ISLNK(info.st_mode) or info.st_uid != os.getuid() or
                            not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode))):
                        fail("installation_owned_drift", 3, "ownership")
                    if not stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) not in ({0o600} if name == MANIFEST else {0o600, 0o700}):
                        fail("installation_owned_drift", 3, "ownership")
                    if stat.S_ISDIR(info.st_mode):
                        if stat.S_IMODE(info.st_mode) != 0o700:
                            fail("installation_owned_drift", 3, "ownership")
                        visit(selected.child(entry.name), name + "/")
        visit(directory)
    absent = expected - inventory
    if absent and (not missing_helpers or any(name.startswith("backups/") or name == MANIFEST for name in absent)):
        fail("installation_owned_inventory_drift", 3, "ownership",
             "A repository-owned file is missing. Use a healthy external CLI to uninstall while preserving the backups.")
    for name, expected_file in value["files"].items():
        path = base / name
        if name in absent:
            continue
        raw = read(snapshot, path)
        if digest(raw) != expected_file["sha256"] or list(identity(path.lstat())) != expected_file["identity"]:
            fail("installation_owned_drift", 3, "ownership", "Preserve the changed owned file and backups. Restore its recorded bytes/identity or review the installation manually.")
    if originals:
        for hook in value["hooks"]:
            snapshot.trusted_location(Path(hook["path"]))
            current = snapshot.read(Path(hook["path"]), missing=True, trusted=True)
            observed = snapshot.observed[Path(hook["path"])]
            if ((current is None) != (hook["state"] == "absent") or
                    observed is not None and (list(observed[0]) != hook["identity"] or observed[1] != hook["sha256"])):
                fail("installation_original_hook_drift", 3, "composition",
                     "An original hook changed or was added. Preserve it and review/reinstall the repository gates before retrying.")


def record(directory, name, raw, *, executable=False):
    parts = Path(name).parts
    selected = directory
    for component in parts[:-1]:
        try:
            selected = selected.child(component)
        except FileNotFoundError:
            child = selected.child(component, create=True)
            os.fsync(selected.descriptor)
            selected = child
    selected.write(parts[-1], raw, mode=0o700 if executable else 0o600)
    with selected.open(parts[-1]) as (handle, _):
        os.fsync(handle.fileno())
    os.fsync(selected.descriptor)
    info = os.stat(parts[-1], dir_fd=selected.descriptor, follow_symlinks=False)
    return {"sha256": digest(raw), "identity": list(identity(info))}


def atomic(directory, name, raw):
    directory.validate()
    temporary = "." + name + ".new"
    directory.write(temporary, raw)
    try:
        with directory.open(temporary) as (handle, _):
            os.fsync(handle.fileno())
        os.replace(temporary, name, src_dir_fd=directory.descriptor, dst_dir_fd=directory.descriptor)
        os.fsync(directory.descriptor)
    finally:
        try:
            os.unlink(temporary, dir_fd=directory.descriptor)
        except FileNotFoundError:
            pass


@contextlib.contextmanager
def locked(snapshot, gitdir, config, *, recovery=None):
    import fcntl
    with contextlib.ExitStack() as resources:
        parent = Directory(gitdir, snapshot.context, resources, private=False)
        name = "scan-secrets-install.lock"
        descriptor = os.open(name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=parent.descriptor)
        resources.callback(os.close, descriptor)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600:
            fail("installation_lock_unsafe", 3, "lock")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            fail("installation_busy", 2, "lock", "Another repository installer holds the lock. Let it finish and retry explicitly.")
        config_parent = Directory(config.parent, snapshot.context, resources, private=False)
        lock_name = config.name + ".lock"
        try:
            lock_fd = os.open(lock_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=config_parent.descriptor)
        except FileExistsError:
            existing = os.stat(lock_name, dir_fd=config_parent.descriptor, follow_symlinks=False)
            if recovery is None or list(identity(existing)) != recovery:
                fail("installation_config_busy", 2, "lock", "Git configuration is locked or ownership is ambiguous. Let an active writer finish; preserve/review an orphan config.lock and private phase journal before retrying. Never remove a foreign lock.")
            lock_fd = os.open(lock_name, os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=config_parent.descriptor)
            if list(identity(os.fstat(lock_fd))) != recovery:
                os.close(lock_fd)
                fail("installation_config_busy", 2, "lock")
        resources.callback(os.close, lock_fd)
        lock_info = os.fstat(lock_fd)
        promoted = False
        def promote(raw):
            nonlocal promoted
            parent.validate()
            config_parent.validate()
            now = os.stat(lock_name, dir_fd=config_parent.descriptor, follow_symlinks=False)
            if (now.st_dev, now.st_ino) != (lock_info.st_dev, lock_info.st_ino):
                fail("installation_config_lock_changed", 2, "promotion")
            if raw is None:
                try:
                    os.unlink(config.name, dir_fd=config_parent.descriptor)
                except FileNotFoundError:
                    pass
                os.unlink(lock_name, dir_fd=config_parent.descriptor)
                promoted = True
                os.fsync(config_parent.descriptor)
                return
            os.lseek(lock_fd, 0, os.SEEK_SET)
            os.ftruncate(lock_fd, 0)
            remaining = memoryview(raw)
            while remaining:
                written = os.write(lock_fd, remaining)
                if written <= 0:
                    raise OSError("short configuration write")
                remaining = remaining[written:]
            os.fsync(lock_fd)
            os.replace(lock_name, config.name, src_dir_fd=config_parent.descriptor, dst_dir_fd=config_parent.descriptor)
            promoted = True
            os.fsync(config_parent.descriptor)
        try:
            yield parent, promote, list(identity(lock_info))
        finally:
            if not promoted:
                try:
                    now = os.stat(lock_name, dir_fd=config_parent.descriptor, follow_symlinks=False)
                    if (now.st_dev, now.st_ino) == (lock_info.st_dev, lock_info.st_ino):
                        os.unlink(lock_name, dir_fd=config_parent.descriptor)
                except FileNotFoundError:
                    pass


def executable_digest(snapshot, path):
    """Hash a bounded trusted tool without retaining its binary in memory."""
    snapshot.trusted_location(path)
    with snapshot.reader.open_selected(path) as descriptor:
        info = os.fstat(descriptor)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or not info.st_mode & 0o111
                or info.st_uid not in {0, os.getuid()} or info.st_mode & 0o022 or info.st_size > 67108864):
            fail("installation_lfs_tool_untrusted", 3, "composition")
        result = hashlib.sha256()
        with os.fdopen(os.dup(descriptor), "rb") as stream:
            while True:
                snapshot.context.check_deadline()
                chunk = stream.read(65536)
                if not chunk:
                    break
                result.update(chunk)
        if identity(info) != identity(os.fstat(descriptor)):
            fail("installation_lfs_tool_changed", 3, "composition")
        return result.hexdigest()
