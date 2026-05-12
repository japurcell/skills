#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "## Summary",
    "## Files to Review",
    "## Reviewer Focus",
    "## Validation",
    "## Follow-Ups",
]
VAGUE_VALIDATION_PHRASES = ["normal tests", "usual checks", "standard tests"]


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


def contains_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def section_body(markdown: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, markdown, re.DOTALL)
    return match.group(1).strip() if match else ""


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


def headings_in_order(markdown: str) -> bool:
    positions = []
    for heading in REQUIRED_HEADINGS:
        position = markdown.find(heading)
        if position == -1:
            return False
        positions.append(position)
    return positions == sorted(positions)


def find_output_markdown(run_dir: Path) -> Path | None:
    outputs_dir = run_dir / "outputs"
    preferred_names = ["review-handoff.md", "handoff.md", "output.md"]
    for name in preferred_names:
        candidate = outputs_dir / name
        if candidate.exists():
            return candidate

    candidates = [
        path
        for path in outputs_dir.rglob("*.md")
        if path.name not in {"transcript.md", "output.md"} and "SKILL.md" not in path.name
    ]
    return sorted(candidates)[0] if candidates else None


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def grade_common(markdown: str) -> list[dict]:
    files_to_review = section_body(markdown, "## Files to Review")
    validation = section_body(markdown, "## Validation")
    follow_ups = section_body(markdown, "## Follow-Ups")
    duplicates = duplicate_bullets(markdown)
    return [
        expectation(
            "The handoff uses Summary, Files to Review, Reviewer Focus, Validation, and Follow-Ups headings in order.",
            headings_in_order(markdown),
            "headings found in required order" if headings_in_order(markdown) else "missing heading or incorrect order",
        ),
        expectation(
            "Files to Review includes at least one path-style reference.",
            contains_any(files_to_review, ["/", ".py", ".ts", ".tsx", ".sql", "`"]),
            files_to_review or "missing Files to Review section body",
        ),
        expectation(
            "Validation names a concrete command or explicitly says validation is still missing.",
            contains_any(validation, ["python3", "pytest", "npm test", "not run", "none yet", "missing", "still needed"]),
            validation or "missing Validation section body",
        ),
        expectation(
            "Validation avoids vague 'normal tests' phrasing.",
            not contains_any(validation, VAGUE_VALIDATION_PHRASES),
            validation or "missing Validation section body",
        ),
        expectation(
            "Follow-Ups is present and not empty.",
            bool(follow_ups),
            follow_ups or "missing Follow-Ups section body",
        ),
        expectation(
            "The handoff does not contain duplicate bullet lines.",
            not duplicates,
            "no duplicate bullets found" if not duplicates else f"duplicate bullets: {duplicates}",
        ),
    ]


def grade_eval_zero(markdown: str) -> list[dict]:
    validation = section_body(markdown, "## Validation")
    follow_ups = section_body(markdown, "## Follow-Ups")
    reviewer_focus = section_body(markdown, "## Reviewer Focus")
    return [
        expectation(
            "Reviewer Focus calls out stale auth or logout invalidation risk.",
            contains_any(reviewer_focus, ["stale auth", "logout", "invalidation", "token cache"]),
            reviewer_focus or "missing Reviewer Focus section body",
        ),
        expectation(
            "Validation names both pytest commands.",
            "python3 -m pytest tests/auth/test_token_cache.py" in validation
            and "python3 -m pytest tests/auth/test_middleware.py" in validation,
            validation or "missing Validation section body",
        ),
        expectation(
            "Follow-Ups explicitly says there are no follow-ups.",
            contains_any(follow_ups, ["none", "no follow-up", "no follow ups", "no follow-ups"]),
            follow_ups or "missing Follow-Ups section body",
        ),
    ]


