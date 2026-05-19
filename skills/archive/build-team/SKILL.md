---
name: build-team
description: Execute an existing `$plan` continuously by routing ready implementation and fix tasks to fresh subagents, updating `$plan` as the source of truth, then running simplification, review, and durable lesson capture. If review finds issues, add fix tasks to `$plan` and repeat until review is clean or escalation is required.
---

# Build Team

## Overview
Execute an existing `$plan` continuously as the orchestrator:
- dispatch each ready implementation or fix task to a fresh implementer subagent with a lean handoff
- update `$plan` after each completed task
- run simplification and review with fresh role-appropriate subagents
- if review finds issues, add fix tasks to `$plan`, implement them, then repeat simplification and review
Use a fresh subagent for each unit of work:
- implementer for implementation and fix tasks
- code-simplifier for simplification
- code-reviewer for review

## When to Use
- `$plan` already exists and contains pending implementation tasks
- the user wants execution, not planning from scratch
- work should continue through ready tasks without repeated check-ins
- you need an orchestrator/subagent boundary

## Input
- `$plan` (required): path to an existing implementation plan file, typically `.agents/scratchpad/<feature>/plan.md`
## Review Cycle
A review cycle begins when Phase 2 starts after implementation work is exhausted and ends when Code Review completes with `DONE` or escalation stops execution.

## Shared Rules

### Status Rules
Use these rules everywhere unless a phase says otherwise:
- **DONE:** mark the matching task complete in `$plan`, save, re-read, and verify before continuing
- **DONE_WITH_CONCERNS:** treat as incomplete unless every concern is explicitly confirmed non-blocking; if all are non-blocking, record the note and treat the result as `DONE`; otherwise re-dispatch or escalate
- **NEEDS_CONTEXT:** provide the missing context and re-dispatch; do not mark complete
- **BLOCKED:** try to unblock with better context, a smaller slice, or a stronger model; if still blocked, stop and escalate; do not mark complete

### Core Execution Rules
- Treat `$plan` as the sole source of truth and only execution record.
- Chat state, memory, scratch notes, SQL tables, databases, spreadsheets, and task tools are not execution records and must never determine official task status.
- A task is complete only after its finished state is written to `$plan` and verified by re-reading `$plan`.
- Mark completed tasks with `[x]`.
- Select the next ready task only from the latest re-read contents of `$plan`.
- If any external tracker is used for convenience, it must exactly mirror `$plan` and must never be used instead of updating `$plan` first.
- Leave all repository changes uncommitted.
- Reuse [implementer-prompt.md](./implementer-prompt.md), [code-simplifier-prompt.md](./code-simplifier-prompt.md), and [code-reviewer-prompt.md](./code-reviewer-prompt.md) instead of improvising prompts, statuses, or report formats.
- Use `addy-planning-and-task-breakdown` when adding new tasks to `$plan`.
- Stop only for a real blocker, a broken/inadequate plan, or full completion. Do not stop just to ask whether to continue.

### Plan Update Transaction
Whenever a task reaches a state that permits completion, the orchestrator must perform this exact sequence before any further dispatch or task selection:
1. Read the current `$plan`.
2. Locate the exact matching task in `$plan`.
3. Change its checkbox from `[ ]` to `[x]` or make the required plan edit for the current phase.
4. Save `$plan`.
5. Re-read `$plan`.
6. Verify the saved contents reflect the intended change.
7. Only then select or dispatch the next task.

## Workflow

### Phase 1: Implementation Orchestration
1. Invoke `addy-context-engineering` to load only the minimum context needed.
2. Read `$plan` and select the next ready task. A task is ready only if it is an unchecked implementation or fix task and all listed dependencies/prerequisites are complete.
3. Dispatch one fresh implementer subagent using [implementer-prompt.md](./implementer-prompt.md). Include:
   - the exact task text
   - the minimum relevant `$plan` excerpt: dependencies, acceptance criteria, verification notes, and nearby task boundaries if needed
4. Wait for the result and apply **Status Rules**.
5. Continue through ready implementation and fix tasks without pausing for permission.
6. When no ready implementation or fix tasks remain, build `$review_scope_files`:
   - start with every file reported changed by any implementer
   - add files from `git status --porcelain`
   - remove deleted files, `.gitignore`, and git-ignored paths
   - deduplicate
   - convert to repo-relative paths
7. Proceed to simplification. If `$plan` has contradictory dependencies, invalid task order, missing required task details, or cannot support the required implementation/review loop, escalate to the human instead of silently rewriting it.

