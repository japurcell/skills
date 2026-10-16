"""Full selected-index collection and strict caller-owned gate admission.

A dispatcher must call validate_result on the captured process output with its
own expected identities. Scanner self-validation cannot authorize Git or prove
that an absent/crashed scanner returned a result. Status is never admission.
"""
from __future__ import annotations

import hashlib
import json
import math
import re

from .scan_git import capture_git, parse_index_record
from .scan_types import ScanSecurityError, ScanLimitExceeded

SCHEMA = "scan_secrets_gate_v1"
POLICY = "selected_index_v1"
UNITS = dict(max_objects="snapshots", max_candidate_bytes="bytes", max_seconds="seconds",
             max_capture_bytes="bytes", max_temp_bytes="bytes")
COUNT_KEYS = {"candidates", "inspected_snapshots", "candidate_bytes", "capture_bytes",
              "temp_peak_bytes", "processed_findings", "retained_findings", "omitted_findings"}


def repository_identity(repository):
    return hashlib.sha256(b"\0".join(str(path).encode("utf-8", "surrogateescape")
        for path in (repository.root, repository.gitdir, repository.common))).hexdigest()


def collect_index(context, root):
    """Every stage-zero path in the captured index, even unchanged HEAD paths."""
    candidates = set()
    with capture_git(context, ["ls-files", "--stage", "-z"], cwd=root,
                     deadline=context.deadline) as capture:
        for row in capture.records(b"\0"):
            source, path, _ = parse_index_record(row, allowed_stages={0, 1, 2, 3},
                                                operation="git_index", canonical_path=True)
            if source != "staged":
                raise ScanSecurityError("index_unresolved", "git_index")
            if (source, path) in candidates:
                raise ScanSecurityError("git_output_invalid", "git_index")
            candidates.add((source, path))
            if len(candidates) > context.limits.max_objects:
                raise ScanLimitExceeded("snapshot_count_limit", "git_index",
                                        measured=len(candidates), limit=context.limits.max_objects)
    return sorted(candidates, key=lambda item: item[1])


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate gate field")
        result[key] = value
    return result


def validate_result(raw, exit_code, *, action, build, repository_identity,
                    index_identity, budget_identity, scope_identity=None):
    """Reject unusable process output; return a validated result, never a pass bool.

    The caller may proceed only when this succeeds AND exit_code == 0. Expected
    identities come from that invocation's trusted caller, never saved status or
    fields copied from the untrusted response. Nonzero valid results still deny.
    """
    try:
        if type(raw) is not bytes or not raw or len(raw) > 131072 or type(exit_code) is not int:
            raise ValueError
        value = json.loads(raw, object_pairs_hook=_unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        keys = {"schema", "cli_version", "schema_version", "build", "policy_version", "scope", "scope_identity",
                "outcome", "coverage_complete", "counts", "elapsed_seconds", "reason", "audit_outcome",
                "status_outcome", "status_reason", "security_outcome", "limits", "budget_identity", "phase",
                "diagnostic", "findings", "recovery", "action", "repository_identity", "index_identity",
                "budget_profile", "accounting_units", "scope_description", "exit_code"}
        if type(value) is not dict or value.keys() != keys:
            raise ValueError
        if (value["schema"] != SCHEMA or value["schema_version"] != 1 or type(value["schema_version"]) is not int
                or value["action"] != action or action != "pre-commit" or value["scope"] != "index"
                or value["scope_description"] != "full_selected_index" or value["policy_version"] != POLICY
                or value["budget_profile"] != "checkpoint" or value["accounting_units"] != UNITS
                or value["exit_code"] != exit_code or type(value["exit_code"]) is not int
                or value["cli_version"] != "1.0.0"):
            raise ValueError
        for key, expected in (("build", build), ("repository_identity", repository_identity),
                              ("index_identity", index_identity), ("budget_identity", budget_identity)):
            if type(expected) is not str or re.fullmatch(r"[0-9a-f]{64}", expected) is None or value[key] != expected:
                raise ValueError
        if type(value["scope_identity"]) is not str or re.fullmatch(r"[0-9a-f]{64}", value["scope_identity"]) is None:
            raise ValueError
        if scope_identity is not None and value["scope_identity"] != scope_identity:
            raise ValueError
        if (type(value["coverage_complete"]) is not bool or type(value["elapsed_seconds"]) not in (int, float)
                or not math.isfinite(value["elapsed_seconds"]) or value["elapsed_seconds"] < 0):
            raise ValueError
        counts = value["counts"]
        if (type(counts) is not dict or counts.keys() != COUNT_KEYS
                or any(type(n) is not int or not 0 <= n < 2**63 for n in counts.values())
                or counts["retained_findings"] + counts["omitted_findings"] != counts["processed_findings"]
                or counts["inspected_snapshots"] > counts["candidates"]):
            raise ValueError
        if (type(value["findings"]) is not list or len(value["findings"]) != counts["retained_findings"]
                or len(value["findings"]) > 100):
            raise ValueError
        for finding in value["findings"]:
            if (type(finding) is not dict or finding.keys() != {"pattern", "severity", "path", "line", "redactedMatch"}
                    or finding["redactedMatch"] != "[REDACTED]" or type(finding["line"]) is not int or finding["line"] < 1
                    or any(type(finding[k]) is not str or len(finding[k]) > 2048 for k in ("pattern", "severity", "path"))):
                raise ValueError
        from .scan_budget import RANGES
        limits = value["limits"]
        if type(limits) is not dict or limits.keys() != UNITS.keys():
            raise ValueError
        for key, (low, high) in RANGES["checkpoint"].items():
            n = limits[key]
            if type(n) not in ((int, float) if key == "max_seconds" else (int,)) or not math.isfinite(n) or not low <= n <= high:
                raise ValueError
        security = "findings" if counts["processed_findings"] else "clean" if value["coverage_complete"] else "incomplete"
        if value["security_outcome"] != security or value["audit_outcome"] not in {"written", "failed", "not_attempted"}:
            raise ValueError
        if value["status_outcome"] not in {"written", "failed"} or type(value["status_reason"]) is not str:
            raise ValueError
        for key in ("reason", "phase", "recovery", "cli_version"):
            if type(value[key]) is not str or not value[key] or len(value[key]) > 2048:
                raise ValueError
        if value["outcome"] in {"complete_clean", "complete_findings"}:
            expected_code = 1 if counts["processed_findings"] else 0
            if (exit_code != expected_code or value["outcome"] != ("complete_findings" if expected_code else "complete_clean")
                    or not value["coverage_complete"] or value["audit_outcome"] != "written"
                    or counts["inspected_snapshots"] != counts["candidates"]
                    or value["reason"] != ("findings" if expected_code else "clean") or value["phase"] != "complete"
                    or value["diagnostic"] is not None):
                raise ValueError
        elif value["outcome"] == "incomplete":
            if exit_code not in {2, 130} or value["coverage_complete"] and value["audit_outcome"] != "failed":
                raise ValueError
        elif value["outcome"] != "invalid" or exit_code != 3 or value["coverage_complete"]:
            raise ValueError
        return value
    except (ValueError, TypeError, KeyError, OverflowError, UnicodeError):
        raise ValueError("invalid gate result") from None
