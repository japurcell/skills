#!/usr/bin/env python3
# Generated from hooks/families/scan_runtime.py by scripts/generate-hooks.py. Do not edit.
"""One result-producing scanner, independent of provider transport and renderers."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import time

from .scan_types import (
    ScanContext, ScanFailure, ScanLimits, ScanLimitExceeded, MAX_RETAINED_FINDINGS,
    CANDIDATE_UNTRACKED, CANDIDATE_UNMERGED_STAGES, CANDIDATE_UNMERGED_WORKTREE,
)
from .scan_git import (
    ScanBudget, capture_git, collect_files, has_head, is_inside_git_repo,
    repo_root, snapshot_source, snapshot_diff_inputs,
)
from .scan_stream import (
    StreamReport, StreamDiffError, diff_added_line_events, full_line_events, scan_line_events,
)
from .scan_allowlist import allowlist_contains
from .scan_reporting import report_label


@dataclass(frozen=True)
class ScanPolicy:
    """Captured policy inputs. Adapters translate legacy environment explicitly."""

    build: str
    scope: str = "diff"
    version: str = "pending_snapshots_v1"
    allowlist: tuple[dict[str, str], ...] = ()
    staged_gate: bool = False

    def __post_init__(self):
        if self.scope not in {"diff", "staged"}:
            raise ValueError("invalid scan scope")


@dataclass
class ScanResult:
    schema_version: int
    build: str
    policy_version: str
    scope: str
    scope_identity: str
    outcome: str
    coverage_complete: bool
    findings: list[dict[str, object]]
    counts: dict[str, int]
    elapsed_seconds: float
    reason: str
    audit_outcome: str = "not_attempted"
    status_outcome: str = "not_attempted"
    failure: ScanFailure | None = field(default=None, repr=False)
    root: Path | None = field(default=None, repr=False)
    env_files: list[str] = field(default_factory=list, repr=False)
    skipped: bool = False

    @property
    def security_outcome(self) -> str:
        if self.counts["processed_findings"]:
            return "findings"
        return "clean" if self.coverage_complete else "incomplete"

    def summary(self) -> dict[str, object]:
        """Allowlisted bounded metadata for audit/status adapters."""
        return {key: getattr(self, key) for key in (
            "schema_version", "build", "policy_version", "scope", "scope_identity",
            "outcome", "coverage_complete", "counts", "elapsed_seconds", "reason",
            "audit_outcome", "status_outcome",
        )}


class RetainedFindings(list):
    """Only bounded display-safe fields enter retained state."""

    def append(self, finding):
        pattern, severity, path, line, redacted = finding
        if len(self) < MAX_RETAINED_FINDINGS:
            super().append((pattern, severity, report_label(path), line, redacted))


def build_findings_json(findings):
    return [dict(pattern=pattern, severity=severity, path=report_label(path),
                 line=line, redactedMatch=redacted)
            for pattern, severity, path, line, redacted in findings]


def is_env_path(path: str) -> bool:
    import re
    return bool(re.search(r"(^|/)\.env($|[.])", path.lower()))


def is_credential_path(path: str) -> bool:
    import re
    lowered = path.lower()
    base_name = lowered.rsplit("/", 1)[-1]
    if base_name in {"credentials", ".git-credentials"} or base_name.startswith("credentials."):
        return True
    return any(re.search(pattern, lowered) for pattern in (
        r"(^|/)\.ssh(/|$)", r"(^|/)\.aws(/|$)", r"(^|/)\.gnupg(/|$)",
        r"(^|/)\.?credentials(/|$)", r"(^|/)\.?secrets(/|$)",
    ))


def redact_match(match: str) -> str:
    return "[REDACTED]" if len(match) <= 8 else f"{match[:4]}...{match[-4:]}"


def scan_diff_added_lines(context, root, path, source, report, is_allowlisted, *, root_has_head, snapshot):
    from .scan_types import GitCommandError
    with snapshot_diff_inputs(context, root, path, source, snapshot) as (before, after):
        with capture_git(context, [
            "diff", "--no-index", "--text", "--diff-algorithm=" + snapshot.diff_algorithm,
            "--indent-heuristic" if snapshot.indent_heuristic else "--no-indent-heuristic", "--no-ext-diff", "--no-color", "--no-textconv",
            "--unified=0", "--src-prefix=a/", "--dst-prefix=b/", "--output-indicator-new=+",
            "--output-indicator-old=-", "--output-indicator-context= ", "--", str(before), str(after),
        ], cwd=root, deadline=context.deadline, allow_nonzero=True, literal_diff_inputs=True,
           auto_crlf=snapshot.conversion == "auto" and not snapshot.baseline_has_crlf,
           private_git_dir=snapshot.private_git_dir) as capture:
            try:
                scan_line_events(path, diff_added_line_events(capture.chunks(), context.check_deadline),
                                 report, is_allowlisted, redact_match, context.check_deadline)
            except StreamDiffError as exc:
                raise GitCommandError("git_output_invalid", "git_diff") from exc


def scan(work_dir: Path, policy: ScanPolicy, limits: ScanLimits, *, started: float | None = None,
         context: ScanContext | None = None) -> ScanResult:
    """Inspect protected pending snapshots and retain partial findings on failure.

    Returned snapshots are scoped to the captured reads. Worktree collection is
    not globally atomic. A caller owns audit and presentation after inspection.
    """
    context = ScanContext(limits, started) if context is None else context
    if context.limits != limits:
        raise ValueError("scan context limits mismatch")
    findings = RetainedFindings()
    report = StreamReport(findings)
    budget = ScanBudget(context)
    env_files = []
    candidates = []
    checked = 0
    failure = None
    root = work_dir
    identity = hashlib.sha256()
    skipped = False
    try:
        context.phase = "repository"
        if not is_inside_git_repo(context, work_dir, deadline=context.deadline):
            skipped = True
        else:
            root = repo_root(context, work_dir, deadline=context.deadline)
            root_has_head = has_head(context, root, deadline=context.deadline)
            candidates = collect_files(context, root, policy.scope, root_has_head, deadline=context.deadline)
            context.phase = "candidate_scan"
            is_allowlisted = lambda key: allowlist_contains("scan_secrets", key, policy.allowlist)
            with snapshot_source(root, candidates, budget,
                                 diff_baselines=policy.scope == "diff" and root_has_head, verify_objects=policy.staged_gate) as snapshots:
                for source, path in candidates:
                    context.phase = "candidate_read"
                    with snapshots.acquire((source, path)) as snapshot:
                        if snapshot is None:
                            continue
                        context.phase = "candidate_scan"
                        context.check_deadline()
                        checked += 1
                        identity.update(source.encode() + b"\0" + path.encode("utf-8", "surrogateescape") + b"\0")
                        # Classification already traversed every byte of this same
                        # protected capture; its digest identifies the decision input.
                        identity.update(snapshot.digest)
                        if is_env_path(path) and path not in env_files:
                            env_files.append(path)
                        if is_credential_path(path):
                            key = f"{path}:1:credential_path:[SENSITIVE PATH]"
                            if not is_allowlisted(key):
                                report.record_findings(1, (("credential_path", "critical", path, 1, "[SENSITIVE PATH]"),))
                        if not report.stopped:
                            if (snapshot.classification == "binary" or policy.scope == "staged"
                                  or not root_has_head or source == CANDIDATE_UNTRACKED
                                  or source in CANDIDATE_UNMERGED_STAGES or source == CANDIDATE_UNMERGED_WORKTREE):
                                scan_line_events(path, full_line_events(snapshot.chunks(), snapshot.classification,
                                                 context.check_deadline), report, is_allowlisted,
                                                 redact_match, context.check_deadline)
                            else:
                                scan_diff_added_lines(context, root, path, source, report,
                                                      is_allowlisted, root_has_head=root_has_head, snapshot=snapshot)
                        identity.update(b"conversion\0" + snapshot.conversion.encode("ascii") + b"\0")
                        identity.update(snapshot.diff_algorithm.encode("ascii") + bytes([snapshot.indent_heuristic]))
                        identity.update(b"baseline\0" + (snapshot.baseline_oid or b"empty") + b"\0")
                        context.phase = "candidate_scan"
                        if report.stopped:
                            raise ScanLimitExceeded("findings_limit", "candidate_scan", measured=report.processed, limit=1000)
            context.check_deadline()
    except Exception as exc:
        failure = exc if isinstance(exc, ScanFailure) else ScanFailure("internal_error", context.phase)
    complete = failure is None and not skipped
    outcome = "incomplete" if not complete else "complete_findings" if report.processed else "complete_clean"
    return ScanResult(1, policy.build, policy.version, policy.scope, identity.hexdigest(), outcome, complete,
                      build_findings_json(findings),
                      {"candidates": len(candidates), "inspected_snapshots": checked,
                       "candidate_bytes": budget.used_bytes, "capture_bytes": context.capture_bytes,
                       "temp_peak_bytes": context.temp_peak_bytes, "processed_findings": report.processed,
                       "retained_findings": len(findings), "omitted_findings": max(0, report.processed - len(findings))},
                      round(max(0.0, time.monotonic() - context.started), 6),
                      failure.cause if failure else "not_repository" if skipped else "findings" if report.processed else "clean",
                      failure=failure, root=root, env_files=env_files, skipped=skipped)
