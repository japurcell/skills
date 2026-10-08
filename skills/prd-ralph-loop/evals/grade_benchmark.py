#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        return {}


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


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
    total_duration = timing.get("total_duration_seconds")
    metrics = read_json(run_dir / "metrics.json")
    return {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": metrics.get("tool_calls"),
            "total_tool_calls": metrics.get("total_tool_calls"),
            "total_steps": metrics.get("total_steps"),
            "errors_encountered": metrics.get("errors_encountered"),
            "output_chars": output_chars,
            "transcript_chars": len(transcript),
        },
        "timing": {
            "executor_duration_seconds": total_duration,
            "grader_duration_seconds": None,
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
            "overall": "Scenario-specific protocol and wording heuristics; not a general manifest, transcript, or natural-language verifier. Missing runtime metrics are unavailable, not zero.",
        },
    }


def eval_zero(result: dict, decision_md: str) -> list[dict]:
    return [
        expectation("Returns a complete status.", result.get("status") == "complete", result.get("status", "<missing>")),
        expectation("Outputs exactly <promise>COMPLETE</promise>.", decision_md.strip() == "<promise>COMPLETE</promise>", decision_md or "<empty md>"),
        expectation("Has no target_task_id.", result.get("target_task_id") is None, str(result.get("target_task_id"))),
    ]


def eval_one(result: dict, decision_md: str) -> list[dict]:
    # Frozen dependent/worker.json reports US-002 success, prerequisite proof,
    # and an audited commit. This is a fixture heuristic, not a summary verifier.
    text = normalize(decision_md)
    retained_summary = all(re.search(pattern, text) for pattern in (
        r"\bus-002\b",
        r"\b(?:passed|completed|succeeded|successful)\b",
        r"\b(?:prerequisite|prerequisites|prereq|prereqs|precondition|preconditions|dependency|dependencies)\b",
        r"\b(?:evidence|proof|verified|validated|checked)\b",
        r"\bcommit\b",
        r"\b(?:audited|reviewed|inspected)\b|\baudit\s+(?:(?:was|is)\s+)?(?:passed|complete|completed|successful)\b",
    )) and set(re.findall(r"\bus-\d+\b", text)) == {"us-002"}
    contradictions = (
        r"\b(?:us-002|tests?|checks?|verification)\s+(?:(?:has|have|had|still|were|was)\s+)*(?:failed|failing|fails)\b",
        r"\b(?:us-002|tests?|checks?|verification)\s+(?:(?:did|does|has|have|was|were|is|are)\s+)?not\s+(?:pass|passed|complete|completed|successful|verified)\b",
        r"\b(?:no|without|missing|unaudited|unreviewed)\s+(?:(?:an?|the|audited|reviewed)\s+)?commit\b",
        r"\bcommit(?:\s+\w+){0,3}\s+(?:not|never)\s+(?:audited|reviewed|inspected|created|made|recorded)\b",
        r"\bcommit\s+(?:is|was|remains)\s+(?:missing|absent|unaudited|unreviewed)\b",
        r"\bcommit\s+(?:(?:audit|review)\s+)?(?:(?:is|was|remains)\s+)?(?:failed|pending|unavailable)\b",
    )
    retained_summary = retained_summary and not any(re.search(pattern, text) for pattern in contradictions)
    return [
        expectation("Returns a looping status.", result.get("status") == "looping", result.get("status", "<missing>")),
        expectation("Leaves task selection to the worker.", result.get("target_task_id") is None, str(result.get("target_task_id"))),
        expectation("Continues after TASK_COMPLETE with a fresh Ralph worker.", decision_md.startswith("<promise>TASK_COMPLETE</promise>") and "fresh" in decision_md.lower() and "ralph" in decision_md.lower(), decision_md or "<empty md>"),
        expectation("Retains the completed worker task and its prerequisite and commit evidence.", retained_summary, decision_md or "<empty md>"),
    ]


def eval_two(result: dict, decision_md: str) -> list[dict]:
    return [
        expectation("Returns a blocked status.", result.get("status") == "blocked", result.get("status", "<missing>")),
        expectation("Preserves the worker invalid-input blocker.", decision_md.startswith("<promise>BLOCKED</promise>") and ("missing" in decision_md.lower() or "invalid" in decision_md.lower()), decision_md or "<empty md>"),
        expectation("Does not proceed with routing or looping.", result.get("target_task_id") is None and result.get("routing_decision") is None and result.get("next_action") == "stop", str(result)),
    ]


def eval_blocked(result: dict, decision_md: str) -> list[dict]:
    text = decision_md.lower()
    return [
        expectation("Stops blocked without selecting or routing work.", result.get("status") == "blocked" and result.get("next_action") == "stop" and result.get("target_task_id") is None and result.get("routing_decision") is None, str(result)),
        expectation("Reports actionable blocker and does not retry.", decision_md.startswith("<promise>BLOCKED</promise>") and "unavailable" in text and "restore" in text and any(phrase in text for phrase in ("without retry", "halt until", "do not retry", "stop until")), decision_md),
    ]


def eval_dispatch(result: dict, decision_md: str) -> list[dict]:
    text = normalize(decision_md)
    return [
        expectation("Dispatches fresh worker without task selection.", result.get("status") == "looping" and result.get("target_task_id") is None and "fresh" in text and "prd-ralph" in text, str(result) + decision_md),
        expectation("Forwards explicit inputs and user limits.", all(term in text for term in ("prd_file=tasks.json", "progress_file=audit.txt", "commit=false", "docs-only", "owner approval")), decision_md),
        expectation("Remains blind to manifest and progress.", "do not read manifest or progress" in text, decision_md),
    ]


def grade_expectations(eval_id: int, run_dir: Path) -> list[dict]:
    result = read_json(run_dir / "outputs" / "decision.json")
    decision_md = read_text(run_dir / "outputs" / "decision.md")
    if not result:
        return [expectation("decision.json exists and is valid JSON.", False, "missing or invalid outputs/decision.json")]
    scenarios = {0: eval_zero, 1: eval_one, 2: eval_two, 3: eval_blocked, 4: eval_dispatch}
    scenario = scenarios.get(eval_id) if type(eval_id) is int else None
    if scenario is None:
        return [expectation(f"Unknown eval id {eval_id}.", False, f"Unsupported eval_id={eval_id}")]
    status, action, routing = (result.get(key) for key in ("status", "next_action", "routing_decision"))
    fields_present = all(key in result for key in ("status", "next_action", "target_task_id", "routing_decision"))
    consistent = fields_present and result.get("target_task_id") is None and (
        (status in ("complete", "blocked") and action == "stop" and routing is None)
        or (status == "looping" and isinstance(action, str) and bool(action.strip())
            and action.strip().lower() != "stop" and isinstance(routing, str) and bool(routing.strip()))
    )
    return [expectation("Decision fields are complete and consistent with status.", consistent, str(result))] + scenario(result, decision_md)


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
