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
    return re.sub(r"\s+", " ", text.lower()).strip()


def has_any(text: str, *terms: str) -> bool:
    normalized = normalize(text)
    return any(term.lower() in normalized for term in terms)


def has_all(text: str, *terms: str) -> bool:
    normalized = normalize(text)
    return all(term.lower() in normalized for term in terms)


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
        "stays open",
        "stay open",
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
    )
    return passed, evidence_for(
        text,
        "stop before the next wave",
        "do not advance to the next wave",
        "do not proceed to the next wave",
        "halt",
        "blocked",
    )


def eval_0(text: str) -> list[tuple[bool, str]]:
    return [
        (
            has_any(text, "expo-router verify", "expo-router: command not found", "expo-router cli", "missing expo-router"),
            evidence_for(text, "expo-router verify", "expo-router: command not found", "missing expo-router"),
        ),
        (
            has_any(text, "do not substitute", "cannot substitute", "not an acceptable substitute", "weaker proxy", "not good enough", "substitute")
            and has_any(text, "static analysis", "code inspection", "manual inspection", "tsc --noemit", "tsc"),
            evidence_for(text, "do not substitute", "cannot substitute", "substitute", "manual inspection", "tsc"),
        ),
        issue_open_check(text, "5101"),
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
        and has_any(text, "insufficient", "not enough", "cannot substitute", "do not substitute", "weaker", "not an approved replacement", "not approved replacement")
    )
    return [
        (before_review, evidence_for(text, "checkpoint before review", "controller checkpoint", "before review")),
        (skipped_typegen, evidence_for(text, "pnpm exec next typegen", "next typegen", "next is unavailable")),
        (substitute_rejected, evidence_for(text, "eslint", "generated types file", "cannot substitute", "insufficient")),
        issue_open_check(text, "5104"),
    ]


def eval_2(text: str) -> list[tuple[bool, str]]:
    both_blocked = (
        (has_all(text, "#6101", "#6102") or has_any(text, "both issues", "both child issues", "shared command group covers both"))
        and has_any(text, "do not close", "remain open", "stays open", "cannot close", "block closure")
    )
    missing_bundle = has_any(text, "bundle exec rspec", "bundle: command not found", "missing bundle", "bundle is unavailable")
    diff_rejected = (
        has_any(text, "diff looks correct", "looks satisfied", "diff inspection", "code inspection", "do not close #6101 independently", "do not close independently")
        and has_any(text, "not enough", "cannot substitute", "do not close", "insufficient", "not acceptable", "must pass before either can close", "shared verification command covers both issues")
    )
    return [
        (both_blocked, evidence_for(text, "#6101", "#6102", "both issues", "shared command group covers both")),
        (missing_bundle, evidence_for(text, "bundle exec rspec", "bundle: command not found", "missing bundle")),
        (diff_rejected, evidence_for(text, "diff looks correct", "looks satisfied", "diff inspection", "insufficient")),
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
    ]


CHECKS = {
    0: eval_0,
    1: eval_1,
    2: eval_2,
    3: eval_3,
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
