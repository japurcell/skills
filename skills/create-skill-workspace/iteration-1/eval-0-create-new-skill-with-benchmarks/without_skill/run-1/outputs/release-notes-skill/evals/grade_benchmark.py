#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "## Highlights",
    "## Grouped Changes",
    "## Upgrade Notes",
    "## Follow-Ups",
]

SENTINEL_BULLET = re.compile(
    r"^-\s*(none(?: called out)?|none\.|no action required\.?|no migration required\.?)$",
    re.IGNORECASE,
)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def find_output_markdown(run_dir: Path) -> Path | None:
    outputs_dir = run_dir / "outputs"
    preferred = outputs_dir / "output.md"
    if preferred.exists():
        return preferred

    candidates = [
        path
        for path in outputs_dir.rglob("*.md")
        if path.is_file() and path.name not in {"transcript.md", "output.md"}
    ]
    return sorted(candidates)[0] if candidates else None


def section_body(markdown: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, markdown, re.DOTALL)
    return match.group(1).strip() if match else ""


def has_required_structure(markdown: str) -> bool:
    return all(heading in markdown for heading in REQUIRED_HEADINGS)


def grouped_changes_has_theme(markdown: str) -> bool:
    return "### " in section_body(markdown, "## Grouped Changes")


def bullet_lines(markdown: str) -> list[str]:
    return [line.strip() for line in markdown.splitlines() if line.strip().startswith("- ")]


def duplicate_bullets(markdown: str) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for bullet in bullet_lines(markdown):
        if SENTINEL_BULLET.match(bullet):
            continue
        key = normalize(bullet)
        if key in seen and key not in duplicates:
            duplicates.append(key)
        seen.add(key)
    return duplicates


def contains_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def explicit_no_action(upgrade_section: str) -> bool:
    return contains_any(
        upgrade_section,
        ["none called out", "no migration required", "no action required"],
    )


def grade_common(markdown: str) -> list[dict]:
    duplicates = duplicate_bullets(markdown)
    return [
        expectation(
            "Release notes use the expected Highlights, Grouped Changes, Upgrade Notes, and Follow-Ups headings.",
            has_required_structure(markdown),
            "all required headings present" if has_required_structure(markdown) else "missing one or more required headings",
        ),
        expectation(
            "Grouped Changes includes at least one themed subsection.",
            grouped_changes_has_theme(markdown),
            "found a themed subsection" if grouped_changes_has_theme(markdown) else "missing themed subsection under Grouped Changes",
        ),
        expectation(
            "The output does not contain duplicate substantive bullets.",
            not duplicates,
            "no duplicate substantive bullets found" if not duplicates else f"duplicate bullets: {duplicates}",
        ),
    ]


def grade_eval_zero(markdown: str) -> list[dict]:
    upgrade = section_body(markdown, "## Upgrade Notes")
    follow_ups = section_body(markdown, "## Follow-Ups")
    return [
        expectation(
            "Release notes mention SSO support for workspace members.",
            contains_any(markdown, ["sso", "okta", "microsoft entra"]),
            "found SSO-related language" if contains_any(markdown, ["sso", "okta", "microsoft entra"]) else "missing SSO-related language",
        ),
        expectation(
            "Release notes mention export or webhook retry improvements.",
            contains_any(markdown, ["retry progress", "retry", "webhook", "export"]),
            "found retry-related language" if contains_any(markdown, ["retry progress", "retry", "webhook", "export"]) else "missing retry-related language",
        ),
        expectation(
            "Upgrade Notes calls out the REPORTS_BUCKET configuration rename.",
            contains_any(upgrade, ["reports_bucket", "report_export_bucket", "env var", "config"]),
            upgrade or "missing Upgrade Notes section body",
        ),
        expectation(
            "Follow-Ups explicitly says there are no remaining follow-ups if none are provided.",
            contains_any(follow_ups, ["none", "no follow-up", "no follow ups", "no follow-ups"]),
            follow_ups or "missing Follow-Ups section body",
        ),
    ]


