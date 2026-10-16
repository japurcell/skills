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
MODULES = ("scan_types", "scan_reporting", "scan_allowlist", "scan_stream", "scan_git", "scan_engine", "scan_native_file", "scan_audit", "scan_budget", "scan_repository", "scan_gate", "scan_transaction", "scan_publication")


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
    root.add_argument("--version", action="version", version=f"scan-secrets {VERSION}; result {SCHEMA}; status scan_secrets_status_v1; policy {POLICY}; budget schema 1")
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
    pre_commit.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
    pre_commit.add_argument("--budget-file", help="explicit schema-1 JSON budget file; uses checkpoint profile")
    pre_push = gates.add_parser("pre-push", parents=[common], allow_abbrev=False,
        help="inspect the actual outgoing Git transaction", description="Read Git pre-push tuples once through EOF. Inspect complete immutable outgoing history, messages and supported paths. Components and full encoded paths are limited to 4096 bytes; CR, LF, backslashes and gitlinks are unsupported and block publication. Recognized LFS publication requires later verified payload support.")
    pre_push.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
    pre_push.add_argument("--remote", required=True, help="Git-supplied destination name")
    pre_push.add_argument("--url", required=True, help="Git-supplied destination URL (never displayed)")
    pre_push.add_argument("--budget-file", help="explicit schema-1 JSON budget file; uses publication profile")
    status = commands.add_parser("status", parents=[common], allow_abbrev=False,
        help="display the last scan without inspecting content", description="Display historical scan metadata only. Never scans or authorizes publication.",
        epilog="Examples: scan-secrets status --repo .; scan-secrets status --repo . --json. Exit 0 means valid information, including not_scanned; unreadable or corrupt reports exit 2. Reports are bounded to 64 KiB, use metadata reads with a two-second deadline, and live outside the worktree and executable bundle under XDG_DATA_HOME/scan-secrets/status, macOS Application Support/scan-secrets/status, or Windows LOCALAPPDATA/scan-secrets/status. Status never waits for a scan or certifies current content.")
    status.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
    help_parser = commands.add_parser("help", allow_abbrev=False, help="show command help")
    help_parser.add_argument("topic", nargs="?", choices=("check", "status", "gate"))
    return root, {"check": check, "status": status, "gate": gate}


def output(value, *, json_mode, quiet=False):
    if json_mode:
        data = json.dumps(value, ensure_ascii=True, separators=(",", ":")) + "\n"
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
    target = sys.stdout if json_mode or value["outcome"] in {"complete_clean", "complete_findings"} else sys.stderr
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


def check(args, *, load, runtime, entry, status_capture):
    started = time.monotonic()
    is_gate = args.command == "gate"
    publication = is_gate and args.action == "pre-push"
    build = hashlib.sha256()
    try:
        try:
            status_source = (runtime / "scan_status.py").read_bytes()
        except OSError:
            status_source = None
        status_capture["source"] = status_source
        sources = {name: (runtime / (name + ".py")).read_bytes() for name in MODULES}
        for name, raw in ((entry.name, entry.read_bytes()), ("scan_cli.py", load.sources["scan_cli"]),
                          ("scan_status.py", status_source if status_source is not None else b"status-runtime-unavailable"),
                          *((name + ".py", sources[name]) for name in MODULES)):
            build.update(name.encode() + b"\0" + raw)
        modules = {name: load(name, sources[name]) for name in MODULES}
    except Exception:
        raise Failure("runtime_unavailable") from None
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
    try:
        with repository.ProtectedRepository(context, args.repo, selected_index=os.environ.get("GIT_INDEX_FILE") if is_gate else None, capture_selected_index=is_gate and not publication, publication=publication) as protected:
            status_capture["repository"] = {"root": protected.root, "gitdir": protected.gitdir, "common": protected.common}
            if publication:
                transaction = modules["scan_transaction"].capture_transaction(protected.object_format, args.remote, args.url, context)
                status_capture["gate"] = dict(repository_identity=gate.repository_identity(protected),
                    transaction_identity=transaction.identity, destination_identity=transaction.destination_identity)
                result = modules["scan_publication"].scan(protected, transaction, build.hexdigest())
            else:
                if is_gate:
                    status_capture["gate"] = dict(repository_identity=gate.repository_identity(protected), index_identity=protected.index_identity)
                result = engine.scan(protected.root, engine.ScanPolicy(build.hexdigest(), scope="staged" if args.scope == "index" else "diff",
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
                details={"build": build.hexdigest(), "policy_version": modules["scan_publication"].POLICY if publication else gate.POLICY if is_gate else POLICY, "scope": args.scope,
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
    save_display(value, args, load=load, entry=entry, capture=status_capture)
    code = (130 if result.failure and result.failure.cause == "cancelled" else
            2 if result.outcome == "incomplete" else 1 if result.counts["processed_findings"] else 0)
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
    invocation = next((item for item in argv if item in {"check", "status", "gate", "help"}), None)
    gate_invocation = invocation == "gate"
    status_invocation = invocation == "status"
    try:
        root, topics = parser()
        args = root.parse_args(argv)
        if args.command is None or args.command == "help":
            (topics.get(getattr(args, "topic", None), root)).print_help()
            sys.stdout.flush()
            return 0
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
