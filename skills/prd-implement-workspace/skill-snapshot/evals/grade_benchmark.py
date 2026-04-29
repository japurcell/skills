#!/usr/bin/env python3
"""Grade prd-implement benchmark runs from saved response artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def normalize(text: str) -> str:
    text = re.sub(r"[`*_]+", "", text.lower())
    text = re.sub(r"[^\w\s#\[\]-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def has_any(text: str, *terms: str) -> bool:
    normalized = normalize(text)
    return any(normalize(term) in normalized for term in terms)


def has_all(text: str, *terms: str) -> bool:
    normalized = normalize(text)
    return all(normalize(term) in normalized for term in terms)


def excerpt(text: str, term: str, radius: int = 110) -> str:
    lowered = text.lower()
    idx = lowered.find(term.lower())
    if idx == -1:
        return ""
    start = max(0, idx - radius)
    end = min(len(text), idx + len(term) + radius)
    return text[start:end].replace("\n", " ").strip()


def evidence_for(text: str, *terms: str) -> str:
    for term in terms:
        snippet = excerpt(text, term)
        if snippet:
            return snippet
    return "No supporting excerpt found."


def issue_open_check(text: str, *issue_numbers: str) -> tuple[bool, str]:
    normalized = normalize(text)
    issue_phrases = [f"#{number}" for number in issue_numbers]
    open_terms = (
        "remain open",
        "remains open",
        "stays open",
        "stay open",
        "still open",
        "is still open",
        "not ready to close",
        "do not close",
        "cannot close",
        "keep open",
        "leave open",
        "controller checkpoint failed",
        "blocked by shared verification",
        "no review or closure should proceed",
    )
    if any(issue in normalized for issue in issue_phrases):
        passed = any(term in normalized for term in open_terms)
        return passed, evidence_for(text, *issue_phrases, *open_terms)
    passed = any(term in normalized for term in open_terms)
    return passed, evidence_for(text, *open_terms)


def parent_unchecked_check(text: str, *issue_numbers: str) -> tuple[bool, str]:
    normalized = normalize(text)
    issue_phrases = [f"#{number}" for number in issue_numbers]
    parent_line_terms = (
        "parent task-graph line",
        "parent prd task-graph line",
        "parent task graph line",
        "parent prd task graph line",
        "parent task-graph lines",
        "parent prd task-graph lines",
        "parent task graph lines",
        "parent prd task graph lines",
        "parent checkbox",
    )
    unchecked_terms = (
        "leave the parent task-graph line unchecked",
        "leave the parent prd task-graph line unchecked",
        "leave the parent task graph line unchecked",
        "leave the parent prd task graph line unchecked",
        "keep the parent task-graph line unchecked",
        "keep the parent prd task-graph line unchecked",
        "keep the parent task graph line unchecked",
        "keep the parent prd task graph line unchecked",
        "leave the parent checkbox unchecked",
        "keep the parent checkbox unchecked",
        "parent task-graph line remains [ ]",
        "parent prd task-graph line remains [ ]",
        "parent task graph line remains [ ]",
        "parent prd task graph line remains [ ]",
        "parent task-graph line still shows [ ]",
        "parent prd task-graph line still shows [ ]",
        "parent task graph line still shows [ ]",
        "parent prd task graph line still shows [ ]",
        "parent task-graph lines remain [ ]",
        "parent prd task-graph lines remain [ ]",
        "parent task graph lines remain [ ]",
        "parent prd task graph lines remain [ ]",
        "remain unchecked",
        "remains unchecked",
        "stay unchecked",
        "still unchecked",
        "do not check off",
        "do not mark either complete",
        "do not mark it complete",
        "unchecked until",
    )
    mentions_issues = all(issue in normalized for issue in issue_phrases) if issue_phrases else True
    passed = (
        mentions_issues
        and any(term in normalized for term in parent_line_terms)
        and any(term in normalized for term in unchecked_terms)
    )
    return passed, evidence_for(text, *issue_phrases, *parent_line_terms, *unchecked_terms)


def parent_checked_check(text: str, *issue_numbers: str) -> tuple[bool, str]:
    normalized = normalize(text)
    issue_phrases = [f"#{number}" for number in issue_numbers]
    parent_line_terms = (
        "parent task-graph line",
        "parent prd task-graph line",
        "parent task graph line",
        "parent prd task graph line",
        "parent checkbox",
    )
    checked_terms = (
        "check off the matching parent task-graph line",
        "check off the parent task-graph line",
        "check off the parent task graph line",
        "mark the parent task-graph line [x]",
        "mark the parent task graph line [x]",
        "update the parent task-graph line from [ ] to [x]",
        "update the parent task graph line from [ ] to [x]",
        "parent task-graph line was updated from [ ] to [x]",
        "parent task graph line was updated from [ ] to [x]",
        "synced the parent task-graph line",
        "synced the parent task graph line",
        "sync the parent task-graph line",
        "sync the parent task graph line",
        "checked the parent task-graph line",
        "checked the parent task graph line",
        "parent checkbox is now [x]",
        "parent line is now [x]",
        "parent line now shows [x]",
        "parent task-graph line is now [x]",
        "parent task-graph line now shows [x]",
        "parent task graph line is now [x]",
        "parent task graph line now shows [x]",
        "synchronize the parent checkbox",
        "sync the parent checkbox",
        "mark it [x]",
        "from [ ] to [x]",
    )
    mentions_issues = all(issue in normalized for issue in issue_phrases) if issue_phrases else True
    passed = (
        mentions_issues
        and any(term in normalized for term in parent_line_terms)
        and any(term in normalized for term in checked_terms)
    )
    return passed, evidence_for(text, *issue_phrases, *parent_line_terms, *checked_terms)


def parent_issue_open_check(text: str) -> tuple[bool, str]:
    parent_terms = (
        "parent prd issue",
        "parent issue",
    )
    open_terms = (
        "leave open",
        "remains open",
        "remain open",
        "stays open",
        "stay open",
        "do not close",
        "keeps open",
    )
    passed = has_any(text, *parent_terms) and has_any(text, *open_terms)
    return passed, evidence_for(text, *open_terms, *parent_terms)


def checkbox_only_update_check(text: str) -> tuple[bool, str]:
    only_checkbox = has_any(
        text,
        "only the checkbox should change",
        "replace only the leading checkbox",
        "only change the checkbox",
        "change only the checkbox",
        "only the checkbox changed",
    )
    preserve_rest = has_any(
        text,
        "preserve the rest of the line",
        "rest of the managed task-graph line stays the same",
        "rest of the managed task graph line stays the same",
        "rest of the managed line stayed the same",
        "rest of the managed line stays the same",
        "preserve the rest of the managed line",
        "leave the rest of the line unchanged",
        "do not rewrite the task graph",
        "do not rewrite the managed block",
    )
    passed = only_checkbox and preserve_rest
    return passed, evidence_for(
        text,
        "only the checkbox should change",
        "replace only the leading checkbox",
        "preserve the rest of the line",
        "leave the rest of the line unchanged",
        "do not rewrite the task graph",
    )


def comment_only_rejected_check(text: str) -> tuple[bool, str]:
    passed = (
        has_any(
            text,
            "comment-only completion",
            "comment only completion",
            "comment-only status",
            "comment only status",
            "comments do not count as completion",
            "a comment is not enough",
            "status-only comment is not completion",
            "status note does not count as completion",
            "ready to close note does not count",
            "progress evidence only",
        )
        or (
            has_any(text, "comment", "status note", "ready to close")
            and has_any(text, "not enough", "does not count", "not completion", "still incomplete", "cannot move on")
        )
    )
    return passed, evidence_for(
        text,
        "comment-only completion",
        "comments do not count as completion",
        "a comment is not enough",
        "status-only comment is not completion",
        "ready to close note does not count",
    )


def real_closeout_required_check(text: str, issue_number: str) -> tuple[bool, str]:
    issue_term = f"#{issue_number}"
    close_required = has_any(
        text,
        "close the child issue",
        "close child issue",
        f"close {issue_term}",
        f"child issue {issue_term} open",
        f"{issue_term} remains open until",
        f"{issue_term} remains open",
    )
    sync_required = has_any(
        text,
        "check the exact parent task-graph line",
        "check the matching parent task-graph line",
        "update the matching parent task-graph line",
        "sync the parent task-graph line",
        "sync the parent checkbox",
        "from [ ] to [x]",
    )
    github_state_required = has_any(
        text,
        "gh-cli",
        "real github state changes",
        "actual github state changes",
        "real github updates",
        "actual github updates",
    )
    passed = close_required and sync_required and github_state_required
    return passed, evidence_for(
        text,
        "gh-cli",
        "real github state changes",
        "actual github state changes",
        "close the child issue",
        f"close {issue_term}",
        "sync the parent task-graph line",
        "sync the parent checkbox",
        "from [ ] to [x]",
    )


def stop_progress_check(text: str) -> tuple[bool, str]:
    passed = (
        has_any(text, "stop before the next wave", "do not advance to the next wave", "do not proceed to the next wave")
        or (
            has_any(text, "stop", "halt", "blocked")
            and has_any(text, "next wave", "review", "new work", "further closure", "advance")
        )
        or (
            has_any(text, "next ready work:")
            and has_any(text, "- none", "none")
            and has_any(text, "must pass before", "no review or closure should proceed", "remains blocked", "do not close")
        )
        or (
            has_any(text, "blocked / waiting:")
            and has_any(text, "next ready work:", "- none", "none")
        )
    )
    return passed, evidence_for(
        text,
        "stop before the next wave",
        "do not advance to the next wave",
        "do not proceed to the next wave",
        "halt",
        "blocked",
    )


def landing_out_of_scope_check(text: str) -> tuple[bool, str]:
    landing_terms = (
        "landing work",
        "commit",
        "push",
        "open a pr",
        "pr creation",
        "pull request",
    )
    boundary_terms = (
        "out of scope",
        "separate workflow",
        "separate request",
        "separate follow-up",
        "not part of prd-implement",
        "stops here",
    )
    passed = has_any(text, *landing_terms) and has_any(text, *boundary_terms)
    return passed, evidence_for(text, *boundary_terms, *landing_terms)


def no_landing_now_check(text: str) -> tuple[bool, str]:
    passed = has_any(
        text,
        "no commit, push, or pr actions",
        "no commit, push, or pull request actions",
        "no commit, push, or pr action will be performed in this run",
        "no pr will be opened and no commit or push will be performed",
        "will not commit, push, or open a pr",
        "will not commit, push, or open a pull request",
        "do not commit, push, or open a pr",
        "do not commit, push, or open a pull request",
        "no pr creation",
    )
    return passed, evidence_for(
        text,
        "no commit, push, or pr actions",
        "no pr will be opened and no commit or push will be performed",
        "will not commit, push, or open a pr",
        "do not commit, push, or open a pr",
    )


def local_only_check(text: str) -> tuple[bool, str]:
    passed = has_any(
        text,
        "local changes only",
        "local-only",
        "remain uncommitted",
        "stays uncommitted",
        "leave the worktree uncommitted",
        "changes remain local",
        "uncommitted",
    )
    return passed, evidence_for(
        text,
        "local changes only",
        "local-only",
        "remain uncommitted",
        "changes remain local",
        "uncommitted",
    )


def separate_followup_commit_check(text: str) -> tuple[bool, str]:
    passed = (
        has_any(text, "commit-to-pr", "`commit-to-pr`", "`commit`", "commit skill", "separate commit or commit-to-pr request")
        and (
            has_any(text, "separate request", "separate follow-up", "after this skill finishes", "after this run", "later request")
            or (has_any(text, "separate") and has_any(text, "request"))
        )
    )
    return passed, evidence_for(
        text,
        "commit-to-pr",
        "`commit`",
        "separate request",
        "separate follow-up",
        "after this skill finishes",
    )


def unauthorized_landing_violation_check(text: str) -> tuple[bool, str]:
    passed = (
        has_any(text, "git commit", "already ran git commit", "committed")
        and has_any(text, "workflow violation", "unauthorized", "out-of-scope landing action", "out of scope", "must stop")
    )
    return passed, evidence_for(
        text,
        "git commit",
        "already ran git commit",
        "workflow violation",
        "unauthorized",
        "must stop",
    )


def eval_0(text: str) -> list[tuple[bool, str]]:
    return [
        (
            has_any(text, "expo-router verify", "expo-router: command not found", "expo-router cli", "missing expo-router"),
            evidence_for(text, "expo-router verify", "expo-router: command not found", "missing expo-router"),
        ),
        (
            has_any(text, "do not substitute", "cannot substitute", "not an acceptable substitute", "weaker proxy", "not good enough", "substitute", "cannot validate", "cannot prove")
            and has_any(text, "static analysis", "code inspection", "manual inspection", "tsc --noemit", "tsc"),
            evidence_for(text, "do not substitute", "cannot substitute", "substitute", "manual inspection", "tsc"),
        ),
        issue_open_check(text, "5101"),
        parent_unchecked_check(text, "5101"),
        stop_progress_check(text),
    ]


def eval_1(text: str) -> list[tuple[bool, str]]:
    before_review = (
        has_any(text, "checkpoint before review", "controller checkpoint", "before review")
        and has_any(text, "stop", "halt", "blocked", "do not proceed")
    )
    skipped_typegen = has_any(
        text,
        "pnpm exec next typegen",
        "next typegen",
    ) and has_any(text, "unavailable", "skipped", "could not run", "next is unavailable", "missing")
    substitute_rejected = (
        has_any(text, "eslint", "read the generated types file", "generated types file", "file inspection")
        and has_any(text, "insufficient", "not enough", "cannot substitute", "do not substitute", "weaker", "not an approved replacement", "not approved replacement", "not acceptable substitute", "not acceptable substitutes")
    )
    return [
        (before_review, evidence_for(text, "checkpoint before review", "controller checkpoint", "before review")),
        (skipped_typegen, evidence_for(text, "pnpm exec next typegen", "next typegen", "next is unavailable")),
        (substitute_rejected, evidence_for(text, "eslint", "generated types file", "cannot substitute", "insufficient")),
        issue_open_check(text, "5104"),
        parent_unchecked_check(text, "5104"),
    ]


def eval_2(text: str) -> list[tuple[bool, str]]:
    both_blocked = (
        (
            has_all(text, "#6101", "#6102")
            or has_any(text, "both issues", "both child issues", "both covered issues", "shared command group covers both")
        )
        and has_any(
            text,
            "do not close",
            "remain open",
            "stays open",
            "cannot close",
            "block closure",
            "blocks closure for both covered issues",
            "same shared verification blocker",
        )
    )
    missing_bundle = has_any(text, "bundle exec rspec", "bundle: command not found", "missing bundle", "bundle is unavailable")
    diff_rejected = (
        has_any(text, "diff looks correct", "looks satisfied", "diff inspection", "code inspection", "do not close #6101 independently", "do not close independently")
        and has_any(text, "not enough", "cannot substitute", "do not close", "insufficient", "not acceptable", "not a substitute", "must pass before either can close", "shared verification command covers both issues")
    )
    return [
        (both_blocked, evidence_for(text, "#6101", "#6102", "both issues", "shared command group covers both")),
        (missing_bundle, evidence_for(text, "bundle exec rspec", "bundle: command not found", "missing bundle")),
        (diff_rejected, evidence_for(text, "diff looks correct", "looks satisfied", "diff inspection", "insufficient")),
        parent_unchecked_check(text, "6101", "6102"),
        stop_progress_check(text),
    ]


def eval_3(text: str) -> list[tuple[bool, str]]:
    original_missing = has_any(
        text,
        "pnpm: command not found",
        "pnpm command not found",
        "pnpm unavailable",
        "pnpm is unavailable",
        "pnpm was unavailable",
        "when pnpm was unavailable",
        "could not run because `pnpm` is unavailable",
        "could not run because pnpm is unavailable",
    )
    fallback_used = has_any(text, "yarn rw test", "`yarn rw test", "fallback command")
    explicit_reason = (
        has_any(text, "explicitly allowed", "explicitly listed", "because the issue says", "because the child issue says", "documented fallback", "as specified in child issue", "issue explicitly allowed", "child issue explicitly allowed")
        and has_any(text, "fallback", "alternative", "instead", "documented")
    )
    close_allowed = has_any(text, "#7101 is ready to close", "#7101 can close", "close #7101", "issue can close", "ready for closure", "blocked / waiting: none", "blocked / waiting:\n\n1. none", "blocked / waiting: 1. none")
    return [
        (original_missing, evidence_for(text, "pnpm: command not found", "pnpm unavailable")),
        (fallback_used, evidence_for(text, "yarn rw test", "fallback command")),
        (explicit_reason, evidence_for(text, "explicitly allowed", "explicitly listed", "because the child issue says", "documented fallback", "as specified in child issue")),
        (close_allowed, evidence_for(text, "#7101", "ready to close", "can close", "ready for closure", "Blocked / waiting:")),
        parent_checked_check(text, "7101"),
        parent_issue_open_check(text),
    ]


def eval_4(text: str) -> list[tuple[bool, str]]:
    mismatch_identified = (
        has_any(
            text,
            "closed-child / unchecked-parent mismatch",
            "closed child / unchecked parent mismatch",
            "closed but its parent task-graph line is still unchecked",
            "closed but its parent task graph line is still unchecked",
            "closed child issue #8201",
        )
        and has_any(text, "parent task-graph line", "parent task graph line", "parent checkbox")
    )
    ready_after_sync = (
        has_any(text, "w2", "#8202", "next ready work")
        and has_any(text, "ready", "can proceed", "start w2", "before starting w2", "after the parent checkbox is synchronized")
    )
    return [
        (mismatch_identified, evidence_for(text, "closed-child / unchecked-parent mismatch", "closed but its parent task-graph line is still unchecked", "closed child issue #8201")),
        parent_checked_check(text, "8201"),
        checkbox_only_update_check(text),
        (ready_after_sync, evidence_for(text, "W2", "#8202", "next ready work", "before starting W2")),
        parent_issue_open_check(text),
    ]


def eval_5(text: str) -> list[tuple[bool, str]]:
    hitl_remaining = (
        has_any(text, "#9005", "hitl", "only hitl work remains")
        or parent_issue_open_check(text)[0]
    )
    return [
        landing_out_of_scope_check(text),
        no_landing_now_check(text),
        local_only_check(text),
        separate_followup_commit_check(text),
        (hitl_remaining, evidence_for(text, "#9005", "HITL", "only HITL work remains", "parent PRD issue remains open")),
    ]


def eval_6(text: str) -> list[tuple[bool, str]]:
    stop_before_review = (
        has_any(text, "review", "verification", "issue closure", "pr creation", "pull request")
        and has_any(text, "stop", "must stop", "do not proceed", "halt", "blocked")
    )
    no_permission_to_continue = (
        has_any(text, "will not push", "do not push", "will not open a pr", "do not open a pr", "do not treat the commit as permission", "not permission to continue")
        or no_landing_now_check(text)[0]
    )
    return [
        unauthorized_landing_violation_check(text),
        (stop_before_review, evidence_for(text, "review", "verification", "issue closure", "PR creation", "must stop")),
        issue_open_check(text, "9101"),
        parent_unchecked_check(text, "9101"),
        (no_permission_to_continue, evidence_for(text, "will not push", "will not open a PR", "do not treat the commit as permission", "not permission to continue")),
    ]


def eval_7(text: str) -> list[tuple[bool, str]]:
    return [
        comment_only_rejected_check(text),
        real_closeout_required_check(text, "9301"),
        issue_open_check(text, "9301"),
        parent_unchecked_check(text, "9301"),
        parent_issue_open_check(text),
        stop_progress_check(text),
    ]


CHECKS = {
    0: eval_0,
    1: eval_1,
    2: eval_2,
    3: eval_3,
    4: eval_4,
    5: eval_5,
    6: eval_6,
    7: eval_7,
}


def build_user_notes_summary(user_notes: str) -> dict:
    note = user_notes.strip()
    if not note:
        return {"uncertainties": [], "needs_review": [], "workarounds": []}
    return {"uncertainties": [note], "needs_review": [], "workarounds": []}


def timing_for_run(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if timing_path.exists():
        return json.loads(timing_path.read_text(encoding="utf-8"))
    return {"total_tokens": 0, "total_duration_seconds": 0.0}


def grade_run(eval_dir: Path, config_dir: Path) -> None:
    metadata = json.loads((eval_dir / "eval_metadata.json").read_text(encoding="utf-8"))
    eval_id = int(metadata["eval_id"])
    assertions = metadata["assertions"]

    for run_dir in sorted(path for path in config_dir.glob("run-*") if path.is_dir()):
        outputs_dir = run_dir / "outputs"
        response = read_text(outputs_dir / "response.md")
        transcript = read_text(run_dir / "transcript.md")
        user_notes = read_text(outputs_dir / "user_notes.md")
        combined = f"{response}\n\n{transcript}"

        checks = CHECKS[eval_id](combined)
        if len(checks) != len(assertions):
            raise ValueError(f"Eval {eval_id} has {len(assertions)} assertions but {len(checks)} checks")

        graded_expectations = [
            {"text": text, "passed": passed, "evidence": evidence}
            for text, (passed, evidence) in zip(assertions, checks)
        ]
        passed = sum(1 for item in graded_expectations if item["passed"])
        total = len(graded_expectations)
        grading = {
            "expectations": graded_expectations,
            "summary": {
                "passed": passed,
                "failed": total - passed,
                "total": total,
                "pass_rate": round(passed / total, 3) if total else 0.0,
            },
            "execution_metrics": {
                "tool_calls": {},
                "total_tool_calls": 0,
                "total_steps": len([line for line in transcript.splitlines() if line.strip()]),
                "errors_encountered": 0,
                "output_chars": len(response),
                "transcript_chars": len(transcript),
            },
            "timing": timing_for_run(run_dir),
            "claims": [],
            "user_notes_summary": build_user_notes_summary(user_notes),
        }
        (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py <iteration-dir>", file=sys.stderr)
        return 1

    iteration_dir = Path(sys.argv[1]).resolve()
    for eval_dir in sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-")):
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            if list(config_dir.glob("run-*")):
                grade_run(eval_dir, config_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
