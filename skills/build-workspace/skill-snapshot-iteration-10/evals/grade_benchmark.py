#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from typing import Dict, List


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


def normalize_text(text: str) -> str:
    normalized = text.lower()
    replacements = {
        "`": "",
        "**": "",
        "→": " to ",
        "≤": " <= ",
        "≥": " >= ",
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return " ".join(normalized.split())


def has_any(text: str, phrases: List[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def has_all(text: str, phrases: List[str]) -> bool:
    return all(phrase in text for phrase in phrases)


def grade(eval_name: str, response_text: str) -> List[Dict]:
    text = normalize_text(response_text)

    if eval_name == "dispatch-clear-task-early":
        return [
            {
                "text": "Says the manager should dispatch once the task is clear enough, rather than pre-reading lots of files first.",
                "passed": has_any(text, ["dispatch immediately", "dispatch right away", "dispatch as soon as", "dispatch quickly", "dispatch now", "ready to dispatch now", "send the implementer", "launch the implementer"]) and not has_any(text, ["read a stack of files first", "pre-read the codebase first", "study the codebase before dispatch"]),
                "evidence": "Response tells the manager to dispatch promptly once the task is clear." if has_any(text, ["dispatch immediately", "dispatch right away", "dispatch as soon as", "dispatch quickly", "dispatch now", "ready to dispatch now", "send the implementer", "launch the implementer"]) and not has_any(text, ["read a stack of files first", "pre-read the codebase first", "study the codebase before dispatch"]) else "Response does not clearly prioritize immediate dispatch over manager-side exploration."
            },
            {
                "text": "Defines a lean handoff that includes task text, success criteria, known constraints or commands, and only already-known file hints.",
                "passed": has_all(text, ["task", "criteria"]) and has_any(text, ["constraint", "command", "validation command"]) and has_any(text, ["already-known file", "known file", "file hint", "named file"]),
                "evidence": "Response describes a lean handoff with task, criteria, constraints/commands, and already-known file hints." if has_all(text, ["task", "criteria"]) and has_any(text, ["constraint", "command", "validation command"]) and has_any(text, ["already-known file", "known file", "file hint", "named file"]) else "Response does not describe the expected lean handoff contents."
            },
            {
                "text": "States that discovery, pattern lookup, and first-pass design belong to the implementer.",
                "passed": (has_any(text, ["implementer owns discovery", "implementer handles discovery", "implementer owns repo discovery", "repo discovery"]) or has_any(text, ["must stay with the implementer", "stays with the implementer", "what stays with the implementer"])) and has_any(text, ["pattern lookup", "find patterns", "patterns"]) and has_any(text, ["first-pass design", "first pass design", "initial design", "first approach"]),
                "evidence": "Response keeps discovery, pattern lookup, and first-pass design with the implementer." if (has_any(text, ["implementer owns discovery", "implementer handles discovery", "implementer owns repo discovery", "repo discovery"]) or has_any(text, ["must stay with the implementer", "stays with the implementer", "what stays with the implementer"])) and has_any(text, ["pattern lookup", "find patterns", "patterns"]) and has_any(text, ["first-pass design", "first pass design", "initial design", "first approach"]) else "Response does not clearly keep discovery, patterns, and first-pass design with the implementer."
            },
            {
                "text": "Explicitly says the manager should not draft the solution or likely patches before dispatch.",
                "passed": has_any(text, ["do not draft the solution", "should not draft the solution", "do not sketch likely patches", "should not sketch likely patches", "do not pre-solve", "should not pre-solve", "draft designs", "sketch patches", "pre-solved design"]) or (has_any(text, ["sketch likely patches", "sketch patches", "design the pagination approach", "draft the pagination design"]) and has_any(text, ["do not", "do **not**", "should not"])),
                "evidence": "Response explicitly forbids manager-side solution drafting before dispatch." if has_any(text, ["do not draft the solution", "should not draft the solution", "do not sketch likely patches", "should not sketch likely patches", "do not pre-solve", "should not pre-solve", "draft designs", "sketch patches", "pre-solved design"]) or (has_any(text, ["sketch likely patches", "sketch patches", "design the pagination approach", "draft the pagination design"]) and has_any(text, ["do not", "do **not**", "should not"])) else "Response never explicitly forbids manager-side solution drafting before dispatch."
            },
        ]

    if eval_name == "invalid-needs-context-for-discovery":
        return [
            {
                "text": "States that ordinary repo exploration is not a valid reason for NEEDS_CONTEXT.",
                "passed": has_any(text, ["not a valid needs_context", "not valid needs_context", "needs_context is not for ordinary", "needs_context is not for routine", "ordinary repo exploration is not", "routine exploration is not", "routine repo exploration is the implementer's job", "ordinary repo exploration is implementer work", "needs_context rejected", "is not a valid `needs_context`", "is **not** a valid `needs_context`"]),
                "evidence": "Response explicitly limits NEEDS_CONTEXT away from routine exploration." if has_any(text, ["not a valid needs_context", "not valid needs_context", "needs_context is not for ordinary", "needs_context is not for routine", "ordinary repo exploration is not", "routine exploration is not", "routine repo exploration is the implementer's job", "ordinary repo exploration is implementer work", "needs_context rejected", "is not a valid `needs_context`", "is **not** a valid `needs_context`"]) else "Response does not explicitly say that ordinary exploration is not a valid NEEDS_CONTEXT reason."
            },
            {
                "text": "Keeps file discovery and pattern lookup assigned to the implementer.",
                "passed": (has_any(text, ["implementer should explore", "implementer should read the relevant files", "implementer should discover", "push exploration back to the implementer", "please explore the repo", "explore the repo and re-report"]) and has_any(text, ["pattern", "patterns"])) or has_any(text, ["pattern lookup stay with the implementer", "pattern lookup is implementer work", "ordinary repo discovery, pattern lookup, and first-pass design belong to the implementer", "repo discovery, pattern lookup, and first-pass design belong to the implementer", "part of your role"]),
                "evidence": "Response pushes file discovery and pattern lookup back to the implementer." if (has_any(text, ["implementer should explore", "implementer should read the relevant files", "implementer should discover", "push exploration back to the implementer", "please explore the repo", "explore the repo and re-report"]) and has_any(text, ["pattern", "patterns"])) or has_any(text, ["pattern lookup stay with the implementer", "pattern lookup is implementer work", "ordinary repo discovery, pattern lookup, and first-pass design belong to the implementer", "repo discovery, pattern lookup, and first-pass design belong to the implementer", "part of your role"]) else "Response does not clearly keep discovery and pattern lookup with the implementer."
            },
            {
                "text": "Does not tell the manager to pre-read the codebase or hand over a solution.",
                "passed": has_any(text, ["must not pre-read", "should not pre-read", "not going to read the repo", "not do the exploration", "not pre-read files", "not read the repo or hand you the solution", "not going to read the repo or hand you the solution"]) or not has_any(text, ["manager should read the relevant files", "manager should explore the repo", "hand over the solution", "draft the solution for them"]),
                "evidence": "Response avoids telling the manager to pre-read files or provide the solution." if has_any(text, ["must not pre-read", "should not pre-read", "not going to read the repo", "not do the exploration", "not pre-read files", "not read the repo or hand you the solution", "not going to read the repo or hand you the solution"]) or not has_any(text, ["manager should read the relevant files", "manager should explore the repo", "hand over the solution", "draft the solution for them"]) else "Response incorrectly tells the manager to explore or provide the solution."
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
                "passed": has_any(text, ["conflicts with the plan", "plan conflict", "task conflicts", "not clear enough to dispatch", "do not dispatch yet", "plan/task contradiction", "task/plan contradiction", "plan and task contradict", "mismatch between the plan and task", "plan/task conflict"]),
                "evidence": "Response identifies the plan/task conflict and stops dispatch." if has_any(text, ["conflicts with the plan", "plan conflict", "task conflicts", "not clear enough to dispatch", "do not dispatch yet", "plan/task contradiction", "task/plan contradiction", "plan and task contradict", "mismatch between the plan and task", "plan/task conflict"]) else "Response does not clearly identify the plan/task conflict before dispatch."
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
                "passed": has_any(text, ["read the concerns before", "review the concerns before", "do not update tracking until you read the concerns", "read the implementer", "triage the concerns"]) and has_any(text, ["do not update tracking yet", "before updating tracking", "before marking the task done"]),
                "evidence": "Response says the concerns must be read before tracking updates." if has_any(text, ["read the concerns before", "review the concerns before", "do not update tracking until you read the concerns", "read the implementer", "triage the concerns"]) and has_any(text, ["do not update tracking yet", "before updating tracking", "before marking the task done"]) else "Response does not clearly require reading the concerns before updating tracking."
            },
            {
                "text": "Treats correctness or scope concerns as something to address before marking the task done.",
                "passed": has_any(text, ["scope concern", "correctness concern", "before marking it done", "before marking the task done", "before updating tracking", "touch correctness or scope", "address them first"]),
                "evidence": "Response treats scope/correctness concerns as unresolved work." if has_any(text, ["scope concern", "correctness concern", "before marking it done", "before marking the task done", "before updating tracking", "touch correctness or scope", "address them first"]) else "Response does not clearly treat scope/correctness concerns as unresolved work."
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
                "text": "Runs the per-task tracking update for the finished task immediately.",
                "passed": has_any(text, ["update the plan and todo tracker", "update tracking for task a", "record the verification", "mark task a done", "mark the task done now", "task-complete tracking update"]),
                "evidence": "Response updates tracking immediately for the finished task." if has_any(text, ["update the plan and todo tracker", "update tracking for task a", "record the verification", "mark task a done", "mark the task done now", "task-complete tracking update"]) else "Response does not clearly perform the per-task tracking update when the implementer returns DONE."
            },
            {
                "text": "Keeps the manager moving to the remaining implementer work in the current wave.",
                "passed": has_any(text, ["dispatch task b", "dispatch the remaining task", "keep dispatching implementers", "continue with the next task in the wave", "remaining implementer work", "finish the rest of the wave"]),
                "evidence": "Response keeps the wave moving to the remaining implementer work." if has_any(text, ["dispatch task b", "dispatch the remaining task", "keep dispatching implementers", "continue with the next task in the wave", "remaining implementer work", "finish the rest of the wave"]) else "Response does not clearly continue the current wave after the finished task."
            },
            {
                "text": "Explicitly waits until every task in the current wave is implemented and marked done before starting code-simplifier.",
                "passed": has_any(text, ["do not start code-simplifier yet", "don't launch code-simplifier yet", "wait until every task in the current wave is implemented and marked done", "only after all tasks in the wave are done", "after every task in the wave is done", "code-simplifier is a post-wave step"]),
                "evidence": "Response waits until the whole wave is done before code-simplifier." if has_any(text, ["do not start code-simplifier yet", "don't launch code-simplifier yet", "wait until every task in the current wave is implemented and marked done", "only after all tasks in the wave are done", "after every task in the wave is done", "code-simplifier is a post-wave step"]) else "Response does not clearly delay code-simplifier until the whole wave is implemented and marked done."
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
                "passed": has_any(text, ["bash -n", "shell check", "shell validation", "py_compile", "python checks", "python validation", "shellcheck", "pytest", "stack-specific validators", "run grade_benchmark", "shell → shell checks", "python → python checks"]),
                "evidence": "Response picks shell/Python-style checks instead of generic frontend commands." if has_any(text, ["bash -n", "shell check", "shell validation", "py_compile", "python checks", "python validation", "shellcheck", "pytest", "stack-specific validators", "run grade_benchmark", "shell → shell checks", "python → python checks"]) else "Response does not clearly choose stack-matching shell/Python checks."
            },
            {
                "text": "Keeps validation ownership with the implementer.",
                "passed": has_any(text, ["implementer should choose", "implementer owns verification", "implementer owns validation", "implementer should run the matching checks", "implementer verification selection", "keep verification ownership with the implementer", "implementer owns discovery, chooses matching validators", "chooses matching validators", "must record verification results"]),
                "evidence": "Response keeps verification ownership with the implementer." if has_any(text, ["implementer should choose", "implementer owns verification", "implementer owns validation", "implementer should run the matching checks", "implementer verification selection", "keep verification ownership with the implementer", "implementer owns discovery, chooses matching validators", "chooses matching validators", "must record verification results"]) else "Response does not clearly keep validation ownership with the implementer."
            },
        ]

    if eval_name == "code-simplifier-concerns-before-review":
        return [
            {
                "text": "Says the manager must read the code-simplifier's concerns before continuing to code-reviewer.",
                "passed": has_any(text, ["read the concerns before code-reviewer", "review the concerns before code-reviewer", "before continuing to code-reviewer", "before proceeding to code-reviewer", "read the simplifier", "do not proceed to code-reviewer", "stop the pipeline before code review", "before code review", "concern must be read"]),
                "evidence": "Response requires reading simplifier concerns before code-reviewer." if has_any(text, ["read the concerns before code-reviewer", "review the concerns before code-reviewer", "before continuing to code-reviewer", "before proceeding to code-reviewer", "read the simplifier", "do not proceed to code-reviewer", "stop the pipeline before code review", "before code review", "concern must be read"]) else "Response does not clearly require reading simplifier concerns before code-reviewer."
            },
            {
                "text": "Treats correctness or scope concerns as unresolved work that must be addressed before continuing.",
                "passed": has_any(text, ["scope concern", "correctness concern", "unresolved work", "address them first", "before continuing"]),
                "evidence": "Response treats simplifier concerns as unresolved work." if has_any(text, ["scope concern", "correctness concern", "unresolved work", "address them first", "before continuing"]) else "Response does not clearly treat correctness/scope concerns as unresolved work."
            },
            {
                "text": "Reopens any affected task that was already marked done before re-dispatching the fix.",
                "passed": has_any(text, ["reopen the task", "reopen any affected done task", "reopen the affected task", "reopen the already-done task", "reopen the done task"]),
                "evidence": "Response reopens the affected done task before routing the fix." if has_any(text, ["reopen the task", "reopen any affected done task", "reopen the affected task", "reopen the already-done task", "reopen the done task"]) else "Response does not clearly reopen an affected done task before re-dispatch."
            },
            {
                "text": "Allows re-dispatching the subagent that should own the fix instead of having the manager patch it manually.",
                "passed": has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should patch it directly", "fix it yourself as manager"]),
                "evidence": "Response routes the fix to the owning subagent." if has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should patch it directly", "fix it yourself as manager"]) else "Response does not clearly route the fix back to an owning subagent."
            },
            {
                "text": "Does not continue with stale tracking or proceed straight to code-reviewer.",
                "passed": (has_any(text, ["do not proceed to code-reviewer", "before code review", "stop the pipeline", "tracking cannot stay stale", "do not leave tracking stale", "re-sync tracking after the fix"]) or has_any(text, ["reopen"])) and not has_any(text, ["continue straight to code-reviewer", "proceed to code-reviewer now"]),
                "evidence": "Response stops the flow until tracking and the fix are handled." if (has_any(text, ["do not proceed to code-reviewer", "before code review", "stop the pipeline", "tracking cannot stay stale", "do not leave tracking stale", "re-sync tracking after the fix"]) or has_any(text, ["reopen"])) and not has_any(text, ["continue straight to code-reviewer", "proceed to code-reviewer now"]) else "Response does not clearly stop the flow before code-reviewer or keep tracking current."
            },
        ]

    if eval_name == "code-review-findings-block-tracking":
        return [
            {
                "text": "Says the manager must address code-review findings before ending the wave.",
                "passed": has_any(text, ["address findings before ending the wave", "before ending the build wave", "before finishing the wave", "before the final tracking sync", "before closing the wave"]),
                "evidence": "Response blocks wave completion on reviewer findings." if has_any(text, ["address findings before ending the wave", "before ending the build wave", "before finishing the wave", "before the final tracking sync", "before closing the wave"]) else "Response does not clearly block wave completion on reviewer findings."
            },
            {
                "text": "Reopens any affected task that was already marked done before routing the fix.",
                "passed": has_any(text, ["reopen the task", "reopen any affected done task", "reopen the affected task", "reopen the already-done task", "reopen the done task"]),
                "evidence": "Response reopens the affected done task before routing the fix." if has_any(text, ["reopen the task", "reopen any affected done task", "reopen the affected task", "reopen the already-done task", "reopen the done task"]) else "Response does not clearly reopen an affected done task before routing the fix."
            },
            {
                "text": "Routes the fix to the subagent that should own it instead of having the manager do the repair inline.",
                "passed": has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should fix it directly", "repair it inline yourself"]),
                "evidence": "Response routes review findings to an owning subagent." if has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should fix it directly", "repair it inline yourself"]) else "Response does not clearly route review findings to an owning subagent."
            },
            {
                "text": "Re-syncs tracking only after the final reviewer comes back `DONE`.",
                "passed": has_any(text, ["re-sync tracking after the final reviewer returns done", "after the final reviewer comes back done", "after every reviewer returns done", "only after the final code-reviewer returns done", "final tracking sync after the reviewer returns done"]),
                "evidence": "Response waits for the reviewer wave to reach DONE before the final tracking sync." if has_any(text, ["re-sync tracking after the final reviewer returns done", "after the final reviewer comes back done", "after every reviewer returns done", "only after the final code-reviewer returns done", "final tracking sync after the reviewer returns done"]) else "Response does not clearly wait for reviewer DONE before the final tracking sync."
            },
        ]

    if eval_name == "code-reviewer-handoff-includes-uncommitted-files":
        return [
            {
                "text": "Builds one deduped review scope from the touched files plus the filtered uncommitted files.",
                "passed": (has_any(text, ["deduped review scope", "dedupe the review scope", "review_scope_files", "single review scope", "single file list", "one review scope"]) or has_any(text, ["union of the touched files", "union of touched files"])) and has_any(text, ["touched files", "files the implementer touched", "files changed"]) and has_any(text, ["uncommitted files", "git status --porcelain", "notes.txt"]),
                "evidence": "Response builds one controller-owned review scope from touched plus filtered uncommitted files." if (has_any(text, ["deduped review scope", "dedupe the review scope", "review_scope_files", "single review scope", "single file list", "one review scope"]) or has_any(text, ["union of the touched files", "union of touched files"])) and has_any(text, ["touched files", "files the implementer touched", "files changed"]) and has_any(text, ["uncommitted files", "git status --porcelain", "notes.txt"]) else "Response does not clearly build one deduped review scope from touched and filtered uncommitted files."
            },
            {
                "text": "Excludes deleted files and `.gitignore` files from that deduped review scope.",
                "passed": (has_any(text, ["excluding deleted files", "exclude deleted files", "without deleted files"]) or has_any(text, ["scratch.tmp", "deleted"])) and (has_any(text, ["excluding .gitignore files", "exclude .gitignore files", "without .gitignore files"]) or has_any(text, [".gitignore", "gitignore file"])),
                "evidence": "Response excludes deleted files and `.gitignore` from the review scope." if (has_any(text, ["excluding deleted files", "exclude deleted files", "without deleted files"]) or has_any(text, ["scratch.tmp", "deleted"])) and (has_any(text, ["excluding .gitignore files", "exclude .gitignore files", "without .gitignore files"]) or has_any(text, [".gitignore", "gitignore file"])) else "Response does not clearly exclude deleted files and `.gitignore` from the review scope."
            },
            {
                "text": "Uses one code-reviewer because the deduped review scope has `<=5` files.",
                "passed": has_any(text, ["one code-reviewer", "single code-reviewer", "1 code-reviewer", "one reviewer", "single reviewer"]) and has_any(text, ["<=5 files", "≤5 files", "five files or fewer", "small scope", "only three files", "3 files"]),
                "evidence": "Response uses one reviewer and ties it to the small-scope rule." if has_any(text, ["one code-reviewer", "single code-reviewer", "1 code-reviewer", "one reviewer", "single reviewer"]) and has_any(text, ["<=5 files", "≤5 files", "five files or fewer", "small scope", "only three files", "3 files"]) else "Response does not clearly use one reviewer because the deduped scope is small."
            },
            {
                "text": "Passes the deduped review scope and current verification context to that reviewer before the final tracking sync.",
                "passed": has_any(text, ["review scope", "review_scope_files", "single file list", "those three files"]) and has_any(text, ["current verification context", "verification context", "validation context", "verification results"]) and has_any(text, ["before the final tracking sync", "before syncing tracking", "before the final tracker sync", "wait for the reviewer to return done before the final tracking sync"]),
                "evidence": "Response passes review scope plus verification context forward before the final tracking sync." if has_any(text, ["review scope", "review_scope_files", "single file list", "those three files"]) and has_any(text, ["current verification context", "verification context", "validation context", "verification results"]) and has_any(text, ["before the final tracking sync", "before syncing tracking", "before the final tracker sync", "wait for the reviewer to return done before the final tracking sync"]) else "Response does not clearly pass the deduped review scope and verification context forward before the final tracking sync."
            },
        ]

    if eval_name == "final-done-updates-tracking-without-commit":
        return [
            {
                "text": "Syncs the plan and todo tracker to the final reviewed state.",
                "passed": has_any(text, ["final reviewed state", "sync the plan and todo tracker", "sync tracking to the final reviewed state", "final tracking sync", "sync the tracker to the final state"]),
                "evidence": "Response syncs tracking to the final reviewed state." if has_any(text, ["final reviewed state", "sync the plan and todo tracker", "sync tracking to the final reviewed state", "final tracking sync", "sync the tracker to the final state"]) else "Response does not clearly sync the plan and todo tracker to the final reviewed state."
            },
            {
                "text": "Records any additional verification actually performed during review.",
                "passed": has_any(text, ["additional verification", "verification during review", "record any additional verification", "record the extra verification", "record further verification"]),
                "evidence": "Response records review-time verification." if has_any(text, ["additional verification", "verification during review", "record any additional verification", "record the extra verification", "record further verification"]) else "Response does not clearly record any additional verification performed during review."
            },
            {
                "text": "Does not create, amend, push, or otherwise publish a commit, PR, or tag.",
                "passed": has_any(text, ["do not commit", "must not commit", "do not create a commit", "do not push", "do not open the pr", "do not create or publish", "must not publish", "no commit, pr, or tag", "leave it unpublished"]),
                "evidence": "Response forbids publishing work." if has_any(text, ["do not commit", "must not commit", "do not create a commit", "do not push", "do not open the pr", "do not create or publish", "must not publish", "no commit, pr, or tag", "leave it unpublished"]) else "Response does not clearly forbid creating or publishing a commit, PR, or tag."
            },
            {
                "text": "Leaves the changes uncommitted and local.",
                "passed": has_any(text, ["leave the working tree dirty", "leave the changes uncommitted", "leave the changes local", "keep it local", "leave it dirty and local", "uncommitted and local"]),
                "evidence": "Response leaves the work dirty and local." if has_any(text, ["leave the working tree dirty", "leave the changes uncommitted", "leave the changes local", "keep it local", "leave it dirty and local", "uncommitted and local"]) else "Response does not clearly say to leave the work uncommitted and local."
            },
        ]

    if eval_name == "large-review-scope-partitions-code-reviewers":
        return [
            {
                "text": "Uses multiple parallel code-reviewers because the deduped review scope has `>5` files.",
                "passed": has_any(text, ["multiple parallel code-reviewers", "launch multiple reviewers in parallel", "parallel code-reviewers", "launch the reviewers in parallel", "split across reviewers", "two parallel code-reviewers", "2 parallel code-reviewers"]) and has_any(text, [">5 files", "more than five files", "8 files", "eight files"]),
                "evidence": "Response uses a parallel reviewer wave and ties that choice to the large review scope." if has_any(text, ["multiple parallel code-reviewers", "launch multiple reviewers in parallel", "parallel code-reviewers", "launch the reviewers in parallel", "split across reviewers", "two parallel code-reviewers", "2 parallel code-reviewers"]) and has_any(text, [">5 files", "more than five files", "8 files", "eight files"]) else "Response does not clearly use parallel reviewers because the review scope is larger than five files."
            },
            {
                "text": "Partitions the files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one reviewer scope.",
                "passed": has_any(text, ["non-overlapping", "exactly one reviewer scope", "each file appears in exactly one reviewer scope", "no file appears in more than one scope"]) and has_any(text, ["module", "directory", "logical area", "auth", "billing", "group"]),
                "evidence": "Response partitions the review into coherent non-overlapping scopes." if has_any(text, ["non-overlapping", "exactly one reviewer scope", "each file appears in exactly one reviewer scope", "no file appears in more than one scope"]) and has_any(text, ["module", "directory", "logical area", "auth", "billing", "group"]) else "Response does not clearly partition the large review scope into non-overlapping logical groups."
            },
            {
                "text": "Keeps the reviewer file lists manager-authored instead of telling reviewers to recompute or narrow scope.",
                "passed": has_any(text, ["manager owns the partitions", "manager-authored", "controller-authored", "give each reviewer the exact file list", "reviewers do not recompute", "do not recompute scope", "do not narrow scope"]),
                "evidence": "Response keeps scope ownership with the manager instead of the reviewers." if has_any(text, ["manager owns the partitions", "manager-authored", "controller-authored", "give each reviewer the exact file list", "reviewers do not recompute", "do not recompute scope", "do not narrow scope"]) else "Response does not clearly keep reviewer file lists manager-authored."
            },
            {
                "text": "Waits for every reviewer to return `DONE` before the final tracking sync.",
                "passed": has_any(text, ["every reviewer", "all reviewers", "all reviewer partitions", "each reviewer partition", "both reviewers"]) and has_any(text, ["return done", "returns done", "before the final tracking sync", "only then sync tracking", "tracking stays untouched"]),
                "evidence": "Response waits for the whole reviewer wave to finish before the final tracking sync." if has_any(text, ["every reviewer", "all reviewers", "all reviewer partitions", "each reviewer partition", "both reviewers"]) and has_any(text, ["return done", "returns done", "before the final tracking sync", "only then sync tracking", "tracking stays untouched"]) else "Response does not clearly wait for every reviewer to return DONE before the final tracking sync."
            },
        ]

    if eval_name == "large-review-scope-partitions-code-simplifiers":
        return [
            {
                "text": "Uses multiple parallel code-simplifiers because the deduped review scope has `>5` files.",
                "passed": has_any(text, ["multiple parallel code-simplifiers", "launch multiple simplifiers in parallel", "parallel code-simplifiers", "launch the simplifiers in parallel", "split across simplifiers", "2 code-simplifier subagents in parallel", "dispatch parallel code-simplifier subagents"]) and has_any(text, [">5 files", "more than five files", "8 files", "eight files"]),
                "evidence": "Response uses a parallel simplifier wave and ties that choice to the large review scope." if has_any(text, ["multiple parallel code-simplifiers", "launch multiple simplifiers in parallel", "parallel code-simplifiers", "launch the simplifiers in parallel", "split across simplifiers", "2 code-simplifier subagents in parallel", "dispatch parallel code-simplifier subagents"]) and has_any(text, [">5 files", "more than five files", "8 files", "eight files"]) else "Response does not clearly use parallel simplifiers because the review scope is larger than five files."
            },
            {
                "text": "Partitions the files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one simplifier scope.",
                "passed": has_any(text, ["non-overlapping", "exactly one simplifier scope", "each file appears in exactly one simplifier scope", "no file appears in more than one scope"]) and has_any(text, ["module", "directory", "logical area", "auth", "billing", "group"]),
                "evidence": "Response partitions the simplifier wave into coherent non-overlapping scopes." if has_any(text, ["non-overlapping", "exactly one simplifier scope", "each file appears in exactly one simplifier scope", "no file appears in more than one scope"]) and has_any(text, ["module", "directory", "logical area", "auth", "billing", "group"]) else "Response does not clearly partition the large simplifier scope into non-overlapping logical groups."
            },
            {
                "text": "Keeps the simplifier file lists manager-authored instead of telling simplifiers to recompute or narrow scope.",
                "passed": has_any(text, ["manager owns the partitions", "manager-authored", "controller-authored", "give each simplifier the exact file list", "simplifiers do not recompute", "do not recompute scope", "do not narrow scope", "manager materialized", "pass only that exact stable file list", "manager-owned"]),
                "evidence": "Response keeps scope ownership with the manager instead of the simplifiers." if has_any(text, ["manager owns the partitions", "manager-authored", "controller-authored", "give each simplifier the exact file list", "simplifiers do not recompute", "do not recompute scope", "do not narrow scope", "manager materialized", "pass only that exact stable file list", "manager-owned"]) else "Response does not clearly keep simplifier file lists manager-authored."
            },
            {
                "text": "Waits for every code-simplifier to return `DONE` before launching code-reviewers or updating tracking.",
                "passed": has_any(text, ["every code-simplifier", "all code-simplifiers", "all simplifier partitions", "each simplifier partition", "both simplifiers"]) and has_any(text, ["return done", "returns done", "before launching code-reviewers", "before code-review begins", "before updating tracking", "begin code-review only after", "after every simplifier returns done"]),
                "evidence": "Response waits for the whole simplifier wave to finish before moving downstream." if has_any(text, ["every code-simplifier", "all code-simplifiers", "all simplifier partitions", "each simplifier partition", "both simplifiers"]) and has_any(text, ["return done", "returns done", "before launching code-reviewers", "before code-review begins", "before updating tracking", "begin code-review only after", "after every simplifier returns done"]) else "Response does not clearly wait for every simplifier to return DONE before moving downstream."
            },
        ]

    if eval_name == "direct-commit-request-is-refused":
        return [
            {
                "text": "States that the build skill's no-commit override still applies even when asked directly.",
                "passed": has_any(text, ["build skill override", "no-commit override", "still applies", "even if you asked", "cannot override the build rule", "commit override still applies"]),
                "evidence": "Response keeps the override active even under a direct request." if has_any(text, ["build skill override", "no-commit override", "still applies", "even if you asked", "cannot override the build rule", "commit override still applies"]) else "Response does not clearly say the build skill override still applies."
            },
            {
                "text": "Refuses to create, amend, push, or otherwise publish a commit, PR, or tag.",
                "passed": has_any(text, ["do not commit", "will not commit", "do not push", "will not push", "do not open the pr", "will not open the pr", "do not publish", "no commit, pr, or tag"]),
                "evidence": "Response refuses to publish the work." if has_any(text, ["do not commit", "will not commit", "do not push", "will not push", "do not open the pr", "will not open the pr", "do not publish", "no commit, pr, or tag"]) else "Response does not clearly refuse to create or publish the work."
            },
            {
                "text": "Leaves the working tree dirty and local for the human to review manually.",
                "passed": has_any(text, ["leave the working tree dirty", "leave it local", "leave the changes uncommitted", "human can review manually", "for the human to review manually"]),
                "evidence": "Response leaves the work dirty and local for manual review." if has_any(text, ["leave the working tree dirty", "leave it local", "leave the changes uncommitted", "human can review manually", "for the human to review manually"]) else "Response does not clearly leave the work dirty and local for the human."
            },
            {
                "text": "Does not offer a workaround that still publishes the changes.",
                "passed": not has_any(text, ["i can push it for you", "i can open the pr", "i can tag it", "i can publish it another way", "i can hand it to a git skill to commit"]),
                "evidence": "Response does not propose an alternate way to publish the work." if not has_any(text, ["i can push it for you", "i can open the pr", "i can tag it", "i can publish it another way", "i can hand it to a git skill to commit"]) else "Response offers a workaround that still publishes the work."
            },
        ]

    raise ValueError(f"Unknown eval name: {eval_name}")


def write_grading(run_dir: Path) -> None:
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


def iter_run_dirs(path: Path) -> list[Path]:
    if (path / "outputs" / "response.md").exists():
        return [path]

    eval_dirs = sorted(path.glob("eval-*"))
    if not eval_dirs:
        return []

    run_dirs: list[Path] = []
    for eval_dir in eval_dirs:
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            if (run_dir / "outputs" / "response.md").exists():
                run_dirs.append(run_dir)
    return run_dirs


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py <run-dir-or-iteration-dir>", file=sys.stderr)
        return 2

    target = Path(sys.argv[1]).resolve()
    run_dirs = iter_run_dirs(target)
    if not run_dirs:
        print(f"No benchmark run directories found under {target}", file=sys.stderr)
        return 2

    for run_dir in run_dirs:
        write_grading(run_dir)
        print(f"Graded {run_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
