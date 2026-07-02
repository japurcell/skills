---
name: prd-ralph
description: Implement one eligible task from prd.json, verify it, update progress, and commit.
disable-model-invocation: true
---

# /prd-ralph

## Inputs

- `prd_file` required: path to `prd.json`
- `progress_file` optional: defaults to `dirname(prd_file) + "/progress.txt"`
- `task_id` optional: specific task to implement; it must be incomplete and have all dependencies passing.

## Workflow

1. Read `prd_file`.
2. Resolve `progress_file`. If missing, create it with `## Codebase Patterns`.
3. Read `## Codebase Patterns` from `progress_file`.
4. If every `tasks[].passes` is `true`, reply with `<promise>COMPLETE</promise>`.
5. Select the task to implement:
   - If `task_id` is provided, select that task only if it exists, has `passes: false`, and every `dependsOn` task has `passes: true`.
   - Otherwise, select the incomplete task with the lowest numeric `priority` where every `dependsOn` task has `passes: true`.
   - If incomplete tasks exist but none are eligible, stop and explain the blocking dependencies.
6. Run `/tdd` and implement only that task.
   - Use `description`, `acceptanceCriteria`, `filesLikelyTouched`, and `designGuidance`.
   - Keep changes focused and minimal.
   - Follow existing repo patterns and nearby `AGENTS.md`.
7. Run the task’s required verification.
   - Use exact commands from `acceptanceCriteria` when present.
   - Always satisfy `Typecheck passes`.
   - If the task requires browser verification, use the `playwright-cli` skill.
8. If verification fails:
   - Do not mark the task complete.
   - Append progress with failure details.
   - Stop without committing.
9. If verification passes:
   - Set that task’s `passes` to `true` in `prd_file`.
   - Append progress to `progress_file`.
   - Add reusable patterns to the top `## Codebase Patterns` section only if broadly useful.
   - Run `/self-improve` only if you discovered durable, reusable repo knowledge worth preserving in nearby `AGENTS.md`.
   - Commit all task-related changes with message: `feat: [Task ID] - [Task Title]`.

## Progress append format

APPEND to `progress_file`:

```text
## [Date/Time] - [Task ID]
- Implemented: ...
- Files changed: ...
- Verification: ...
- Learnings:
  - ...
---
```

The learnings section is critical. It helps future iterations avoid repeating mistakes and understand the codebase better.

## Rules

- Work on exactly one task per invocation.
- `prd_file` is the official completion source.
- Never mark `passes: true` unless verification passed.
- Do not start tasks with incomplete dependencies.
- Do not implement out-of-scope or unrelated work.
- Do not invent commands, paths, or requirements.
- Keep CI green.

## Stop condition

After the task, reread `prd_file`.

If every `tasks[].passes` is `true`, reply with `<promise>COMPLETE</promise>`.

Otherwise, end normally.
