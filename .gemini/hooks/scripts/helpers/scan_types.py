#!/usr/bin/env python3
# Generated from hooks/families/scan_runtime.py by scripts/generate-hooks.py. Do not edit.
"""Explicit scanner limits, invocation state, and safe failures."""
from __future__ import annotations
from dataclasses import dataclass
import math
import time

TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".csv",
    ".env",
    ".go",
    ".h",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".svg",
    ".tf",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
MAX_FILES = 256
MAX_TOTAL_BYTES = 8388608
MAX_GIT_OUTPUT_BYTES = 8388608
MAX_SCAN_SECONDS = 8.0
GIT_COMPLETION_WAIT_SECONDS = 0.005
MAX_RETAINED_FINDINGS = 100
MAX_PROCESSED_FINDINGS = 1000
MAX_LOG_RECORD_BYTES = 65536
LOG_LOCK_TIMEOUT_SECONDS = 1.0
LOG_LOCK_POLL_SECONDS = 0.05
CANDIDATE_STAGED = "staged"
CANDIDATE_WORKTREE = "worktree"
CANDIDATE_UNTRACKED = "untracked"
CANDIDATE_UNMERGED_STAGES = ("unmerged-base", "unmerged-ours", "unmerged-theirs")
CANDIDATE_UNMERGED_WORKTREE = "unmerged-worktree"

