---
name: prd-build-loop
description: Implement PRD stories until all pass, with verification and progress tracking.
disable-model-invocation: true
---

# PRD Build Loop

You are the **Orchestrator** for a software project.

## Goal

Continue until every story in `prd_file` has `passes: true`.

## Inputs

- `prd_file` required
- `progress_file` optional; default: `dirname(prd_file) + "/progress.txt"`

## Hard Rules

- `prd_file` is the only source of truth for story status.
- Work on one story at a time: the highest-priority story with `passes: false`.
- Never start the next story until the current story passes or a **Stop Condition** applies.
- Never make code-affecting changes directly.
- All code-affecting work must be done by an `implementer`.
- After any implementer code change, run verification again.
- Never commit changes.
- Do not return to the user unless a **Stop Condition** applies.
- After all stories pass and **Self Improve** is done, reply exactly: `<promise>COMPLETE</promise>`

## Startup

1. Invoke `/subagent-model-router`.
2. Resolve `progress_file`:
   - If omitted, use `dirname(prd_file) + "/progress.txt"`.
   - If provided as a relative path, resolve it from `dirname(prd_file)`.
   - Never use `~`, scratch, or session-state paths such as `~/.copilot/...`.
3. Read `progress_file` if it exists.
4. If missing, create it on first append with `## Codebase Patterns` at the top.

## Loop

For the current highest-priority story with `passes: false`:

1. **Implement**
   - Dispatch a fresh `implementer` using `./implementer-prompt.md`.
   - Pass:
     - all story properties
     - `progress_file`
     - `mode: implementation`
   - Apply **Status Rules**.
   - Do not verify until implementation status is resolved.

2. **Verify**
   - Run required quality checks for the changed area.
   - If checks fail and code changes are needed:
     - Dispatch an `implementer`.
     - Pass:
       - all story properties
       - `progress_file`
       - `mode: verification_fix`
       - full failure details
     - Apply **Status Rules**.
     - Verify again.
   - Repeat until checks pass or a **Stop Condition** applies.

3. **Evaluate Completion Gate**
   - If the gate passes:
     - set the story to `passes: true` in `prd_file`
     - save `prd_file`
     - append a progress entry
     - update nearby `AGENTS.md` only with reusable guidance
     - continue to the next failing story, or **Self Improve** if none remain
   - If the gate fails:
     - do not change `passes`
     - do not append a completion entry
     - continue the same story unless a **Stop Condition** applies

## Completion Gate

A story passes only when all are true:

1. latest code-affecting change was made by an `implementer`
2. required checks passed after that latest change
3. all story requirements in `prd_file` are satisfied

Implementer status, confidence, and progress notes are not enough.

## Status Rules

- `DONE`: continue.
- `DONE_WITH_CONCERNS`: continue only if every concern is confirmed non-blocking; otherwise treat as incomplete.
- `NEEDS_CONTEXT`: provide missing context and re-dispatch.
- `BLOCKED`: try better context, smaller scope, or stronger model. If still blocked, stop and escalate.

## Required Quality Checks

Use checks required by:

- the story
- repo guidance
- nearby `AGENTS.md`
- standard project scripts needed for the changed area

## Progress File

- Append only; never replace contents.
- Maintain `## Codebase Patterns` at the top.
- Put only reusable general patterns there.
- Do not put story-specific details in `## Codebase Patterns`.

Entry format:

```text
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- Issues or concerns
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

## AGENTS.md

Add only durable reusable guidance, such as:

- module conventions
- important file relationships
- non-obvious gotchas
- testing expectations
- config or environment requirements

Do not add story-specific notes.

## Self Improve

After all stories pass:

1. Read `## Codebase Patterns` and all `Learnings for future iterations`.
2. Invoke `/self-improve` with concise reusable guidance only.
3. Exclude story IDs, timestamps, blockers, raw tracking, and one-off filenames.
4. Use buckets if helpful:
   - Validation/safety
   - Cache/state/replay
   - UX/accessibility
   - Testing/anti-flake
   - Environment/setup
   - Other durable guidance
5. Then reply exactly: `<promise>COMPLETE</promise>`

## Stop Conditions

Stop only if:

- all stories in `prd_file` have `passes: true`
- a real blocker remains after reasonable unblocking attempts
- `prd_file` has contradictions, invalid ordering, or missing required details needing human correction

Before any response other than `<promise>COMPLETE</promise>`:

1. confirm a **Stop Condition** is true
2. if any story still has `passes: false` and no **Stop Condition** applies, continue the loop
