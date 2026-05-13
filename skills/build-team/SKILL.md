---
name: build-team
description: Execute an existing $plan continuously. Orchestrate ready implementation and fix tasks through fresh subagents, keep $plan as the source of truth, then run simplification, review, and durable lesson capture. If review finds issues, create new fix tasks in $plan and repeat simplification/review as needed before stopping.
---

# Build Team

## Overview

Execute an existing `$plan` continuously. You are the orchestrator:
- dispatch each ready implementation or fix task to a fresh implementer subagent
- update `$plan` after each completed task
- run code simplification and code review with fresh role-appropriate subagents
- if review finds issues, create new fix tasks in `$plan` and repeat simplification/review

Use a fresh subagent for each dispatched unit of work:
- implementer for implementation and fix tasks
- code-simplifier for simplification
- code-reviewer for review

## When to Use

- `$plan` already exists and has pending implementation tasks.
- The user wants execution of an existing plan, not planning from scratch.
- Work should continue through ready tasks without repeated check-ins.
- Not for creating a plan, writing a spec, or breaking work down from scratch.

## Input

- `$plan` (required): path to an existing implementation plan file, typically `.agents/scratchpad/<feature>/plan.md`.

## Workflow

### Phase 1: Implementation Orchestration

1. Read `$plan` and select the next ready task. In Phase 1, a task is ready if it is an unchecked implementation or fix task with no incomplete dependency or prerequisite listed in `$plan`.
2. Dispatch one fresh implementer subagent using [implementer-prompt.md](./implementer-prompt.md). Include:
   - the exact task text
   - the minimum relevant `$plan` excerpt: dependencies, acceptance criteria, verification notes, and nearby task boundaries if needed
3. Wait for the implementer result.
4. Handle statuses exactly:
   - **DONE:** mark the matching task complete in `$plan`, save, re-read, and verify before starting the next task
   - **DONE_WITH_CONCERNS:** resolve correctness or scope concerns before marking complete; non-blocking notes should be reported under `DONE`
   - **NEEDS_CONTEXT:** provide missing context and re-dispatch; do not mark complete
   - **BLOCKED:** try to unblock with better context, a smaller slice, or a stronger model; if still blocked, stop and escalate to the human; do not mark complete
5. Continue through ready implementation and fix tasks without pausing for permission.
6. When no ready implementation or fix tasks remain, build `$review_scope_files`:
   - include every file any implementer reported changing
   - add uncommitted files from `git status --porcelain`
   - exclude deleted files, `.gitignore`, and git-ignored paths
   - deduplicate
   - keep paths relative to the repository root
7. Proceed to simplification. Stop only for a real blocker. If `$plan` is materially wrong, inconsistent, or missing required information, escalate to the human instead of silently rewriting it.

### Phase 2: Code Simplification

1. Add a "Code Simplification" task to `$plan` with the full `$review_scope_files` list in the description.
2. Dispatch fresh code-simplifier subagents using [code-simplifier-prompt.md](./code-simplifier-prompt.md). Include the exact file list for each subagent.
   - **≤5 files:** 1 agent for all files
   - **>5 files:** partition into non-overlapping groups by module, directory, or logical area, and launch one agent per group in parallel
   - each file must appear in exactly one simplifier scope
3. Wait for all simplifier results.
4. Handle statuses exactly:
   - **DONE:** when all subagents report `DONE`, mark the simplification task complete in `$plan`, save, re-read, and verify, then proceed
   - **DONE_WITH_CONCERNS:** resolve correctness or scope concerns before marking complete; non-blocking notes should be reported under `DONE`
   - **NEEDS_CONTEXT:** provide context and re-dispatch; do not mark complete
   - **BLOCKED:** try to unblock with better context, a smaller slice, or a stronger model; if still blocked, stop and escalate; do not mark complete
5. Keep the existing "Code Simplification" task open across simplification/review iterations for the same review cycle unless the plan format explicitly requires otherwise.

### Phase 3: Code Review

**Review loop:** finding → new fix task → implementer fix → update `$review_scope_files` → simplification on affected scope → review again → complete only when review returns `DONE`.

1. Add a "Code Review" task to `$plan` with the full `$review_scope_files` list in the description.
2. Dispatch fresh code-reviewer subagents using [code-reviewer-prompt.md](./code-reviewer-prompt.md). Include the exact file list for each subagent.
   - **≤5 files:** 1 agent for all files
   - **>5 files:** multiple agents in parallel with different focuses such as correctness, security, or performance
   - reviewers are read-only; overlapping review scopes are allowed