INCOMPLETE_CAUSES = {
    "publication_validation_unavailable": ("publication validation runtime is unavailable", "Restore SQLite support in the recorded Python interpreter and retry publication.", ""),
    "cancelled": ("publication inspection was cancelled", "Rerun the explicit Git action when ready.", ""),
    "transaction_invalid": ("pre-push records are malformed", "Supply Git's complete four-field pre-push records with final newlines.", ""),
    "transaction_interactive": ("pre-push stdin is interactive", "Run this gate from Git pre-push or pipe a complete transaction.", ""),
    "transaction_unavailable": ("pre-push stdin is unavailable", "Supply a readable completed transaction stream.", ""),
    "transaction_timeout": ("pre-push input deadline reached", "Close the transaction input stream and rerun the Git action.", "seconds"),
    "transaction_bytes_limit": ("pre-push input byte limit exceeded", "Reduce the ref-update transaction and rerun the Git action.", "bytes"),
    "transaction_records_limit": ("pre-push record limit exceeded", "Reduce the ref-update transaction and rerun the Git action.", "records"),
    "object_count_limit": ("publication object limit exceeded", "Adjust max_objects in the explicit publication budget and rerun.", "objects"),
    "publication_path_unsupported": ("publication path shape is unsupported", "Use components and full encoded paths of at most 4096 bytes, without CR, LF, backslashes or gitlinks; rerun publication with supported paths.", "bytes"),
    "history_unsupported": ("source history or object storage is unsupported", "Use complete ordinary local object storage without shallow, graft or alternate substitutions.", ""),
    "object_missing": ("required publication object is missing", "Restore complete local publication objects and rerun; inspection never fetches.", ""),
    "lfs_unsupported": ("LFS publication requires verified payload handling", "Use a gate with verified LFS payload support before publishing these objects.", ""),
    "git_unavailable": ("Git is unavailable", "Check Git availability in the hook environment.", ""),
    "audit_unavailable": ("audit storage is unavailable", "Check hook audit storage.", ""),
    "input_invalid": ("hook input is invalid", "Check the provider hook envelope.", ""),
    "git_failed": ("Git command failed", "Check repository accessibility and Git health.", ""),
    "git_capture_failed": ("Git capture failed", "Check temporary storage and Git execution.", ""),
    "git_descendant_running": ("Git left a running descendant", "Check Git process completion and retry.", ""),
    "git_head_invalid": ("Git HEAD verification failed", "Check repository HEAD and integrity.", ""),
    "git_output_invalid": ("Git output is invalid", "Check Git compatibility and repository integrity.", ""),
    "repository_unavailable": ("repository inspection failed", "Check repository accessibility.", ""),
    "scan_timeout": ("scan time limit reached", "Check repository size and Git responsiveness, then retry.", "seconds"),
    "git_timeout": ("Git time limit reached", "Check Git responsiveness and retry.", "seconds"),
    "snapshot_count_limit": ("candidate snapshot limit exceeded", "Check pending snapshots and unintended generated artifacts.", "snapshots"),
    "total_bytes_limit": ("total candidate byte limit exceeded", "Check pending scan size and unintended generated artifacts.", "bytes"),
    "git_output_limit": ("Git capture byte limit exceeded", "Check pending scan size and Git output volume.", "bytes"),
    "git_input_limit": ("Git request byte limit exceeded", "Check pending scan size.", "bytes"),
    "candidate_unsafe": ("candidate cannot be read safely", "Check pending file types and repository boundaries.", ""),
    "candidate_read_failed": ("candidate read failed", "Check pending file accessibility.", ""),
    "log_unavailable": ("scan log is unavailable", "Check secure hook log storage.", ""),
    "log_unsafe": ("scan log cannot be accessed safely", "Check secure hook log storage and file types.", ""),
    "log_lock_timeout": ("scan log lock time limit reached", "Check concurrent hook log writers and retry.", "seconds"),
    "log_configuration_invalid": ("scan log rotation configuration is invalid", "Check hook log rotation settings.", ""),
    "log_record_limit": ("scan log record byte limit exceeded", "Check hook log rotation settings and scan volume.", "bytes"),
    "capture_bytes_limit": ("aggregate Git capture byte limit exceeded", "Increase the explicit capture budget within its supported range or reduce the scan scope.", "bytes"),
    "temporary_bytes_limit": ("private temporary byte limit exceeded", "Increase the explicit temporary budget within its supported range or repair temporary storage.", "bytes"),
    "conversion_unsupported": ("declared Git conversion requires unsupported inspection", "Review the declared conversion and use a supported full-content check.", ""),
    "candidate_changed": ("candidate changed during capture", "Retry against a stable candidate.", ""),
    "index_unresolved": ("index contains unresolved conflicts", "Resolve and stage the conflicts, then rerun the index check.", ""),
    "index_flags_unsupported": ("index flags prevent complete worktree inspection", "Use an ordinary full worktree index, then rerun the check.", ""),
    "cleanup_failed": ("private capture cleanup failed", "Repair temporary storage permissions and rerun the explicit check.", ""),
    "findings_limit": ("finding inspection limit reached", "Reduce pending findings and rerun the scan.", "findings"),
    "internal_error": ("internal scanner failure", "Check the hook installation and retry.", ""),
}
INCOMPLETE_OPERATIONS = {
    "initialization", "input", "repository", "git_repository", "git_head",
    "git_candidates", "git_index", "git_diff", "git_command",
    "candidate_read", "candidate_scan", "scan_log",
}


class ScanFailure(RuntimeError):
    """Carry only scanner-owned vocabulary and bounded numeric measurements."""

    def __init__(self, cause: str, operation: str | None = None, *,
                 capture_step: str | None = None, **numbers: int | float) -> None:
        self.cause = cause if cause in INCOMPLETE_CAUSES else "internal_error"
        phase = "initialization" if operation is None else operation
        self.operation = phase if phase in INCOMPLETE_OPERATIONS else "initialization"
        self.capture_step = capture_step if capture_step in {
            "temporary_file", "verify_capture", "request_write", "spawn",
            "wait", "descendants", "consume", "cleanup",
        } else None
        self.numbers = {
            key: value for key, value in numbers.items()
            if key in {"exit_status", "measured", "limit", "seconds", "os_errno", "attempts"}
            and (type(value) is int or key == "seconds" and type(value) is float and math.isfinite(value))
            and (-2147483648 if key == "exit_status" else 0) <= value <= 9223372036854775807
        }
        super().__init__(self.cause)

    def diagnostic(self) -> dict[str, object]:
        result: dict[str, object] = {"cause": self.cause, "operation": self.operation, **self.numbers}
        if self.capture_step is not None:
            result["capture_step"] = self.capture_step
        return result

    def detail(self) -> str:
        description, recovery, unit = INCOMPLETE_CAUSES[self.cause]
        measures = []
        if self.capture_step is not None:
            measures.append(f"capture step {self.capture_step}")
        if "os_errno" in self.numbers:
            measures.append(f"OS error {self.numbers['os_errno']}")
        if "attempts" in self.numbers:
            measures.append(f"launch attempts {self.numbers['attempts']}")
        if "exit_status" in self.numbers:
            measures.append(f"exit status {self.numbers['exit_status']}")
        if "measured" in self.numbers:
            measures.append(f"measured {self.numbers['measured']} {unit}".rstrip())
        if "limit" in self.numbers:
            measures.append(f"limit {self.numbers['limit']} {unit}".rstrip())
        if "seconds" in self.numbers:
            measures.append(f"limit {self.numbers['seconds']} seconds")
        suffix = f" ({', '.join(measures)})" if measures else ""
        return f"{self.cause}/{self.operation}: {description}{suffix}. {recovery}"


