---
name: prd-ralph
description: Attempt at most one eligible unfinished PRD task, verify it, append progress, and commit scoped changes unless commit is false.
---

# /prd-ralph

Attempt to complete **at most one** eligible unfinished PRD task.

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
- Keep changes minimal and task-scoped.
- Preserve unrelated user changes.
- Never invent commands, paths, requirements, or acceptance criteria.
- Use existing repo scripts, documented commands, or commands required by acceptance criteria. If no suitable verification exists, block rather than inventing one.
- Never commit `prd_file`, `progress_file`, unrelated changes, or blocked/failing work.
- After any command/tool failure or timeout, read `references/failures.md`.
- Set `passes: true` only after required verification passes, the commit gate is satisfied, and progress is appended successfully.

## References

Read only when triggered:

- `references/browser-verification.md` — when browser/UI/auth/routing/DOM/interactive behavior is mentioned or implied.
- `references/failures.md` — after any command/tool failure or timeout.
- `references/progress.md` — before appending progress.
- `references/commit.md` — after verification passes when commit is enabled.

## Workflow

### 1. Prepare

1. Read `prd_file`.
2. If `prd_file` cannot be read, report the blocker and stop.
3. If all `tasks[].passes` are `true`, output exactly: `<promise>COMPLETE</promise>`. Then stop.
4. Resolve `progress_file`:
   - if missing, create it with `## Codebase Patterns` at the top
   - else read it, especially `## Codebase Patterns`
5. Read repo guidance files if present: `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`.
6. Check recent history: `git log --oneline -20`.
7. If any command/tool failed or timed out before task selection:
   - read `references/failures.md` and `references/progress.md`
   - append a `PREPARE` progress block
   - stop only if the failure blocks safe task selection

### 2. Select one task

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

### 3. Implement

1. Activate or load the `tdd` skill.
2. Follow the selected task’s `description`, `acceptanceCriteria`, `filesLikelyTouched`, `designGuidance`, repo patterns, and repo guidance.
3. For testable code changes:
   - RED: add a failing test for the required behavior.
   - GREEN: make the smallest change that passes.
   - REFACTOR: only if needed while tests stay green.
4. For non-testable doc/config-only work:
   - do not invent tests
   - record the reason in `progress_file`
5. If any command/tool fails or times out, read `references/failures.md`.

### 4. Verify

Run only required verification to avoid unnecessary churn. Prefer filtered runs over full runs.

Required verification means the smallest existing test/typecheck/lint/build/browser checks needed to prove the selected task’s acceptance criteria.

1. Determine verification from:
   - existing repo commands needed for relevant tests/typechecks/lints/builds
   - commands listed in `acceptanceCriteria`
2. Run the commands, capturing exact command, output, and exit code.
3. If the selected task mentions or implies browser-visible behavior, read and apply `references/browser-verification.md`.
4. If any command/tool fails or times out, read `references/failures.md`.

### 5. Finish or block

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

### 6. Commit gate

#### If commit is enabled

1. Read and follow `references/commit.md`.
2. Create exactly one scoped commit for task changes before setting `passes: true`.
3. Exclude `prd_file`, `progress_file`, and unrelated changes.
4. If committing is blocked:
   - do not set `passes: true`
   - read `references/progress.md`
   - append progress with verification evidence and commit blocker
   - report the blocker
   - stop
5. Record the commit hash.
6. Read `references/progress.md`.
7. Append progress with verification evidence, command/tool failures, and commit hash.
8. Confirm the progress block is well formed.
9. Set the selected task `passes` to `true` in `prd_file`.
10. `prd_file` and `progress_file` may remain modified and uncommitted.

#### If commit is disabled

1. Read `references/progress.md`.
2. Append progress with verification evidence, command/tool failures, and `disabled by input`.
3. Confirm the progress block is well formed.
4. Set the selected task `passes` to `true` in `prd_file`.
5. Do not commit.

### 7. Final response

Before responding, confirm:

- `progress_file` was appended for any attempted selected task
- every command/tool failure or timeout was recorded in `progress_file`
- every mistake and/or workaround was recorded in `Learnings`
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
