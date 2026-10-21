"""Validated repository launchers and original-path hook composition.

Unrelated hooks exec their original path with inherited streams and environment,
including duplex hook protocols. Gated hooks admit a fresh process result first.
"""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import sys

from .scan_budget import load_budget
from .scan_gate import repository_identity, validate_result
from .scan_git import capture_git
from .scan_repo_install import Snapshot, identity, configuration, environment
from .scan_repo_state import MANIFEST, OWNER_MAX_BYTES, context, owner, read, validate
from .scan_repository import ProtectedRepository
from .scan_types import ScanContext, ScanLimits, ScanFailure, ScanLimitExceeded


def report(value):
    # Gate reports already passed the shared strict validator. Display only
    # structured finding metadata, never captured child output or match bytes.
    sys.stderr.write("scan-secrets: " + value.get("reason", "installation_unavailable") + ". " + value.get("recovery", "Repair the repository gates using a healthy CLI.") + "\n")
    for finding in value.get("findings", [])[:3]:
        fields = [finding["path"], finding["pattern"]]
        safe = ["".join(c if 32 <= ord(c) < 127 else "?" for c in field)[:512] for field in fields]
        sys.stderr.write(f"  {safe[0]}:{finding['line']} {safe[1]}\n")
    sys.stderr.flush()


def run(args, *, build, entry):
    try:
        if os.name != "posix":
            raise ValueError
        from .scan_status import discover
        base = Path(args.installation)
        if not base.is_absolute():
            raise ValueError
        snapshot = Snapshot()
        snapshot.context = context()
        snapshot.reader.context = snapshot.context
        raw = read(snapshot, base / MANIFEST, maximum=OWNER_MAX_BYTES)
        document = __import__("json").loads(raw)
        repository = discover(document["repository"]["root"], snapshot.context.deadline)
        value = owner(raw, base, repository)
        if value["phase"] not in {"active", "prepared"} or value["build"] != build or value["interpreter"] != str(Path(sys.executable).resolve()):
            raise ValueError
        validate(snapshot, base, value)
        git = Path(value["git"])
        snapshot.trusted_location(git)
        if list(identity(git.lstat())) != value["git_identity"]:
            raise ValueError
        # Protect against delegated hooks recursively redispatching our wrapper.
        name = args.hook
        hook = next(item for item in value["hooks"] if item["name"] == name)
        marker = value["repository"]["gitdir"] + ":" + name
        if os.environ.get("SCAN_SECRETS_ACTIVE_HOOK") == marker:
            raise ValueError
        env = environment(snapshot)
        _, configured_hooks, _, _ = configuration(snapshot, git, env, repository["root"])
        direct = [item for item in configured_hooks if item["origin"] == value["config"] and item["value"] == value["installed_value"]]
        original_entries = [item for item in configured_hooks if item not in direct]
        effective_original = value["previous_value"] if value["previous_value"] is not None else original_entries[-1]["value"] if original_entries else str(repository["common"] / "hooks")
        if len(direct) != 1 or not configured_hooks or configured_hooks[-1] != direct[0] or effective_original != value["original_effective"]:
            report(dict(reason="hook_configuration_drift", recovery="Original hooksPath selection changed. Review the current configuration and explicitly reinstall to capture the intended original hook paths; no downstream hook ran."))
            return 3
        inherited = os.environ.copy()
        inherited["SCAN_SECRETS_ACTIVE_HOOK"] = marker
        if args.arguments[:1] == ["--"]:
            args.arguments = args.arguments[1:]
        if name == "pre-commit":
            code = pre_commit(snapshot, value, build, entry)
            if code:
                return code
        elif name == "pre-push":
            if len(args.arguments) != 2:
                raise ValueError
            from .scan_dispatch import run as dispatch
            from .scan_private import decoded
            chosen = None
            for binding_name in value["bindings"]:
                binding = decoded(read(snapshot, base / binding_name))
                if [binding["remote"], binding["url"]] == args.arguments:
                    chosen = base / binding_name
                    break
            if chosen is None:
                report(dict(reason="installation_destination_unbound", recovery="Install an explicit binding for this remote name and URL using --remote and --url. No remote was changed."))
                return 3
            import argparse
            result, code = dispatch(argparse.Namespace(repo=value["repository"]["root"], git=value["git"], binding=str(chosen), destination=args.arguments), build=build, entry=entry)
            if code:
                report(result)
            return code
        # Preserve cwd, arguments, streams, original $0 and sibling resources.
        # No subprocess capture/deadline is imposed on unrelated hook protocols.
        if hook["executable"]:
            os.execve(hook["path"], [hook["path"], *args.arguments], inherited)
        return 0
    except KeyboardInterrupt:
        report(dict(reason="cancelled", recovery="Retry the explicit Git action when ready."))
        return 130
    except ScanFailure as error:
        report(dict(reason=error.cause, recovery=error.detail()))
        return 2
    except Exception:
        report(dict(reason="installation_validation_failed", recovery="Run hooks uninstall from a healthy source or neutral CLI to restore original hooks, then reinstall. Preserve changed files and backups for review."))
        return 2


