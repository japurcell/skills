#!/usr/bin/env python3

import json
import re
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


def has_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def has_all(text: str, phrases: list[str]) -> bool:
    return all(phrase in text for phrase in phrases)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def has_code_or_patch(raw_text: str) -> bool:
    patterns = [
        r"```",
        r"(?m)^diff --git ",
        r"(?m)^@@ ",
        r"(?m)^\+\+\+ ",
        r"(?m)^--- ",
    ]
    return any(re.search(pattern, raw_text) for pattern in patterns)


def expectation(text: str, passed: bool, success: str, failure: str) -> dict:
    return {
        "text": text,
        "passed": passed,
        "evidence": success if passed else failure,
    }


def grade(eval_name: str, response_text: str) -> list[dict]:
    raw_text = response_text
    text = normalize_text(response_text)
    compact = word_count(raw_text)

    if eval_name == "dispatch-clear-task-early":
        dispatches_early = (
            has_any(text, [
                "dispatch immediately",
                "dispatch right away",
                "dispatch as soon as",
                "dispatch now",
                "send the implementer",
                "launch the implementer",
                "single-task wave",
                "single task wave",
                "only the setup work",
            ])
            and not has_any(text, [
                "read a stack of files first",
                "pre-read the codebase first",
                "study the codebase before dispatch",
                "read the relevant repo files",
                "inspect the relevant code and patterns",
            ])
        )
        return [
            expectation(
                "Says the manager should dispatch once the task is clear enough, rather than pre-reading lots of files first.",
                dispatches_early,
                "Response keeps the manager on setup and prompt dispatch.",
                "Response does not clearly prioritize immediate dispatch over manager-side exploration.",
            ),
            expectation(
                "Defines a lean handoff that includes task text, success criteria, known constraints or commands, and only already-known file hints.",
                has_all(text, ["task", "criteria"]) and has_any(text, ["constraint", "command", "validation command"]) and has_any(text, ["already-known file", "known file", "file hint", "named file"]),
                "Response describes the expected lean handoff contents.",
                "Response does not describe the expected lean handoff contents.",
            ),
            expectation(
                "States that discovery, pattern lookup, and first-pass design belong to the implementer.",
                has_any(text, [
                    "implementer owns discovery",
                    "implementer handles discovery",
                    "implementer owns repo discovery",
                    "must stay with the implementer",
                    "stays with the implementer",
                ]) and has_any(text, ["pattern lookup", "find patterns", "patterns"]) and has_any(text, ["first-pass design", "first pass design", "initial design", "first approach"]),
                "Response keeps discovery, pattern lookup, and first-pass design with the implementer.",
                "Response does not clearly keep discovery, patterns, and first-pass design with the implementer.",
            ),
            expectation(
                "Explicitly says the manager should not draft the solution or likely patches before dispatch.",
                has_any(text, [
                    "do not draft the solution",
                    "should not draft the solution",
                    "do not sketch likely patches",
                    "should not sketch likely patches",
                    "do not pre-solve",
                    "should not pre-solve",
                    "no repo exploration or patch drafting",
                    "no patch drafting",
                ]),
                "Response explicitly forbids manager-side solution drafting before dispatch.",
                "Response never explicitly forbids manager-side solution drafting before dispatch.",
            ),
        ]

    if eval_name == "invalid-needs-context-for-discovery":
        return [
            expectation(
                "States that ordinary repo exploration is not a valid reason for NEEDS_CONTEXT.",
                has_any(text, [
                    "not a valid needs_context",
                    "not valid needs_context",
                    "needs_context is not for ordinary",
                    "needs_context is not for routine",
                    "ordinary repo exploration is not",
                    "routine exploration is not",
                    "ordinary repo exploration is never",
                    "do not ask for needs_context just because you have not explored",
                ]),
                "Response explicitly rejects routine exploration as a NEEDS_CONTEXT reason.",
                "Response does not explicitly say that ordinary exploration is not a valid NEEDS_CONTEXT reason.",
            ),
            expectation(
                "Keeps file discovery and pattern lookup assigned to the implementer.",
                has_any(text, [
                    "implementer should explore",
                    "push exploration back to the implementer",
                    "that is implementer work",
                    "that stays with the implementer",
                    "repo discovery, pattern lookup, and first-pass design belong to the implementer",
                ]),
                "Response keeps file discovery and pattern lookup with the implementer.",
                "Response does not clearly keep discovery and pattern lookup with the implementer.",
            ),
            expectation(
                "Does not tell the manager to pre-read the codebase or hand over a solution.",
                not has_any(text, [
                    "manager should read the relevant files",
                    "manager should explore the repo",
                    "hand over the solution",
                    "draft the solution for them",
                    "ill read the relevant repo files",
                    "ill inspect the relevant code and patterns",
                ]),
                "Response avoids telling the manager to explore or provide the solution.",
                "Response incorrectly tells the manager to explore or provide the solution.",
            ),
            expectation(
                "Reserves NEEDS_CONTEXT for genuinely missing requirements, constraints, or conflicting signals.",
                has_any(text, [
                    "missing requirement",
                    "missing requirements",
                    "missing constraint",
                    "missing constraints",
                    "conflicting signal",
                    "conflicting signals",
                ]),
                "Response reserves NEEDS_CONTEXT for missing requirements/constraints or conflicting signals.",
                "Response does not restate the valid reasons for NEEDS_CONTEXT.",
            ),
        ]

    if eval_name == "task-conflicts-with-plan":
        return [
            expectation(
                "Recognizes that the task conflicts with the plan and is not clear enough to dispatch yet.",
                has_any(text, [
                    "conflicts with the plan",
                    "plan conflict",
                    "task conflicts",
                    "not clear enough to dispatch",
                    "do not dispatch yet",
                    "plan/task contradiction",
                    "plan and task contradict",
                    "mismatch between the plan and task",
                ]),
                "Response identifies the plan/task conflict and stops dispatch.",
                "Response does not clearly identify the plan/task conflict before dispatch.",
            ),
            expectation(
                "Says the manager should resolve the ambiguity or escalate to the human before implementation starts.",
                has_any(text, ["resolve the ambiguity", "resolve the conflict", "ask the human", "escalate to the human", "clarify with the human"]),
                "Response routes the conflict to ambiguity resolution or human escalation.",
                "Response does not clearly route the conflict to ambiguity resolution or human escalation.",
            ),
            expectation(
                "Keeps the manager focused on ambiguity resolution rather than speculative implementation.",
                has_any(text, ["ambiguity", "conflict"]) and not has_any(text, ["go ahead and implement", "pick one and proceed", "start implementation anyway"]),
                "Response keeps the manager on ambiguity resolution instead of speculative implementation.",
                "Response drifts into speculative implementation instead of conflict resolution.",
            ),
            expectation(
                "Does not silently choose one interpretation and proceed.",
                not has_any(text, ["just follow the task text", "just follow the plan", "pick whichever seems right", "choose one interpretation"]),
                "Response avoids silently picking one interpretation.",
                "Response silently picks an interpretation instead of resolving the conflict.",
            ),
        ]

    if eval_name == "done-with-concerns-scope-check":
        return [
            expectation(
                "Says the manager must read the concerns before updating tracking.",
                has_any(text, ["read the concerns before", "review the concerns before", "do not update tracking until you read the concerns", "triage the concerns"]) and has_any(text, ["do not update tracking yet", "before updating tracking", "before marking the task done"]),
                "Response says the concerns must be read before tracking updates.",
                "Response does not clearly require reading the concerns before updating tracking.",
            ),
            expectation(
                "Treats correctness or scope concerns as something to address before marking the task done.",
                has_any(text, ["scope concern", "correctness concern", "before marking it done", "before marking the task done", "before updating tracking", "address them first"]),
                "Response treats scope/correctness concerns as unresolved work.",
                "Response does not clearly treat scope/correctness concerns as unresolved work.",
            ),
            expectation(
                "Allows re-dispatching another implementer if needed to resolve the concern.",
                has_any(text, ["re-dispatch", "dispatch another implementer", "send another implementer"]),
                "Response allows another implementer pass to resolve the concern.",
                "Response does not mention re-dispatching another implementer.",
            ),
            expectation(
                "Does not immediately mark the task done just because tests passed.",
                not has_any(text, ["mark it done now", "update tracking now because tests passed", "tests passed so mark done"]),
                "Response avoids immediately marking the task done just because tests passed.",
                "Response incorrectly marks the task done just because tests passed.",
            ),
        ]

    if eval_name == "done-dispatches-code-simplifier":
        return [
            expectation(
                "Runs the per-task tracking update for the finished task immediately.",
                has_any(text, ["update the plan and todo tracker", "update tracking for task a", "record the verification", "mark task a done", "task-complete tracking update"]),
                "Response updates tracking immediately for the finished task.",
                "Response does not clearly perform the per-task tracking update when the implementer returns DONE.",
            ),
            expectation(
                "Keeps the manager moving to the remaining implementer work in the current wave.",
                has_any(text, ["dispatch task b", "dispatch the remaining task", "keep dispatching implementers", "continue with the next task in the wave", "remaining implementer work", "finish the rest of the wave"]),
                "Response keeps the wave moving to the remaining implementer work.",
                "Response does not clearly continue the current wave after the finished task.",
            ),
            expectation(
                "Explicitly waits until every task in the current wave is implemented and marked done before starting code-simplifier.",
                has_any(text, ["do not start code-simplifier yet", "dont launch code-simplifier yet", "wait until every task in the current wave is implemented and marked done", "only after all tasks in the wave are done", "code-simplifier is a post-wave step"]),
                "Response waits until the whole wave is done before code-simplifier.",
                "Response does not clearly delay code-simplifier until the whole wave is implemented and marked done.",
            ),
            expectation(
                "Does not send the main agent back into manual simplification or discovery first.",
                not has_any(text, ["manager should simplify", "simplify the code yourself", "manager should review every file first", "manager should rediscover the codebase"]),
                "Response keeps the main agent out of manual simplification or rediscovery work.",
                "Response sends the main agent back into manual simplification or rediscovery.",
            ),
        ]

    if eval_name == "weak-model-validation-selection":
        return [
            expectation(
                "Keeps the manager handoff lean instead of pre-solving or pre-reading the task.",
                not has_any(text, [
                    "manager should read the files first",
                    "manager should pre-solve",
                    "manager should draft the solution",
                    "read the file and map the task before you start",
                ]) and has_any(text, ["lean handoff", "task text", "success criteria", "known constraints", "known validation commands", "only the file hints"]),
                "Response keeps the manager handoff lean.",
                "Response does not clearly keep the manager handoff lean.",
            ),
            expectation(
                "Says the implementer should infer the slice's surface or stack before choosing validation.",
                has_any(text, ["infer the slice", "infer the stack", "infer the surface", "classify the slice first", "determine the stack first", "figure out the stack first"]),
                "Response tells the implementer to infer the slice's surface/stack before choosing validation.",
                "Response does not clearly say to infer the slice's surface or stack first.",
            ),
            expectation(
                "Chooses matching shell or Python checks rather than generic frontend commands.",
                has_any(text, ["bash -n", "shell validation", "py_compile", "python validation", "shellcheck", "shell + python", "shell/script validation", "targeted python", "grade_benchmark"]) and not has_any(text, ["default to npm test", "default to npm run build", "default to frontend commands"]),
                "Response picks shell/Python-style checks instead of generic frontend commands.",
                "Response does not clearly choose stack-matching shell/Python checks.",
            ),
            expectation(
                "Keeps validation ownership with the implementer.",
                has_any(text, ["implementer should choose", "implementer owns verification", "implementer owns validation", "implementer should run the matching checks", "keep verification ownership with the implementer"]),
                "Response keeps verification ownership with the implementer.",
                "Response does not clearly keep validation ownership with the implementer.",
            ),
        ]

    if eval_name == "code-simplifier-concerns-before-review":
        return [
            expectation(
                "Says the manager must read the code-simplifier's concerns before continuing to code-reviewer.",
                has_any(text, ["read the concerns before code-reviewer", "before continuing to code-reviewer", "before proceeding to code-reviewer", "do not proceed to code-reviewer", "before code review"]),
                "Response requires reading simplifier concerns before code-reviewer.",
                "Response does not clearly require reading simplifier concerns before code-reviewer.",
            ),
            expectation(
                "Treats correctness or scope concerns as unresolved work that must be addressed before continuing.",
                has_any(text, ["scope concern", "correctness concern", "unresolved work", "address them first", "before continuing"]),
                "Response treats simplifier concerns as unresolved work.",
                "Response does not clearly treat correctness/scope concerns as unresolved work.",
            ),
            expectation(
                "Reopens any affected task that was already marked done before re-dispatching the fix.",
                has_any(text, ["reopen the task", "reopen any affected done task", "reopen the affected task", "reopen the done task"]),
                "Response reopens the affected done task before routing the fix.",
                "Response does not clearly reopen an affected done task before re-dispatch.",
            ),
            expectation(
                "Allows re-dispatching the subagent that should own the fix instead of having the manager patch it manually.",
                has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should patch it directly", "fix it yourself as manager"]),
                "Response routes the fix to the owning subagent.",
                "Response does not clearly route the fix back to an owning subagent.",
            ),
            expectation(
                "Does not continue with stale tracking or proceed straight to code-reviewer.",
                (has_any(text, ["do not proceed to code-reviewer", "before code review", "stop the pipeline", "tracking cannot stay stale", "do not leave tracking stale", "re-sync tracking after the fix"]) or has_any(text, ["reopen"])) and not has_any(text, ["continue straight to code-reviewer", "proceed to code-reviewer now"]),
                "Response stops the flow until tracking and the fix are handled.",
                "Response does not clearly stop the flow before code-reviewer or keep tracking current.",
            ),
        ]

    if eval_name == "code-review-findings-block-tracking":
        return [
            expectation(
                "Says the manager must address code-review findings before ending the wave.",
                has_any(text, ["address findings before ending the wave", "before ending the build wave", "before finishing the wave", "before the final tracking sync", "before closing the wave"]),
                "Response blocks wave completion on reviewer findings.",
                "Response does not clearly block wave completion on reviewer findings.",
            ),
            expectation(
                "Reopens any affected task that was already marked done before routing the fix.",
                has_any(text, ["reopen the task", "reopen any affected done task", "reopen the affected task", "reopen the done task"]),
                "Response reopens the affected done task before routing the fix.",
                "Response does not clearly reopen an affected done task before routing the fix.",
            ),
            expectation(
                "Routes the fix to the subagent that should own it instead of having the manager do the repair inline.",
                has_any(text, ["re-dispatch", "dispatch the subagent that should own the fix", "send it back to the implementer", "send it back to the code-simplifier"]) and not has_any(text, ["manager should fix it directly", "repair it inline yourself"]),
                "Response routes review findings to an owning subagent.",
                "Response does not clearly route review findings to an owning subagent.",
            ),
            expectation(
                "Re-syncs tracking only after the final reviewer comes back `DONE`.",
                has_any(text, ["after every reviewer returns done", "after both reviewers return done", "after the final reviewer returns done", "only after the final code-reviewer returns done", "wait for every reviewer to return done"]),
                "Response waits for the reviewer wave to reach DONE before the final tracking sync.",
                "Response does not clearly wait for reviewer DONE before the final tracking sync.",
            ),
        ]

    if eval_name == "code-reviewer-handoff-includes-uncommitted-files":
        return [
            expectation(
                "Builds one deduped review scope from the touched files plus the filtered uncommitted files.",
                has_any(text, ["deduped review scope", "dedupe the review scope", "review_scope_files", "single review scope", "one review scope", "review scope"]) and has_any(text, ["touched files", "files the implementer touched", "files changed"]) and has_any(text, ["uncommitted files", "git status --porcelain", "notes.txt"]),
                "Response builds one manager-owned review scope from touched plus filtered uncommitted files.",
                "Response does not clearly build one deduped review scope from touched and filtered uncommitted files.",
            ),
            expectation(
                "Excludes deleted files and `.gitignore` files from that deduped review scope.",
                has_any(text, ["exclude deleted files", "excluding deleted files", "scratch.tmp", "deleted"]) and has_any(text, ["exclude .gitignore", "excluding .gitignore", ".gitignore"]),
                "Response excludes deleted files and `.gitignore` from the review scope.",
                "Response does not clearly exclude deleted files and `.gitignore` from the review scope.",
            ),
            expectation(
                "Uses one code-reviewer because the deduped review scope has `<=5` files.",
                has_any(text, ["one code-reviewer", "single code-reviewer", "1 code-reviewer", "one reviewer", "single reviewer"]) and has_any(text, ["<=5 files", "five files or fewer", "small scope", "only three files", "3 files"]),
                "Response uses one reviewer and ties it to the small-scope rule.",
                "Response does not clearly use one reviewer because the deduped scope is small.",
            ),
            expectation(
                "Passes the deduped review scope and current verification context to that reviewer before the final tracking sync.",
                has_any(text, ["review scope", "review_scope_files", "single file list"]) and has_any(text, ["current verification context", "verification context", "validation context", "verification results"]) and has_any(text, ["before the final tracking sync", "before syncing tracking", "wait for the reviewer to return done before the final tracking sync"]),
                "Response passes review scope plus verification context forward before the final tracking sync.",
                "Response does not clearly pass the deduped review scope and verification context forward before the final tracking sync.",
            ),
        ]

    if eval_name == "final-done-updates-tracking-without-commit":
        return [
            expectation(
                "Syncs the plan and todo tracker to the final reviewed state.",
                has_any(text, ["final reviewed state", "sync the plan and todo tracker", "sync tracking to the final reviewed state", "final tracking sync", "sync the tracker to the final state"]),
                "Response syncs tracking to the final reviewed state.",
                "Response does not clearly sync the plan and todo tracker to the final reviewed state.",
            ),
            expectation(
                "Records any additional verification actually performed during review.",
                has_any(text, ["additional verification", "verification during review", "record any additional verification", "record the extra verification", "record further verification"]),
                "Response records review-time verification.",
                "Response does not clearly record any additional verification performed during review.",
            ),
            expectation(
                "Does not create, amend, push, or otherwise publish a commit, PR, or tag.",
                has_any(text, ["do not commit", "must not commit", "do not create a commit", "do not push", "do not open the pr", "do not create or publish", "must not publish", "no commit, pr, or tag", "leave it unpublished"]),
                "Response forbids publishing work.",
                "Response does not clearly forbid creating or publishing a commit, PR, or tag.",
            ),
            expectation(
                "Leaves the changes uncommitted and local.",
                has_any(text, ["leave the working tree dirty", "leave the changes uncommitted", "leave the changes local", "keep it local", "leave it dirty and local", "uncommitted and local"]),
                "Response leaves the work dirty and local.",
                "Response does not clearly say to leave the work uncommitted and local.",
            ),
        ]

    if eval_name == "large-review-scope-partitions-code-reviewers":
        return [
            expectation(
                "Uses multiple parallel code-reviewers because the deduped review scope has `>5` files.",
                has_any(text, ["multiple parallel code-reviewers", "launch multiple reviewers in parallel", "parallel code-reviewers", "two parallel code-reviewers", "2 parallel code-reviewers", "two parallel code-reviewer subagents"]) and has_any(text, [">5 files", "more than five files", "8 files", "eight files"]),
                "Response uses a parallel reviewer wave and ties that choice to the large review scope.",
                "Response does not clearly use parallel reviewers because the review scope is larger than five files.",
            ),
            expectation(
                "Partitions the files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one reviewer scope.",
                has_any(text, ["non-overlapping", "exactly one reviewer scope", "each file appears in exactly one reviewer scope", "no file appears in more than one scope"]) and has_any(text, ["module", "directory", "logical area", "auth", "billing", "group"]),
                "Response partitions the review into coherent non-overlapping scopes.",
                "Response does not clearly partition the large review scope into non-overlapping logical groups.",
            ),
            expectation(
                "Keeps the reviewer file lists manager-authored instead of telling reviewers to recompute or narrow scope.",
                has_any(text, ["manager owns the partitions", "manager-authored", "give the exact file list", "reviewers do not recompute", "do not recompute scope", "reuse the same partitions"]),
                "Response keeps scope ownership with the manager instead of the reviewers.",
                "Response does not clearly keep reviewer file lists manager-authored.",
            ),
            expectation(
                "Waits for every reviewer to return `DONE` before the final tracking sync.",
                has_any(text, ["every reviewer", "all reviewers", "both reviewers"]) and has_any(text, ["return done", "returns done", "before the final tracking sync", "then run the final tracking sync", "only then sync tracking"]),
                "Response waits for the whole reviewer wave to finish before the final tracking sync.",
                "Response does not clearly wait for every reviewer to return DONE before the final tracking sync.",
            ),
        ]

    if eval_name == "large-review-scope-partitions-code-simplifiers":
        return [
            expectation(
                "Uses multiple parallel code-simplifiers because the deduped review scope has `>5` files.",
                has_any(text, ["multiple parallel code-simplifiers", "launch multiple simplifiers in parallel", "parallel code-simplifiers", "2 code-simplifier subagents in parallel", "two parallel code-simplifier subagents", "two parallel code-simplifiers"]) and has_any(text, [">5 files", "more than five files", "8 files", "eight files"]),
                "Response uses a parallel simplifier wave and ties that choice to the large review scope.",
                "Response does not clearly use parallel simplifiers because the review scope is larger than five files.",
            ),
            expectation(
                "Partitions the files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one simplifier scope.",
                has_any(text, ["non-overlapping", "exactly one simplifier scope", "each file appears in exactly one simplifier scope", "no file appears in more than one scope"]) and has_any(text, ["module", "directory", "logical area", "auth", "billing", "group"]),
                "Response partitions the simplifier wave into coherent non-overlapping scopes.",
                "Response does not clearly partition the large simplifier scope into non-overlapping logical groups.",
            ),
            expectation(
                "Keeps the simplifier file lists manager-authored instead of telling simplifiers to recompute or narrow scope.",
                has_any(text, ["manager owns the partitions", "manager-authored", "give the exact file list", "simplifiers do not recompute", "do not recompute scope", "reuse the same partitions"]),
                "Response keeps scope ownership with the manager instead of the simplifiers.",
                "Response does not clearly keep simplifier file lists manager-authored.",
            ),
            expectation(
                "Waits for every code-simplifier to return `DONE` before launching code-reviewers or updating tracking.",
                has_any(text, ["every code-simplifier", "all code-simplifiers", "both simplifiers"]) and has_any(text, ["return done", "returns done", "before launching code-reviewers", "before code-review begins", "after every simplifier returns done"]),
                "Response waits for the whole simplifier wave to finish before moving downstream.",
                "Response does not clearly wait for every simplifier to return DONE before moving downstream.",
            ),
        ]

    if eval_name == "direct-commit-request-is-refused":
        return [
            expectation(
                "States that the build skill's no-commit override still applies even when asked directly.",
                has_any(text, ["build skill override", "no-commit override", "commit override still applies", "still applies even when asked directly", "under the build workflow i wont"]) and has_any(text, ["still applies", "under the build workflow"]),
                "Response keeps the override active even under a direct request.",
                "Response does not clearly say the build skill override still applies.",
            ),
            expectation(
                "Refuses to create, amend, push, or otherwise publish a commit, PR, or tag.",
                has_any(text, ["do not commit", "will not commit", "wont commit", "do not push", "will not push", "wont push", "do not open the pr", "will not open the pr", "do not publish", "no commit, pr, or tag"]),
                "Response refuses to publish the work.",
                "Response does not clearly refuse to create or publish the work.",
            ),
            expectation(
                "Leaves the working tree dirty and local for the human to review manually.",
                has_any(text, ["leave the working tree dirty", "leave it local", "leave the changes uncommitted", "human can review manually", "for the human to review manually"]),
                "Response leaves the work dirty and local for manual review.",
                "Response does not clearly leave the work dirty and local for the human.",
            ),
            expectation(
                "Does not offer a workaround that still publishes the changes.",
                not has_any(text, ["i can push it for you", "i can open the pr", "i can tag it", "i can publish it another way", "i can hand it to a git skill to commit"]),
                "Response does not propose an alternate way to publish the work.",
                "Response offers a workaround that still publishes the work.",
            ),
        ]

    if eval_name == "manager-refuses-pre-solving-patch":
        return [
            expectation(
                "Refuses to read the file and paste the patch on the manager's behalf.",
                has_any(text, ["not read the file and paste the patch", "will not read the file and paste the patch", "do not pre-solve", "wont pre-solve", "will not pre-solve", "will not paste the patch"]),
                "Response refuses manager-side patching.",
                "Response does not clearly refuse manager-side file reading and patch drafting.",
            ),
            expectation(
                "Keeps repo discovery, pattern lookup, and first-pass design with the implementer.",
                has_any(text, ["repo discovery", "pattern lookup", "first-pass design", "first pass design"]) and has_any(text, ["implementer", "stays with the implementer", "belongs to the implementer"]),
                "Response keeps discovery and design with the implementer.",
                "Response does not clearly keep discovery, pattern lookup, and first-pass design with the implementer.",
            ),
            expectation(
                "Allows the manager to forward only already-known hints such as the task text or existing file hint.",
                has_any(text, ["already-known hint", "already-known file hint", "task text", "existing file hint", "only the file hint you already have", "forward the hint"]),
                "Response allows only already-known hints in the handoff.",
                "Response does not clearly limit the manager to already-known hints.",
            ),
            expectation(
                "Does not include code fences, diff hunks, or an inline patch.",
                not has_code_or_patch(raw_text),
                "Response contains no code fence or patch artifact.",
                "Response includes code-style or patch-style content instead of a lean manager handoff.",
            ),
            expectation(
                "Keeps the response concise instead of turning the handoff into a long design writeup.",
                compact <= 140,
                f"Response stays concise at {compact} words.",
                f"Response is too long for a lean manager handoff at {compact} words.",
            ),
        ]

    if eval_name == "blocked-review-scope-splits-partitions":
        return [
            expectation(
                "Uses the BLOCKED escalation ladder instead of retrying the same stuck attempt unchanged.",
                has_any(text, ["blocked", "escalation ladder", "too large", "split it into smaller pieces", "smaller pieces"]) and not has_any(text, ["rerun the same review", "retry the same partition unchanged"]),
                "Response follows the BLOCKED path instead of repeating the same stuck attempt.",
                "Response does not clearly follow the BLOCKED ladder.",
            ),
            expectation(
                "Recognizes that an oversized partition should be split into smaller pieces.",
                has_any(text, ["split it into smaller pieces", "split the partition", "smaller partition", "smaller pieces", "separate auth and billing"]),
                "Response shrinks the oversized partition.",
                "Response does not clearly split the oversized partition.",
            ),
            expectation(
                "Keeps partition ownership with the manager and re-dispatches the review rather than reviewing inline.",
                has_any(text, ["manager owns the partitions", "manager should repartition", "manager-authored partitions", "re-dispatch"]) and not has_any(text, ["review it inline", "manager should review it directly"]),
                "Response keeps partition ownership with the manager and re-dispatches.",
                "Response does not clearly keep partition ownership with the manager or avoid inline review.",
            ),
            expectation(
                "Avoids escalating to the human unless the plan itself is wrong.",
                not has_any(text, ["ask the human now", "escalate to the human now"]) or has_any(text, ["if the plan is wrong", "unless the plan itself is wrong"]),
                "Response keeps human escalation conditional on the plan being wrong.",
                "Response escalates to the human too early instead of using the split/re-dispatch path.",
            ),
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
            "overall": "No evaluator suggestions.",
        },
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