def grade_eval_one(markdown: str) -> list[dict]:
    upgrade = section_body(markdown, "## Upgrade Notes")
    follow_ups = section_body(markdown, "## Follow-Ups")
    has_topics = (
        contains_any(markdown, ["token"])
        and contains_any(markdown, ["alert-rule", "alert rule", "severity", "owner"])
        and contains_any(markdown, ["queue", "shutdown", "drain"])
    )
    return [
        expectation(
            "Release notes keep the 3.2.0 release label.",
            contains_any(markdown, ["release notes: 3.2.0", "release notes 3.2.0", "3.2.0"]),
            markdown.splitlines()[0] if markdown else "missing markdown output",
        ),
        expectation(
            "Release notes mention scoped tenant API tokens, alert-rule export filters, and graceful queue shutdown.",
            has_topics,
            "found all expected topic clusters" if has_topics else "missing one or more expected topics",
        ),
        expectation(
            "Upgrade Notes explicitly says no action is required.",
            explicit_no_action(upgrade),
            upgrade or "missing Upgrade Notes section body",
        ),
        expectation(
            "Follow-Ups mentions the outdated dashboard screenshots.",
            contains_any(follow_ups, ["dashboard screenshot", "old token ui", "docs"]),
            follow_ups or "missing Follow-Ups section body",
        ),
    ]


def grade_eval_two(markdown: str) -> list[dict]:
    upgrade = section_body(markdown, "## Upgrade Notes")
    follow_ups = section_body(markdown, "## Follow-Ups")
    return [
        expectation(
            "Release notes mention payout exception CSV export and the failed payment reason column.",
            contains_any(markdown, ["csv"]) and contains_any(markdown, ["failed payment reason", "reason column"]),
            "found CSV and failed-reason language" if contains_any(markdown, ["csv"]) and contains_any(markdown, ["failed payment reason", "reason column"]) else "missing payout CSV detail",
        ),
        expectation(
            "Release notes mention the duplicate-email fix for nightly reconciliation.",
            contains_any(markdown, ["duplicate emails", "duplicate email", "nightly reconciliation", "reruns"]),
            "found duplicate-email language" if contains_any(markdown, ["duplicate emails", "duplicate email", "nightly reconciliation", "reruns"]) else "missing duplicate-email fix",
        ),
        expectation(
            "Follow-Ups mentions the historical backfill did not ship in 1.9.4.",
            contains_any(follow_ups, ["backfill", "historical", "did not ship", "1.9.4"]),
            follow_ups or "missing Follow-Ups section body",
        ),
        expectation(
            "Upgrade Notes explicitly says no action is required.",
            explicit_no_action(upgrade),
            upgrade or "missing Upgrade Notes section body",
        ),
    ]


def grade_markdown(eval_id: int, markdown: str) -> list[dict]:
    expectations = grade_common(markdown)
    if eval_id == 0:
        expectations.extend(grade_eval_zero(markdown))
    elif eval_id == 1:
        expectations.extend(grade_eval_one(markdown))
    elif eval_id == 2:
        expectations.extend(grade_eval_two(markdown))
    else:
        expectations.append(
            expectation(
                "Eval id is recognized by the grader.",
                False,
                f"unrecognized eval id {eval_id}",
            )
        )
    return expectations


def build_grading(run_dir: Path, expectations: list[dict]) -> dict:
    timing = load_json(run_dir / "timing.json")
    metrics = load_json(run_dir / "outputs" / "metrics.json")
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    return {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": metrics.get("tool_calls", {}),
            "total_tool_calls": metrics.get("total_tool_calls", 0),
            "total_steps": metrics.get("total_steps", 0),
            "errors_encountered": metrics.get("errors_encountered", 0),
            "output_chars": metrics.get("output_chars", 0),
            "transcript_chars": metrics.get("transcript_chars", 0),
        },
        "timing": {
            "executor_duration_seconds": timing.get("total_duration_seconds", 0.0),
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": timing.get("total_duration_seconds", 0.0),
        },
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
        "eval_feedback": {
            "suggestions": [],
            "overall": "No evaluator suggestions.",
        },
    }


def iter_run_dirs(path: Path) -> list[tuple[int, Path]]:
    run_pairs: list[tuple[int, Path]] = []
    for eval_dir in sorted(path.glob("eval-*")):
        metadata = load_json(eval_dir / "eval_metadata.json")
        eval_id = metadata.get("eval_id")
        if eval_id is None:
            continue
        for config_dir in sorted(child for child in eval_dir.iterdir() if child.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                run_pairs.append((int(eval_id), run_dir))
    return run_pairs


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 grade_benchmark.py skills/release-notes-skill-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    run_pairs = iter_run_dirs(iteration_dir)
    if not run_pairs:
        print(f"No benchmark run directories found under {iteration_dir}")
        return 1

    for eval_id, run_dir in run_pairs:
        output_path = find_output_markdown(run_dir)
        markdown = read_text(output_path) if output_path else ""
        expectations = grade_markdown(eval_id, markdown)
        grading = build_grading(run_dir, expectations)
        (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
