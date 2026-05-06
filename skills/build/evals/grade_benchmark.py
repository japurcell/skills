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
                "passed": has_any(text, ["conflicts with the plan", "plan conflict", "task conflicts", "not clear enough to dispatch", "do not dispatch yet", "plan/task contradiction", "task/plan contradiction", "plan and task contradict", "mismatch between the plan and task"]),
                "evidence": "Response identifies the plan/task conflict and stops dispatch." if has_any(text, ["conflicts with the plan", "plan conflict", "task conflicts", "not clear enough to dispatch", "do not dispatch yet", "plan/task contradiction", "task/plan contradiction", "plan and task contradict", "mismatch between the plan and task"]) else "Response does not clearly identify the plan/task conflict before dispatch."
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

    if eval_name == "done-dispatches-code-simplifier":
        return [
            {
                "text": "Says the manager should dispatch the code-simplifier before updating tracking.",
                "passed": has_any(text, ["dispatch the code-simplifier", "send the code-simplifier", "run the code-simplifier", "launch the code-simplifier"]) and has_any(text, ["before updating tracking", "before update tracking", "before marking it done", "before marking the task done", "do not update tracking yet", "only update tracking after"]),
                "evidence": "Response dispatches the code-simplifier before tracking updates." if has_any(text, ["dispatch the code-simplifier", "send the code-simplifier", "run the code-simplifier", "launch the code-simplifier"]) and has_any(text, ["before updating tracking", "before update tracking", "before marking it done", "before marking the task done", "do not update tracking yet", "only update tracking after"]) else "Response does not clearly route completed implementer work through the code-simplifier before tracking."
            },
            {
                "text": "Passes the files touched by the implementer to the code-simplifier.",
                "passed": has_any(text, ["files the implementer touched", "touched files", "files changed", "four files they touched"]),
                "evidence": "Response forwards the touched files to the code-simplifier." if has_any(text, ["files the implementer touched", "touched files", "files changed", "four files they touched"]) else "Response does not clearly pass the implementer's touched files to the code-simplifier."
            },
            {
                "text": "Carries forward relevant validation context or results from the implementer.",
                "passed": has_any(text, ["validation context", "validation results", "verification results", "tests they ran", "commands they ran"]),
                "evidence": "Response carries forward validation context from the implementer." if has_any(text, ["validation context", "validation results", "verification results", "tests they ran", "commands they ran"]) else "Response does not clearly mention carrying forward validation context."
            },
            {
                "text": "Does not send the main agent back into manual simplification or discovery first.",
                "passed": not has_any(text, ["manager should simplify", "simplify the code yourself", "manager should review every file first", "manager should rediscover the codebase"]),
                "evidence": "Response keeps the main agent out of manual simplification or rediscovery work." if not has_any(text, ["manager should simplify", "simplify the code yourself", "manager should review every file first", "manager should rediscover the codebase"]) else "Response sends the main agent back into manual simplification or rediscovery."
            },
        ]

    if eval_name == "weak-model-validation-selection":
        return [
            {
                "text": "Keeps the manager handoff lean instead of pre-solving or pre-reading the task.",
                "passed": has_any(text, ["lean handoff", "manager handoff", "handoff (lean)", "dispatch immediately", "do not pre-read", "do not draft the solution"]) and not has_any(text, ["manager should read the files first", "manager should pre-solve", "manager should draft the solution"]),
                "evidence": "Response keeps the manager side lean." if has_any(text, ["lean handoff", "manager handoff", "handoff (lean)", "dispatch immediately", "do not pre-read", "do not draft the solution"]) and not has_any(text, ["manager should read the files first", "manager should pre-solve", "manager should draft the solution"]) else "Response does not clearly keep the manager handoff lean."
            },
            {
                "text": "Says the implementer should infer the slice's surface or stack before choosing validation.",
                "passed": has_any(text, ["infer the slice", "infer the stack", "infer the surface", "figure out what stack", "determine the stack first", "infer stack from file types", "infer the slice/stack", "infer stack from filenames", "stack from file types"]),
                "evidence": "Response tells the implementer to infer the slice's surface/stack before choosing validation." if has_any(text, ["infer the slice", "infer the stack", "infer the surface", "figure out what stack", "determine the stack first", "infer stack from file types", "infer the slice/stack", "infer stack from filenames", "stack from file types"]) else "Response does not clearly say to infer the slice's surface or stack first."
            },
            {
                "text": "Chooses matching shell or Python checks rather than generic frontend commands.",
                "passed": has_any(text, ["bash -n", "shell check", "shell validation", "py_compile", "python checks", "python validation", "shellcheck", "pytest", "stack-specific validators", "run grade_benchmark"]) and not has_any(text, ["npm run test", "npm run build", "frontend commands by default"]),
                "evidence": "Response picks shell/Python-style checks instead of generic frontend commands." if has_any(text, ["bash -n", "shell check", "shell validation", "py_compile", "python checks", "python validation", "shellcheck", "pytest", "stack-specific validators", "run grade_benchmark"]) and not has_any(text, ["npm run test", "npm run build", "frontend commands by default"]) else "Response does not clearly choose stack-matching shell/Python checks."
            },
            {
                "text": "Keeps validation ownership with the implementer.",
                "passed": has_any(text, ["implementer should choose", "implementer owns verification", "implementer owns validation", "implementer should run the matching checks", "implementer verification selection", "keep verification ownership with the implementer"]),
                "evidence": "Response keeps verification ownership with the implementer." if has_any(text, ["implementer should choose", "implementer owns verification", "implementer owns validation", "implementer should run the matching checks", "implementer verification selection", "keep verification ownership with the implementer"]) else "Response does not clearly keep validation ownership with the implementer."
            },
        ]

    if eval_name == "code-simplifier-concerns-before-review":
        return [
            {
                "text": "Says the manager must read the code-simplifier's concerns before continuing to code-reviewer.",
                "passed": has_any(text, ["read the concerns before code-reviewer", "review the concerns before code-reviewer", "before continuing to code-reviewer", "before proceeding to code-reviewer"]),
                "evidence": "Response requires reading simplifier concerns before code-reviewer." if has_any(text, ["read the concerns before code-reviewer", "review the concerns before code-reviewer", "before continuing to code-reviewer", "before proceeding to code-reviewer"]) else "Response does not clearly require reading simplifier concerns before code-reviewer."
            },
            {
                "text": "Treats correctness or scope concerns as unresolved work that must be addressed before continuing.",
                "passed": has_any(text, ["scope concern", "correctness concern", "unresolved work", "address them first", "before continuing"]),
                "evidence": "Response treats simplifier concerns as unresolved work." if has_any(text, ["scope concern", "correctness concern", "unresolved work", "address them first", "before continuing"]) else "Response does not clearly treat correctness/scope concerns as unresolved work."
            },
            {
                "text": "Allows re-dispatching the subagent that should own the fix instead of having the manager patch it manually.",
                "passed": has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should patch it directly", "fix it yourself as manager"]),
                "evidence": "Response routes the fix to the owning subagent." if has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should patch it directly", "fix it yourself as manager"]) else "Response does not clearly route the fix back to an owning subagent."
            },
            {
                "text": "Does not update tracking yet.",
                "passed": not has_any(text, ["update tracking now", "mark it done now", "record it done now"]),
                "evidence": "Response avoids updating tracking before the concern is resolved." if not has_any(text, ["update tracking now", "mark it done now", "record it done now"]) else "Response incorrectly updates tracking before resolving the concern."
            },
        ]

    if eval_name == "code-review-findings-block-tracking":
        return [
            {
                "text": "Says the manager must address code-review findings before updating tracking.",
                "passed": has_any(text, ["address findings before update tracking", "address findings before updating tracking", "before updating tracking", "before marking the task done"]),
                "evidence": "Response blocks tracking on reviewer findings." if has_any(text, ["address findings before update tracking", "address findings before updating tracking", "before updating tracking", "before marking the task done"]) else "Response does not clearly block tracking on reviewer findings."
            },
            {
                "text": "Routes the fix to the subagent that should own it instead of having the manager do the repair inline.",
                "passed": has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should fix it directly", "repair it inline yourself"]),
                "evidence": "Response routes review findings to an owning subagent." if has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should fix it directly", "repair it inline yourself"]) else "Response does not clearly route review findings to an owning subagent."
            },
            {
                "text": "Requires the final subagent to return `DONE` before marking the task done.",
                "passed": has_any(text, ["final subagent returns done", "reviewer returns done", "after the final reviewer comes back done", "only after the final subagent returns done"]),
                "evidence": "Response requires a final DONE before marking the task done." if has_any(text, ["final subagent returns done", "reviewer returns done", "after the final reviewer comes back done", "only after the final subagent returns done"]) else "Response does not clearly require a final DONE before marking the task done."
            },
            {
                "text": "Does not ignore findings just because earlier stages already returned `DONE`.",
                "passed": not has_any(text, ["ignore the findings", "earlier done means you can update tracking", "skip the findings because implementer and simplifier returned done"]),
                "evidence": "Response does not ignore reviewer findings despite earlier DONE statuses." if not has_any(text, ["ignore the findings", "earlier done means you can update tracking", "skip the findings because implementer and simplifier returned done"]) else "Response incorrectly ignores reviewer findings because earlier stages returned DONE."
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
