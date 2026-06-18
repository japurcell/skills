---
name: prd-build-loop-review
description: Use when asked to autonomously implement every failing PRD story, complete all non-passing items in `prd_file`, run a final combined simplify/review/verify/record pass, resume from `progress_file`, or continue until PRD completion without handing control back between stories.
---

# PRD Build Loop

Autonomously implement all `passes: false` stories in `prd_file`; stop only for a **Stop Condition**. Do not commit.

## Inputs

- `prd_file` required.
- `progress_file` optional; default: `dirname(prd_file) + "/progress.txt"`.

## Non-Negotiables

- `prd_file` is the only official source for story status/completion.
- `progress_file` is append-only resume/tracking data; never use it as official completion.
- If all stories already have `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
- If required details are missing, ambiguous, contradictory, invalidly ordered, or require a human choice, stop and ask.
- Orchestrator never makes code-affecting changes directly.
- Any code-affecting change must be made by a fresh `implementer`.
- Any new implementer change resets finalization: simplify, review, and verify must rerun on the combined final state.
- Never simplify, review, analyze, or change files ignored by repository `.gitignore`; if ignore status is unclear, skip those files and report uncertainty.

## When to Use

Use this skill for requests like:

- “Implement all failing PRD stories.”
- “Complete every `passes: false` item in this PRD.”
- “Run the PRD build loop.”
- “Resume PRD implementation from progress.”
- “Finish the PRD without stopping between stories.”
- “Implement, simplify, review, verify, and mark PRD stories complete.”
- “Use `prd_file` and `progress_file` to continue until complete.”

## Path Rules

- Resolve `progress_file` from `prd_file`, not from session state, scratchpads, home directories, or `~/.copilot/...`.
- Relative paths are relative to the repo or provided `prd_file`.
- Use the explicit `progress_file` only if provided; otherwise use the default.

## Roles

- **Orchestrator:** selects stories, resumes from `progress_file`, dispatches subagents, applies status rules, verifies after clean review, updates `prd_file`, appends `progress_file`, invokes `self-improve`, and updates reusable nearby `AGENTS.md` guidance.
- **Implementer:** performs story-specific discovery, reads relevant code/tests/docs, designs and makes code changes, runs initial verification, returns a `Progress block`.
- **Requirements collector:** fast-tier subagent that collects/dedupes requirements before final review, returns a `Progress block`.
- **Code simplifier:** runs after all implementation and after every review-fix implementation; scopes only relevant non-ignored changes; returns a `Progress block`.
- **Reviewer:** runs after simplification; reviews relevant non-ignored changes for missing/partial requirements, scope creep, correctness, readability, architecture, security, performance, and similar issues; returns a `Progress block`.

## Progress Discipline

Subagent output is not “consumed” until recorded.

- Every subagent must return a `Progress block`.
- The orchestrator must append every subagent `Progress block` to `progress_file` immediately after the subagent returns and before interpreting, acting on, summarizing, discarding, or moving to another phase.
- This applies to `implementer`, `requirements-collector`, `code-simplifier`, and `reviewer`, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
- Missing a subagent progress entry is a rule violation; append a corrective orchestrator entry if discovered.

## Startup

1. Invoke `subagent-model-router`.
2. Resolve `progress_file`.
3. If `progress_file` exists, read `## Codebase Patterns` and latest entries.
4. Otherwise create it on first append with `## Codebase Patterns` at the top.

## Fresh-Subagent Rule

- Use a fresh subagent for each unit of work.
- Before dispatching an `implementer`, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to select/dispatch work.
- Do not do story-specific repo discovery, code/test reading, behavior verification, or code-affecting work before dispatching an `implementer`.
- If no fresh `implementer` has handled the current code-affecting unit, dispatch one before investigation or changes.

## Phase 1: Implementation Loop

Repeat for the highest-priority `passes: false` story until all failing stories are implemented and awaiting finalization, or a **Stop Condition** applies:

1. Determine next step from `prd_file` and `progress_file`.
2. Dispatch a fresh `implementer` using `./implementer-prompt.md`.
   - Include all story properties, `progress_file`, nearby `AGENTS.md`, and mode such as `initial_implementation` or follow-up.
   - Require a `Progress block`.
   - Do not pre-read story-specific repo files, tests, code, or behavior.
3. Append the returned `Progress block` immediately.
4. Apply **Status Rules**.
5. If implemented but awaiting finalization, record that in `progress_file`; leave `passes: false`.

## Phase 2: Single Finalization Pass

Run once across the combined final state of all Phase 1 changes. Restore review-fix iteration count from `progress_file`; otherwise use `0`.

### 1. Simplify