def pre_commit(snapshot, value, build, entry):
    import tempfile
    import stat
    from .scan_private import Directory
    with contextlib.ExitStack() as resources:
        budget = value["budget_file"]
        if budget is not None:
            path = Path(budget)
            snapshot.trusted_location(path)
            raw = snapshot.read(path, trusted=True)
            info = path.lstat()
            if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
                raise ValueError
            temporary = Path(tempfile.mkdtemp(prefix="scan-commit-budget-"))
            directory = Directory(temporary, snapshot.context, resources)
            resources.callback(directory.cleanup)
            budget = str(directory.write("budget.json", raw))
        configured, budget_identity = load_budget(budget)
        scan_context = ScanContext(ScanLimits(**configured, max_capture_total_bytes=configured["max_capture_bytes"]))
        with ProtectedRepository(scan_context, value["repository"]["root"], selected_index=os.environ.get("GIT_INDEX_FILE"),
                capture_selected_index=True, executable=value["git"]) as protected:
            scanner_environment = os.environ.copy()
            scanner_environment["XDG_DATA_HOME"] = str(Path(value["data"]).parent)
            arguments = ["-I", "-S", "-B", str(entry), "gate", "pre-commit", "--json", "--repo", str(protected.root), "--git", value["git"]]
            if budget is not None:
                arguments += ["--budget-file", budget]
            parent_scan_temp = scan_context.temp_bytes
            with capture_git(scan_context, arguments, cwd=protected.root, executable=sys.executable,
                    environment=scanner_environment, allow_nonzero=True, command_seconds=configured["max_seconds"], deadline=scan_context.deadline) as captured:
                raw = b"".join(captured.chunks())
                result = validate_result(raw, captured.exit_code, action="pre-commit", build=build,
                    repository_identity=repository_identity(protected), index_identity=protected.index_identity, budget_identity=budget_identity)
                if not captured.exit_code:
                    scan_context.charge_capture(result["counts"]["capture_bytes"])
                    composed_peak = parent_scan_temp + result["counts"]["temp_peak_bytes"] + len(raw)
                    if composed_peak > configured["max_temp_bytes"]:
                        raise ScanLimitExceeded("temporary_bytes_limit", "repository", measured=composed_peak, limit=configured["max_temp_bytes"])
                else:
                    report(result)
                return captured.exit_code


def passthrough(hook, interpreter):
    """Produce a stdlib-only original-path launcher independent of scan assets.

    Git invokes reference-transaction and post-index-change during repair too.
    Missing scanner modules must never make those operations scanner-dependent.
    """
    import shlex
    script = '''import hashlib, os, stat, sys
hook = HOOK_RECORD
try:
    path = hook["path"]
    parent = os.open(os.path.sep, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            for part in path.split(os.path.sep)[1:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                os.close(parent)
                parent = child
            descriptor = os.open(os.path.basename(path), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        except FileNotFoundError:
            if hook["state"] == "absent":
                raise SystemExit(0)
            raise
    finally:
        os.close(parent)
    with os.fdopen(descriptor, "rb") as handle:
        info = os.fstat(handle.fileno())
        current = [info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns]
        if not stat.S_ISREG(info.st_mode) or current != hook["identity"] or info.st_size > 65536:
            raise ValueError()
        raw = handle.read(65537)
        if hashlib.sha256(raw).hexdigest() != hook["sha256"]:
            raise ValueError()
    if not hook["executable"]:
        raise SystemExit(0)
    marker = path
    if os.environ.get("SCAN_SECRETS_PASSTHROUGH") == marker:
        raise ValueError()
    environment = os.environ.copy()
    environment["SCAN_SECRETS_PASSTHROUGH"] = marker
    os.execve(path, [path, *sys.argv[1:]], environment)
except Exception:
    os.write(2, b"scan-secrets: original_hook_drift. Review changed original hooks and rerun hooks install from a healthy CLI.\\n")
    raise SystemExit(2)
'''.replace("HOOK_RECORD", repr(hook))
    return ("#!/bin/sh\nexec " + shlex.join([interpreter, "-I", "-S", "-B", "-c", script]) + ' "$@"\n').encode()
