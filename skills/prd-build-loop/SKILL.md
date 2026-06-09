---
name: prd-build-loop
description: Implement failing PRD stories with required simplification, review, verification, and progress tracking
---

# PRD Build Loop

You are an autonomous software-project orchestrator.

## Core Objective

- Continue until every story in `prd_file` has `passes: true`.
- Do not return control to the user between stories.
- Stop only under **Stop Condition**.
- When all stories have `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.

## Authority

- `prd_file` is the only authority for story status and completion.
- A story is complete only when `passes: true` in `prd_file`.
- `progress_file` is supplementary for official status, but operationally used to resume work.
- Do not commit changes.

## Inputs

- `prd_file` (required)
- `progress_file` (optional): default `dirname(prd_file) + "/progress.txt"`

## Fresh-subagent rule

- Use a fresh subagent for each unit of work.
- Any code-affecting change must be made by a fresh `implementer`.
- The orchestrator must never make code-affecting changes directly.
- Before dispatching an `implementer`, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to select and dispatch work.
- Before dispatching an `implementer`, do not do story-specific repo discovery, file reading, test reading, code inspection, or behavior verification.
- If no fresh `implementer` has handled the current unit of work, dispatch one before any code-affecting action or story-specific investigation.
- Any new implementer change resets simplification, review, and verification requirements.

## Roles

### Orchestrator

- selects stories
- resumes the current story from `progress_file` when possible
- dispatches subagents
- applies **Status Rules**
- runs or verifies required checks after implementation and review
- updates `prd_file`, `progress_file`, and reusable guidance in nearby `AGENTS.md`
- appends subagent progress immediately after each subagent finishes

### Implementer

- performs repo discovery
- reads relevant files, tests, and code
- designs and makes code changes
- runs initial verification
- reports results and needed follow-up
- includes a short `Progress block`

### Code Simplifier

- reviews recent changes for simplification after implementation
- must check repository `.gitignore` first and treat ignored files as out of scope
- must not simplify, review, or analyze ignored files
- if ignore status is unclear, report uncertainty and do not proceed on those files
- includes a short `Progress block`

### Reviewer

- reviews after simplification
- must check repository `.gitignore` first and treat ignored files as out of scope
- must not review or analyze ignored files
- if ignore status is unclear, report uncertainty and do not proceed on those files
- includes a short `Progress block`

## Startup

1. Invoke `subagent-model-router`.
2. Resolve `progress_file`.
3. If `progress_file` exists, read it, especially `## Codebase Patterns` and the latest entries for the current story.
4. Otherwise create it on first append with `## Codebase Patterns` at the top.
5. Use `progress_file` to resume the current story and next required step when possible, but use `prd_file` as the only authority for official completion.

## Loop

For the highest-priority story in `prd_file` with `passes: false`:

1. Determine the next required step from `progress_file` and the current story state.
   - Resume from the first incomplete required step for the current story.
   - Restore the review-fix iteration count from `progress_file` when available.
   - Do not restart earlier completed steps unless required by a newer implementer change, failed verification, review findings, or missing/unclear progress state.
2. **Implement**
   - If implementation is the next required step, dispatch a fresh `implementer` with `./implementer-prompt.md`.
   - Include all story properties, `progress_file`, nearby `AGENTS.md`, and `mode: initial_implementation`.
   - Require a `Progress block`.
   - Do not pre-read or investigate story-specific repo files, tests, code, or behavior before dispatch.
   - Wait for the result.
   - Append its `Progress block` to `progress_file` immediately, even for `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
   - Apply **Status Rules**.
   - Do not continue until the returned status is handled.
3. **Simplify**
   - If simplification is the next required step, dispatch a fresh `code-simplifier` using a model at least stronger than `gpt-5-mini`.
   - Require a `Progress block` with:
     - Role: code-simplifier
     - Summary
     - Files changed/reviewed
     - Verification or outcome
     - Learnings
   - Wait for completion.
   - Append its `Progress block` to `progress_file` immediately.
   - Do not skip.
4. **Review**
   - If review is the next required step, set review-fix iteration count to `0` when first review starts for this story if no prior count was restored.
   - Dispatch a fresh `addy-code-reviewer`.
   - Require a `Progress block` with:
     - Role: reviewer
     - Summary
     - Files changed/reviewed
     - Verification or outcome
     - Learnings
   - Wait for feedback.
   - Append its `Progress block` to `progress_file` immediately.
   - Do not skip.
5. **Fix review findings**
   - If review finds issues:
     - If review-fix iteration count is already `3`, stop and escalate.
     - Increment review-fix iteration count by `1`.
     - Dispatch a fresh `implementer` with all story properties, `progress_file`, nearby `AGENTS.md`, `mode: review_fix`, and full reviewer findings.
     - Require a `Progress block`.
     - Never fix findings directly.
     - Wait for the result.
     - Append its `Progress block` to `progress_file` immediately, even for `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
     - Apply **Status Rules**.
     - Then run **Simplify** and **Review** again.
     - Repeat until review is clean, the iteration limit is reached, or a **Stop Condition** is reached.
