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


def decision_text(run_dir: Path) -> str:
    return read_text(run_dir / "outputs" / "decision.md")


def has_all(text: str, items: list[str]) -> bool:
    lowered = normalize(text)
    return all(item.lower() in lowered for item in items)


def mentions_progress_path(text: str) -> bool:
    lowered = normalize(text)
    return (
        'dirname(prd_file) + "/progress.txt"' in text
        or "evals/files/startup-fixture/progress.txt" in text
        or "progress.txt" in lowered
    )


def grade(eval_id: int, output_text: str) -> list[dict]:
    normalized = normalize(output_text)

    if eval_id == 0:
        return [
            expectation(
                "The decision says `prd_file` is official source of truth and `progress_file` is supplemental.",
                "prd_file" in normalized
                and "source of truth" in normalized
                and "progress_file" in normalized,
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision resolves the default `progress_file` to `dirname(prd_file) + \"/progress.txt\"` or the fixture `progress.txt` path.",
                mentions_progress_path(output_text),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision selects the highest-priority `passes: false` story.",
                ("highest-priority" in normalized or "highest priority" in normalized)
                and "passes: false" in normalized,
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision dispatches a fresh implementer before story-specific repo discovery.",
                ("fresh implementer" in normalized or "dispatch" in normalized)
                and (
                    "before story-specific" in normalized
                    or "do not read story-specific" in normalized
                    or "before any story-specific" in normalized
                ),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 1:
        return [
            expectation(
                "The decision appends the implementer `Progress block` before acting on it.",
                "progress block" in normalized
                and "append" in normalized
                and "before" in normalized,
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision reruns `code-simplifier` and `addy-code-reviewer` after the review fix.",
                has_all(output_text, ["code-simplifier", "addy-code-reviewer"])
                and ("rerun" in normalized or "run again" in normalized)
                and ("review fix" in normalized or "review_fix" in normalized),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision keeps `passes: true` blocked until review is clean and final checks pass.",
                ("passes: true" in output_text or "`passes: true`" in output_text)
                and ("do not" in normalized or "leave" in normalized or "blocked" in normalized)
                and "review is clean" in normalized
                and ("checks" in normalized or "verify" in normalized),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 2:
        return [
            expectation(
                "The decision stops because the review-fix iteration limit is reached.",
                "review-fix" in normalized
                and "limit" in normalized
                and ("reached" in normalized or "already 3" in normalized or "iteration count is 3" in normalized)
                and "stop" in normalized,
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision says not to fix findings directly or dispatch another review-fix implementer.",
                ("do not" in normalized or "cannot" in normalized)
                and ("fix directly" in normalized or "another review_fix" in normalized or "another review-fix" in normalized),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision rereads `prd_file`, appends stop state to `progress_file`, and asks the user to decide the blocker.",
                has_all(output_text, ["prd_file", "progress_file"])
                and ("stop-state" in normalized or "stop state" in normalized)
                and ("ask user" in normalized or "ask the user" in normalized)
                and ("blocker" in normalized or "decide" in normalized),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 3:
        return [
            expectation(
                "The output is exactly `<promise>COMPLETE</promise>`.",
                output_text.strip() == "<promise>COMPLETE</promise>",
                output_text or "missing decision.md",
            )
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
                grading = build_grading(grade(eval_id, decision_text(run_dir)), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
