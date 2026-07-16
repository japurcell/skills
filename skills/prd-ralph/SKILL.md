---
name: prd-ralph
description: Complete exactly one eligible unfinished task from prd.json, verify it, update progress, and optionally commit only scoped task changes.
---

# /prd-ralph

Complete **one** eligible unfinished PRD task. Verify before marking it passed.

## Inputs

- `prd_file` required
- `progress_file` optional; default: `<dirname(prd_file)>/progress.txt`
- `task_id` optional
- `commit` optional; default: `true`

## Rules

- Do not interview the user. Make reasonable assumptions and record them in `progress_file`.
- Stop if requirements are unsafe, contradictory, missing, or dependency-blocked.
- Do at most one task.
- Treat `prd_file` as source of truth.
- Never start a task unless all `dependsOn` tasks have `passes: true`.
- Never invent commands, paths, requirements, or acceptance criteria.
- Keep changes minimal and task-scoped.
- Preserve unrelated user changes.
- Append progress after any attempted task.
- Set `passes: true` only after required verification passes.
- Never commit `prd_file` or `progress_file`.

## References

Read only when needed:

- `references/browser-verification.md` — browser/UI/auth/routing/interactive verification gate.
- `references/progress.md` — progress entry format.
- `references/commit.md` — scoped commit rules.

## Workflow

### 1. Prepare

1. Read `prd_file`.
2. Resolve `progress_file`.
   - If missing, create it with:
     ```text
     ## Codebase Patterns
     ```
3. Read `progress_file`, especially `## Codebase Patterns`.
4. Read applicable repo guidance, including `AGENTS.md`.
5. Check recent history:
   ```bash
   git log --oneline -20
   ```

### 2. Stop if complete

If all `tasks[].passes` are `true`, output exactly:

```xml
<promise>COMPLETE</promise>
```

Then stop.

### 3. Select one task

If `task_id` is provided, use it only if:

- it exists
- `passes` is `false`
- all dependencies pass

Otherwise stop and report why.

If `task_id` is not provided:

- Select the incomplete eligible task with the lowest numeric `priority`.
- Eligible means `passes: false` and all `dependsOn` tasks have `passes: true`.

If no incomplete task is eligible, stop and list blockers.

### 4. Check browser gate

Read `references/browser-verification.md` if the task mentions or implies browser-visible behavior, including browser, Playwright, `playwright-cli`, interactive validation, UI, auth, routing, navigation, rendering, DOM changes, or client-side interaction.

For UI, auth, or routing work, require browser verification unless the PRD explicitly says otherwise.

### 5. Implement with TDD

Activate or load the `tdd` skill.

Use repo test patterns. For testable code changes:

1. **RED:** add a failing test for the task behavior.
2. **GREEN:** make the smallest change that passes.
3. **REFACTOR:** only if needed while tests stay green.

For non-testable doc/config-only work, do not invent tests; document the reason in progress.

Follow the selected task’s:

- `description`
- `acceptanceCriteria`
- `filesLikelyTouched`
- `designGuidance`
- relevant repo patterns and `AGENTS.md`

### 6. Verify

Run only required verification:

- exact commands from `acceptanceCriteria`, when listed
- existing repo commands for requirements like “tests pass” or “typecheck passes”
- browser verification, when required

For each command, capture:

- exact command
- pass/fail result or concise output excerpt

### 7. Finish or block

Before marking done, rescan the task for all acceptance criteria and browser-verification triggers.

If required verification failed or is missing:

1. Do not update `passes`.
2. Do not commit.
3. Append progress using `references/progress.md`.
4. Report blocker/failure and next steps.
5. Stop.

If all required verification passed:

1. Append progress using `references/progress.md`.
2. Confirm the progress entry includes required evidence.
3. Set selected task `passes` to `true` in `prd_file`.
4. If `commit: true`, follow `references/commit.md`.
5. If `commit: false`, do not commit.

### 8. Final response

Reread `prd_file`.

If all `tasks[].passes` are `true`, output exactly:

```xml
<promise>COMPLETE</promise>
```

Otherwise summarize concisely:

- task completed or blocked
- verification results
- browser evidence, if required
- files changed
- commit status
