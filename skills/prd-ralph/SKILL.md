---
name: prd-ralph
description: Complete one eligible unfinished PRD task, verify it, append progress, and commit scoped changes unless commit is explicitly false.
---

# /prd-ralph

Complete **exactly one** eligible unfinished PRD task.

## Inputs

- `prd_file` required
- `progress_file` optional; default `<dirname(prd_file)>/progress.txt`
- `task_id` optional
- `commit` optional; default `true`
  - Only boolean `false` or string `"false"` disables commit.

## Core rules

- Do not interview the user. Make reasonable assumptions and record them in `progress_file`.
- Treat `prd_file` as source of truth.
- Do not start unsafe, contradictory, missing, or dependency-blocked work.
- Do at most one task.
- A task is eligible only when `passes: false` and every `dependsOn` task has `passes: true`; missing or empty `dependsOn` means no dependencies.
- Keep changes minimal and task-scoped.
- Preserve unrelated user changes.
- Never invent commands, paths, requirements, or acceptance criteria.
- Append progress after any attempted task.
- Set `passes: true` only after required verification passes and the commit gate is satisfied.
- Never commit `prd_file`, `progress_file`, unrelated changes, or failing/blocked work.

## References

Read only when triggered:

- `references/browser-verification.md` — browser/UI/auth/routing/DOM/interactive behavior.
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

### 2. Stop if already complete

If all `tasks[].passes` are `true`, output exactly:

```xml
<promise>COMPLETE</promise>
```

Then stop.

### 3. Select one task

- Use the eligibility rule above.

If `task_id` is provided, use it only if it exists, is unfinished, and dependencies pass. Otherwise stop and report why.

If `task_id` is omitted, select the eligible unfinished task with the lowest numeric `priority`. Missing or non-numeric priorities sort last. Break ties by PRD order.

If no task is eligible, stop and list blockers.

### 4. Check browser trigger

Read `references/browser-verification.md` if browser-visible behavior is possible.

### 5. Implement

Activate or load the `tdd` skill.

For testable code changes:

1. RED: add a failing test for the required behavior.
2. GREEN: make the smallest change that passes.
3. REFACTOR: only if needed while tests stay green.

For non-testable doc/config-only work, do not invent tests; record the reason in progress.

Follow the selected task’s `description`, `acceptanceCriteria`, `filesLikelyTouched`, `designGuidance`, repo patterns, and `AGENTS.md`.

### 6. Verify

Run only required verification:

- exact commands listed in `acceptanceCriteria`
- existing repo commands for required tests/typechecks/lints
- browser verification when required

Capture each exact command and pass/fail evidence.

### 7. Finish or block

Rescan the selected task for all acceptance criteria, required verification, and browser triggers.

If verification failed or is missing:

1. Do not set `passes: true`.
2. Do not commit.
3. Read `references/progress.md`.
4. Append failure/blocker evidence.
5. Report blocker/failure and next steps.
6. Stop.

If all required verification passed, apply the commit gate.

#### Commit enabled

Commit is enabled unless `commit` is boolean `false` or string `"false"`.

If enabled:

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
8. Append progress with verification evidence and commit hash.
9. Confirm the progress block is well formed.

#### Commit disabled

If disabled:

1. Set the selected task `passes` to `true` in `prd_file`.
2. Do not commit.
3. Read `references/progress.md`.
4. Append progress with verification evidence and `commit disabled by input`.
5. Confirm the progress block is well formed.

### 8. Final response

Before responding, confirm:

- progress was appended for any attempted task
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
- files changed
- commit status