class GitCommandError(ScanFailure):
    pass


class ScanSecurityError(ScanFailure):
    pass


class ScanLimitExceeded(ScanSecurityError):
    pass


def enforce_deadline(deadline: float | None) -> None:
    if deadline is not None and time.monotonic() >= deadline:
        raise ScanLimitExceeded("scan_timeout", seconds=int(MAX_SCAN_SECONDS))




@dataclass(frozen=True)
class ScanLimits:
    max_objects: int = MAX_FILES
    max_candidate_bytes: int = MAX_TOTAL_BYTES
    max_seconds: float = MAX_SCAN_SECONDS
    # Per-command ceiling is preserved for legacy adapters. New callers also
    # bind the independently approved aggregate and temporary limits explicitly.
    max_capture_bytes: int = MAX_GIT_OUTPUT_BYTES
    max_capture_total_bytes: int | None = None
    max_temp_bytes: int | None = None

    def __post_init__(self):
        for value in (self.max_objects, self.max_candidate_bytes, self.max_capture_bytes):
            if type(value) is not int or value < 1:
                raise ValueError("invalid scan limit")
        for value in (self.max_capture_total_bytes, self.max_temp_bytes):
            if value is not None and (type(value) is not int or value < 1):
                raise ValueError("invalid scan limit")
        if type(self.max_seconds) not in (int, float) or not math.isfinite(self.max_seconds) or self.max_seconds <= 0:
            raise ValueError("invalid scan limit")


class ScanContext:
    # One scan's explicit budgets and phase; never module-global state.

    def __init__(self, limits: ScanLimits, started: float | None = None):
        self.limits = limits
        self.started = time.monotonic() if started is None else started
        self.deadline = self.started + limits.max_seconds
        self.phase = "initialization"
        self.capture_bytes = 0
        self.temp_bytes = 0
        self.temp_peak_bytes = 0
        self.repository_context = None

    def check_deadline(self, deadline: float | None = None):
        effective = self.deadline if deadline is None else min(deadline, self.deadline)
        if time.monotonic() >= effective:
            raise ScanLimitExceeded("scan_timeout", self.phase, seconds=self.limits.max_seconds)

    def charge_capture(self, size: int):
        self.capture_bytes += size
        limit = self.limits.max_capture_total_bytes
        if limit is not None and self.capture_bytes > limit:
            raise ScanLimitExceeded("capture_bytes_limit", self.phase,
                                    measured=self.capture_bytes, limit=limit)

    def charge_temp(self, size: int):
        self.temp_bytes += size
        self.temp_peak_bytes = max(self.temp_peak_bytes, self.temp_bytes)
        limit = self.limits.max_temp_bytes
        if limit is not None and self.temp_bytes > limit:
            raise ScanLimitExceeded("temporary_bytes_limit", self.phase,
                                    measured=self.temp_bytes, limit=limit)

    def release_temp(self, size: int):
        self.temp_bytes -= size
