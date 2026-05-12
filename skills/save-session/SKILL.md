---
name: save-session
description: Compact the current conversation into a continuation document for a future agent session. Write `save-session.md` under `.agents/scratchpad/` or the active feature folder in scope.
---

# Save Session

Create a continuation document for the next agent so that it can continue the work without redundant investigation.

## Use this skill when

- The user asks to save progress, write a continuation document, capture session state, or leave resumable context.
- Work is stopping mid-task and another agent may continue later.

## The Workflow

1. **Gather context**
   - If available, invoke `addy-context-engineering` first.
   - If unavailable, apply the same principle directly.
   - Read applicable instruction files already in scope, including relevant `AGENTS.md` files.
   - Read the active scratchpad `spec.md` or `plan.md` if one exists.
   - Read only the files, diffs, or errors needed to explain status and next step.
   - Do not reread the whole repo just to save session state.

2. **Choose the $output_path**
   - If the user explicitly names `.agents/scratchpad/<feature>/spec.md` or `plan.md`, use `.agents/scratchpad/<feature>`.
   - Otherwise, if there is an active in-scope feature folder with `spec.md` or `plan.md`, use that feature folder.
   - Otherwise, use `.agents/scratchpad/`.
   - If multiple candidates remain equally plausible, ask the user.

3. **Write concisely**
   - Target about 150-300 words plus short file bullets.
   - Be shorter if little progress exists.
   - If no work has started, say so in `Current Status`.
   - If `$output_path/save-session.md` already exists, update in place, preserving useful unresolved blockers if still relevant. Preserve existing durable learnings and relevant files only if they still help the next agent resume work quickly; remove stale or redundant items.

4. **If something goes wrong**
   - If the path is ambiguous, ask the user.
   - If writing fails, provide the draft inline and explain why.
   - If `.agents/scratchpad/` is missing, create it.
   - If an existing `$output_path/save-session.md` cannot be read, write a fresh version and note that prior contents could not be preserved.

5. **Report Output**
   In your final reply, include:
     - the absolute path of the generated file
     - whether it is feature-scoped or root-scoped
     - the single most important note for the next agent

## Durable Learnings

Good examples:

- commands that were useful
- code patterns or conventions followed
- tests that worked
- environment quirks
- warnings or gotchas
- human interventions, redirections, or decisions that shaped the session's course

Format:

- `<command-or-pattern>` - `<brief-description>`

If none, write:

- `- None.`

## Template

Write `$output_path/save-session.md` using this template:

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

## Rules

- Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.
- Never write outside `.agents/scratchpad/`.

### Keep / Skip

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

## Validation

Before finishing, confirm:

- [ ] the file path is under `.agents/scratchpad/`.
- [ ] the headings and order match the template.
- [ ] each `Relevant Files` entry has a reason.
- [ ] the document is concise and continuation-oriented.
