#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
    except json.JSONDecodeError:
        return {}


def has_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def has_all(text: str, phrases: list[str]) -> bool:
    return all(phrase in text for phrase in phrases)


def grade(eval_name: str, response_text: str) -> list[dict]:
    text = response_text.lower()

    if eval_name == "dispatch-clear-task-early":
        return [
            {
                "text": "Says the manager should dispatch once the task is clear enough, rather than pre-reading lots of files first.",
                "passed": has_any(text, ["dispatch immediately", "dispatch right away", "dispatch as soon as", "send the implementer", "launch the implementer"]) and not has_any(text, ["read a stack of files first", "pre-read the codebase first", "study the codebase before dispatch"]),
                "evidence": "Response tells the manager to dispatch promptly once the task is clear." if has_any(text, ["dispatch immediately", "dispatch right away", "dispatch as soon as", "send the implementer", "launch the implementer"]) and not has_any(text, ["read a stack of files first", "pre-read the codebase first", "study the codebase before dispatch"]) else "Response does not clearly prioritize immediate dispatch over manager-side exploration."
            },
            {
                "text": "Defines a lean handoff that includes task text, success criteria, known constraints or commands, and only already-known file hints.",
                "passed": has_all(text, ["task", "criteria"]) and has_any(text, ["constraint", "command", "validation command"]) and has_any(text, ["already-known file", "known file", "file hint", "named file"]),
                "evidence": "Response describes a lean handoff with task, criteria, constraints/commands, and already-known file hints." if has_all(text, ["task", "criteria"]) and has_any(text, ["constraint", "command", "validation command"]) and has_any(text, ["already-known file", "known file", "file hint", "named file"]) else "Response does not describe the expected lean handoff contents."
            },
            {
                "text": "States that discovery, pattern lookup, and first-pass design belong to the implementer.",
                "passed": has_any(text, ["implementer owns discovery", "implementer handles discovery", "implementer owns repo discovery"]) and has_any(text, ["pattern lookup", "find patterns"]) and has_any(text, ["first-pass design", "first pass design", "initial design", "first approach"]),
                "evidence": "Response keeps discovery, pattern lookup, and first-pass design with the implementer." if has_any(text, ["implementer owns discovery", "implementer handles discovery", "implementer owns repo discovery"]) and has_any(text, ["pattern lookup", "find patterns"]) and has_any(text, ["first-pass design", "first pass design", "initial design", "first approach"]) else "Response does not clearly keep discovery, patterns, and first-pass design with the implementer."
            },
            {
                "text": "Explicitly says the manager should not draft the solution or likely patches before dispatch.",
                "passed": has_any(text, ["do not draft the solution", "should not draft the solution", "do not sketch likely patches", "should not sketch likely patches", "do not pre-solve", "should not pre-solve"]),
                "evidence": "Response explicitly forbids manager-side solution drafting before dispatch." if has_any(text, ["do not draft the solution", "should not draft the solution", "do not sketch likely patches", "should not sketch likely patches", "do not pre-solve", "should not pre-solve"]) else "Response never explicitly forbids manager-side solution drafting before dispatch."
            },
        ]

    if eval_name == "invalid-needs-context-for-discovery":
        return [
            {
                "text": "States that ordinary repo exploration is not a valid reason for NEEDS_CONTEXT.",
                "passed": has_any(text, ["not a valid needs_context", "not valid needs_context", "needs_context is not for ordinary", "needs_context is not for routine", "ordinary repo exploration is not", "routine exploration is not"]),
                "evidence": "Response explicitly limits NEEDS_CONTEXT away from routine exploration." if has_any(text, ["not a valid needs_context", "not valid needs_context", "needs_context is not for ordinary", "needs_context is not for routine", "ordinary repo exploration is not", "routine exploration is not"]) else "Response does not explicitly say that ordinary exploration is not a valid NEEDS_CONTEXT reason."
            },
            {
                "text": "Keeps file discovery and pattern lookup assigned to the implementer.",
                "passed": has_any(text, ["implementer should explore", "implementer should read the relevant files", "implementer should discover", "push exploration back to the implementer"]) and has_any(text, ["pattern", "patterns"]),
                "evidence": "Response pushes file discovery and pattern lookup back to the implementer." if has_any(text, ["implementer should explore", "implementer should read the relevant files", "implementer should discover", "push exploration back to the implementer"]) and has_any(text, ["pattern", "patterns"]) else "Response does not clearly keep discovery and pattern lookup with the implementer."
            },
            {
                "text": "Does not tell the manager to pre-read the codebase or hand over a solution.",
                "passed": not has_any(text, ["manager should read the relevant files", "manager should explore the repo", "tell them the solution", "hand over the solution", "draft the solution for them"]),
                "evidence": "Response avoids telling the manager to pre-read files or provide the solution." if not has_any(text, ["manager should read the relevant files", "manager should explore the repo", "tell them the solution", "hand over the solution", "draft the solution for them"]) else "Response incorrectly tells the manager to explore or provide the solution."
            },
            {
                "text": "Reserves NEEDS_CONTEXT for genuinely missing requirements, constraints, or conflicting signals.",
                "passed": has_any(text, ["missing requirement", "missing requirements", "missing constraint", "missing constraints", "conflicting signal", "conflicting signals"]),
                "evidence": "Response reserves NEEDS_CONTEXT for missing requirements/constraints or conflicting signals." if has_any(text, ["missing requirement", "missing requirements", "missing constraint", "missing constraints", "conflicting signal", "conflicting signals"]) else "Response does not restate the valid reasons for NEEDS_CONTEXT."
            },
        ]

    if eval_name == "task-conflicts-with-plan":
        return [
            {
                "text": "Recognizes that the task conflicts with the plan and is not clear enough to dispatch yet.",
                "passed": has_any(text, ["conflicts with the plan", "plan conflict", "task conflicts", "not clear enough to dispatch", "do not dispatch yet"]),
                "evidence": "Response identifies the plan/task conflict and stops dispatch." if has_any(text, ["conflicts with the plan", "plan conflict", "task conflicts", "not clear enough to dispatch", "do not dispatch yet"]) else "Response does not clearly identify the plan/task conflict before dispatch."
            },
            {
                "text": "Says the manager should resolve the ambiguity or escalate to the human before implementation starts.",
                "passed": has_any(text, ["resolve the ambiguity", "resolve the conflict", "ask the human", "escalate to the human", "clarify with the human"]),
                "evidence": "Response routes the conflict to ambiguity resolution or human escalation." if has_any(text, ["resolve the ambiguity", "resolve the conflict", "ask the human", "escalate to the human", "clarify with the human"]) else "Response does not clearly route the conflict to ambiguity resolution or human escalation."
            },
            {
                "text": "Keeps the manager focused on ambiguity resolution rather than speculative implementation.",
                "passed": has_any(text, ["ambiguity", "conflict"]) and not has_any(text, ["go ahead and implement", "pick one and proceed", "start implementation anyway"]),
                "evidence": "Response keeps the manager on ambiguity resolution instead of speculative implementation." if has_any(text, ["ambiguity", "conflict"]) and not has_any(text, ["go ahead and implement", "pick one and proceed", "start implementation anyway"]) else "Response drifts into speculative implementation instead of conflict resolution."
            },
            {
                "text": "Does not silently choose one interpretation and proceed.",
                "passed": not has_any(text, ["just follow the task text", "just follow the plan", "pick whichever seems right", "choose one interpretation"]),
                "evidence": "Response avoids silently picking one interpretation." if not has_any(text, ["just follow the task text", "just follow the plan", "pick whichever seems right", "choose one interpretation"]) else "Response silently picks an interpretation instead of resolving the conflict."
            },
        ]

    if eval_name == "done-with-concerns-scope-check":
        return [
            {
                "text": "Says the manager must read the concerns before updating tracking.",
                "passed": has_any(text, ["read the concerns before", "review the concerns before", "do not update tracking until you read the concerns"]),
                "evidence": "Response says the concerns must be read before tracking updates." if has_any(text, ["read the concerns before", "review the concerns before", "do not update tracking until you read the concerns"]) else "Response does not clearly require reading the concerns before updating tracking."
            },
            {
                "text": "Treats correctness or scope concerns as something to address before marking the task done.",
                "passed": has_any(text, ["scope concern", "correctness concern", "before marking it done", "before marking the task done", "before updating tracking"]),
                "evidence": "Response treats scope/correctness concerns as unresolved work." if has_any(text, ["scope concern", "correctness concern", "before marking it done", "before marking the task done", "before updating tracking"]) else "Response does not clearly treat scope/correctness concerns as unresolved work."
            },
            {
                "text": "Allows re-dispatching another implementer if needed to resolve the concern.",
                "passed": has_any(text, ["re-dispatch", "dispatch another implementer", "send another implementer"]),
                "evidence": "Response allows another implementer pass to resolve the concern." if has_any(text, ["re-dispatch", "dispatch another implementer", "send another implementer"]) else "Response does not mention re-dispatching another implementer."
            },
            {
                "text": "Does not immediately mark the task done just because tests passed.",
                "passed": not has_any(text, ["mark it done now", "update tracking now because tests passed", "tests passed so mark done"]),
                "evidence": "Response avoids immediately marking the task done just because tests passed." if not has_any(text, ["mark it done now", "update tracking now because tests passed", "tests passed so mark done"]) else "Response incorrectly marks the task done just because tests passed."
            },
        ]

    raise ValueError(f"Unknown eval name: {eval_name}")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py <run-dir>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    metadata_path = run_dir.parent.parent / "eval_metadata.json"
    response_path = run_dir / "outputs" / "response.md"

    metadata = json.loads(metadata_path.read_text())
    response_text = read_text(response_path)
    expectations = grade(metadata["eval_name"], response_text)
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    failed = total - passed
    timing = load_timing(run_dir)

    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": len(response_text),
            "transcript_chars": 0,
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
            "overall": "No evaluator suggestions."
        }
    }

    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