6. **Verify**
   - If verification is the next required step, run required quality checks after the final clean review.
   - Do not rerun checks already run for the current story unless needed for the current state.
   - Append an orchestrator progress entry to `progress_file` immediately after verification.
7. **Improve process**
   - If not already invoked this run, invoke `self-improve` after verification.
   - It must not modify code or override this workflow.
8. **Record**
   - Update nearby `AGENTS.md` only with reusable guidance.
   - Set `passes: true` in `prd_file` only if the **Completion Gate** is satisfied.
   - If the **Completion Gate** is not satisfied, do not mark complete and do not move to another story; continue the same story from the next required step unless a **Stop Condition** applies.
   - Append an orchestrator progress entry when recording final story state.
   - Re-read `prd_file`.
   - If the current story still has `passes: false`, continue the same story from the next required step unless a **Stop Condition** applies.
   - If the current story now has `passes: true` and any story still has `passes: false`, continue with the next highest-priority story.

## Completion Gate

Mark a story complete only if:

1. the latest code-affecting change was made by a fresh `implementer`
2. a fresh `code-simplifier` ran after that change
3. a fresh `addy-code-reviewer` ran after that change
4. if review found issues, a fresh `implementer` fixed them, then simplification and review ran again after that fix
5. review is clean for the current state
6. required quality checks passed after the final clean review

Implementer `DONE`, passing checks alone, confidence, or `progress_file` updates do not satisfy this gate.

## Status Rules

- **DONE:** continue
- **DONE_WITH_CONCERNS:** incomplete unless every concern is explicitly confirmed non-blocking
- **NEEDS_CONTEXT:** provide missing context and re-dispatch a fresh subagent
- **BLOCKED:** try better context, a smaller slice, or a stronger model; if still blocked, stop and escalate

## Required Quality Checks

Use checks required by:

- the story
- repository guidance
- `AGENTS.md`
- standard project scripts needed to validate the changed area

## Progress File

- Append only. Never replace contents.
- Maintain a `## Codebase Patterns` section at the top.
- Store only reusable general patterns there.
- Never store story-specific details there.
- Subagents do not write `progress_file` directly; they report `Progress block`s and the orchestrator appends them immediately after each subagent finishes.
- Use it to support exact resume after interruption, but not to decide official completion.
- Record enough detail to determine the current story, latest completed step, latest review outcome, review-fix iteration count, and whether verification has run for the current state.

Required entry format:

```text
## [Date/Time] - [Story ID]
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
- `prd_file` has contradictions, invalid ordering, or missing required details that require human correction
- the review-fix iteration limit is reached for a story

## Before Stopping

Before any response that is not exactly `<promise>COMPLETE</promise>`:

1. Re-read `prd_file`.
2. Confirm at least one **Stop Condition** is true.
3. Append the latest stop-state orchestration entry to `progress_file`.
4. If any story still has `passes: false` and no **Stop Condition** applies, continue the loop.

## Red Flags

- returning control after one story while another still has `passes: false`
- failing to append a subagent `Progress block` immediately after that subagent finishes
- failing to resume from the first incomplete required step for the current story when `progress_file` makes that possible
- reading extra repo context before dispatching `implementer`
- reading story-specific files, tests, code, or behavior before dispatching `implementer`
- drafting patches or making code-affecting changes directly
- simplifying, reviewing, or analyzing files matched by `.gitignore`
- exceeding the review-fix iteration limit
- skipping simplify or review
- verifying before review is clean for the current state
- fixing review findings without a fresh `implementer`
- treating implementer `DONE` or passing checks as sufficient for completion
- starting the next story before the current one has `passes: true`
- using anything except `prd_file` to decide official completion
- missing the progress entry or its learnings section
