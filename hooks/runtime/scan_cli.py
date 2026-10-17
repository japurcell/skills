"""Provider-neutral explicit checkpoint CLI; detector imports stay lazy."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import stat
import time

VERSION = "1.0.0"
SCHEMA = "scan_secrets_check_v1"
POLICY = "pending_snapshots_v1"
MODULES = ("scan_types", "scan_reporting", "scan_allowlist", "scan_stream", "scan_git", "scan_engine", "scan_native_file", "scan_native_process", "scan_audit", "scan_budget", "scan_repository", "scan_gate", "scan_transaction", "scan_lfs", "scan_private", "scan_publication", "scan_dispatch", "scan_repo_install", "scan_repo_state", "scan_repo_dispatch")


class Failure(Exception):
    def __init__(self, reason, code=2, phase="initialization", recovery="Restore the scanner runtime and retry.", *, details=None):
        self.reason, self.code, self.phase, self.recovery = reason, code, phase, recovery
        self.details = details or {}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Failure("invalid_arguments", 3, "arguments", "Run scan-secrets help COMMAND for supported options.")

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        raise SystemExit(status)


def parser():
    common = Parser(add_help=False, allow_abbrev=False)
    for flag, text in (("--json", "print one versioned JSON result"), ("--no-input", "never prompt (check and status never read stdin)"),
                       ("--quiet", "suppress human success output"), ("--no-color", "disable terminal color")):
        common.add_argument(flag, action="store_true", default=argparse.SUPPRESS, help=text)
    root = Parser(prog="scan-secrets", description="Explicit, synchronous secret checks. No background scans.",
                  parents=[common], allow_abbrev=False)
    root.add_argument("--version", action="version", version=f"scan-secrets {VERSION}; result {SCHEMA}; status scan_secrets_status_v1; policy {POLICY}; repository installation scan_secrets_repo_install_v1; budget schema 1")
    commands = root.add_subparsers(dest="command")
    check = commands.add_parser("check", parents=[common], allow_abbrev=False,
        help="inspect pending worktree or staged index content", description="Inspect captured pending content without changing source, index, refs or Git configuration.",
        epilog="Examples: scan-secrets check --repo .; scan-secrets check --scope index --json. Publication uses gate pre-push with Git transaction stdin. Required audit data uses XDG_DATA_HOME/scan-secrets, macOS Application Support/scan-secrets, or Windows LOCALAPPDATA/scan-secrets. The last scan is saved for informational status; status never authorizes publication.")
    check.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
    check.add_argument("--scope", choices=("worktree", "index"), default="worktree",
                       help="worktree: pending changes, conflicts and untracked; index: staged versions in full")
    check.add_argument("--budget-file", help="explicit schema-1 JSON budget file; otherwise built-in finite defaults")
    gate = commands.add_parser("gate", parents=[common], allow_abbrev=False,
        help="inspect a captured Git action", description="Synchronous fail-closed Git feedback. No stdin is read for pre-commit.")
    gates = gate.add_subparsers(dest="action")
    pre_commit = gates.add_parser("pre-commit", parents=[common], allow_abbrev=False,
        help="inspect changed staged files in full", description="Inspect full stored versions of files changed between captured HEAD and Git's selected index. This feedback describes the captured staged state; later hooks may change it.")
    pre_commit.add_argument("--git", help=argparse.SUPPRESS)
    pre_commit.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
    pre_commit.add_argument("--budget-file", help="explicit schema-1 JSON budget file; uses checkpoint profile")
    pre_push = gates.add_parser("pre-push", parents=[common], allow_abbrev=False,
        help="inspect the actual outgoing Git transaction", description="Read Git pre-push tuples once through EOF. Inspect complete immutable outgoing history, messages and supported paths. Components and full encoded paths are limited to 4096 bytes; CR, LF, backslashes and gitlinks are unsupported and block publication. Canonical v1 LFS pointers require complete ordinary local payloads matching declared size and SHA256; inspection never downloads.")
    pre_push.add_argument("--git", help=argparse.SUPPRESS)
    pre_push.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
    pre_push.add_argument("--remote", required=True, help="Git-supplied destination name")
    pre_push.add_argument("--url", required=True, help="Git-supplied destination URL (never displayed)")
    pre_push.add_argument("--budget-file", help="explicit schema-1 JSON budget file; uses publication profile")
    pre_push.add_argument("--invocation", help=argparse.SUPPRESS)
    dispatch = commands.add_parser("dispatch", parents=[common], allow_abbrev=False,
        help="scan then run an explicitly bound publication workflow", description="Own one synchronous pre-push invocation. Inspect and audit before any downstream step. Replay exact Git stdin and arguments to preserved hooks. Basic HTTP LFS upload uses verified private bytes and a pinned Git LFS 3.8.0 binary. Inspection and downstream steps have separate finite deadlines. Downstream errors preserve their exit status; scan errors use 1/2/3/130. No saved status authorizes dispatch.")
    dispatch.add_argument("--git", help=argparse.SUPPRESS)
    dispatch.add_argument("action", choices=("pre-push",))
    dispatch.add_argument("--repo", default=".")
    dispatch.add_argument("--binding", required=True, help="owner-only schema-1 installation binding")
    dispatch.add_argument("destination", nargs=2, help="-- followed by original remote name and URL")
    hooks = commands.add_parser("hooks", parents=[common], allow_abbrev=False,
        help="install explicit repository Git gates", description="Install, preview or restore repository-owned Git gates. Installation never executes existing hooks or contacts remotes.")
    hook_actions = hooks.add_subparsers(dest="action")
    for action in ("install", "uninstall"):
        command = hook_actions.add_parser(action, parents=[common], allow_abbrev=False,
            help=f"{action} repository Git gates",
            epilog="Examples: scan-secrets hooks " + action + " --repo . --dry-run --json; scan-secrets hooks " + action + " --repo . --git /absolute/trusted/git. Exit 0 means successful installation/restoration, idempotent no-op, or read-only preview; 2 means unavailable infrastructure/lock contention; 3 means invalid or unsupported configuration; 130 means cancelled. Dry-run writes no configuration, locks, reports, backups or hooks. Normal installation holds installer and Git config locks for cooperating writers, prepares complete private generations, then activates configuration; simultaneous direct editor replacement is outside that guarantee. Backups and retired generations remain private. Explicitly rerun after cancellation or journaled interruption; ambiguous orphan locks require manual review and are never deleted by guesswork. Discovery limits: 10 seconds overall, 2 per Git command, 64 KiB per metadata file, 1 MiB captured output, 2048 settings and 128 worktrees. Installation limits: 20 seconds, 1 MiB per runtime file, 16 MiB captured/temporary bytes, 128 owned files per generation, 16 retained generations; pinned LFS tools are hashed within 64 MiB. Installation never runs original hooks, managers, credential helpers or network. Direct Git selection is required for Apple launchers. Shared multi-worktree scope, included local hook bindings, branch-dependent includes, URL rewrites and custom LFS managers are refused. Already enabled worktree configuration requires --scope worktree; no extension is enabled. Destination bindings use unambiguous configured push URLs or paired --remote NAME --url URL. Budget LOCATION is pinned; valid owner-only content edits apply on explicit retry without reinstall. An explicit install updates changed binding/runtime selections and captures original hook edits; identical state is a no-op.")
        command.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
        command.add_argument("--budget-file", help="explicit trusted schema-1 budget file location; otherwise built-in finite defaults")
        command.add_argument("--git", help="absolute trusted direct Git executable for discovery; Apple launchers require explicit selection")
        command.add_argument("--dry-run", action="store_true", help="discover and describe intended operations without writes")
        command.add_argument("--scope", choices=("repository", "worktree"), help="explicit configuration scope; worktree requires extensions.worktreeConfig already enabled")
        command.add_argument("--remote", help="explicit destination name, paired with --url")
        command.add_argument("--url", help="exact destination URL, paired with --remote; never displayed")
        command.add_argument("--lfs", help="absolute pinned Git LFS 3.8.0 tool for a recognized standard pre-push hook")
        command.add_argument("--lfs-endpoint", help="explicit basic HTTP LFS endpoint; HTTP is limited to 127.0.0.1")
    internal_hook = commands.add_parser("repository-hook", allow_abbrev=False, help="advanced: invoke an owned repository hook launcher")
    internal_hook.add_argument("--installation", required=True)
    internal_hook.add_argument("hook")
    internal_hook.add_argument("arguments", nargs=argparse.REMAINDER)
    status = commands.add_parser("status", parents=[common], allow_abbrev=False,
        help="display the last scan without inspecting content", description="Display historical scan metadata only. Never scans or authorizes publication.",
        epilog="Examples: scan-secrets status --repo .; scan-secrets status --repo . --json. Exit 0 means valid information, including not_scanned; unreadable or corrupt reports exit 2. Reports are bounded to 64 KiB, use metadata reads with a two-second deadline, and live outside the worktree and executable bundle under XDG_DATA_HOME/scan-secrets/status, macOS Application Support/scan-secrets/status, or Windows LOCALAPPDATA/scan-secrets/status. Status never waits for a scan or certifies current content.")
    status.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
    help_parser = commands.add_parser("help", allow_abbrev=False, help="show command help")
    help_parser.add_argument("topic", nargs="?", choices=("check", "status", "gate", "dispatch", "hooks"))
    return root, {"check": check, "status": status, "gate": gate, "dispatch": dispatch, "hooks": hooks}


def output(value, *, json_mode, quiet=False):
    if json_mode:
        data = json.dumps(value, ensure_ascii=True, separators=(",", ":")) + "\n"
    elif value.get("schema") == "scan_secrets_dispatch_v1":
        data = "" if quiet and value["exit_code"] == 0 else f"scan-secrets: publication {value['outcome']}; {value['reason']}; {value.get('completed_steps', 0)} downstream steps completed. {value['recovery']}\n"
    elif value.get("schema") == "scan_secrets_repo_install_v1" and value["outcome"] != "preview" and value.get("exit_code") == 0:
        data = "" if quiet else f"scan-secrets: repository gates {value['outcome']}; {value['recovery']}\n"
    elif value.get("schema") == "scan_secrets_repo_install_v1" and value["outcome"] == "preview":
        data = "" if quiet else (f"scan-secrets: read-only {value['action']} preview.\n"
            + f"  Repository: {value['snapshot']['repository']['root']}\n"
            + f"  Scope: {value['snapshot']['repository']['proposed_scope']}\n"
            + f"  Hook source: {value['snapshot']['hooks_path']['effective']}\n"
            + "".join("  Proposed: " + operation + "\n" for operation in value["proposed_operations"]) + value["recovery"] + "\n")
    elif value.get("schema") == "scan_secrets_status_v1":
        data = f"scan-secrets: last scan unavailable; saved time and scope unavailable; {value['reason']}. {value['recovery']}\n"
    elif value["outcome"] == "complete_clean":
        data = "" if quiet else f"scan-secrets: complete clean; {value['counts']['inspected_snapshots']} snapshots inspected.\n"
    elif value["outcome"] == "complete_findings":
        data = f"scan-secrets: complete findings; {value['counts']['processed_findings']} findings. {value['recovery']}\n"
        data += "".join(f"  {finding['path']}:{finding['line']} {finding['pattern']}\n" for finding in value["findings"][:3])
        if len(value["findings"]) > 3:
            data += "  Use --json for the bounded finding report.\n"
    else:
        data = f"scan-secrets: {value['outcome']}; {value['reason']}. {value['recovery']}\n"
    target = sys.stdout if json_mode or value["outcome"] in {"complete_clean", "complete_findings", "preview"} or value.get("schema") == "scan_secrets_repo_install_v1" and value.get("exit_code") == 0 else sys.stderr
    target.write(data)
    target.flush()
    if value.get("status_outcome") == "failed":
        sys.stderr.write(f"scan-secrets: last-scan display was not saved; {value['status_reason']}. Repair the platform data directory or status runtime, then rerun an explicit check.\n")
        sys.stderr.flush()


def data_root():
    if os.name == "nt":
        value = os.environ.get("LOCALAPPDATA")
        base = Path(value) if value else Path.home() / "AppData" / "Local"
    elif os.environ.get("XDG_DATA_HOME"):
        base = Path(os.environ["XDG_DATA_HOME"])
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    if not base.is_absolute():
        raise Failure("audit_location_invalid", phase="scan_log", recovery="Choose an absolute platform data directory and retry.")
    return base / "scan-secrets"


def safe_audit_location(path):
    # Resolve only after rejecting redirected user directories. macOS provides
    # these root-owned system aliases for otherwise ordinary platform paths.
    path = Path(os.path.abspath(path))
    current = Path(path.anchor)
    deadline = time.monotonic() + 2
    for component in path.parts[1:]:
        if time.monotonic() >= deadline:
            raise Failure("audit_location_invalid", phase="scan_log")
        current = current / component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            if not (sys.platform == "darwin" and str(current) in {"/var", "/tmp"} and info.st_uid == 0):
                raise Failure("audit_location_invalid", phase="scan_log")
    if sys.platform == "darwin":
        for alias in (Path("/var"), Path("/tmp")):
            if path.is_relative_to(alias):
                path = alias.resolve(strict=True) / path.relative_to(alias)
                break
    return path / "audit.jsonl"


def audit_inside_directory(path, directory):
    if path.is_relative_to(directory):
        return True
    root = directory.stat()
    deadline = time.monotonic() + 2
    for ancestor in (path, *path.parents):
        if time.monotonic() >= deadline:
            raise Failure("audit_location_invalid", phase="scan_log")
        try:
            info = ancestor.stat()
        except FileNotFoundError:
            continue
        if (info.st_dev, info.st_ino) == (root.st_dev, root.st_ino):
            return True
    return False


def diagnostic(failure, types):
    if failure is None:
        return None
    value = failure.diagnostic()
    unit = types.INCOMPLETE_CAUSES[failure.cause][2]
    if unit:
        value["unit"] = unit
    return value


def recovery_for(result):
    if result.audit_outcome == "failed":
        return "Choose an absolute platform data directory outside the scanned worktree and scanner bundle (XDG_DATA_HOME on Unix/macOS or LOCALAPPDATA on Windows). Repair its permissions, file types or storage, then rerun the explicit check."
    if result.failure:
        details = result.failure.detail()
        if result.reason in {"snapshot_count_limit", "total_bytes_limit", "capture_bytes_limit", "temporary_bytes_limit", "git_output_limit", "scan_timeout"}:
            details += " Adjust the reported limit in an explicit schema-1 budget file within its supported range, then rerun the check."
        return details
    return "Remove the reported credentials from the selected content and rerun the check." if result.counts["processed_findings"] else "No action required."


def runtime_modules(load, runtime, entry):
    build = hashlib.sha256()
    try:
        try:
            status_source = (runtime / "scan_status.py").read_bytes()
        except OSError:
            status_source = None
        sources = {name: (runtime / (name + ".py")).read_bytes() for name in MODULES}
        for name, raw in ((entry.name, entry.read_bytes()), ("scan_cli.py", load.sources["scan_cli"]),
                          ("scan_status.py", status_source if status_source is not None else b"status-runtime-unavailable"),
                          *((name + ".py", sources[name]) for name in MODULES)):
            build.update(name.encode() + b"\0" + raw)
        modules = {name: load(name, sources[name]) for name in MODULES}
    except Exception:
        raise Failure("runtime_unavailable") from None
    return modules, build.hexdigest(), status_source


def check(args, *, load, runtime, entry, status_capture):
    import contextlib
    # The invocation handles outlive graph/repository capture, required audit
    # and handoff emission. Reopening the root pathname would lose that anchor.
    with contextlib.ExitStack() as invocation_resources:
        if getattr(args, "invocation", None):
            import signal
            # Dispatcher cancellation terminates this controlled child. Convert
            # that termination into normal stack unwinding for private captures.
            def terminate(signum, frame):
                raise KeyboardInterrupt
            previous = signal.signal(signal.SIGTERM, terminate)
            invocation_resources.callback(signal.signal, signal.SIGTERM, previous)
        return _check(args, load=load, runtime=runtime, entry=entry, status_capture=status_capture,
                      invocation_resources=invocation_resources)


def _check(args, *, load, runtime, entry, status_capture, invocation_resources):
    started = time.monotonic()
    is_gate = args.command == "gate"
    publication = is_gate and args.action == "pre-push"
    modules, build, status_source = runtime_modules(load, runtime, entry)
    status_capture["source"] = status_source
    gate = modules["scan_gate"] if is_gate else None
    types = modules["scan_types"]
    engine = modules["scan_engine"]
    audit = modules["scan_audit"]
    try:
        configured, budget_identity = modules["scan_budget"].load_budget(args.budget_file, profile="publication" if publication else "checkpoint")
    except Exception:
        raise Failure("budget_invalid", 3, "configuration", "Supply a regular schema-1 JSON budget file with complete checkpoint and publication profiles and finite limits in the documented ranges.") from None
    limits = types.ScanLimits(**configured, max_capture_total_bytes=configured["max_capture_bytes"])
    context = types.ScanContext(limits, started)
    repository = modules["scan_repository"]
    result = None
    handoff = None
    records = []
    try:
        with repository.ProtectedRepository(context, args.repo, selected_index=os.environ.get("GIT_INDEX_FILE") if is_gate else None, capture_selected_index=is_gate and not publication, publication=publication, executable=getattr(args, "git", None)) as protected:
            status_capture["repository"] = {"root": protected.root, "gitdir": protected.gitdir, "common": protected.common}
            if publication:
                transaction = modules["scan_transaction"].capture_transaction(protected.object_format, args.remote, args.url, context)
                status_capture["gate"] = dict(repository_identity=gate.repository_identity(protected),
                    transaction_identity=transaction.identity, destination_identity=transaction.destination_identity)
                invocation = getattr(args, "invocation", None)
                if invocation:
                    handoff = modules["scan_dispatch"].scan_request(invocation, protected, transaction, build, budget_identity, resources=invocation_resources)
                result = modules["scan_publication"].scan(protected, transaction, build,
                    payload_directory=handoff[1] if handoff else None, retained=records if handoff else None)
                if handoff:
                    # The repository context closes its held handles on exit;
                    # handoff is emitted below only after required audit succeeds.
                    status_capture["handoff_request"] = handoff[2]
            else:
                if is_gate:
                    status_capture["gate"] = dict(repository_identity=gate.repository_identity(protected), index_identity=protected.index_identity)
                result = engine.scan(protected.root, engine.ScanPolicy(build, scope="staged" if args.scope == "index" else "diff",
                                 version=gate.POLICY if is_gate else POLICY, staged_gate=is_gate),
                                 limits, context=context)
    except repository.NotRepository:
        raise Failure("not_repository", 3, "repository", "Choose a Git worktree with --repo PATH.") from None
    except types.ScanFailure as failure:
        if result is not None:
            result.outcome, result.reason, result.failure = "incomplete", failure.cause, failure
            result.coverage_complete = False
        else:
            raise Failure(failure.cause, 2, failure.operation, failure.detail(),
                details={"build": build, "policy_version": modules["scan_publication"].POLICY if publication else gate.POLICY if is_gate else POLICY, "scope": args.scope,
                         "limits": configured, "budget_identity": budget_identity, "diagnostic": diagnostic(failure, types)}) from None
    except Exception:
        if result is not None:
            result.failure = types.ScanFailure("cleanup_failed", "repository", capture_step="cleanup")
            result.outcome, result.reason = "incomplete", "cleanup_failed"
            result.coverage_complete = False
        else:
            raise Failure("repository_unavailable", 2, "repository", "Check repository and temporary storage accessibility, then rerun the check.") from None
    if result.skipped:
        raise Failure("not_repository", 3, "repository", "Choose a Git worktree with --repo PATH.")
    gate_metadata = {}
    if is_gate:
        gate_metadata = dict(action=args.action, **status_capture["gate"],
            budget_profile="publication" if publication else "checkpoint",
            accounting_units=modules["scan_publication"].UNITS if publication else gate.UNITS,
            scope_description="complete_outgoing_transaction" if publication else "changed_staged_files")
    result.audit_outcome = "written"
    try:
        requested_data = data_root()
        audit_path = safe_audit_location(requested_data)
        if (audit_inside_directory(audit_path, result.root) or audit_inside_directory(audit_path, entry.parent.parent)):
            raise Failure("audit_location_invalid", phase="scan_log")
        audit.append_scan_log(audit.AuditPolicy(result.build, "standalone", args.action if is_gate else "check", max_objects=limits.max_objects),
            log_path=audit_path, status=result.security_outcome if result.coverage_complete else "incomplete",
            session_id="", timestamp="", mode="block", scope=args.scope,
            repo_root_path=result.root, env_files=result.env_files, findings=result.findings,
            omitted_findings=result.counts["omitted_findings"], scan_result={**result.summary(), **gate_metadata, "limits": configured, "budget_identity": budget_identity},
            diagnostic=result.failure.diagnostic() if result.failure else None,
            security_outcome=result.security_outcome, deadline=time.monotonic() + 2,
            profile=result.policy_version, route="git_gate" if is_gate else "pending_scan")
    except Exception:
        result.audit_outcome = "failed"
        result.outcome = "incomplete"
        result.reason = "audit_unavailable"
    value = {"schema": SCHEMA, "cli_version": VERSION, **result.summary(), "security_outcome": result.security_outcome, "scope": args.scope,
             "limits": configured, "budget_identity": budget_identity,
             "phase": result.failure.operation if result.failure else "scan_log" if result.audit_outcome == "failed" else "complete",
             "diagnostic": diagnostic(result.failure, types),
             "findings": [{**finding, "redactedMatch": "[REDACTED]"} for finding in result.findings],
             "recovery": recovery_for(result)}
    if is_gate:
        value.update(gate_metadata)
    code = (130 if result.failure and result.failure.cause == "cancelled" else
            2 if result.outcome == "incomplete" else 1 if result.counts["processed_findings"] else 0)
    if publication:
        value["lfs_handoff_identity"] = None
        if handoff and code == 0:
            try:
                directory = handoff[0]
                directory.validate()
                value["lfs_handoff_identity"] = modules["scan_dispatch"].write_handoff(directory, status_capture["handoff_request"], records)
                value["counts"]["capture_bytes"] = context.capture_bytes
                value["counts"]["temp_peak_bytes"] = context.temp_peak_bytes
            except Exception as error:
                failure = error if isinstance(error, types.ScanFailure) else types.ScanSecurityError("handoff_invalid", "repository")
                value.update(outcome="incomplete", coverage_complete=False, security_outcome="incomplete",
                    reason=failure.cause, phase=failure.operation, diagnostic=diagnostic(failure, types), recovery=failure.detail())
                value["counts"]["capture_bytes"] = context.capture_bytes
                value["counts"]["temp_peak_bytes"] = context.temp_peak_bytes
                code = 2
    save_display(value, args, load=load, entry=entry, capture=status_capture)
    if is_gate:
        value.update(schema=gate.SCHEMA, exit_code=code)
    return value, code


def save_display(value, args, *, load, entry, capture):
    try:
        if "scan_native_file" not in load.sources:
            load("scan_native_file")
        if "source" in capture:
            if capture["source"] is None:
                raise OSError
            status_module = load("scan_status", capture["source"])
        else:
            status_module = load("scan_status")
        value["status_outcome"], value["status_reason"] = status_module.save_status(
            args.repo, data_root, entry.parent.parent, value, version=VERSION, captured_repository=capture.get("repository"))
    except Exception:
        value["status_outcome"], value["status_reason"] = "failed", "status_runtime_unavailable"


def _main(argv, *, load, runtime, entry):
    json_mode = "--json" in argv
    args = None
    status_capture = {}
    invocation = next((item for item in argv if item in {"check", "status", "gate", "dispatch", "hooks", "help"}), None)
    gate_invocation = invocation == "gate"
    dispatch_invocation = invocation == "dispatch"
    status_invocation = invocation == "status"
    hooks_invocation = invocation == "hooks"
    try:
        root, topics = parser()
        args = root.parse_args(argv)
        if args.command is None or args.command == "help":
            (topics.get(getattr(args, "topic", None), root)).print_help()
            sys.stdout.flush()
            return 0
        if args.command == "hooks":
            if args.action is None:
                topics["hooks"].print_help()
                return 0
            for name in ("scan_types", "scan_git", "scan_native_file", "scan_repository", "scan_status", "scan_budget"):
                load(name)
            installer = load("scan_repo_install")
            if not args.dry_run:
                runtime_modules(load, runtime, entry)
            for name in ("scan_lfs", "scan_private", "scan_gate", "scan_repo_state", "scan_repo_dispatch"):
                load(name)
            value, code = installer.run(args, entry=entry, runtime=runtime)
            output(value, json_mode=getattr(args, "json", False), quiet=getattr(args, "quiet", False))
            return code
        if args.command == "repository-hook":
            load("scan_status")
            modules, build, _ = runtime_modules(load, runtime, entry)
            return modules["scan_repo_dispatch"].run(args, build=build, entry=entry)
        if args.command == "status":
            try:
                load("scan_native_file")
                status_module = load("scan_status")
            except Exception:
                raise Failure("status_runtime_unavailable", phase="status", recovery="Restore the status runtime and retry.") from None
            value, code = status_module.read_status(args.repo, data_root, entry.parent.parent)
            if getattr(args, "json", False):
                output(value, json_mode=True)
            elif code:
                sys.stderr.write(f"scan-secrets: last scan unavailable; saved time and scope unavailable; {value['reason']}. Repair status storage and rerun an explicit check.\n")
                sys.stderr.flush()
            elif not getattr(args, "quiet", False):
                last = value["last_scan"]
                description = (f"{last['completed_at']}; scope {last['scope']}; {last['outcome']}; reason {last['reason']}; "
                               f"{last['counts']['processed_findings']} findings" if last else
                               f"not_scanned; no saved scan time or scope; {value['reason']}")
                sys.stdout.write(f"scan-secrets: last scan: {description}. {value['message']}\n")
                sys.stdout.flush()
            return code
        if args.command == "dispatch":
            modules, build, _ = runtime_modules(load, runtime, entry)
            if args.destination[:1] == ["--"]:
                args.destination = args.destination[1:]
            value, code = modules["scan_dispatch"].run(args, build=build, entry=entry)
            output(value, json_mode=getattr(args, "json", False), quiet=getattr(args, "quiet", False))
            return code
        if args.command == "gate":
            if args.action is None:
                topics["gate"].print_help()
                return 0
            args.scope = "outgoing" if args.action == "pre-push" else "index"
        value, code = check(args, load=load, runtime=runtime, entry=entry, status_capture=status_capture)
        output(value, json_mode=getattr(args, "json", False), quiet=getattr(args, "quiet", False))
        return code
    except Failure as failure:
        value = {"schema": SCHEMA, "cli_version": VERSION, "outcome": "invalid" if failure.code == 3 else "incomplete",
                 "coverage_complete": False, "reason": failure.reason, "phase": failure.phase, "recovery": failure.recovery, **failure.details}
        if hooks_invocation:
            value.update(schema="scan_secrets_repo_install_v1", activated=False, changes_applied=False, authorizes_publication=False, exit_code=failure.code)
        if dispatch_invocation:
            value.update(schema="scan_secrets_dispatch_v1", exit_code=failure.code)
        if gate_invocation:
            value.update(schema="scan_secrets_gate_v1", action=getattr(args, "action", None), scope="outgoing" if getattr(args, "action", None) == "pre-push" else "index", exit_code=failure.code)
        if status_invocation:
            value = {"schema": "scan_secrets_status_v1", "cli_version": VERSION, "historical": True,
                     "authorizes_publication": False, "last_scan": None, "outcome": "invalid" if failure.code == 3 else "unavailable",
                     "reason": failure.reason, "phase": failure.phase, "recovery": failure.recovery}
        elif args is not None and args.command in {"check", "gate"} and failure.code == 2:
            value["scope"] = args.scope
            value["security_outcome"] = "incomplete"
            save_display(value, args, load=load, entry=entry, capture=status_capture)
        output(value, json_mode=json_mode)
        return failure.code
    except KeyboardInterrupt:
        value = {"schema": "scan_secrets_status_v1" if status_invocation else SCHEMA,
                 "outcome": "unavailable" if status_invocation else "incomplete", "coverage_complete": False,
                 "reason": "cancelled", "phase": "cancellation", "recovery": "Rerun the explicit command when ready."}
        if hooks_invocation:
            value.update(schema="scan_secrets_repo_install_v1", activated=False, changes_applied=False, authorizes_publication=False, exit_code=130)
        if dispatch_invocation:
            value.update(schema="scan_secrets_dispatch_v1", exit_code=130)
        if gate_invocation:
            value.update(schema="scan_secrets_gate_v1", action=getattr(args, "action", None), scope="outgoing" if getattr(args, "action", None) == "pre-push" else "index", exit_code=130)
        if status_invocation:
            value.update(historical=True, authorizes_publication=False, last_scan=None)
        elif args is not None and args.command in {"check", "gate"}:
            value.update(scope=args.scope, security_outcome="incomplete")
            save_display(value, args, load=load, entry=entry, capture=status_capture)
        output(value, json_mode=json_mode)
        return 130
    except BrokenPipeError:
        raise
    except Exception:
        value = {"schema": "scan_secrets_status_v1" if status_invocation else SCHEMA,
                 "outcome": "unavailable" if status_invocation else "incomplete", "coverage_complete": False,
                 "reason": "internal_error", "phase": "initialization", "recovery": "Restore the scanner runtime and retry."}
        if hooks_invocation:
            value.update(schema="scan_secrets_repo_install_v1", activated=False, changes_applied=False, authorizes_publication=False, exit_code=2)
        if dispatch_invocation:
            value.update(schema="scan_secrets_dispatch_v1", exit_code=2)
        if gate_invocation:
            value.update(schema="scan_secrets_gate_v1", action=getattr(args, "action", None), scope="outgoing" if getattr(args, "action", None) == "pre-push" else "index", exit_code=2)
        if status_invocation:
            value.update(historical=True, authorizes_publication=False, last_scan=None)
        output(value, json_mode=json_mode)
        return 2


def main(argv, *, load, runtime, entry):
    try:
        return _main(argv, load=load, runtime=runtime, entry=entry)
    except BrokenPipeError:
        descriptor = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(descriptor, sys.stdout.fileno())
        finally:
            os.close(descriptor)
        return 2
