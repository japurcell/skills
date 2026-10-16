"""Read-only, bounded repository installation discovery. Never activates gates.

Metadata queries retain Git configuration origins, unlike scanner acquisition.
No configuration value is an executable input. Existing hooks are only read.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import shutil
import sys

from .scan_cli import Failure, data_root, safe_audit_location
from .scan_budget import load_budget, unique
from .scan_git import capture_git
from .scan_repository import ProtectedRepository
from .scan_types import ScanContext, ScanFailure, ScanLimits

SCHEMA = "scan_secrets_repo_install_v1"
LIMITS = {"seconds": 10, "command_seconds": 2, "file_bytes": 65536,
          "capture_bytes": 1048576, "config_entries": 2048, "worktrees": 128}
HOOKS = ("applypatch-msg", "pre-applypatch", "post-applypatch", "pre-commit", "pre-merge-commit",
    "prepare-commit-msg", "commit-msg", "post-commit", "pre-rebase", "post-checkout", "post-merge",
    "pre-push", "pre-receive", "update", "proc-receive", "post-receive", "post-update",
    "reference-transaction", "push-to-checkout", "pre-auto-gc", "post-rewrite", "sendemail-validate",
    "fsmonitor-watchman", "p4-changelist", "p4-prepare-changelist", "p4-post-changelist", "p4-pre-submit",
    "post-index-change")
RECEIVE_HOOKS = {"pre-receive", "update", "proc-receive", "post-receive", "post-update", "push-to-checkout"}
RECOVERY = "No changes were applied. Review the repository scope, locations and proposed operations before activation."


def fail(reason, code=2, phase="discovery", recovery="Repair the reported metadata or choose an ordinary unlinked location, then rerun with --dry-run.", **details):
    raise Failure(reason, code, phase, recovery, details=details)


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def path_value(value):
    if not value or len(os.fsencode(value)) > 4096 or any(ord(c) < 32 or ord(c) == 127 for c in value):
        fail("installation_path_invalid", 3)
    if "://" in value or value.startswith(("!", "%(")) or (value.startswith("~") and not value.startswith("~/")):
        fail("installation_path_unsupported", 3)
    if value.startswith("~/"):
        value = str(Path.home() / value[2:])
    return Path(value)


def absolute_location(path):
    selected = Path(os.path.abspath(path))
    if sys.platform == "darwin":
        for alias in (Path("/tmp"), Path("/var")):
            if selected.is_relative_to(alias):
                info = alias.lstat()
                if stat.S_ISLNK(info.st_mode) and info.st_uid == 0:
                    return alias.resolve(strict=True) / selected.relative_to(alias)
                break
    return selected


class Snapshot:
    def __init__(self):
        self.context = ScanContext(ScanLimits(max_seconds=LIMITS["seconds"], max_capture_bytes=LIMITS["file_bytes"],
            max_capture_total_bytes=LIMITS["capture_bytes"], max_temp_bytes=LIMITS["capture_bytes"]))
        self.reader = ProtectedRepository(self.context, Path.cwd())
        self.observed = {}

    def read(self, path, *, missing=False, trusted=False):
        path = Path(os.path.abspath(path))
        try:
            with self.reader.open_selected(path, missing=missing) as descriptor:
                if descriptor is None:
                    self.observed[path] = None
                    return None
                info = os.fstat(descriptor)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    fail("installation_file_unsafe")
                if trusted and os.name != "nt" and (info.st_uid not in {0, os.getuid()} or info.st_mode & 0o022):
                    fail("installation_file_untrusted")
                raw = self.reader.read(path, descriptor=descriptor, maximum=LIMITS["file_bytes"])
                self.observed[path] = (identity(info), hashlib.sha256(raw).hexdigest())
                return raw
        except FileNotFoundError:
            if missing:
                self.directory(path.parent, missing=True)
                self.observed[path] = None
                return None
            raise

    def directory(self, path, *, missing=False):
        # open_selected holds every ancestor without following links; the dummy
        # leaf is never opened. This also admits a not-yet-created destination.
        path = Path(path) if Path(path).is_absolute() else Path.cwd() / path
        while True:
            try:
                with self.reader.open_selected(path / ".preview-never-opened", parent_only=True):
                    return path
            except FileNotFoundError:
                if not missing or path.parent == path:
                    raise
                path = path.parent

    def trusted_location(self, path):
        path = absolute_location(path)
        self.directory(path if path.is_dir() else path.parent, missing=True)
        if os.name == "nt":
            fail("installation_platform_unverified", 3, "preflight", "Repository installation preview requires verified native ownership checks on this platform.")
        for parent in (path, *path.parents):
            self.context.check_deadline()
            try:
                info = parent.lstat()
            except FileNotFoundError:
                continue
            if (info.st_uid not in {0, os.getuid()} or
                (info.st_mode & 0o022 and not (info.st_uid == 0 and info.st_mode & stat.S_ISVTX))):
                fail("installation_location_untrusted", 3)

    def unchanged(self):
        before = self.observed.copy()
        for path, expected in before.items():
            self.read(path, missing=expected is None)
            if self.observed[path] != expected:
                fail("installation_metadata_changed")

    def query(self, git, env, root, *arguments):
        with capture_git(self.context, list(arguments), cwd=root, deadline=self.context.deadline,
                executable=str(git), environment=env, command_seconds=LIMITS["command_seconds"]) as capture:
            return b"".join(capture.chunks())


def trusted_git(snapshot, repository, explicit):
    root, common = repository["root"], repository["common"]
    ambient = shutil.which("git")
    candidate = path_value(explicit) if explicit else Path(ambient) if ambient else None
    if candidate is None:
        fail("installation_git_unavailable", 3, "preflight", "Select an absolute trusted direct Git executable with --git PATH and retry.")
    if not candidate.is_absolute():
        fail("installation_git_location_unsafe", 3, "preflight", "Select an absolute trusted direct Git executable with --git PATH.")
    repository_roots = (root, common.parent if common.name == ".git" else common)
    if any(candidate.is_relative_to(location) for location in repository_roots):
        fail("installation_git_location_unsafe", 3, "preflight", "Select a trusted Git executable outside the repository with --git PATH.")
    snapshot.directory(candidate.parent)
    selected = candidate.resolve(strict=True)
    if sys.platform == "darwin" and selected in {Path("/usr/bin/git"), Path("/usr/bin/xcrun")}:
        fail("installation_git_selection_required", 3, "preflight",
             "Select the intended trusted direct Git binary with --git PATH, for example the installed developer-toolchain usr/bin/git. The Apple launcher cannot be resolved by this read-only preview.")
    if any(selected.is_relative_to(location) for location in repository_roots):
        fail("installation_git_location_unsafe", 3, "preflight", "Select a trusted Git executable outside the repository with --git PATH.")
    snapshot.trusted_location(selected)
    info = selected.lstat()
    if not stat.S_ISREG(info.st_mode) or not os.access(selected, os.X_OK):
        fail("installation_git_location_unsafe", 3)
    return selected


def environment(snapshot):
    keys = ("HOME", "USERPROFILE", "XDG_CONFIG_HOME", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "TMPDIR")
    env = {key: os.environ[key] for key in keys if key in os.environ}
    for key in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM"):
        if key in os.environ:
            path = path_value(os.environ[key])
            if not path.is_absolute():
                fail("installation_config_location_invalid", 3)
            if str(path) != os.devnull:
                snapshot.read(path, missing=True, trusted=True)
            env[key] = str(path)
    if "GIT_CONFIG_NOSYSTEM" in os.environ:
        env["GIT_CONFIG_NOSYSTEM"] = os.environ["GIT_CONFIG_NOSYSTEM"]
    env.update(PATH=os.defpath, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="", SSH_ASKPASS="", GIT_PAGER="cat",
        GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0", LC_ALL="C")
    settings = {"core.fsmonitor": "false", "core.untrackedCache": "false", "core.pager": "cat",
                "maintenance.auto": "false", "gc.auto": "0"}
    env["GIT_CONFIG_COUNT"] = str(len(settings))
    for index, (key, value) in enumerate(settings.items()):
        env[f"GIT_CONFIG_KEY_{index}"] = key
        env[f"GIT_CONFIG_VALUE_{index}"] = value
    return env


def configuration(snapshot, git, env, root):
    raw = snapshot.query(git, env, root, "config", "--includes", "--null", "--show-origin", "--show-scope", "--list")
    fields = raw.split(b"\0")
    if fields[-1] or len(fields) % 3 != 1:
        fail("installation_config_invalid")
    count = (len(fields) - 1) // 3
    if count > LIMITS["config_entries"]:
        fail("installation_config_entry_limit", measured=count, limit=LIMITS["config_entries"], unit="entries")
    entries, origins, seen = [], {}, set()
    worktree_config = False
    for offset in range(0, len(fields) - 1, 3):
        scope, origin, setting = (os.fsdecode(value) for value in fields[offset:offset + 3])
        key, separator, value = setting.partition("\n")
        if scope == "command":
            continue  # Only our fixed inert execution overrides can enter here.
        if scope not in {"system", "global", "local", "worktree"} or not origin.startswith("file:"):
            fail("installation_config_origin_unsupported", 3)
        source = path_value(origin[5:])
        source = source if source.is_absolute() else root / source
        source = Path(os.path.abspath(source))
        if source not in origins:
            contents = snapshot.read(source, trusted=True)
            origins[source] = {"path": str(source), "sha256": hashlib.sha256(contents).hexdigest()}
        if key.lower() == "extensions.worktreeconfig":
            if value.lower() not in {"true", "false", "yes", "no", "on", "off", "1", "0", ""}:
                fail("installation_config_invalid", 3)
            worktree_config = value.lower() in {"true", "yes", "on", "1", ""}
        if key.lower() != "core.hookspath":
            continue
        if not separator or (scope, source) in seen:
            fail("installation_hooks_path_ambiguous", 3)
        seen.add((scope, source))
        path = path_value(value)
        entries.append({"scope": scope, "origin": str(source), "value": str(path), "precedence": len(entries)})
    return raw, entries, list(origins.values()), worktree_config


def interpreter():
    try:
        if sys.version_info < (3, 12):
            raise ValueError
        import sqlite3
        connection = sqlite3.connect(":memory:", timeout=0, autocommit=True)
        try:
            connection.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE, False)
        finally:
            connection.close()
    except Exception:
        fail("installation_interpreter_unsupported", 3, "interpreter",
             "Use an isolated Python 3.12 or newer interpreter with sqlite3 autocommit and SQLITE_DBCONFIG_DEFENSIVE/setconfig support, then retry.")
    return {"path": str(Path(sys.executable).resolve(strict=True)), "python": ".".join(map(str, sys.version_info[:3])),
            "sqlite": sqlite3.sqlite_version, "sqlite_autocommit": True, "sqlite_setconfig": True}


def run(args, *, entry, runtime):
    if not args.dry_run:
        fail("installation_activation_unavailable", 3, "activation", "Use hooks install/uninstall --dry-run to preview. Activation and rollback are not implemented yet.")
    capabilities = interpreter()
    if os.name != "posix":
        fail("installation_platform_unverified", 3, "preflight", "Repository installation preview requires verified native ownership checks on this platform.")
    from .scan_status import discover, StatusError
    snapshot = Snapshot()
    try:
        repository = discover(args.repo, snapshot.context.deadline)
        if repository is None:
            fail("not_repository", 3)
        snapshot.directory(Path(args.repo))
        root, gitdir, common = (repository[key] for key in ("root", "gitdir", "common"))
        for directory in (root, gitdir, common):
            snapshot.directory(directory)
        # Read metadata again through held ancestry. Discovery itself never uses
        # inherited repository redirects; compare with Git's own metadata view.
        for path in (root / ".git", gitdir / "HEAD", gitdir / "commondir"):
            if path.is_dir():
                snapshot.directory(path)
            else:
                metadata = snapshot.read(path, missing=True)
                if metadata is not None and (path == root / ".git" or path.name == "commondir"):
                    target = metadata[8:] if path.name == ".git" else metadata
                    target = path_value(os.fsdecode(target.rstrip(b"\r\n")))
                    snapshot.directory(target if target.is_absolute() else path.parent / target)
        git = trusted_git(snapshot, repository, args.git)
        env = environment(snapshot)
        raw = snapshot.query(git, env, root, "rev-parse", "--path-format=absolute", "--show-toplevel", "--absolute-git-dir", "--git-common-dir", "--show-object-format")
        rows = raw.splitlines()
        if len(rows) != 4 or rows[3] not in {b"sha1", b"sha256"} or [Path(os.fsdecode(row)).resolve() for row in rows[:3]] != [root, gitdir, common]:
            fail("installation_repository_ambiguous", 3)
        config_raw, entries, origins, worktree_config = configuration(snapshot, git, env, root)
        selected = Path(entries[-1]["value"]) if entries else common / "hooks"
        hooks = []
        for name in HOOKS:
            cwd = gitdir if name in RECEIVE_HOOKS else root
            path = selected / name if selected.is_absolute() else cwd / selected / name
            path = Path(os.path.abspath(path))
            raw = snapshot.read(path, missing=True)
            observed = snapshot.observed[path]
            info = observed[0] if observed else None
            hooks.append({"name": name, "path": str(path), "cwd": str(cwd), "state": "present" if raw is not None else "absent",
                "executable": bool(info and info[2] & 0o111), "identity": list(info) if info else None,
                "sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None})
        ownership_path = gitdir / "scan-secrets/repository-installation.json"
        ownership_raw = snapshot.read(ownership_path, missing=True, trusted=True)
        if ownership_raw is not None:
            # No accepted activation schema exists in T7a. Never reinterpret a
            # neutral bundle installation.json as repository ownership.
            ownership = {"path": str(ownership_path), "state": "unrecognized",
                "identity": list(snapshot.observed[ownership_path][0]), "sha256": hashlib.sha256(ownership_raw).hexdigest()}
            try:
                document = json.loads(ownership_raw, object_pairs_hook=unique)
                if not isinstance(document, dict):
                    raise ValueError
            except (ValueError, UnicodeError, RecursionError):
                fail("installation_ownership_invalid", 3, "ownership", "Preserve and review the malformed repository ownership manifest; no restoration was attempted.", ownership=ownership)
            fail("installation_ownership_unsupported", 3, "ownership", "Preserve the existing repository manifest for review; this version cannot validate or restore an activated installation.", ownership=ownership)
        worktree_raw = snapshot.query(git, env, root, "worktree", "list", "--porcelain", "-z")
        worktrees = [os.fsdecode(field[9:]) for field in worktree_raw.split(b"\0") if field.startswith(b"worktree ")]
        if not worktrees or len(worktrees) > LIMITS["worktrees"]:
            fail("installation_worktree_limit", measured=len(worktrees), limit=LIMITS["worktrees"], unit="worktrees")
        for worktree in worktrees:
            path_value(worktree)
        budget_path = None
        if args.budget_file:
            budget_path = absolute_location(args.budget_file)
            snapshot.trusted_location(budget_path)
            snapshot.read(budget_path, trusted=True)
            info = snapshot.observed[budget_path][0]
            if os.name != "nt" and (budget_path.lstat().st_uid != os.getuid() or info[2] & 0o077):
                fail("installation_budget_untrusted", 3, "configuration", "Use an owner-only ordinary schema-1 budget file outside linked or writable ancestors and retry.")
        try:
            checkpoint, budget_identity = load_budget(str(budget_path) if budget_path else None)
            publication, publication_identity = load_budget(str(budget_path) if budget_path else None, profile="publication")
            if budget_identity != publication_identity or (budget_path and budget_identity != snapshot.observed[budget_path][1]):
                fail("installation_budget_changed", 3, "configuration", "Keep the owner-selected budget stable during preview and retry.")
        except (ValueError, OSError):
            fail("invalid_budget", 3, "configuration", "Choose a trusted complete schema-1 budget file within the documented ranges and retry.")
        for location in (entry, runtime, Path(capabilities["path"])):
            snapshot.trusted_location(location)
        data = safe_audit_location(data_root()).parent
        if data.is_relative_to(root) or data.is_relative_to(entry.parent.parent):
            fail("installation_data_location_unsafe", 3)
        snapshot.trusted_location(data)
        if configuration(snapshot, git, env, root)[0] != config_raw:
            fail("installation_metadata_changed")
        snapshot.unchanged()
        scope = "selected_worktree" if worktree_config else "shared_config_requires_scope_decision" if len(worktrees) > 1 else "repository"
        result = {"schema": SCHEMA, "action": args.action, "outcome": "preview", "reason": "read_only_preview",
            "phase": "preview", "dry_run": True, "activated": False, "changes_applied": False, "authorizes_publication": False,
            "recovery": RECOVERY, "limits": LIMITS,
            "snapshot": {"repository": {"root": str(root), "gitdir": str(gitdir), "common": str(common), "object_format": rows[3].decode(),
                "linked": gitdir != common, "worktree_config_enabled": worktree_config, "worktrees": worktrees, "proposed_scope": scope},
                "git": str(git), "git_selection": "explicit" if args.git else "trusted_path", "configuration_sources": origins,
                "hooks_path": {"source": "configuration" if entries else "default", "entries": entries,
                    "effective": str(selected), "relative_to": "hook_cwd" if not selected.is_absolute() else "absolute"},
                "hooks": hooks, "ownership": {"path": str(ownership_path), "state": "absent"},
                "interpreter": capabilities, "locations": {"entrypoint": str(entry.resolve()), "runtime": str(runtime.resolve()),
                    "data": str(data), "budget_file": str(budget_path) if budget_path else None,
                    "dispatchers": str(gitdir / "scan-secrets/hooks")},
                "budget": {"identity": budget_identity, "checkpoint": checkpoint, "publication": publication}},
            "proposed_operations": (["validate trusted runtime and explicit repository scope", "capture original configuration and every supported hook identity",
                "prepare repository-owned dispatchers and ownership manifest", "set an explicit local configuration binding after ownership and recovery validation"]
                if args.action == "install" else ["validate exact repository installation ownership", "restore only unchanged owned configuration and files after recovery is implemented"])}
        return result, 0
    except Failure:
        raise
    except StatusError:
        fail("installation_metadata_unsafe")
    except ScanFailure as error:
        numbers = dict(error.numbers)
        if "measured" in numbers and "unit" not in numbers:
            numbers["unit"] = "bytes"
        if "seconds" in numbers:
            numbers["unit"] = "seconds"
        fail("installation_" + error.cause, phase="discovery", **numbers)
    except (OSError, ValueError, RuntimeError):
        fail("installation_metadata_unsafe")
