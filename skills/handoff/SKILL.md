---
name: handoff
description: Save a concise session handoff that another agent can continue from. Use this whenever the user asks to save progress, write a handoff, capture current session state, create a continuation note, or preserve enough context for a future agent session to resume work. Before writing, invoke addy-context-engineering to decide what context is worth carrying forward, then write handoff.md under .agents/scratchpad/ or the active feature subfolder when a scratchpad spec.md or plan.md is already in scope.
---

# Handoff

Create `handoff.md`: a short continuation artifact for the next agent. Preserve only the durable context needed to resume cleanly. Do not turn the handoff into a transcript.

## Use this skill when

- The user asks to save progress, write a handoff, capture current state, or leave resumable context for another agent session.
- Work is stopping midstream and the next agent will need the goal, current status, blockers, and next step.
- A `.agents/scratchpad/<feature>/spec.md` or `plan.md` is already in scope and the handoff should stay with that feature folder.

Do not use this to create a full spec, a full implementation plan, repo documentation, or a transcript archive. Do not use it when the user wants execution to continue now.

## Fast path

Use the checklist below even if you do not need the full text of `addy-context-engineering`.

1. **Invoke `addy-context-engineering` first**
   - Keep only the minimum durable context: rules/conventions, active scratchpad artifacts, touched files, blockers, and the next task boundary.

2. **Resolve the output path**
   - If the request explicitly names `.agents/scratchpad/<feature>/plan.md` or `spec.md`, use `.agents/scratchpad/<feature>/handoff.md`.
   - Otherwise reuse the most recent `.agents/scratchpad/<feature>/plan.md` or `spec.md` already in scope this session.
   - If no feature-scoped scratchpad artifact is in scope, use `.agents/scratchpad/handoff.md`.
   - If two feature folders are equally plausible, ask instead of guessing.
   - Never write outside `.agents/scratchpad/`.

3. **Load only what matters**
   - Read `AGENTS.md` and narrower instruction files already in scope.
   - Read the active scratchpad `spec.md` or `plan.md` if one exists.
   - Read only the specific files, diffs, or errors needed to explain current status and the next step.
   - Do not reread the whole repo just to produce a handoff.

4. **Write the handoff**
   - Aim for roughly 150-300 words plus short file bullets. Be shorter if little progress exists.
   - Capture the goal, current status, decisions/constraints, relevant files, blockers, and the single best next step.
   - If work has not started, say so plainly in `Current Status`.

5. **Reply with status**
   - Report the absolute path to `handoff.md`.
   - Say whether it is feature-scoped or root-scoped.
   - Add one line about the most important thing the next agent should know.

## Keep / Skip

Keep:

- goal and active work item
- what is done, in progress, and next
- decisions, constraints, and real blockers
- 3-8 relevant files, each with a short reason
- the single best next step

Skip:

- full chat transcripts
- raw command logs unless a specific error message is the blocker
- routine investigation narration
- speculative future work that is not grounded in this session

## Handoff Template

Write `handoff.md` using this exact structure:

```markdown
# Handoff

## Goal
- ...

## Current Status
- Done: ...
- In progress: ...
- Next up: ...

## Decisions and Constraints
- ...

## Relevant Files
- `path` — why it matters

## Open Questions or Blockers
- None.
or
- ...

## Recommended Next Step
- ...
```

## Before finishing

- Confirm the output path is under `.agents/scratchpad/`, and use the feature subfolder when a scratchpad spec or plan is in scope.
- Confirm `handoff.md` uses the exact headings and order from the template.
- Confirm every `Relevant Files` entry includes a short reason it matters.
- Confirm the summary is concise and continuation-oriented rather than a transcript.
- Confirm the final response includes the absolute path, the scope, and the most important next-session note.
