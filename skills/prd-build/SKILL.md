---
name: prd-build
description: Implement PRD stories until all pass, with verification and progress tracking.
---

# PRD Build Loop

You are the orchestrator for a software project.

## Objective

Continue until every story in `prd_file` has `passes: true`.

- `prd_file` is the only source of truth for story status.
- `progress_file` is supplementary only.
- Do not return control to the user unless a **Stop Condition** applies.
- When all stories pass, reply exactly: `<promise>COMPLETE</promise>`

## Roles

**Orchestrator**

- selects the current highest-priority story with `passes: false`
- dispatches subagents
- runs verification
- updates `prd_file`, `progress_file`, and nearby `AGENTS.md`
- never makes code-affecting changes directly

**Implementer**

- does repo discovery, design, code changes, and verification-support work

## Hard Rules

- Use a fresh subagent for each unit of work.
- Any code-affecting change must be done by a fresh `implementer`.
- Code-affecting changes include code, tests, config, migrations, and implementation docs.
- If more code-affecting work is needed, dispatch a fresh `implementer`; never fix it directly.
- Any new implementer change resets verification; verify again after it.
- Never commit changes.
- Never start another story until the current story is either:
  - marked `passes: true` in `prd_file`, or
  - blocked under **Stop Condition**.
- Keep instructions compact and explicit.

## Inputs

- `prd_file` (required)
- `progress_file` (optional): default `dirname(prd_file) + "/progress.txt"`

## Startup

1. Resolve `progress_file`.
2. If it exists, read it, especially `## Codebase Patterns`.
3. If not, create it on first append with `## Codebase Patterns` at the top.

## Loop

For the highest-priority story in `prd_file` with `passes: false`:

1. **Implement**
   - Dispatch a fresh `implementer` with `./implementer-prompt.md`
   - Pass all story properties, `progress_file`, and `mode: implementation`
   - Wait for the result and apply **Status Rules**
   - Do not continue until resolved

2. **Verify**
   - Run the required quality checks for the current state
   - If verification fails and code-affecting work is needed:
     - Dispatch a fresh `implementer`
     - Pass all story properties, `progress_file`, `mode: verification_fix`, and full failure details
     - Apply **Status Rules**
     - Verify again
     - Repeat until verification passes or a **Stop Condition** applies

3. **Improve process**
   - Invoke `self-improve` once, if not already invoked
   - It must not modify code or override this workflow

4. **Record**
   Perform in this order:
   1. Update nearby `AGENTS.md` with reusable guidance only.
   2. Evaluate the **Completion Gate**.
   3. If the gate passes:
      - update the current story in `prd_file` to `passes: true`
      - save and re-read `prd_file`
      - confirm the story now shows `passes: true`
   4. If the gate fails:
      - do not change `passes`
      - do not append a completion entry
      - do not start another story
      - continue the current story unless a **Stop Condition** applies
   5. Only after confirming `passes: true`, append a progress entry to `progress_file`.
   6. Re-read `prd_file`.
   7. If any story still has `passes: false`, continue with the next highest-priority story.
   8. Do not return control to the user between stories.

## Completion Gate

Mark a story complete only if all are true for the current state:

1. the latest code-affecting change was made by a fresh `implementer`
2. required quality checks passed after that latest change
3. all story requirements in `prd_file` are satisfied

Implementer `DONE`, confidence, or `progress_file` updates do not satisfy this gate.

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

- Append only; never replace contents
- Keep `## Codebase Patterns` at the top
- Put only reusable general patterns there, never story-specific details

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

- all stories in `prd_file` have `passes: true`, or
- a real blocker remains after reasonable unblocking attempts, or
- `prd_file` has contradictions, invalid ordering, or missing required details that need human correction

## Before Stopping

Before any response other than `<promise>COMPLETE</promise>`:

1. Re-read `prd_file`
2. Confirm a **Stop Condition** is true
3. If any story still has `passes: false` and no **Stop Condition** applies, continue the loop

## Red Flags

- returning control after one story while another still has `passes: false`
- making code-affecting changes directly
- verifying before the latest implementer change is complete
- fixing verification failures without a fresh `implementer`
- using anything except `prd_file` as the official completion source
- appending a completion progress entry before confirming `passes: true`
- starting the next story before the current story is complete or blocked
- missing the progress entry or its learnings section
