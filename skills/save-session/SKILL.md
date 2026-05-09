---
name: save-session
description: Save a short continuation note for a future agent session. Keep only durable context, then write `save-session.md` under `.agents/scratchpad/` or the active in-scope feature subfolder.
---

# Save Session

Create `save-session.md` for the next agent. Keep it short and durable. Do not write a transcript.

## Use this skill when

- The user asks to save progress, write a continuation note, capture session state, or leave resumable context.
- Work is stopping mid-task and another agent may continue later.

Do not use this for a full spec, full plan, repo docs, or when the user wants work to continue now.

## Rules

1. **Keep only durable context**
   - Include only what a future agent needs: goal, status, constraints, blockers, touched files, durable learnings, and next step.
   - If available, invoke `addy-context-engineering` first.
   - If unavailable, apply the same principle directly.

2. **Choose the output path**
   - Never write outside `.agents/scratchpad/`.
   - If the user explicitly names `.agents/scratchpad/<feature>/spec.md` or `plan.md`, write `.agents/scratchpad/<feature>/save-session.md`.
   - Otherwise, if a feature `spec.md` or `plan.md` is already in scope this session, write to that feature folder.
   - Otherwise write `.agents/scratchpad/save-session.md`.
   - If two feature folders are equally plausible, ask instead of guessing.

3. **What counts as in scope**
   - A scratchpad artifact is in scope if it was explicitly referenced by the user, read in this session, or modified in this session.
   - If multiple are in scope, prefer the one most recently modified; if none were modified, prefer the one most recently read.

4. **Read only what matters**
   - Read applicable instruction files already in scope, including relevant `AGENTS.md`.
   - Read the active scratchpad `spec.md` or `plan.md` if one exists.
   - Read only the files, diffs, or errors needed to explain status and next step.
   - Do not reread the whole repo just to save session state.

5. **Write concisely**
   - Target about 150-300 words plus short file bullets.
   - Be shorter if little progress exists.
   - If no work has started, say so in `Current Status`.

6. **If something goes wrong**
   - If the path is ambiguous, ask the user.
   - If writing fails, provide the draft inline and explain why.
   - If `.agents/scratchpad/` is missing, create it if allowed; otherwise ask.

## Keep / Skip

Keep:

- goal
- done / in progress / next
- useful suggested skills
- decisions, constraints, blockers
- durable learnings
- smallest useful set of relevant files, each with a reason
- one best next step

Skip:

- full transcript
- routine investigation details
- raw command logs unless an error is the blocker
- speculative future work not grounded in this session

## Durable Learnings

Use one short line per item.

Good examples:

- commands that were useful
- code patterns or conventions followed
- tests that worked
- environment quirks
- warnings or gotchas

Format:

- `<command-or-pattern>` - `<brief-description>`

If none, write:

- `- None.`

## Template

Write `save-session.md` using this exact structure:

```markdown
# Save Session

## Goal

- ...

## Current Status

- Done: ...
- In progress: ...
- Next up: ...

## Suggested Skills

- <skill-name> - reason
- ...

## Decisions and Constraints

- ...

## Relevant Files

- `path` — why it matters

## Durable Learnings

- <command-or-pattern> - <brief-description>
- ...

## Open Questions or Blockers

- None.
  or
- ...

## Recommended Next Step

- ...
```

Allow explicit empties:

- `## Suggested Skills` → `- None.`
- `## Relevant Files` → `- None.`
- `## Durable Learnings` → `- None.`

## Before finishing

- Confirm the file path is under `.agents/scratchpad/`.
- Confirm the headings and order exactly match the template.
- Confirm each `Relevant Files` entry has a reason.
- Confirm the note is concise and continuation-oriented.
- In your final reply, include:
  - the absolute path
  - whether it is feature-scoped or root-scoped
  - the single most important note for the next agent
