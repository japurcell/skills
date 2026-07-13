---
name: prd-ralph
description: Complete exactly one eligible unfinished task from prd.json, verify it, update progress, and optionally commit only scoped task changes.
---

# /prd-ralph

## Inputs

- `prd_file` required
- `progress_file` default: `<dirname(prd_file)>/progress.txt`
- `task_id` optional
- `commit` default: `true`; if `false`, do not commit

## Rules

- Do at most one task.
- `prd_file` is the source of truth.
- Set `passes: true` only after verification passes.
- Never start dependency-blocked tasks.
- Do not invent commands, paths, requirements, or acceptance criteria.
- Keep changes minimal and task-scoped.
- Preserve unrelated user changes.
- Append progress after any attempted task.
- Never commit `prd_file` or `progress_file`.

## Workflow

1. Load context:
   - Read `prd_file`.
   - Resolve `progress_file`; if missing, create it with:
     ```text
     ## Codebase Patterns
     ```
   - Read progress, especially `## Codebase Patterns`.
   - Read applicable `AGENTS.md`.
   - Run:
     ```bash
     git log --oneline -20
     git status --short
     ```

2. If all `tasks[].passes` are `true`, output exactly:

   ```xml
   <promise>COMPLETE</promise>
   ```

   Then stop.

3. Select one task:
   - If `task_id` is provided, use it only if it exists, has `passes: false`, and all `dependsOn` tasks have `passes: true`; otherwise stop with the reason.
   - Otherwise choose the incomplete eligible task with the lowest numeric `priority`; break ties by array order.
   - If incomplete tasks exist but none are eligible, stop and list blockers.

4. Implement with TDD:
   - Use the `tdd` skill.
   - RED: add a failing test for the task behavior.
   - GREEN: make the minimum change to pass.
   - REFACTOR: only if needed while tests stay green.
   - Follow the task `description`, `acceptanceCriteria`, `filesLikelyTouched`, `designGuidance`, repo patterns, and applicable `AGENTS.md`.

5. Verify:
   - Run exact verification commands from `acceptanceCriteria` when present.
   - For “typecheck passes,” use the repo’s existing typecheck command.
   - If browser verification is required, use `playwright-cli`.
   - Do not add unrelated verification gates.

6. Append progress to `progress_file`:

   ```text
   ## [Date/Time] - [Task ID]
   - Implemented: ...
   - Files changed: ...
   - Verification: ...
   - Learnings:
     - ...
   ---
   ```

   - Use the real date/time and selected task ID.
   - Include every field.
   - If no durable learnings, write:
     ```text
     - None beyond task-specific implementation details.
     ```
   - Confirm the block was appended and well formed.
   - Add reusable repo notes to top `## Codebase Patterns` only when broadly useful.
   - Use `self-improve` only for durable repo knowledge worth preserving in nearby `AGENTS.md`.

7. If verification failed:
   - Do not update `passes`.
   - Do not commit.
   - Summarize failure and next steps.
   - Stop.

8. If verification passed:
   - Set the selected task’s `passes` to `true` in `prd_file`.
   - If `commit` is `false`, do not commit.
   - Otherwise commit only task-related code/test/doc changes, excluding `prd_file` and `progress_file`.
   - Before committing, inspect staged changes to ensure scope.
   - Commit message:
     ```text
     feat: [Task ID] - [Task Title]
     - Added [specific changes]
     - Verified with [tests, commands, or manual checks]
     ```
   - If commit is blocked, report the intended message and ask how to proceed.

9. Final response:
   - Reread `prd_file`.
   - If all `tasks[].passes` are `true`, output exactly:
     ```xml
     <promise>COMPLETE</promise>
     ```
   - Otherwise give a concise summary of task, verification, files changed, and commit status.