### Phase 2: Code Simplification
1. Ensure there is exactly one open "Code Simplification" task for the current review cycle in `$plan`. If one already exists, update its description with the current `$review_scope_files`. Otherwise, add a new one.
2. Dispatch fresh code-simplifier subagents using [code-simplifier-prompt.md](./code-simplifier-prompt.md). Include the exact file list for each subagent.
   - **≤5 files:** 1 agent for all files
   - **>5 files:** partition into non-overlapping groups by module, directory, or logical area and launch one agent per group in parallel
   - each file must appear in exactly one simplifier scope
3. Wait for all results, summarize the simplification work and affected files, then announce the summary to the user.
4. Apply **Status Rules**.

### Phase 3: Code Review
Review loop: finding → new fix task → implementer fix → update `$review_scope_files` → simplification on affected scope → review again → complete only when review returns `DONE`.
1. Ensure there is exactly one open "Code Review" task for the current review cycle in `$plan`. If one already exists, update its description with the current `$review_scope_files`. Otherwise, add a new one.
2. Dispatch fresh code-reviewer subagents using [code-reviewer-prompt.md](./code-reviewer-prompt.md). Include the exact file list for each subagent.
   - **≤5 files:** 1 agent for all files
   - **>5 files:** dispatch multiple reviewers in parallel; partition by focus (e.g. correctness, security, or performance), file group, or both; overlap is allowed, but each reviewer must receive an explicit scope and focus
   - reviewers are read-only
3. Wait for all results, summarize the review findings, then announce the summary to the user.
4. Handle statuses as follows:
   - **DONE:** apply **Status Rules**
   - **DONE_WITH_FINDINGS:** for each finding, add a new fix task to `$plan` with the finding, affected files, original task context, and expected correction; dispatch it to a fresh implementer; after the fix lands, update `$review_scope_files` for the affected scope, return to Phase 2, and review again; do not mark the review task complete
   - **NEEDS_CONTEXT:** apply **Status Rules**
   - **BLOCKED:** apply **Status Rules**

### Phase 4: Self-Improve
Before stopping, invoke `self-improve` to capture durable, reusable learnings. Do not record one-off task trivia.

## Role Boundaries
**Orchestrator**
- owns task selection, dispatch, tracking, `$plan` updates, `$review_scope_files`, review partitioning, self-improvement capture, and stop conditions
- dispatches as soon as the task is clear enough
- does not inspect files beyond the minimum needed to identify the task and prepare the handoff
- does not draft solutions, sketch patches, run implementation validation, or change code directly
**Implementer**
- owns repo discovery, pattern lookup, first-pass design, code changes, and verification

## Fix Task Requirements
Every new fix task must include:
- an unchecked checkbox: `[ ]`
- concise task title
- finding/problem statement
- affected file(s)
- original task reference/context
- acceptance criteria or expected correction

## Stop Conditions
Stop only when one of these is true:
- all implementation, simplification, and review work is complete in `$plan`, and `self-improve` has been invoked
- a real blocker remains after reasonable unblocking attempts
- `$plan` has contradictory dependencies, invalid task order, missing required task details, or cannot support the required implementation/review loop and needs human correction

## Common Failure Modes
- reading extra repo context, proposing patches, or running validation before dispatching a clear task
- treating chat state, memory, scratch notes, subagent reports, SQL tables, databases, or task-tracking tools as equivalent to `$plan`
- using any tracker to determine readiness or completion without first updating and re-reading `$plan`
- starting the next task before updating and re-reading `$plan`
- writing code directly instead of using the correct fresh subagent
- skipping simplification or review after implementation completes
- patching review findings inline instead of creating new fix tasks
- stopping between ready tasks to ask for permission
- committing changes or telling subagents to commit
- recording one-off trivia in `self-improve`

## Verification
- [ ] `$plan` existed and determined task order.
- [ ] `$plan` was the sole source of truth for official task state throughout execution.
- [ ] No SQL table, database, scratch tracker, or chat-only state was used as an authoritative execution record.
- [ ] Each dispatched task used a fresh subagent of the correct role.
- [ ] Completed implementation and fix tasks were marked `[x]` in `$plan` only after `DONE` or acceptable `DONE_WITH_CONCERNS` resolution.
- [ ] After each `$plan` update, the file was saved, re-read, and matched execution state before the next task began.
- [ ] Ready implementation and fix tasks were selected from the latest verified contents of `$plan`.
- [ ] Ready implementation and fix tasks ran continuously until completion or escalation.
- [ ] `$review_scope_files` included touched files plus filtered uncommitted files, excluding deleted, ignored, and `.gitignore` paths.
- [ ] Exactly one current-cycle "Code Simplification" task and one current-cycle "Code Review" task were maintained in `$plan`.
- [ ] Review findings created fix tasks with the required structure and were routed to fresh implementer subagents.
- [ ] All work remains uncommitted.
- [ ] `self-improve` captured only durable, reusable learnings.