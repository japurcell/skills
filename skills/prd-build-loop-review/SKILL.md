---
name: prd-build-loop-review
description: Implement all failing PRD stories, then run one final simplify-review-verify-record pass across the combined final state
---

# PRD Build Loop

Use when you must autonomously implement all `passes: false` stories in `prd_file`, without returning control between stories, and only stop for a defined Stop Condition.

## Core Rules

- Continue until every story in `prd_file` has `passes: true`.
- `prd_file` is the only authority for story status and completion.
- `progress_file` is for resume and tracking only; never use it to decide completion.
- Do not commit changes.
- If all stories have `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
- If a required detail is missing, ambiguous, contradictory, or requires a human choice, stop and ask the user to decide.

## Inputs

- `prd_file` (required)
- `progress_file` (optional): if not provided, use `dirname(prd_file) + "/progress.txt"`

## Path Resolution

- Resolve `progress_file` from `prd_file`, never from session state, home directories, or session scratchpads.
- Treat relative paths as relative to the repo or provided `prd_file`.
- Never substitute paths like `~/.copilot/session-state/.../progress.txt`.

## Fresh-Subagent Rule

- Use a fresh subagent for each unit of work.
- Any code-affecting change must be made by a fresh `implementer`.
- The orchestrator must never make code-affecting changes directly.
- Before dispatching an `implementer`, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to select and dispatch work.
- Before dispatching an `implementer`, do not do story-specific repo discovery, file reading, test reading, code inspection, or behavior verification.
- If no fresh `implementer` has handled the current unit of work, dispatch one before any code-affecting action or story-specific investigation.
- Any new implementer change resets downstream finalization requirements.

## Roles

### Orchestrator

- select stories
- resume and track work from `progress_file`
- dispatch subagents
- apply **Status Rules**
- run or verify required checks after final clean review
- update `prd_file`, `progress_file`, and reusable guidance in nearby `AGENTS.md`
- append each subagent `Progress block` to `progress_file` immediately after completion

### Implementer

- perform repo discovery
- read relevant files, tests, and code
- design and make code changes
- run initial verification
- report results and follow-up needs
- return a short `Progress block`

### Code Simplifier

- run after all implementation work is finished, and again after any review-fix implementation
- check repository `.gitignore` first; ignored files are out of scope
- do not simplify, review, or analyze ignored files
- if ignore status is unclear, report uncertainty and do not proceed on those files
- return a short `Progress block`

### Reviewer

- run after simplification
- check repository `.gitignore` first; ignored files are out of scope
- do not review or analyze ignored files
- if ignore status is unclear, report uncertainty and do not proceed on those files
- return a short `Progress block`

## Startup

1. Invoke `subagent-model-router` and `self-improve`.
2. Resolve `progress_file` from `prd_file`.
3. If `progress_file` exists, read `## Codebase Patterns` and latest entries.
4. Otherwise, create it on first append with `## Codebase Patterns` at the top.

## Phase 1: Implementation Loop

For the highest-priority story in `prd_file` with `passes: false`:

1. Determine the next required implementation step from `prd_file` and `progress_file`.
2. Dispatch a fresh `implementer` with `./implementer-prompt.md`.
   - Include all story properties, `progress_file`, nearby `AGENTS.md`, and the correct mode such as `initial_implementation` or follow-up.
   - Require a `Progress block`.
   - Do not pre-read story-specific repo files, tests, code, or behavior.
3. Wait for the result.
4. Append its `Progress block` to `progress_file` immediately, including `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
5. Apply **Status Rules**.
6. Update nearby `AGENTS.md` only with reusable guidance.
7. If the story is implemented and ready for finalization, record that in `progress_file` but leave `passes: false`.
8. Repeat until every failing story is either implemented and awaiting finalization or a **Stop Condition** is reached.

## Phase 2: Single Finalization Pass

After Phase 1, finalize once for the combined final state of all Phase 1 changes.

### 1. Initialize

- Restore the review-fix iteration count from `progress_file`; otherwise use `0`.

### 2. Simplify

- Dispatch a fresh `code-simplifier`.
- Scope: all relevant non-ignored changes in the current combined final state.
- Do not skip.
- Require a `Progress block` containing:
  - Role: code-simplifier
  - Summary
  - Files changed/reviewed
  - Verification or outcome
  - Learnings
- Append it to `progress_file` immediately.

### 3. Review

- First, using a fast-tier subagent, collect and dedupe requirements from:
  1. `prd_file` and other relevant docs in the same directory
  2. GitHub issue references from commit messages, PR metadata, or PRD docs, when available
- Then dispatch a fresh `addy-code-reviewer`.
- Scope: all relevant non-ignored changes after simplification.
- Review for missing or partial requirements, scope creep, incorrect implementation, correctness, readability, architecture, security, performance, and similar issues.
- Do not skip.
- Require a `Progress block` containing:
  - Role: reviewer
  - Summary
  - Files changed/reviewed
  - Verification or outcome
  - Learnings
- Append it to `progress_file` immediately.

### 4. Fix Review Findings

- If review finds issues:
  - If the review-fix iteration count is already `3`, stop and ask the user to decide.
  - Increment the count by `1`.
  - Dispatch a fresh `implementer` with `mode: review_fix` and full reviewer findings.
  - Require a `Progress block`.
  - Never fix findings directly.
  - Append its `Progress block` to `progress_file` immediately, including `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
  - Apply **Status Rules**.
  - Rerun **Simplify** and **Review** for the updated combined final state.
  - Repeat until review is clean, the limit is reached, or a **Stop Condition** is reached.