1. Dispatch a fresh `code-simplifier`.
2. Scope: all relevant non-ignored changes in the combined final state.
3. Do not skip.
4. Append its `Progress block` immediately.

### 2. Review

1. Dispatch a fast-tier `requirements-collector` to collect/dedupe requirements from:
   - `prd_file` and relevant docs in the same directory.
   - GitHub issue references from commit messages, PR metadata, or PRD docs, when available.
2. Append its `Progress block` immediately.
3. Dispatch a fresh `addy-code-reviewer`.
4. Scope: all relevant non-ignored changes after simplification.
5. Do not skip.
6. Append its `Progress block` immediately.

### 3. Fix Review Findings

If review finds issues:

1. If review-fix iteration count is already `3`, stop and ask the user.
2. Increment review-fix iteration count by `1` and append/update it in `progress_file`.
3. Dispatch a fresh `implementer` with `mode: review_fix` and full reviewer findings.
4. Never fix findings directly.
5. Append the implementer `Progress block` immediately.
6. Apply **Status Rules**.
7. Rerun **Simplify** and **Review** on the updated combined final state.
8. Repeat until review is clean, the limit is reached, or a **Stop Condition** applies.

### 4. Verify

- Only after review is clean, run required quality checks for the final state.
- Use checks required by stories, repo guidance, nearby `AGENTS.md`, and standard project scripts needed to validate changed areas.
- Append an orchestrator verification entry immediately.

### 5. Record

1. Invoke `self-improve` to update nearby `AGENTS.md` with reusable guidance only.
2. Set `passes: true` in `prd_file` only for stories satisfying the **Completion Gate**.
3. Append an orchestrator final-state entry.
4. Re-read `prd_file`.

## Completion Gate

Mark a story complete only if:

1. Required implementation was completed by a fresh `implementer`.
2. Latest code-affecting change, including any review fix, was made by a fresh `implementer`.
3. Fresh `code-simplifier` ran after the latest code-affecting change.
4. Fresh `addy-code-reviewer` ran after the latest code-affecting change.
5. If review found issues, a fresh `implementer` fixed them and simplification/review reran after that fix.
6. Review is clean for the final state.
7. Required final-state quality checks passed.

Never treat implementer `DONE`, passing checks alone, confidence, or `progress_file` entries as sufficient.

## Status Rules

- **DONE:** continue.
- **DONE_WITH_CONCERNS:** incomplete unless every concern is explicitly confirmed non-blocking.
- **NEEDS_CONTEXT:** if human decision is required, stop and ask; otherwise provide context and re-dispatch a fresh subagent.
- **BLOCKED:** try better context, a smaller slice, or stronger model; if still blocked, stop and ask.

## Progress File

- Append only; never replace contents.
- Maintain `## Codebase Patterns` at the top.
- Store only reusable general patterns there; never story-specific details.
- Subagents never write `progress_file` directly.
- Record enough to resume exactly:
  - current story
  - implementation state
  - finalization state
  - latest review outcome
  - review-fix iteration count
  - final verification state

Required entry format:

```text
## [Date/Time] - [Story ID or FINALIZATION]
- Role: implementer | requirements-collector | code-simplifier | reviewer | orchestrator
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

Add only reusable guidance:

- module conventions
- non-obvious gotchas
- important file relationships
- testing expectations
- config/environment requirements

Do not add story-specific notes.

## Stop Conditions

Stop only if:

- all stories in `prd_file` have `passes: true`
- a real blocker remains after reasonable unblocking attempts
- `prd_file` has contradictions, invalid ordering, or missing required details needing human correction
- a required human decision is needed
- review-fix iteration limit is reached
- verification failed and needs a human decision

## Before Stopping

Before any response other than exactly `<promise>COMPLETE</promise>`:

1. Re-read `prd_file`.
2. Confirm a **Stop Condition** applies.
3. Append the latest stop-state orchestrator entry to `progress_file`.
4. Ask the user to decide the open question causing the stop.

## Red Flags

- Returning control before all stories have `passes: true` when no **Stop Condition** applies.
- Resolving `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
- Using session-state, scratchpads, home directories, or `~/.copilot/...` for `progress_file`.
- Treating subagent output as consumed before appending its `Progress block`.
- Missing any subagent progress entry, especially `code-simplifier` or `reviewer`.
- Reading story-specific files, tests, code, or behavior before dispatching an `implementer`.
- Making code-affecting changes directly.
- Simplifying, reviewing, analyzing, or changing `.gitignore`-ignored files.
- Skipping simplify or review.
- Verifying before review is clean.
- Fixing review findings without a fresh `implementer`.
- Exceeding review-fix limit.
- Using anything except `prd_file` for official completion.
- Marking `passes: true` before finalization is complete.
