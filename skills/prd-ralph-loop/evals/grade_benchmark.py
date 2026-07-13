#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "## Overview",
    "## When to Use",
    "## Workflow",
    "## Common Rationalizations",
    "## Red Flags",
    "## Verification",
]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def has_required_skill_shape() -> tuple[bool, str]:
    text = read_text(Path("skills/prd-ralph-loop/SKILL.md"))
    ok = all(heading in text for heading in REQUIRED_HEADINGS)
    return ok, "all anatomy headings present" if ok else "missing one or more anatomy headings"


def build_grading(run_dir: Path, expectations: list[dict]) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "outputs" / "transcript.md")
    output_chars = 0
    outputs_dir = run_dir / "outputs"
    if outputs_dir.exists():
        for path in outputs_dir.rglob("*"):
            if path.is_file():
                output_chars += len(read_text(path))
    timing = read_json(run_dir / "timing.json")
    total_duration = timing.get("total_duration_seconds", 0.0)
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
            "executor_duration_seconds": total_duration,
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": total_duration,
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


def eval_zero(result: dict, decision_md: str) -> list[dict]:
    skill_ok, skill_evidence = has_required_skill_shape()
    return [
        expectation("The rewritten skill keeps the standard anatomy headings.", skill_ok, skill_evidence),
        expectation("Returns a complete status.", result.get("status") == "complete", result.get("status", "<missing>")),
        expectation("Outputs exactly <promise>COMPLETE</promise>.", "<promise>COMPLETE</promise>" in decision_md, decision_md or "<empty md>"),
        expectation("Has no target_task_id.", result.get("target_task_id") is None, str(result.get("target_task_id"))),
    ]


def eval_one(result: dict, decision_md: str) -> list[dict]:
    return [
        expectation("Returns a looping status.", result.get("status") == "looping", result.get("status", "<missing>")),
        expectation("Identifies US-002 as the next target task.", result.get("target_task_id") == "US-002", str(result.get("target_task_id"))),
        expectation("Plans to invoke subagent-model-router and spawn subagent for prd-ralph.", "router" in decision_md.lower() or "ralph" in decision_md.lower(), decision_md or "<empty md>"),
    ]


def eval_two(result: dict, decision_md: str) -> list[dict]:
    return [
        expectation("Returns an error status.", result.get("status") == "error", result.get("status", "<missing>")),
        expectation("Explains that the tasks are missing or invalid.", "missing" in decision_md.lower() or "invalid" in decision_md.lower() or "tasks" in decision_md.lower(), decision_md or "<empty md>"),
        expectation("Does not proceed with routing or looping.", result.get("target_task_id") is None, str(result.get("target_task_id"))),
    ]


def grade_expectations(eval_id: int, run_dir: Path) -> list[dict]:
    result = read_json(run_dir / "outputs" / "decision.json")
    decision_md = read_text(run_dir / "outputs" / "decision.md")
    if not result:
        return [expectation("decision.json exists and is valid JSON.", False, "missing or invalid outputs/decision.json")]
    if eval_id == 0:
        return eval_zero(result, decision_md)
    if eval_id == 1:
        return eval_one(result, decision_md)
    if eval_id == 2:
        return eval_two(result, decision_md)
    return [expectation(f"Unknown eval id {eval_id}.", False, f"Unsupported eval_id={eval_id}")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/prd-ralph-loop/evals/grade_benchmark.py skills/prd-ralph-loop-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        metadata = read_json(eval_dir / "eval_metadata.json")
        eval_id = metadata.get("eval_id")
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            run_dirs = sorted(config_dir.glob("run-*"))
            if not run_dirs:
                continue
            for run_dir in run_dirs:
                expectations = grade_expectations(eval_id, run_dir)
                grading = build_grading(run_dir, expectations)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
