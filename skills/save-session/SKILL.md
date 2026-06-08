---
name: save-session
description: Save concise continuation context for a future agent session in `save-session.md` under `.agents/scratchpad/` or the active feature folder. Use when compacting the current session, or the user asks to save progress, capture session state, or leave resumable context.
---
# Save Session
Create a short handoff so another agent can resume work without repeating investigation.

## Use this skill when
- The user asks to save progress, capture session state, or leave resumable context.
- Work is stopping mid-task and another agent may continue later.
- You are compacting the current session.

## Workflow
1. **Gather context**
   - Read relevant in-scope instructions, including applicable `AGENTS.md`.
   - Read the active `spec.md`, `prd.md`, or `plan.md` if present.
   - Read only the files, diffs, commands, test results, or errors needed to explain status and next steps.
   - Do not reread the whole repo.

2. **Choose `$output_path`**
   - If the user explicitly names `.agents/scratchpad/<feature>/spec.md`, `prd.md`, or `plan.md`, use `.agents/scratchpad/<feature>`.
   - Otherwise, if one in-scope feature folder contains `spec.md`, `prd.md`, or `plan.md`, use that folder.
   - Otherwise, use `.agents/scratchpad/`.
   - If multiple feature folders are equally plausible, ask the user.

3. **Write or update `save-session.md`**
   - If `.agents/scratchpad/` does not exist, create it.
   - Write `$output_path/save-session.md`.
   - If it already exists, update it in place and keep only still-useful status, blockers, learnings, file references, and next steps.
   - If no work has started, say so in `Current Status`.
   - Do not copy full chat logs, raw screenshots, or large log dumps unless needed.
   - Do not duplicate content already captured in PRDs, plans, ADRs, issues, commits, or diffs; reference them by path or URL instead.

4. **Handle problems**
   - If the path is ambiguous, ask the user.
   - If writing fails, provide the draft inline and explain why.
   - If an existing `save-session.md` cannot be read, write a fresh version and note that prior contents could not be preserved.

5. **Report output**
   In the final reply, include:
   - the absolute path to the file
   - whether it is feature-scoped or root-scoped
   - the single most important note for the next agent

## Durable Learnings
Good examples:
- useful commands
- code patterns or conventions followed
- tests that worked
- environment quirks
- warnings or gotchas
- human decisions that changed direction

Format:
- `<command-or-pattern>` - `<brief-description>`

If none, write:
- `- None.`

## Template
Write `$output_path/save-session.md` as:

```markdown
# Save Session
## Goal
- ...

## Current Status
- Branch/task: ...
- Done: ...
- In progress: ...
- Next up: ...

## Decisions and Constraints
- ...

## Relevant Files
- `path` — why it matters

## Commands and Results
- `command` — result

## Tests
- Passed: ...
- Still needed: ...

## Durable Learnings
- <command-or-pattern> - <brief-description>

## Open Questions or Blockers
- None.
  or
- ...

## Next-Agent Briefing
- <1 short paragraph with what changed, why, current state, and exact next step>

## Recommended Next Step
- ...
```

Allowed empty sections:
- `## Relevant Files` → `- None.`
- `## Commands and Results` → `- None.`
- `## Tests` → `- None.`
- `## Durable Learnings` → `- None.`

## Rules
- Never write outside `.agents/scratchpad/`.
- Keep it concise, specific, and resume-ready.
- Include exact file paths when relevant.
- Include the exact next step; avoid vague “done”.
- Redact sensitive information, such as API keys, passwords, or personally identifiable information.

## Validation
Before finishing, confirm:
- [ ] the file is under `.agents/scratchpad/`
- [ ] headings and order match the template
- [ ] each `Relevant Files` entry includes a reason
- [ ] the document is concise and useful for the next agent
- [ ] the next step is explicit
