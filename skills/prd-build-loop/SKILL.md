---
name: prd-build-loop
description: Implement failing PRD stories with required simplification, review, verification, and progress tracking.
---

# PRD Build Loop

You are an autonomous orchestrator for a software project.

## Core Objective

Keep running this workflow until every story in `prd_file` has `passes: true`.
If any story in `prd_file` still has `passes: false`, remain in the loop and continue.
Do not return control to the user after completing a story unless **Stop Condition** is met.

## Rules

- `prd_file` is the only authority for story status. A story is complete only when `passes: true` in `prd_file`.
- `progress_file` is supplementary only.
- Use a fresh subagent for each unit of work.
- Any code-affecting change (code, tests, config, migrations, implementation docs) must be done by a fresh `implementer`.
- The orchestrator must never make code-affecting changes directly.
- If no fresh `implementer` has handled the exact current unit of work, dispatch one before any code-affecting action.
- Any new implementer change resets the requirement to review and verify.
- Do not commit changes.
- Do not stop after finishing one story if another story still has `passes: false`.
- Stop only per **Stop Condition**.

## Roles

**Orchestrator**

- selects stories
- dispatches subagents
- applies status rules
- runs or verifies required checks
- updates `prd_file`, `progress_file`, and reusable guidance in nearby `AGENTS.md`

**Implementer**

- performs repo discovery, design, code changes, and verification

## Inputs

- `prd_file` (required)
- `progress_file` (optional): default `dirname(prd_file) + "/progress.txt"`

## Startup

1. Invoke `context-engineering` and `karpathy-guidelines` if not already invoked.
2. Resolve `progress_file`.
3. If `progress_file` exists, read it, especially `## Codebase Patterns`.
4. If it does not exist, create it on first append with `## Codebase Patterns` at the top.

## Loop

For the highest-priority story in `prd_file` with `passes: false`:

1. **Implement**
   - Dispatch a fresh `implementer` with `./implementer-prompt.md`
     - Include all story properties, `progress_file`, and `mode: initial_implementation`
     - Instruct the subagent to invoke `context-engineering`
   - Wait for the result and apply **Status Rules**
   - Do not continue until resolved
2. **Simplify**
   - Dispatch a fresh `code-simplifier`
   - Wait for completion
   - Do not skip
3. **Review**
   - Dispatch a fresh `addy-code-reviewer`
   - Wait for feedback
   - Do not skip
4. **Fix review findings**
   - If review finds issues:
     - Dispatch a fresh `implementer` with all story properties, `progress_file`, `mode: review_fix`, and full reviewer findings
     - Never fix findings directly
     - Wait for the result and apply **Status Rules**
     - Then run **Review** again
     - Repeat until review is clean or **Stop Condition** is reached
5. **Verify**
   - Run required quality checks after the final clean review
6. **Improve process**
   - Invoke `self-improve` only if not already invoked
   - It must not modify code or override this workflow
7. **Record**
   - Update nearby `AGENTS.md` only with reusable guidance
   - Set `passes: true` in `prd_file` only if the **Completion Gate** is satisfied
   - If the **Completion Gate** is not satisfied, do not mark complete and do not start another story
   - Append a progress entry to `progress_file`
   - Immediately re-read `prd_file`
   - If any story still has `passes: false`, continue the loop with the next highest-priority story
   - Do not return control to the user between stories
     When all stories have `passes: true`, reply exactly:
     `<promise>COMPLETE</promise>`

## Completion Gate

A story may be marked complete only if, for its current state:

1. the latest code-affecting change was made by a fresh `implementer`
2. a fresh `code-simplifier` ran after that latest change
3. a fresh `addy-code-reviewer` ran after that latest change
4. if review found issues, a fresh `implementer` fixed them, then review ran again after that fix
5. review is clean for the current state
6. required quality checks passed after the final clean review

Implementer `DONE`, passing checks, confidence, or `progress_file` updates do not satisfy this gate.

## Status Rules

- **DONE:** continue
- **DONE_WITH_CONCERNS:** treat as incomplete unless every concern is explicitly confirmed non-blocking
- **NEEDS_CONTEXT:** provide missing context and re-dispatch a fresh subagent
- **BLOCKED:** try better context, a smaller slice, or a stronger model; if still blocked, stop and escalate

## Required Quality Checks

Use checks required by:

- the story
- repository guidance
- `AGENTS.md`
- standard project scripts needed to validate the changed area

## Progress File

- Append only; never replace contents
- Keep a `## Codebase Patterns` section at the top
- Add only reusable general patterns there, never story-specific details

Required entry format:

```text
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
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

## Before Stopping

Before any response that is not exactly `<promise>COMPLETE</promise>`:

1. Re-read `prd_file`
2. Confirm that at least one **Stop Condition** is true
3. If any story still has `passes: false` and no **Stop Condition** applies, continue the loop instead of stopping

## Red Flags

- returning control after completing one story while another story still has `passes: false`
- reading extra repo context before dispatching the implementer
- drafting patches or changing code directly
- skipping simplify or review
- verifying before review is clean for the current state
- fixing review findings without a fresh `implementer`
- treating implementer `DONE` or passing checks as sufficient for completion
- starting the next story before the current one has `passes: true`
- using anything except `prd_file` to decide official completion
- missing the progress entry or its learnings section
