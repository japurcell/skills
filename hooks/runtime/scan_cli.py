"""Provider-neutral explicit checkpoint CLI; detector imports stay lazy."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

VERSION = "1.0.0"
SCHEMA = "scan_secrets_check_v1"
POLICY = "pending_snapshots_v1"
MODULES = ("scan_types", "scan_reporting", "scan_allowlist", "scan_stream", "scan_git", "scan_engine", "scan_audit", "scan_budget", "scan_repository")


class Failure(Exception):
    def __init__(self, reason, code=2, phase="initialization", recovery="Restore the scanner runtime and retry.", *, details=None):
        self.reason, self.code, self.phase, self.recovery = reason, code, phase, recovery
        self.details = details or {}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Failure("invalid_arguments", 3, "arguments", "Run scan-secrets help check for supported options.")

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        raise SystemExit(status)


def parser():
    common = Parser(add_help=False, allow_abbrev=False)
    for flag, text in (("--json", "print one versioned JSON result"), ("--no-input", "never prompt (checks never read stdin)"),
                       ("--quiet", "suppress human success output"), ("--no-color", "disable terminal color")):
        common.add_argument(flag, action="store_true", default=argparse.SUPPRESS, help=text)
    root = Parser(prog="scan-secrets", description="Explicit, synchronous secret checks. No background scans.",
                  parents=[common], allow_abbrev=False)
    root.add_argument("--version", action="version", version=f"scan-secrets {VERSION}; result {SCHEMA}; policy {POLICY}; budget schema 1")
    commands = root.add_subparsers(dest="command")
    check = commands.add_parser("check", parents=[common], allow_abbrev=False,
        help="inspect pending worktree or staged index content", description="Inspect captured pending content without changing source, index, refs or Git configuration.",
        epilog="Examples: scan-secrets check --repo .; scan-secrets check --scope index --json. Publication checks require a future gate command. Required audit data uses XDG_DATA_HOME/scan-secrets, macOS Application Support/scan-secrets, or Windows LOCALAPPDATA/scan-secrets. No status is saved by this source command.")
    check.add_argument("--repo", default=".", help="Git worktree path (default: current directory)")
    check.add_argument("--scope", choices=("worktree", "index"), default="worktree",
                       help="worktree: pending changes, conflicts and untracked; index: staged versions in full")
    check.add_argument("--budget-file", help="explicit schema-1 JSON budget file; otherwise built-in finite defaults")
    help_parser = commands.add_parser("help", allow_abbrev=False, help="show command help")
    help_parser.add_argument("topic", nargs="?", choices=("check",))
    return root, check


def output(value, *, json_mode, quiet=False):
    if json_mode:
        data = json.dumps(value, ensure_ascii=True, separators=(",", ":")) + "\n"
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


def check(args, *, load, runtime, entry):
    started = time.monotonic()
    build = hashlib.sha256()
    try:
        sources = {name: (runtime / (name + ".py")).read_bytes() for name in MODULES}
        for name, raw in ((entry.name, entry.read_bytes()), ("scan_cli.py", load.sources["scan_cli"]),
                          *((name + ".py", sources[name]) for name in MODULES)):
            build.update(name.encode() + b"\0" + raw)
        modules = {name: load(name, sources[name]) for name in MODULES}
    except Exception:
        raise Failure("runtime_unavailable") from None
    types = modules["scan_types"]
    engine = modules["scan_engine"]
    audit = modules["scan_audit"]
    try:
        configured, budget_identity = modules["scan_budget"].load_budget(args.budget_file)
    except Exception:
        raise Failure("budget_invalid", 3, "configuration", "Supply a regular schema-1 JSON budget file with complete checkpoint and publication profiles and finite limits in the documented ranges.") from None
    limits = types.ScanLimits(**configured, max_capture_total_bytes=configured["max_capture_bytes"])
    context = types.ScanContext(limits, started)
    repository = modules["scan_repository"]
    result = None
    try:
        with repository.ProtectedRepository(context, args.repo) as protected:
            result = engine.scan(protected.root, engine.ScanPolicy(build.hexdigest(), scope="staged" if args.scope == "index" else "diff"),
                                 limits, context=context)
    except repository.NotRepository:
        raise Failure("not_repository", 3, "repository", "Choose a Git worktree with --repo PATH.") from None
    except types.ScanFailure as failure:
        if result is not None:
            result.outcome, result.reason, result.failure = "incomplete", failure.cause, failure
        else:
            raise Failure(failure.cause, 2, failure.operation, failure.detail(),
                details={"build": build.hexdigest(), "policy_version": POLICY, "scope": args.scope,
                         "limits": configured, "budget_identity": budget_identity, "diagnostic": diagnostic(failure, types)}) from None
    except Exception:
        if result is not None:
            result.failure = types.ScanFailure("cleanup_failed", "repository", capture_step="cleanup")
            result.outcome, result.reason = "incomplete", "cleanup_failed"
        else:
            raise Failure("repository_unavailable", 2, "repository", "Check repository and temporary storage accessibility, then rerun the check.") from None
    if result.skipped:
        raise Failure("not_repository", 3, "repository", "Choose a Git worktree with --repo PATH.")
    result.audit_outcome = "written"
    try:
        requested_data = data_root()
        if requested_data.is_symlink():
            raise Failure("audit_location_invalid", phase="scan_log")
        audit_path = requested_data.parent.resolve() / requested_data.name / "audit.jsonl"
        if (audit_path.is_relative_to(result.root.resolve()) or audit_path.is_relative_to(entry.parent.parent.resolve())):
            raise Failure("audit_location_invalid", phase="scan_log")
        audit.append_scan_log(audit.AuditPolicy(result.build, "standalone", "check", max_objects=limits.max_objects),
            log_path=audit_path, status=result.security_outcome if result.coverage_complete else "incomplete",
            session_id="", timestamp="", mode="block", scope=args.scope,
            repo_root_path=result.root, env_files=result.env_files, findings=result.findings,
            omitted_findings=result.counts["omitted_findings"], scan_result=result.summary(),
            diagnostic=result.failure.diagnostic() if result.failure else None,
            security_outcome=result.security_outcome, deadline=time.monotonic() + 2)
    except Exception:
        result.audit_outcome = "failed"
        result.outcome = "incomplete"
        result.reason = "audit_unavailable"
    value = {"schema": SCHEMA, "cli_version": VERSION, **result.summary(), "scope": args.scope,
             "limits": configured, "budget_identity": budget_identity,
             "phase": result.failure.operation if result.failure else "scan_log" if result.audit_outcome == "failed" else "complete",
             "diagnostic": diagnostic(result.failure, types),
             "findings": [{**finding, "redactedMatch": "[REDACTED]"} for finding in result.findings],
             "recovery": recovery_for(result)}
    return value, 2 if result.outcome == "incomplete" else 1 if result.counts["processed_findings"] else 0


def _main(argv, *, load, runtime, entry):
    json_mode = "--json" in argv
    try:
        root, check_parser = parser()
        args = root.parse_args(argv)
        if args.command is None or args.command == "help":
            (check_parser if getattr(args, "topic", None) == "check" else root).print_help()
            sys.stdout.flush()
            return 0
        value, code = check(args, load=load, runtime=runtime, entry=entry)
        output(value, json_mode=getattr(args, "json", False), quiet=getattr(args, "quiet", False))
        return code
    except Failure as failure:
        value = {"schema": SCHEMA, "cli_version": VERSION, "outcome": "invalid" if failure.code == 3 else "incomplete",
                 "coverage_complete": False, "reason": failure.reason, "phase": failure.phase, "recovery": failure.recovery, **failure.details}
        output(value, json_mode=json_mode)
        return failure.code
    except KeyboardInterrupt:
        output({"schema": SCHEMA, "outcome": "incomplete", "coverage_complete": False,
                "reason": "cancelled", "phase": "cancellation", "recovery": "Rerun the explicit check when ready."}, json_mode=json_mode)
        return 130
    except BrokenPipeError:
        raise
    except Exception:
        output({"schema": SCHEMA, "outcome": "incomplete", "coverage_complete": False,
                "reason": "internal_error", "phase": "initialization", "recovery": "Restore the scanner runtime and retry."}, json_mode=json_mode)
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
