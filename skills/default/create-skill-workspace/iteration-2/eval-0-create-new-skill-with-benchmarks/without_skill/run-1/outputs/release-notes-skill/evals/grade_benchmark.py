#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path
from typing import Optional


REQUIRED_HEADINGS = [
    "## Highlights",
    "## Grouped Changes",
    "## Upgrade Notes",
    "## Follow-Ups",
]


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


def find_output_markdown(run_dir: Path) -> Optional[Path]:
    outputs_dir = run_dir / "outputs"
    preferred = outputs_dir / "output.md"
    if preferred.exists():
        return preferred

    for path in sorted(outputs_dir.rglob("*.md")):
        if path.name == "transcript.md" or not path.is_file():
            continue
        text = read_text(path)
        if text.startswith("# Release Notes:") or text.startswith("# Missing Inputs for Release Notes"):
            return path
    return None


def section_body(markdown: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, markdown, re.DOTALL)
    return match.group(1).strip() if match else ""


def section_start(markdown: str, heading: str) -> int:
    return markdown.find(heading)


def has_title(markdown: str) -> bool:
    first_line = markdown.splitlines()[0].strip() if markdown.splitlines() else ""
    return first_line.startswith("# Release Notes:")


def headings_in_order(markdown: str) -> bool:
    positions = [section_start(markdown, heading) for heading in REQUIRED_HEADINGS]
    return all(position >= 0 for position in positions) and positions == sorted(positions)


def section_has_bullet(markdown: str, heading: str) -> bool:
    body = section_body(markdown, heading)
    return any(line.strip().startswith("- ") for line in body.splitlines())


def grouped_changes_has_theme(markdown: str) -> bool:
    grouped = section_body(markdown, "## Grouped Changes")
    return "### " in grouped


def bullet_lines(markdown: str) -> list[str]:
    return [line.strip() for line in markdown.splitlines() if line.strip().startswith("- ")]


def duplicate_bullets(markdown: str) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for bullet in bullet_lines(markdown):
        key = normalize(bullet)
        if key in seen and key not in duplicates:
            duplicates.append(key)
        seen.add(key)
    return duplicates


def contains_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def explicit_no_action(upgrade_section: str) -> bool:
    lowered = upgrade_section.lower()
    return (
        "none called out" in lowered
        or "no migration required" in lowered
        or "no action required" in lowered
    )


def markdown_without_section(markdown: str, heading: str) -> str:
    pattern = rf"\n?{re.escape(heading)}\n.*?(?=\n## |\Z)"
    return re.sub(pattern, "\n", markdown, flags=re.DOTALL)


def grade_common(markdown: str) -> list[dict]:
    duplicates = duplicate_bullets(markdown)
    return [
        expectation(
            "The output starts with a Release Notes title.",
            has_title(markdown),
            markdown.splitlines()[0] if markdown.splitlines() else "missing markdown output",
        ),
        expectation(
            "Release notes use Highlights, Grouped Changes, Upgrade Notes, and Follow-Ups in that order.",
            headings_in_order(markdown),
            "all required headings found in order"
            if headings_in_order(markdown)
            else "missing headings or headings are out of order",
        ),
        expectation(
            "Highlights contains at least one bullet.",
            section_has_bullet(markdown, "## Highlights"),
            section_body(markdown, "## Highlights") or "missing Highlights section body",
        ),
        expectation(
            "Grouped Changes includes at least one themed subsection.",
            grouped_changes_has_theme(markdown),
            "found a ### subsection in Grouped Changes"
            if grouped_changes_has_theme(markdown)
            else "missing themed subsection under Grouped Changes",
        ),
        expectation(
            "The output does not contain duplicate bullet lines.",
            not duplicates,
            "no duplicate bullet lines found" if not duplicates else f"duplicate bullets: {duplicates}",
        ),
    ]


