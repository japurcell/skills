"""Bounded origin-aware repository discovery and explicit gate installation.

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
        owned = None
        ownership = {"path": str(ownership_path), "state": "absent"}
        if ownership_raw is not None:
            owner_info = ownership_path.lstat()
            if owner_info.st_uid != os.getuid() or stat.S_IMODE(owner_info.st_mode) != 0o600:
                fail("installation_ownership_invalid", 3, "ownership")
            from .scan_repo_state import owner
            try:
                document = json.loads(ownership_raw, object_pairs_hook=unique)
                if not isinstance(document, dict):
                    raise ValueError
            except (ValueError, UnicodeError, RecursionError):
                fail("installation_ownership_invalid", 3, "ownership", "Preserve and review the malformed repository ownership manifest; no restoration was attempted.",
                    ownership={"path": str(ownership_path), "sha256": hashlib.sha256(ownership_raw).hexdigest()})
            try:
                owned = owner(ownership_raw, None, repository)
            except Failure as error:
                error.details["ownership"] = {"path": str(ownership_path), "sha256": hashlib.sha256(ownership_raw).hexdigest()}
                raise
            ownership = {"path": str(ownership_path), "state": owned["phase"], "sha256": hashlib.sha256(ownership_raw).hexdigest()}
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
                "hooks": hooks, "ownership": ownership,
                "interpreter": capabilities, "locations": {"entrypoint": str(entry.resolve()), "runtime": str(runtime.resolve()),
                    "data": str(data), "budget_file": str(budget_path) if budget_path else None,
                    "dispatchers": owned["installed_value"] if owned else str(gitdir / "scan-secrets/installations")},
                "budget": {"identity": budget_identity, "checkpoint": checkpoint, "publication": publication}},
            "proposed_operations": (["validate trusted runtime and explicit repository scope", "capture original configuration and every supported hook identity",
                "prepare repository-owned dispatchers and ownership manifest", "set an explicit local configuration binding after ownership and recovery validation"]
                if args.action == "install" else ["validate exact repository installation ownership", "restore the exact owned binding while preserving unrelated settings, original hooks and private recovery backups"])}
        if not args.dry_run:
            return activate(args, snapshot, result, owned, repository, git, env, entry, runtime)
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


def config_bytes(snapshot, git, env, root, directory, raw, value):
    """Let Git parse/edit only a private copy; append our last binding explicitly.

    Included local hooksPath settings are refused by activation admission, so
    restoring a direct value cannot reorder it relative to an included binding.
    """
    from .scan_repo_state import read
    name = "config-edit"
    path = directory.write(name, raw)
    try:
        # --unset-all exits 5 when the key is absent. Capture that without
        # reinterpreting arbitrary stderr or invoking a config writer on live data.
        with capture_git(snapshot.context, ["config", "--file", name, "--unset-all", "core.hooksPath"],
                cwd=root, executable=str(git), environment=env, allow_nonzero=True, cwd_descriptor=directory.descriptor,
                command_seconds=LIMITS["command_seconds"], deadline=snapshot.context.deadline) as captured:
            if captured.exit_code not in {0, 5}:
                fail("installation_config_edit_failed", 3, "preparation")
        edited = directory.read(name, maximum=65536)
        if value is not None:
            quoted = value.replace("\\", "\\\\").replace('"', '\\"')
            edited += ('\n[core]\n\thooksPath = "' + quoted + '"\n').encode()
        return edited
    finally:
        os.unlink(name, dir_fd=directory.descriptor)


def destinations(snapshot, git, env, root, args):
    if bool(args.remote) != bool(args.url):
        fail("installation_destination_selection_invalid", 3, "configuration", "Pair --remote NAME with --url URL, or use the unambiguous configured destinations.")
    raw = snapshot.query(git, env, root, "config", "--includes", "--null", "--list")
    for field in raw.split(b"\0"):
        key = os.fsdecode(field).partition("\n")[0].lower()
        if key.startswith("includeif.onbranch:"):
            fail("installation_branch_include_unsupported", 3, "configuration", "Branch-dependent includes can change original hook selection during checkout. Use a stable hook configuration before installing; no extension or hooks were changed.")
        if key.startswith("url.") and key.endswith((".insteadof", ".pushinsteadof")):
            fail("installation_url_rewrite_unsupported", 3, "configuration", "URL rewrite settings are unsupported for exact destination admission. Choose an explicit ordinary configuration without insteadOf/pushInsteadOf before installation; no remote was changed.")
    if args.remote:
        selected = [(args.remote, args.url)]
    else:
        remotes = {}
        for field in raw.split(b"\0"):
            key, separator, value = os.fsdecode(field).partition("\n")
            if not separator or not key.startswith("remote."):
                continue
            middle, _, suffix = key[7:].rpartition(".")
            if suffix in {"url", "pushurl"}:
                remotes.setdefault(middle, {}).setdefault(suffix, []).append(value)
        selected = []
        for name, values in remotes.items():
            urls = values.get("pushurl", values.get("url", []))
            if len(urls) != 1:
                fail("installation_destination_ambiguous", 3, "configuration", "Choose one exact destination using --remote NAME --url URL; no remote was changed.")
            selected.append((name, urls[0]))
    if len(selected) > 32:
        fail("installation_destination_limit", 3, "configuration")
    for remote, url in selected:
        if any(not item or len(os.fsencode(item)) > 8192 or any(ord(c) < 32 or ord(c) == 127 for c in item) for item in (remote, url)):
            fail("installation_destination_selection_invalid", 3, "configuration")
    return selected


def composition(snapshot, hooks, args, git, env, root, object_format):
    from .scan_repo_state import digest
    steps, lfs = [], None
    standard = (b'#!/bin/sh\ncommand -v git-lfs >/dev/null 2>&1 || { printf >&2 "\\n%s\\n\\n" "This repository is configured for Git LFS but \'git-lfs\' was not found on your path. If you no longer wish to use Git LFS, remove this hook by deleting the \'pre-push\' file in the hooks directory (set by \'core.hookspath\'; usually \'.git/hooks\')."; exit 2; }\ngit lfs pre-push "$@"\n')
    for hook in hooks:
        if not hook["executable"]:
            continue
        raw = snapshot.read(Path(hook["path"]), trusted=True)
        lowered = raw.lower()
        if any(token in lowered for token in (b"husky", b"lefthook", b"pre_commit", b"pre-commit.com", b"scan-secrets", b"repository-hook")):
            fail("installation_hook_manager_unsupported", 3, "composition", "Review the existing hook manager or recursive wrapper. This installer supports ordinary original-path hooks and the exact standard Git LFS pre-push hook.")
        if hook["name"] != "pre-push":
            continue
        if raw == standard:
            if not args.lfs or not args.lfs_endpoint or sys.platform != "darwin" or object_format != "sha1":
                fail("installation_lfs_selection_required", 3, "composition", "The standard LFS hook requires macOS/SHA-1, --lfs PATH for Git LFS 3.8.0, and --lfs-endpoint URL for basic HTTP. No upload was performed.")
            tool = path_value(args.lfs)
            if not tool.is_absolute() or tool.is_relative_to(root) or tool.is_relative_to(root / ".git"):
                fail("installation_lfs_tool_untrusted", 3, "composition")
            snapshot.trusted_location(tool)
            from .scan_repo_state import executable_digest
            tool_digest = executable_digest(snapshot, tool)
            # Pin only; never execute tools or hooks during discovery/install.
            lfs = {"path": str(tool), "sha256": tool_digest, "version": "3.8.0"}
            from urllib.parse import urlsplit
            endpoint = urlsplit(args.lfs_endpoint)
            if (endpoint.scheme not in {"http", "https"} or not endpoint.hostname or endpoint.username or endpoint.password
                    or endpoint.query or endpoint.fragment or any(ord(c) <= 32 or c in '"\\' for c in args.lfs_endpoint)
                    or endpoint.scheme == "http" and endpoint.hostname != "127.0.0.1"):
                fail("installation_lfs_endpoint_unsupported", 3, "configuration")
            steps.append({"kind": "lfs"})
        elif b"git lfs" in lowered or b"git-lfs" in lowered:
            fail("installation_lfs_hook_unsupported", 3, "composition", "Only the exact standard Git LFS pre-push hook can be replaced by the verified uploader. Preserve and review this custom hook.")
        else:
            steps.append({"kind": "hook", "path": hook["path"], "sha256": hook["sha256"]})
    if lfs is None and (args.lfs or args.lfs_endpoint):
        fail("installation_lfs_hook_unsupported", 3, "composition", "LFS selection requires the recognized standard pre-push hook; no configuration was changed.")
    return steps, lfs


def activate(args, snapshot, result, owned, repository, git, env, entry, runtime):
    import contextlib
    import secrets
    import shlex
    from types import SimpleNamespace
    from .scan_gate import repository_identity
    from .scan_cli import MODULES
    from .scan_private import Directory, encoded
    from .scan_repo_state import MANIFEST, OWNER_SCHEMA, atomic, context, digest, locked, owner, read, record, validate
    root, gitdir, common = (repository[key] for key in ("root", "gitdir", "common"))
    view = result["snapshot"]
    if view["repository"]["proposed_scope"] == "shared_config_requires_scope_decision":
        fail("installation_shared_worktree_scope_unsupported", 3, "scope", "Shared configuration would affect sibling worktrees. Enable worktree configuration separately if desired, then choose --scope worktree; this installer never enables extensions.")
    scope = "worktree" if view["repository"]["worktree_config_enabled"] else "repository"
    if scope == "worktree" and args.scope != "worktree" or args.scope is not None and args.scope != scope:
        fail("installation_scope_selection_required", 3, "scope", "Choose --scope worktree only when extensions.worktreeConfig is already enabled; ordinary repositories use --scope repository.")
    target = gitdir / "config.worktree" if scope == "worktree" else common / "config"
    target_scope = "worktree" if scope == "worktree" else "local"
    for setting in view["hooks_path"]["entries"]:
        if setting["scope"] == target_scope and setting["origin"] != str(target):
            fail("installation_included_hooks_path_unsupported", 3, "scope", "An included configuration file defines this scope's hooksPath. Preserve it and choose an unambiguous direct configuration arrangement before installation.")
    control = gitdir / "scan-secrets"
    for location in (gitdir, target, control):
        snapshot.trusted_location(location)
    if args.action == "install":
        destinations(snapshot, git, env, root, args)
    if owned is not None and args.action == "install" and owned["phase"] == "retiring":
        fail("installation_retirement_recovery_required", 3, "recovery", "Finish hooks uninstall using this repository and scope, then repeat the desired install. Current configuration and retained backups were preserved.")
    snapshot.context = context()
    snapshot.reader.context = snapshot.context
    with locked(snapshot, gitdir, target, recovery=owned["config_lock"] if owned else None) as (parent, promote, config_lock):
        current = read(snapshot, target, missing=True, maximum=65536)
        config_absent = current is None
        current = current if current is not None else b""
        current_configuration, entries, _, current_worktree_config = configuration(snapshot, git, env, root)
        if current_worktree_config != view["repository"]["worktree_config_enabled"]:
            fail("installation_scope_changed", 3, "scope", "Worktree configuration changed before lock acquisition. Retry discovery with --dry-run and choose the current explicit scope.")
        if any(item["scope"] == target_scope and item["origin"] != str(target) for item in entries):
            fail("installation_included_hooks_path_unsupported", 3, "scope")
        selected_entries = [item for item in entries if item["scope"] == target_scope and item["origin"] == str(target)]
        current_value = selected_entries[-1]["value"] if selected_entries else None
        with contextlib.ExitStack() as resources:
            controller = None
            if owned is not None:
                controller = Directory(control, snapshot.context, resources)
                # Control children are bounded before descent. Generation payloads
                # are independently owned; old complete generations are retained.
                control_children = set()
                with os.scandir(controller.descriptor) as children:
                    for item in children:
                        if item.name not in {MANIFEST, "installations"} or len(control_children) >= 2:
                            fail("installation_owned_inventory_drift", 3, "ownership")
                        control_children.add(item.name)
                if control_children != {MANIFEST, "installations"}:
                    fail("installation_owned_inventory_drift", 3, "ownership")
                generations = controller.child("installations")
                with os.scandir(generations.descriptor) as children:
                    count = 0
                    for child in children:
                        count += 1
                        if count > 16 or len(child.name) != 32 or any(c not in "0123456789abcdef" for c in child.name):
                            fail("installation_generation_inventory_invalid", 3, "ownership", "Preserve and archive reviewed retired generations before retrying; at most 16 are retained in one installation directory.")
                base = Path(owned["installed_value"]).parent
                validate(snapshot, base, owned, originals=False, missing_helpers=args.action == "uninstall" or owned["phase"] == "retired")
                if owned["scope"] != scope:
                    fail("installation_scope_changed", 3, "ownership")
                if args.action == "install" and owned["phase"] == "prepared":
                    selection = owned["selection"]
                    changed = (selection["interpreter"] != view["interpreter"]["path"]
                        or selection["git"] != str(git) or owned["git_identity"] != list(identity(git.stat()))
                        or selection["data"] != view["locations"]["data"]
                        or args.budget_file is not None and selection["budget_file"] != view["locations"]["budget_file"]
                        or args.remote is not None and selection["destinations"] != digest(encoded(destinations(snapshot, git, env, root, args)))
                        or args.lfs is not None and (selection["lfs"] is None or selection["lfs"]["path"] != str(path_value(args.lfs)))
                        or args.lfs_endpoint is not None and selection["endpoint"] != digest(encoded(args.lfs_endpoint)))
                    if changed:
                        fail("installation_recovery_selection_changed", 3, "recovery", "The requested selection differs from the prepared installation. Run hooks uninstall using this repository and scope to restore the original binding, then repeat the desired install. Current configuration and backups were preserved.")
                if owned["phase"] in {"prepared", "retiring"}:
                    allowed = {owned["before"], owned["after"]} if owned["phase"] == "prepared" else None
                    if allowed is not None and digest(current) not in allowed:
                        fail("installation_configuration_drift", 3, "recovery", "Preserve current configuration and backups. Recovery refuses observed configuration drift.")
                    if args.action == "install" and owned["phase"] == "prepared":
                        validate(snapshot, base, owned)
                        if digest(current) == owned["before"]:
                            promote(read(snapshot, base / "backups/config.after", maximum=65536))
                        owned["phase"] = "active"
                        owned["config_lock"] = None
                        directory = Directory(base, snapshot.context, resources)
                        atomic(directory, MANIFEST, encoded(owned))
                        atomic(controller, MANIFEST, encoded(owned))
                        return installation_result(result, "recovered", True, True)
                if args.action == "uninstall":
                    if owned["phase"] == "retired":
                        return installation_result(result, "already_uninstalled", False, False)
                    directory = Directory(base, snapshot.context, resources)
                    if owned["phase"] == "retiring" and current_value == owned["previous_value"]:
                        owned["phase"] = "retired"
                        owned["config_lock"] = None
                        atomic(directory, MANIFEST, encoded(owned))
                        atomic(controller, MANIFEST, encoded(owned))
                        return installation_result(result, "recovered_uninstall", False, True)
                    permitted = {owned["installed_value"]}
                    if owned["phase"] == "prepared":
                        permitted.add(owned["before_value"])
                    if current_value not in permitted:
                        fail("installation_configuration_drift", 3, "ownership", "The owned hooksPath binding changed; current settings and backups were preserved.")
                    restored = (read(snapshot, base / "backups/config.original", maximum=65536) if digest(current) in {owned["before"], owned["after"]}
                        else config_bytes(snapshot, git, env, root, directory, current, owned["previous_value"]))
                    backup_name = "uninstall-config.before"
                    if backup_name not in owned["files"]:
                        owned["files"][backup_name] = record(directory, backup_name, current)
                    owned["phase"] = "retiring"
                    owned["config_lock"] = config_lock
                    atomic(directory, MANIFEST, encoded(owned))
                    atomic(controller, MANIFEST, encoded(owned))
                    if (read(snapshot, target, missing=True, maximum=65536) or b"") != current:
                        fail("installation_configuration_drift", 3, "promotion")
                    promote(None if owned["config_absent"] and restored == b"" else restored)
                    owned["phase"] = "retired"
                    owned["config_lock"] = None
                    atomic(directory, MANIFEST, encoded(owned))
                    atomic(controller, MANIFEST, encoded(owned))
                    return installation_result(result, "uninstalled", False, True)
                if owned["phase"] == "active" and (current_value != owned["installed_value"] or not entries or entries[-1]["value"] != owned["installed_value"]):
                    fail("installation_configuration_drift", 3, "ownership", "The owned hooksPath binding changed. Preserve current settings and backups, then review the installation.")
                if owned["phase"] == "retired" and current_value != owned["previous_value"]:
                    fail("installation_configuration_drift", 3, "ownership")
            elif args.action == "uninstall":
                return installation_result(result, "not_installed", False, False)
            elif control.exists():
                fail("installation_unknown_directory", 3, "ownership", "Preserve the unrecognized repository installation directory for review; it was not overwritten.")
            # Reinstallation captures the current ORIGINAL paths, including safe
            # user additions/edits, and never re-wraps the owned launchers.
            prior_binding = owned["previous_value"] if owned else current_value
            underlying = [item for item in entries if not owned or not (item["origin"] == owned["config"] and item["value"] == owned["installed_value"])]
            original_effective = prior_binding if prior_binding is not None else underlying[-1]["value"] if underlying else str(common / "hooks")
            original_directory = path_value(original_effective)
            hooks = []
            for prior in owned["hooks"] if owned else view["hooks"]:
                name = prior["name"]
                cwd = gitdir if name in RECEIVE_HOOKS else root
                path = Path(os.path.abspath((original_directory if original_directory.is_absolute() else cwd / original_directory) / name))
                prior = {**prior, "path": str(path), "cwd": str(cwd)}
                snapshot.trusted_location(path)
                raw = snapshot.read(path, missing=True, trusted=True)
                observed = snapshot.observed[path]
                hooks.append({**prior, "state": "present" if raw is not None else "absent", "executable": bool(observed and observed[0][2] & 0o111),
                    "identity": list(observed[0]) if observed else None, "sha256": digest(raw) if raw is not None else None})
            selected_destinations = destinations(snapshot, git, env, root, args)
            steps, lfs = composition(snapshot, hooks, args, git, env, root, view["repository"]["object_format"])
            selection = {"destinations": digest(encoded(selected_destinations)), "lfs": lfs, "endpoint": digest(encoded(args.lfs_endpoint)),
                "budget_file": view["locations"]["budget_file"], "data": view["locations"]["data"], "interpreter": view["interpreter"]["path"], "git": str(git), "original_effective": original_effective}
            assets = {"scripts/scan-secrets.py": read(snapshot, entry), "hooks/runtime/scan_cli.py": read(snapshot, runtime / "scan_cli.py"),
                      "hooks/runtime/scan_status.py": read(snapshot, runtime / "scan_status.py")}
            assets.update({f"hooks/runtime/{name}.py": read(snapshot, runtime / (name + ".py")) for name in MODULES})
            build = hashlib.sha256()
            for name, raw in ((entry.name, assets["scripts/scan-secrets.py"]), ("scan_cli.py", assets["hooks/runtime/scan_cli.py"]),
                    ("scan_status.py", assets["hooks/runtime/scan_status.py"]), *((name + ".py", assets[f"hooks/runtime/{name}.py"]) for name in MODULES)):
                compile(raw, name, "exec")
                build.update(name.encode() + b"\0" + raw)
            if (owned and owned["phase"] == "active" and selection == owned["selection"] and hooks == owned["hooks"]
                    and build.hexdigest() == owned["build"] and list(identity(git.lstat())) == owned["git_identity"]):
                return installation_result(result, "already_installed", True, False)
            if owned and count >= 16:
                fail("installation_generation_limit", 3, "preparation", "Archive reviewed retired private generations before another explicit update; the retained generation limit is 16.")
            snapshot.trusted_location(target)
            # Reobserve only original metadata while both cooperating locks hold.
            if configuration(snapshot, git, env, root)[0] != current_configuration:
                fail("installation_metadata_changed", 2, "preparation")
            token = secrets.token_hex(16)
            base = control / "installations" / token
            parent.validate()
            staging = parent.child(".scan-secrets-prepare-" + secrets.token_hex(16), create=True)
            temporary = staging.path
            if controller is None:
                generations = staging.child("installations", create=True)
                directory = generations.child(token, create=True)
            else:
                directory = staging
            after = config_bytes(snapshot, git, env, root, directory, current, str(base / "hooks"))
            previous_value = owned["previous_value"] if owned else current_value
            if owned is None or owned["phase"] == "retired":
                original = current
            elif digest(current) == owned["after"]:
                original = read(snapshot, Path(owned["installed_value"]).parent / "backups/config.original", maximum=65536)
            else:
                original = config_bytes(snapshot, git, env, root, directory, current, previous_value)
            files = {"bundle/" + name: record(directory, "bundle/" + name, raw) for name, raw in assets.items()}
            for name in HOOKS:
                launcher = "#!/bin/sh\nexec " + shlex.join([view["interpreter"]["path"], "-I", "-S", "-B", str(base / "bundle/scripts/scan-secrets.py"),
                    "repository-hook", "--installation", str(base), name, "--"]) + ' "$@"\n'
                from .scan_repo_dispatch import passthrough
                raw_launcher = launcher.encode() if name in {"pre-commit", "pre-push"} else passthrough(next(hook for hook in hooks if hook["name"] == name), view["interpreter"]["path"])
                files["hooks/" + name] = record(directory, "hooks/" + name, raw_launcher, executable=True)
            bindings = []
            repository_key = repository_identity(SimpleNamespace(**repository))
            for index, (remote, url) in enumerate(selected_destinations):
                binding = dict(schema_version=1, build=build.hexdigest(), repository_identity=repository_key,
                    interpreter=view["interpreter"]["path"], data_directory=view["locations"]["data"], budget_file=view["locations"]["budget_file"],
                    downstream_seconds=120, remote=remote, url=url, endpoint=args.lfs_endpoint if lfs else None, lfs=lfs, steps=steps)
                name = f"bindings/{index}.json"
                bindings.append(name)
                files[name] = record(directory, name, encoded(binding))
            for name, raw in (("backups/config.before", current), ("backups/config.after", after), ("backups/config.original", original)):
                files[name] = record(directory, name, raw)
            manifest = dict(schema=OWNER_SCHEMA, version=1, phase="prepared", repository={key: str(repository[key]) for key in ("root", "gitdir", "common")},
                scope=scope, config=str(target), previous_value=previous_value, before_value=current_value, installed_value=str(base / "hooks"), before=digest(current), after=digest(after),
                build=build.hexdigest(), interpreter=view["interpreter"]["path"], git=str(git), git_identity=list(identity(git.lstat())),
                data=view["locations"]["data"], budget_file=view["locations"]["budget_file"], hooks=hooks, files=files, bindings=bindings, selection=selection, config_lock=config_lock, original_effective=original_effective, config_absent=owned["config_absent"] if owned else config_absent)
            atomic(directory, MANIFEST, encoded(manifest))
            owner(encoded(manifest), base, repository)
            if read(snapshot, target, missing=True, maximum=65536) not in (current, None if not current else current):
                fail("installation_configuration_drift", 3, "promotion")
            parent.validate()
            if controller is None:
                atomic(staging, MANIFEST, encoded(manifest))
                if control.exists():
                    fail("installation_unknown_directory", 3, "promotion")
                os.rename(temporary.name, control.name, src_dir_fd=parent.descriptor, dst_dir_fd=parent.descriptor)
                controller = Directory(control, snapshot.context, resources)
            else:
                generations = controller.child("installations")
                os.rename(temporary.name, token, src_dir_fd=parent.descriptor, dst_dir_fd=generations.descriptor)
                atomic(controller, MANIFEST, encoded(manifest))
            os.fsync(generations.descriptor)
            os.fsync(parent.descriptor)
            validate(snapshot, base, manifest)
            promote(after)
            manifest["phase"] = "active"
            manifest["config_lock"] = None
            directory = Directory(base, snapshot.context, resources)
            atomic(directory, MANIFEST, encoded(manifest))
            atomic(controller, MANIFEST, encoded(manifest))
            return installation_result(result, "updated" if owned else "installed", True, True)


def installation_result(result, outcome, activated, changed):
    result.update(outcome=outcome, reason=outcome, phase="complete", dry_run=False, activated=activated,
        changes_applied=changed, exit_code=0, recovery="Original hooks and unrelated settings are preserved. Private configuration backups remain in the repository installation directory.")
    return result, 0
