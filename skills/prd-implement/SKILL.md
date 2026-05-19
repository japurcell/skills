---
name: prd-implement
description: Implement one failing PRD user story, run checks, update progress, and commit.
---

# Agent Instructions

You are an autonomous coding agent working on a software project.

## Inputs

- `prd_file` (required)
- `progress_file` (default: `<same location as $prd_file>/progress.txt`)

## Task

Complete exactly ONE user story per iteration:

1. Invoke `context-engineering`, `karpathy-guidelines`, and `tdd` if not already invoked.
2. Read `progress_file`, starting with the `## Codebase Patterns` section if present.
3. In `prd_file`, select the highest-priority user story with `passes: false`.
4. Read only the files needed for that story:
   - If the story includes `filesLikelyTouched`, read those first.
   - Also read relevant tests, nearby `AGENTS.md`, and any other files required to complete the steps below.
   - Avoid unrelated exploration.
5. If requirements are ambiguous and codebase patterns do not resolve them, stop and ask the user.
   - If the PRD conflicts with existing code patterns, surface the conflict and ask which to follow.
6. Write a failing test for the expected behavior (RED).
7. Implement the minimum change needed to make the test pass (GREEN).
8. Run required quality checks for the project (for example: typecheck, lint, test).
9. Dispatch a `code-simplifier` subagent and wait for it to finish. Do not invent unavailable agent roles.
10. Record any simplifications made for the progress report.
11. Dispatch an `addy-code-reviewer` subagent and wait for feedback. Do not invent unavailable agent roles.
12. Address reviewer feedback.
13. Run the required quality checks again.
14. Invoke the `self-improve` skill.
15. Update nearby `AGENTS.md` files only if you discovered genuinely reusable guidance for future work in those directories.
16. If all checks pass:
    - Mark the completed story in `prd_file` as `passes: true`
    - Append a progress entry to `progress_file`
    - Create exactly 1 commit containing all changes for this story with message: `feat: [Story ID] - [Story Title]`

## Progress Report

Append to `progress_file` only. Never replace its contents.

Format:

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

The **Learnings for future iterations** section is required.

## Codebase Patterns

Maintain a `## Codebase Patterns` section at the top of `progress_file` (create it if missing).

Add only general, reusable patterns that will help with future stories. Do not add story-specific details.

Examples:

- Use `sql<number>` templates for aggregations
- Always use `IF NOT EXISTS` for migrations
- Export types from `actions.ts` for UI components

## AGENTS.md Updates

When deciding whether to update `AGENTS.md` files:

1. Look at the directories you edited.
2. Check for `AGENTS.md` in those directories or their parents.
3. Add only reusable guidance, such as:
   - module-specific conventions or API patterns
   - non-obvious gotchas or requirements
   - important file relationships or dependencies
   - testing expectations
   - config or environment requirements

Good examples:

- When modifying X, also update Y to keep them in sync
- This module uses pattern Z for API calls
- Tests require the dev server on port 3000
- Field names must match the template exactly

Do not add:

- story-specific implementation details
- temporary debugging notes
- information better kept only in `progress_file`

## Quality Requirements

- Keep changes focused and minimal.
- Follow existing code patterns.
- Do not commit broken code.
- All commits must pass the project’s required quality checks.

## Stop Condition

After finishing the story, check whether all user stories in `prd_file` now have `passes: true`.

- If yes, reply exactly:
  `<promise>COMPLETE</promise>`
- If no, end normally.

## Important

- Work on only ONE user story per iteration.
- Keep CI green.
- Always read `progress_file` first, especially `## Codebase Patterns`.
- Read only the files needed to complete the workflow correctly.