### 5. Verify

- Run required quality checks only after review is clean for the final state.
- Use checks required by the stories, repo guidance, nearby `AGENTS.md`, and standard project scripts needed to validate changed areas.
- Append an orchestrator verification entry to `progress_file` immediately.

### 6. Record

- Update nearby `AGENTS.md` only with reusable guidance.
- Set `passes: true` in `prd_file` only for stories that satisfy the **Completion Gate**.
- Append an orchestrator final-state entry to `progress_file`.
- Re-read `prd_file`.

## Completion Gate

Mark a story complete only if:

1. its required implementation was completed by a fresh `implementer`
2. if review required fixes, the latest code-affecting change was made by a fresh `implementer`
3. a fresh `code-simplifier` ran after the latest code-affecting change
4. a fresh `addy-code-reviewer` ran after the latest code-affecting change
5. if review found issues, a fresh `implementer` fixed them, then simplification and review ran again after that fix
6. review is clean for the final state
7. required quality checks passed for the final state

Only `prd_file` determines official completion. Never treat implementer `DONE`, passing checks alone, confidence, or `progress_file` updates as sufficient.

## Status Rules

- **DONE:** continue
- **DONE_WITH_CONCERNS:** treat as incomplete unless every concern is explicitly confirmed non-blocking
- **NEEDS_CONTEXT:** if a human decision is required, stop and ask the user; otherwise provide the missing context and re-dispatch a fresh subagent
- **BLOCKED:** try better context, a smaller slice, or a stronger model; if still blocked, stop and ask the user

## Progress File

- Append only; never replace contents.
- Maintain a `## Codebase Patterns` section at the top.
- Store only reusable general patterns there, never story-specific details.
- Subagents never write `progress_file` directly; they return `Progress block`s and the orchestrator appends them immediately.
- Use `progress_file` to support exact resume after interruption, not official completion.
- Record enough to determine:
  - current story
  - whether implementation is done
  - whether finalization has started
  - latest review outcome
  - review-fix iteration count
  - whether verification ran for the final state

Required entry format:

```text
## [Date/Time] - [Story ID or FINALIZATION]
- Role: implementer | code-simplifier | reviewer | orchestrator
- Summary
- Files changed/reviewed
- Verification or outcome
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

## AGENTS.md

Add only reusable guidance, such as:

- module conventions
- non-obvious gotchas
- important file relationships
- testing expectations
- config or environment requirements

Do not add story-specific notes.

## Stop Condition

Stop only if:

- all stories in `prd_file` have `passes: true`
- a real blocker remains after reasonable unblocking attempts
- `prd_file` has contradictions, invalid ordering, or missing required details that need human correction
- a required human decision is needed
- the review-fix iteration limit is reached
- verification failed and needs a human decision

## Before Stopping

Before any response other than exactly `<promise>COMPLETE</promise>`:

1. Re-read `prd_file`.
2. Confirm at least one **Stop Condition** is true.
3. Append the latest stop-state orchestrator entry to `progress_file`.
4. Ask the user to decide the open question that caused the stop.

## Red Flags

- returning control before all stories have `passes: true` when no **Stop Condition** applies
- resolving `progress_file` anywhere except `dirname(prd_file) + "/progress.txt"` unless an explicit path was provided
- using session-state, scratchpads, home directories, or `~/.copilot/...` paths for `progress_file`
- failing to append a subagent `Progress block` immediately
- reading extra repo context before dispatching an `implementer`
- reading story-specific files, tests, code, or behavior before dispatching an `implementer`
- making code-affecting changes directly
- simplifying, reviewing, or analyzing files matched by `.gitignore`
- exceeding the review-fix iteration limit
- skipping simplify or review
- verifying before review is clean for the final state
- fixing review findings without a fresh `implementer`
- using anything except `prd_file` to decide official completion
- missing a progress entry or its learnings section
- marking `passes: true` before the single finalization pass is complete
