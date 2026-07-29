---
name: prd-ralph
description: Complete one eligible unfinished PRD task, verify it, append progress, and commit scoped changes unless commit is false.
---

# /prd-ralph

Complete **exactly one** eligible unfinished PRD task.

## Inputs

- `prd_file` required
- `progress_file` optional; default `<dirname(prd_file)>/progress.txt`
- `task_id` optional
- `commit` optional; default `true`
  - Only boolean `false` or string `"false"` disables commit.

## Rules

- Do not interview the user. Make reasonable assumptions and record them in `progress_file`.
- Treat `prd_file` as the source of truth.
- Do not start unsafe, contradictory, missing, or dependency-blocked work.
- Do at most one task.
- Keep changes minimal and task-scoped.
- Preserve unrelated user changes.
- Never invent commands, paths, requirements, or acceptance criteria.
- Never commit `prd_file`, `progress_file`, unrelated changes, or blocked/failing work.
- Record every command/tool failure or timeout in `progress_file`, even if fixed or worked around.
- Set `passes: true` only after required verification passes and the commit gate is satisfied.

## References

Read only when triggered:

- `references/browser-verification.md` — browser/UI/auth/routing/DOM/interactive behavior.
- `references/failures.md` — after any command/tool failure or timeout.
- `references/progress.md` — before appending progress.
- `references/commit.md` — after verification passes when commit is enabled.

## Workflow

### 1. Prepare

1. Read `prd_file`.
2. Resolve `progress_file`; if missing, create it with:
   ```text
   ## Codebase Patterns
   ```
3. Read `progress_file`, especially `## Codebase Patterns`.
4. Read applicable repo guidance, including `AGENTS.md`.
5. Check recent history:
   ```bash
   git log --oneline -20
   ```
6. If any command/tool fails or times out before task selection:
   - read `references/failures.md`
   - append a `PREPARE` progress block
   - stop only if the failure blocks safe task selection

### 2. Stop if already complete

If all `tasks[].passes` are `true`, output exactly:

```xml
<promise>COMPLETE</promise>
```

Then stop.

### 3. Select one task

A task is eligible only when:

- `passes: false`
- every `dependsOn` task has `passes: true`
- missing or empty `dependsOn` means no dependencies

Selection:

- If `task_id` is provided, use it only if it exists, is unfinished, and dependencies pass. Otherwise stop and report why.
- If `task_id` is omitted, select the eligible unfinished task with the lowest numeric `priority`.
- Missing or non-numeric priorities sort last.
- Break ties by PRD order.
- If no task is eligible, stop and list blockers.

### 4. Check browser trigger

If the selected task mentions or implies browser-visible behavior, read `references/browser-verification.md`.

### 5. Implement

1. Activate or load the `tdd` skill.
2. Follow the selected task’s `description`, `acceptanceCriteria`, `filesLikelyTouched`, `designGuidance`, repo patterns, and `AGENTS.md`.
3. For testable code changes:
   - RED: add a failing test for the required behavior.
   - GREEN: make the smallest change that passes.
   - REFACTOR: only if needed while tests stay green.
4. For non-testable doc/config-only work:
   - do not invent tests
   - record the reason in `progress_file`
5. If any command/tool fails or times out, read `references/failures.md`.

### 6. Verify

Run only required verification:

- exact commands listed in `acceptanceCriteria`
- existing repo commands needed for relevant tests/typechecks/lints
- browser verification when required

Capture each exact command and pass/fail evidence.

If any command/tool fails or times out, read `references/failures.md`.

### 7. Finish or block

Rescan the selected task for:

- all acceptance criteria
- required verification
- browser verification triggers

If verification failed or is missing:

1. Do not set `passes: true`.
2. Do not commit.
3. Read `references/progress.md`.
4. Append progress with failure/blocker evidence.
5. Report blocker/failure and next steps.
6. Stop.

If all required verification passed, continue.

### 8. Commit gate

Commit is enabled unless `commit` is boolean `false` or string `"false"`.

#### If commit is enabled

1. Read `references/commit.md`.
2. Create exactly one scoped commit for task changes before setting `passes: true`.
3. Exclude `prd_file`, `progress_file`, and unrelated changes.
4. If committing is blocked:
   - do not set `passes: true`
   - read `references/progress.md`
   - append progress with verification evidence and commit blocker
   - report the blocker
   - stop
5. Record the commit hash.
6. Set the selected task `passes` to `true` in `prd_file`.
7. Read `references/progress.md`.
8. Append progress with verification evidence, command/tool failures, and commit hash.
9. Confirm the progress block is well formed.
10. `prd_file` and `progress_file` may remain modified and uncommitted.

#### If commit is disabled

1. Set the selected task `passes` to `true` in `prd_file`.
2. Do not commit.
3. Read `references/progress.md`.
4. Append progress with verification evidence, command/tool failures, and `disabled by input`.
5. Confirm the progress block is well formed.

### 9. Final response

Before responding, confirm:

- `progress_file` was appended for any attempted selected task
- every command/tool failure or timeout was recorded in `progress_file`
- every workaround was recorded in `Learnings`
- verification passed or the task was blocked
- commit gate is satisfied
- enabled commits exclude `prd_file` and `progress_file`
- disabled commits created no commit

If all `tasks[].passes` are `true` and the commit gate is satisfied, output exactly:

```xml
<promise>COMPLETE</promise>
```

Otherwise summarize briefly:

- task completed or blocked
- verification results
- browser evidence, if required
- command/tool failures or timeouts, if any
- files changed
- commit status