def grade_eval_one(markdown: str) -> list[dict]:
    validation = section_body(markdown, "## Validation")
    follow_ups = section_body(markdown, "## Follow-Ups")
    return [
        expectation(
            "The handoff mentions the missing browser smoke check.",
            contains_any(markdown, ["browser smoke", "browser check", "browser validation"]),
            markdown or "missing markdown output",
        ),
        expectation(
            "Validation includes the executed pytest and npm test commands.",
            "python3 -m pytest tests/billing/test_retry.py" in validation
            and "npm test -- BillingPanel.test.tsx" in validation,
            validation or "missing Validation section body",
        ),
        expectation(
            "Follow-Ups mentions the billing troubleshooting screenshot update.",
            contains_any(follow_ups, ["screenshot", "billing troubleshooting", "docs"]),
            follow_ups or "missing Follow-Ups section body",
        ),
    ]


def grade_eval_two(markdown: str) -> list[dict]:
    validation = section_body(markdown, "## Validation")
    reviewer_focus = section_body(markdown, "## Reviewer Focus")
    risk_mentions = len(re.findall(r"(migration|rollback|backward compatibility)", markdown.lower()))
    return [
        expectation(
            "Reviewer Focus mentions backward compatibility or rollback safety.",
            contains_any(reviewer_focus, ["backward compatibility", "rollback", "rollout"]),
            reviewer_focus or "missing Reviewer Focus section body",
        ),
        expectation(
            "Validation names the pytest command and says staging migration validation is still missing.",
            "python3 -m pytest tests/reviews/test_service.py" in validation
            and contains_any(validation, ["staging", "not been applied", "still missing", "missing validation"]),
            validation or "missing Validation section body",
        ),
        expectation(
            "The output avoids over-repeating the migration risk.",
            risk_mentions <= 4,
            f"risk_mentions={risk_mentions}",
        ),
    ]


def grade_eval_three(markdown: str) -> list[dict]:
    validation = section_body(markdown, "## Validation")
    follow_ups = section_body(markdown, "## Follow-Ups")
    reviewer_focus = section_body(markdown, "## Reviewer Focus")
    return [
        expectation(
            "Reviewer Focus mentions idempotency, retries, or duplicate customer emails.",
            contains_any(reviewer_focus, ["idempotency", "retry", "duplicate customer emails", "duplicate emails"]),
            reviewer_focus or "missing Reviewer Focus section body",
        ),
        expectation(
            "Validation clearly says no validation has run yet or that validation is still missing.",
            contains_any(validation, ["none yet", "not run", "still missing", "missing validation"]),
            validation or "missing Validation section body",
        ),
        expectation(
            "Follow-Ups explicitly says there are no follow-ups.",
            contains_any(follow_ups, ["none", "no follow-up", "no follow ups", "no follow-ups"]),
            follow_ups or "missing Follow-Ups section body",
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
    elif eval_id == 3:
        expectations.extend(grade_eval_three(markdown))
    else:
        expectations.append(expectation("Eval id is recognized by the grader.", False, f"unrecognized eval id {eval_id}"))
    return expectations


def build_grading(run_dir: Path, expectations: list[dict]) -> dict:
    timing = load_json(run_dir / "timing.json")
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    output_path = find_output_markdown(run_dir)
    output_chars = len(read_text(output_path)) if output_path else 0
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "outputs" / "transcript.md")
    return {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": output_chars,
            "transcript_chars": len(transcript),
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


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 grade_benchmark.py <iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    results = []

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        metadata = load_json(eval_dir / "eval_metadata.json")
        eval_id = metadata.get("eval_id")
        if eval_id is None:
            continue

        for run_dir in sorted(eval_dir.glob("*/run-*")):
            output_path = find_output_markdown(run_dir)
            markdown = read_text(output_path) if output_path else ""
            expectations = grade_markdown(eval_id, markdown)
            results.append(
                {
                    "eval_id": eval_id,
                    "run": str(run_dir.relative_to(iteration_dir)),
                    "output_file": str(output_path.relative_to(iteration_dir)) if output_path else "",
                    "grading": build_grading(run_dir, expectations),
                }
            )

    print(json.dumps({"results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
