#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def find_response_text(run_dir: Path) -> str:
    candidates = [
        run_dir / "outputs" / "response.md",
        run_dir / "outputs" / "output.md",
        run_dir / "outputs" / "transcript.md",
        run_dir / "response.md",
        run_dir / "output.md",
        run_dir / "transcript.md",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(errors="replace")
    return ""


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def contains_all(text: str, phrases: list[str]) -> bool:
    return all(phrase in text for phrase in phrases)


def contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def grade(eval_id: int, response_text: str) -> list[dict]:
    text = normalize(response_text)

    if eval_id == 0:
        return [
            expectation(
                "Selects the next pending task from the plan or task list.",
                contains_any(text, ["next pending task", "pick the next pending task", "select the next pending task"]),
                response_text or "missing response",
            ),
            expectation(
                "Reads acceptance criteria before implementation.",
                contains_any(text, ["acceptance criteria", "read its acceptance criteria"]),
                response_text or "missing response",
            ),
            expectation(
                "Writes a failing test before implementation.",
                contains_any(text, ["failing test", "write a failing test", "red"]),
                response_text or "missing response",
            ),
            expectation(
                "Runs the relevant tests and the build.",
                contains_all(text, ["tests"]) and contains_any(text, ["build", "compile"]),
                response_text or "missing response",
            ),
            expectation(
                "Updates plan and task tracking immediately after verification.",
                contains_any(text, ["update the plan", "update the task tracker", "tracking immediately"]),
                response_text or "missing response",
            ),
            expectation(
                "Leaves the work uncommitted.",
                contains_any(text, ["uncommitted", "do not commit", "leave it uncommitted"]),
                response_text or "missing response",
            ),
        ]

    if eval_id == 1:
        return [
            expectation(
                "Resumes from the next pending task instead of redoing completed work.",
                contains_any(text, ["next pending task", "resume", "skip completed work"]),
                response_text or "missing response",
            ),
            expectation(
                "Respects dependency order between tasks.",
                contains_any(text, ["depends on", "dependency order", "after t015"]),
                response_text or "missing response",
            ),
            expectation(
                "Uses the same incremental test-build-verify loop.",
                contains_all(text, ["test"]) and contains_any(text, ["build", "verify"]),
                response_text or "missing response",
            ),
            expectation(
                "Mentions addy-debugging-and-error-recovery when a step fails.",
                "addy-debugging-and-error-recovery" in text,
                response_text or "missing response",
            ),
        ]

    if eval_id == 2:
        return [
            expectation(
                "Does not start the build workflow without an existing plan or task list.",
                contains_any(text, ["no existing plan", "no active tasks", "does not use the build skill"]),
                response_text or "missing response",
            ),
            expectation(
                "Says the skill is not for plan creation or task breakdown.",
                contains_any(text, ["not for plan creation", "not for task breakdown"]),
                response_text or "missing response",
            ),
            expectation(
                "Routes the user to planning or another appropriate workflow.",
                contains_any(text, ["planning", "create-plan", "task breakdown"]),
                response_text or "missing response",
            ),
        ]

    if eval_id == 3:
        return [
            expectation(
                "Mentions addy-debugging-and-error-recovery for the failure.",
                "addy-debugging-and-error-recovery" in text,
                response_text or "missing response",
            ),
            expectation(
                "Does not mark the task done after a failed build.",
                contains_any(text, ["not mark", "stay unmarked", "keep the task open", "do not mark"]),
                response_text or "missing response",
            ),
            expectation(
                "Keeps verification and tracking tied to a passing fix.",
                contains_any(text, ["passing fix", "after the failure is fixed", "before updating tracking"]),
                response_text or "missing response",
            ),
        ]

    return []


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: grade_benchmark.py <iteration-dir>", file=sys.stderr)
        return 2

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"missing iteration dir: {iteration_dir}", file=sys.stderr)
        return 2

    for eval_dir in sorted(p for p in iteration_dir.iterdir() if p.is_dir() and p.name.startswith("eval-")):
        metadata_path = eval_dir / "eval_metadata.json"
        eval_id = json.loads(read_text(metadata_path)).get("eval_id") if metadata_path.exists() else None
        response_text = find_response_text(eval_dir)
        grading = {
            "expectations": grade(eval_id, response_text) if eval_id is not None else [],
        }
        (eval_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