def grade_eval_zero(markdown: str) -> list[dict]:
    upgrade = section_body(markdown, "## Upgrade Notes")
    follow_ups = section_body(markdown, "## Follow-Ups")
    return [
        expectation(
            "Release notes mention SSO support for workspace members.",
            contains_any(markdown, ["sso", "okta", "azure ad"]),
            "found SSO-related language"
            if contains_any(markdown, ["sso", "okta", "azure ad"])
            else "missing SSO-related language",
        ),
        expectation(
            "Release notes mention export or webhook retry improvements.",
            contains_any(markdown, ["retry status", "retry", "webhook", "export"]),
            "found retry-related language"
            if contains_any(markdown, ["retry status", "retry", "webhook", "export"])
            else "missing retry-related language",
        ),
        expectation(
            "Upgrade Notes call out the EXPORTS_BUCKET configuration rename.",
            contains_any(upgrade, ["exports_bucket", "export_job_bucket", "env var", "config"]),
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
    return [
        expectation(
            "Release notes keep the 2.3.0 release label.",
            contains_any(markdown, ["release notes: 2.3.0", "release notes 2.3.0", "2.3.0"]),
            markdown.splitlines()[0] if markdown else "missing markdown output",
        ),
        expectation(
            "Release notes mention scoped tenant API tokens, audit log export filters, and graceful queue shutdown.",
            contains_any(markdown, ["token"])
            and contains_any(markdown, ["audit log", "actor", "event type"])
            and contains_any(markdown, ["queue", "shutdown", "drain"]),
            "found all three topic clusters"
            if contains_any(markdown, ["token"])
            and contains_any(markdown, ["audit log", "actor", "event type"])
            and contains_any(markdown, ["queue", "shutdown", "drain"])
            else "missing one or more expected topics",
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
    non_follow_up_text = markdown_without_section(markdown, "## Follow-Ups")
    return [
        expectation(
            "Release notes mention reconciliation CSV export and the failed invoice reason column.",
            contains_any(markdown, ["csv"]) and contains_any(markdown, ["failed invoice reason", "reason column"]),
            "found CSV and failed-reason language"
            if contains_any(markdown, ["csv"]) and contains_any(markdown, ["failed invoice reason", "reason column"])
            else "missing CSV export detail",
        ),
        expectation(
            "Release notes mention the duplicate-email fix for nightly reconciliation.",
            contains_any(markdown, ["duplicate emails", "duplicate email", "nightly reconciliation", "rerun"]),
            "found duplicate-email language"
            if contains_any(markdown, ["duplicate emails", "duplicate email", "nightly reconciliation", "rerun"])
            else "missing duplicate-email fix",
        ),
        expectation(
            "The historical backfill appears only as a follow-up, not as shipped work.",
            contains_any(follow_ups, ["backfill", "historical", "did not ship"])
            and not contains_any(non_follow_up_text, ["backfill", "historical rows"]),
            "backfill mentioned only in Follow-Ups"
            if contains_any(follow_ups, ["backfill", "historical", "did not ship"])
            and not contains_any(non_follow_up_text, ["backfill", "historical rows"])
            else "backfill missing from Follow-Ups or mentioned outside it",
        ),
        expectation(
            "Upgrade Notes explicitly says no action is required.",
            explicit_no_action(upgrade),
            upgrade or "missing Upgrade Notes section body",
        ),
    ]


def grade_eval_three(markdown: str) -> list[dict]:
    return [
        expectation(
            "The output reports that required inputs are missing before drafting.",
            contains_any(markdown, ["missing input", "missing inputs", "before i can draft", "cannot draft"]),
            markdown or "missing markdown output",
        ),
        expectation(
            "The output specifically asks for a release label.",
            contains_any(markdown, ["release label"]),
            markdown or "missing markdown output",
        ),
        expectation(
            "The output specifically asks for an audience.",
            contains_any(markdown, ["audience"]),
            markdown or "missing markdown output",
        ),
        expectation(
            "The output does not invent a release-notes title or the standard release-note sections.",
            not has_title(markdown) and not headings_in_order(markdown),
            markdown.splitlines()[0] if markdown.splitlines() else "missing markdown output",
        ),
    ]


def grade_markdown(eval_id: int, markdown: str) -> list[dict]:
    if eval_id == 0:
        return grade_common(markdown) + grade_eval_zero(markdown)
    if eval_id == 1:
        return grade_common(markdown) + grade_eval_one(markdown)
    if eval_id == 2:
        return grade_common(markdown) + grade_eval_two(markdown)
    if eval_id == 3:
        return grade_eval_three(markdown)
    return [
        expectation(
            "Eval id is recognized by the grader.",
            False,
            f"unrecognized eval id {eval_id}",
        )
    ]


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
            "executor_duration_seconds": timing.get("executor_duration_seconds", timing.get("total_duration_seconds", 0.0)),
            "grader_duration_seconds": timing.get("grader_duration_seconds", 0.0),
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
