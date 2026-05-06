---
name: handoff
description: Save a concise session handoff that another agent can continue from. Use this whenever the user asks to save progress, write a handoff, capture current session state, create a continuation note, or preserve enough context for a future agent session to resume work. Before writing, invoke addy-context-engineering to decide what context is worth carrying forward, then write handoff.md under .agents/scratchpad/ or the active feature subfolder when a scratchpad spec.md or plan.md is already in scope.
---

# Handoff

## Overview

Create a compact, continuation-oriented artifact for the next agent session. Preserve the durable context the next agent needs to resume cleanly, without forcing it to reconstruct the session from chat history or raw logs.

## When to Use

- Use when the user asks to save progress, write a handoff, capture current session state, create a continuation note, or leave resumable context for another agent session.
- Use when work is stopping midstream and the next agent will need the goal, current state, key decisions, blockers, and next step.
- Use when there is already a `.agents/scratchpad/<feature>/spec.md` or `plan.md` in scope and the next session should stay anchored to that feature workspace.
- Do not use this to create a full spec, a full implementation plan, long-form repo documentation, or a transcript archive.
- Do not use this when the user wants execution to continue now rather than saving a checkpoint for later.

## Workflow

1. **Invoke `addy-context-engineering` first**
   - Use it to decide which context is durable enough to save.
   - Prefer the minimum useful set: rules files and conventions, active spec or plan artifacts, touched or inspected source files, blockers, and the next task boundary.

2. **Resolve the output path**
   - If the user's latest request explicitly names `.agents/scratchpad/<feature>/plan.md` or `.agents/scratchpad/<feature>/spec.md`, treat that as the active feature context.
   - Otherwise reuse the most recent `.agents/scratchpad/<feature>/plan.md` or `.agents/scratchpad/<feature>/spec.md` path created or mentioned earlier in the current session.
   - If a feature-scoped scratchpad artifact is found, write the handoff beside it as `.agents/scratchpad/<feature>/handoff.md`.
   - If no feature-scoped scratchpad artifact is in scope, write `.agents/scratchpad/handoff.md`.
   - If two different feature directories are equally plausible and you cannot tell which one is active, ask the user instead of guessing.
   - Never write outside `.agents/scratchpad/`.

3. **Load only the context that matters**
   - Read `AGENTS.md` and any narrower instruction files already in scope.
   - Read the active scratchpad `spec.md` or `plan.md` if one exists.
   - Read only the specific files, diffs, task artifacts, or error output needed to explain the current state and next step.
   - Do not reread the whole repository just to produce a handoff.

4. **Write a concise, resume-ready handoff**
   - Keep the handoff compact: roughly 150-300 words plus short file bullets. Be shorter if little progress exists.
   - Capture the goal, current status, decisions and constraints, relevant files, blockers, and the single best next step.
   - If work has not started yet, say so plainly in `Current Status` and anchor the next agent to the active spec or plan, if one exists.

5. **Reply with the handoff status**
   - Report the absolute path to `handoff.md`.
   - Say whether it was written to a feature-scoped scratchpad directory or the root scratchpad.
   - Add a one-line note about the most important thing the next agent should know.

## Context Selection Rules

Prioritize durable context over narration. Capture:

- **Goal**: what the user wanted and which feature or work item is active
- **Current status**: what is done, in progress, and next
- **Decisions and constraints**: assumptions, repo rules, path rules, or implementation choices that now matter
- **Relevant files**: 3-8 paths, each with a one-line reason it matters
- **Open questions or blockers**: only real unresolved items
- **Recommended next step**: the single best next action

Do not include:

- a full chat transcript
- raw command logs unless a specific error message is the blocker
- repeated narrative about routine investigation
- speculative future work that is not grounded in the current session

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

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "I'll just dump the transcript so the next agent has everything." | A transcript hides the important state inside noise. A handoff should surface only the durable context needed to continue. |
| "There was a spec earlier, but I'll save to `.agents/scratchpad/handoff.md` to keep things simple." | That breaks feature locality. When a scratchpad spec or plan is in scope, the handoff belongs in the same feature directory. |
| "I remember the key points, so I don't need to invoke `addy-context-engineering` first." | This skill depends on disciplined context selection. Skipping that step increases the chance of missing the exact artifacts the next agent will need. |
| "The next step is obvious, so I don't need to write it down." | A handoff without a concrete next step forces the next agent to re-plan before it can act. |

## Red Flags

- The handoff is saved outside `.agents/scratchpad/`.
- A feature-scoped `spec.md` or `plan.md` was in scope, but the handoff was written to the root scratchpad anyway.
- The handoff reads like a transcript or status diary instead of a continuation artifact.
- `Relevant Files` lists paths without saying why they matter.
- The handoff omits blockers, constraints, or the next step.
- The agent skipped `addy-context-engineering` and guessed what context to keep.

## Verification

After writing the handoff, confirm:

- [ ] `addy-context-engineering` was invoked first and used to decide what context to preserve.
- [ ] The output path is under `.agents/scratchpad/`, and the active feature subfolder was used when a scratchpad spec or plan was in scope.
- [ ] `handoff.md` uses the exact required headings and order from the template.
- [ ] The summary is concise and continuation-oriented rather than a transcript.
- [ ] Every entry in `Relevant Files` includes a short reason the file matters.
- [ ] The final response reports the absolute handoff path, whether it is feature-scoped or root-scoped, and the most important next-session note.