3. Wait for all reviewer results.
4. Handle statuses exactly:
   - **DONE:** when all subagents report `DONE`, mark the review task complete in `$plan`, save, re-read, and verify, then proceed
   - **DONE_WITH_FINDINGS:** add a new fix task to `$plan` with the finding, affected files, and original task context; route it to a fresh implementer subagent; after the fix lands, update `$review_scope_files` for the affected scope, return to Phase 2, and review again; do not mark review complete
   - **NEEDS_CONTEXT:** provide context and re-dispatch; do not mark complete
   - **BLOCKED:** try to unblock with better context, a smaller slice, or a stronger model; if still blocked, stop and escalate; do not mark complete
5. Keep the existing "Code Review" task open across review iterations for the same review cycle unless the plan format explicitly requires otherwise.

### Phase 4: Self-Improve

Before stopping, invoke `self-improve` to capture durable, reusable learnings. Do not record one-off task trivia.

## Stop Conditions

Stop only when one of these is true:
- all implementation, simplification, and review work is complete in `$plan`, and `self-improve` has been invoked
- a real blocker remains after reasonable unblocking attempts
- `$plan` is materially wrong, inconsistent, or missing required information and needs human correction

Do not stop merely to ask whether to continue.

## Specific Techniques

- The orchestrator must not implement, simplify, or patch code directly; code changes must be made by the appropriate subagent role.
- Treat `$plan` as the only execution record. Todo trackers, memory, scratchpads, chat summaries, and subagent reports may help coordination but never replace updating `$plan`.
- A task is complete only after the finished state is written to `$plan` and verified by re-reading `$plan`.
- Send implementers the exact task text plus the relevant `$plan` excerpt. Explicit task boundaries help weaker models.
- When adding new tasks to `$plan`, use `addy-planning-and-task-breakdown` to preserve task format and decomposition.
- Reuse [implementer-prompt.md](./implementer-prompt.md), [code-simplifier-prompt.md](./code-simplifier-prompt.md), and [code-reviewer-prompt.md](./code-reviewer-prompt.md) instead of improvising prompts, statuses, or report formats.
- Leave all repository changes uncommitted.
- Mark completed tasks with `[x]`.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "The implementer said it's done, so I can move on." | `DONE` is not enough. The task is complete only after `$plan` is updated, saved, and re-read. |
| "Implementation is done, so I can skip review." | Simplification and code review are required before handoff. |
| "I can track completion in my todo list or chat summary." | Those are helpers, not execution records. `$plan` is the only source of truth. |
| "I'll just do this task myself instead of dispatching a subagent." | This skill is for orchestration. Use fresh role-appropriate subagents. |
| "I'll stop after this task and ask whether to continue." | Keep going through ready tasks. Stop only for a real blocker, genuine ambiguity, or full completion. |
| "Review findings are faster to patch inline." | Create a new fix task in `$plan` and send it to a fresh implementer. |
| "The plan is done, so the skill is done." | Not yet. Invoke `self-improve` if durable reusable lessons exist. |

## Red Flags

- the orchestrator writes code directly
- starting the next task before `$plan` is updated and re-read
- treating runtime trackers or subagent reports as equivalent to `$plan`
- marking `BLOCKED` or `NEEDS_CONTEXT` work complete
- stopping between ready tasks to ask for permission
- skipping simplification or review after implementation completes
- patching review findings inline instead of creating a new `$plan` task
- committing changes or telling subagents to commit
- skipping `self-improve` when durable lessons exist
- recording one-off trivia as durable lessons
- marking a task complete with anything other than `[x]`

## Verification

- [ ] `$plan` existed and provided task order.
- [ ] Each dispatched task used a fresh subagent of the correct role.
- [ ] Each completed implementation or fix task was written to `$plan` only after `DONE` or an acceptable `DONE_WITH_CONCERNS` resolution.
- [ ] Completed tasks were marked with `[x]` in `$plan`.
- [ ] After each `$plan` update, the file was re-read and matched current execution state before the next task began.
- [ ] Ready implementation and fix tasks ran continuously until completion or escalation.
- [ ] `$review_scope_files` included touched files plus filtered uncommitted files, excluding deleted, ignored, and `.gitignore` paths.
- [ ] A "Code Simplification" task was recorded in `$plan`, completed, saved, and verified by re-reading `$plan`.
- [ ] A "Code Review" task was recorded in `$plan`, completed, saved, and verified by re-reading `$plan`.
- [ ] Any review findings created new fix tasks in `$plan` and were routed to fresh implementer subagents.
- [ ] All work remains uncommitted.
- [ ] `self-improve` was invoked before stopping if durable reusable learnings were produced.
- [ ] Any captured lessons were durable and reusable, not one-off task trivia.