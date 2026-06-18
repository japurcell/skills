#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
    except json.JSONDecodeError:
        return {}


def build_grading(expectations: list[dict], run_dir: Path) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    outputs_dir = run_dir / "outputs"
    output_chars = 0
    if outputs_dir.exists():
        for path in outputs_dir.rglob("*"):
            if path.is_file():
                output_chars += len(read_text(path))
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")
    timing = load_timing(run_dir)
    duration_seconds = timing.get("total_duration_seconds", 0.0)
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
            "executor_duration_seconds": duration_seconds,
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": duration_seconds,
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


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def eval_id_for(eval_dir: Path) -> int | None:
    metadata_path = eval_dir / "eval_metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            if "eval_id" in metadata:
                return int(metadata["eval_id"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    match = re.match(r"eval-(\d+)", eval_dir.name)
    if match:
        return int(match.group(1))
    return None


def find_output(run_dir: Path) -> tuple[str, str]:
    for relative_path in (
        "outputs/review_plan.md",
        "outputs/question.md",
        "outputs/preflight.md",
        "outputs/decisions.json",
    ):
        path = run_dir / relative_path
        if path.exists():
            return relative_path, read_text(path)
    return "", ""


def has_all(text: str, items: list[str]) -> bool:
    lowered = normalize(text)
    return all(item.lower() in lowered for item in items)


def load_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def grade(eval_id: int, output_path: str, output_text: str) -> list[dict]:
    normalized = normalize(output_text)

    if eval_id == 0:
        return [
            expectation(
                "The checklist invokes `subagent-model-router` and `addy-code-review-and-quality`.",
                has_all(output_text, ["subagent-model-router", "addy-code-review-and-quality"]),
                output_text or "missing review_plan.md",
            ),
            expectation(
                "The checklist says the main agent must not read PR or issue content directly and must use `gh` through fast subagents.",
                "must not read pr or issue content directly" in normalized
                and "gh" in normalized
                and "subagent" in normalized,
                output_text or "missing review_plan.md",
            ),
            expectation(
                "The checklist includes the PR early-stop states and rechecks eligibility before `gh pr comment`.",
                has_all(
                    output_text,
                    [
                        "closed",
                        "draft",
                        "review not needed",
                        "already reviewed by you",
                        "gh pr comment",
                    ],
                ),
                output_text or "missing review_plan.md",
            ),
            expectation(
                "The checklist keeps false-positive filtering with scores `75` or `100`.",
                "false_positive_rubric.md" in normalized and "75" in output_text and "100" in output_text,
                output_text or "missing review_plan.md",
            ),
        ]

    if eval_id == 1:
        exact = "Review against what — a branch, a commit, or main?"
        return [
            expectation(
                "The output is exactly `Review against what — a branch, a commit, or main?`.",
                output_text.strip() == exact,
                output_text or "missing question.md",
            )
        ]

    if eval_id == 2:
        return [
            expectation(
                "The checklist names `addy-code-reviewer`, `addy-security-auditor`, and `addy-test-engineer`.",
                has_all(output_text, ["addy-code-reviewer", "addy-security-auditor", "addy-test-engineer"]),
                output_text or "missing preflight.md",
            ),
            expectation(
                "The checklist names maintainability review with `MAINTAINABILITY_CRITERIA.md` and standards review limited to explicit documented rules.",
                "maintainability_criteria.md" in normalized
                and "standards" in normalized
                and "explicit documented rules" in normalized,
                output_text or "missing preflight.md",
            ),
            expectation(
                "The checklist records `no spec available` and skips spec review.",
                "no spec available" in normalized and "skip spec review" in normalized,
                output_text or "missing preflight.md",
            ),
            expectation(
                "The checklist points machine-readable output to `OUTPUT_FORMATS.md`.",
                "machine-readable" in normalized and "output_formats.md" in normalized,
                output_text or "missing preflight.md",
            ),
            expectation(
                "The checklist says not to run builds, typechecks, linters, or benchmarks unless the user explicitly asks.",
                has_all(output_text, ["builds", "typechecks", "linters", "benchmarks", "explicitly asks"]),
                output_text or "missing preflight.md",
            ),
        ]

    if eval_id == 3:
        data = load_json(output_text)
        return [
            expectation(
                "The JSON marks `review_pr_before_merge`, `review_since_main`, and `harsh_wip_diff_review` as true.",
                isinstance(data, dict)
                and data.get("review_pr_before_merge") is True
                and data.get("review_since_main") is True
                and data.get("harsh_wip_diff_review") is True,
                output_text or "missing decisions.json",
            ),
            expectation(
                "The JSON marks `write_pr_description`, `implement_feature`, and `review_product_spec_only` as false.",
                isinstance(data, dict)
                and data.get("write_pr_description") is False
                and data.get("implement_feature") is False
                and data.get("review_product_spec_only") is False,
                output_text or "missing decisions.json",
            ),
        ]

    return [expectation(f"Unknown eval id {eval_id}.", False, "Unsupported eval")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py <iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1]).resolve()
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        eval_id = eval_id_for(eval_dir)
        if eval_id is None:
            print(f"Skipping {eval_dir}: could not determine eval id")
            continue
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                output_path, output_text = find_output(run_dir)
                grading = build_grading(grade(eval_id, output_path, output_text), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
