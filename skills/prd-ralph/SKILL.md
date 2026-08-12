---
name: prd-ralph
description: Complete at most one eligible unfinished PRD task, verify it, log progress, and optionally create one scoped commit.
---

# /prd-ralph

Complete **at most one** eligible unfinished task from `prd_file`.

## Inputs

- `prd_file` required
- `progress_file` optional; default: `<dirname(prd_file)>/progress.txt`
- `task_id` optional
- `commit` optional; default: `true`
  - Only boolean `false` or string `"false"` disables commit.

## Core rules

- Do not interview the user. Make reasonable assumptions and record them in `progress_file`.
- Treat `prd_file` as the source of truth.
- Do not start unsafe, contradictory, missing, or dependency-blocked work.
- Never invent commands, paths, requirements, or acceptance criteria.
- Keep changes minimal and task-scoped. Preserve unrelated user changes.
- After any command/tool failure or timeout, read `references/failures.md`.
- Never commit `prd_file`, `progress_file`, unrelated changes, or blocked/failing work.
- Set `passes: true` only after:
  1. required verification passes,
  2. progress is appended,
  3. commit rules are satisfied,
  4. all session commits are recorded and audited.
- A session commit is any commit in:
  `git log --oneline <session_start_head>..HEAD`
- If session commit audit fails, block and do not set `passes: true`.

## References

Read when triggered:

- `references/verification.md` — before verification.
- `references/browser-verification.md` — when browser/UI/auth/routing/DOM/interactive behavior is mentioned or implied.
- `references/failures.md` — after any command/tool failure or timeout.
- `references/commit.md` — after verification passes when commit is enabled.
- `references/progress.md` — before appending progress.

## Workflow

### 1. Prepare

1. Read `prd_file`. If unreadable, report blocker and stop.
2. If all `tasks[].passes` are `true`, output exactly:
   `<promise>COMPLETE</promise>`
   Then stop.
3. Resolve `progress_file`:
   - if missing, create it with `## Codebase Patterns` at the top
   - otherwise read it, especially `## Codebase Patterns`
4. Read repo guidance files if present: `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`.
5. Run:
   - `git log --oneline -20`
   - `git rev-parse --verify HEAD`
6. Save `HEAD` as `session_start_head`.
7. If any prepare command fails or times out:
   - read `references/failures.md` and `references/progress.md`
   - append a `PREPARE` progress block
   - stop if `prd_file` is unreadable, task selection is unsafe, or `session_start_head` is unavailable

### 2. Select one task

A task is eligible only when:

- `passes: false`
- every `dependsOn` task has `passes: true`
- missing or empty `dependsOn` means no dependencies

Selection:

- If `task_id` is provided, use it only if it exists, is unfinished, and dependencies pass. Otherwise stop and report why.
- If `task_id` is omitted, choose the eligible unfinished task with the lowest numeric `priority`.
- Missing or non-numeric priorities sort last.
- Break ties by PRD order.
- If no task is eligible, stop and list blockers.

Before implementation, inspect the selected task. If requirements or acceptance criteria are missing, unsafe, or contradictory:

1. read `references/progress.md`
2. append a blocked progress block
3. stop

### 3. Implement

1. Activate or load the `tdd` skill.
2. Follow only the selected task’s:
   - `description`
   - `acceptanceCriteria`
   - `filesLikelyTouched`
   - `designGuidance`
   - repo guidance and patterns
3. For testable code changes:
   - RED: add a failing test for the required behavior.
   - GREEN: make the smallest passing change.
   - REFACTOR: only if needed while tests stay green.
4. For doc/config-only work:
   - do not invent tests
   - record why command verification is not applicable in `progress_file`, if true
5. If any command/tool fails or times out, read `references/failures.md`.

### 4. Verify

1. Read `references/verification.md`.
2. Run the smallest required verification.
3. If browser-visible behavior is mentioned or implied, read and apply `references/browser-verification.md`.
4. Record exact commands/checks, concise output, and exit codes.
5. If any command/tool fails or times out, read `references/failures.md`.

### 5. Finish

Rescan the selected task for acceptance criteria and required verification.

To audit session commits:

1. Run `git log --oneline <session_start_head>..HEAD`.
2. For each listed commit, run `git show --name-only --format=oneline <hash>`.
3. Include every session commit in the next progress block.

If verification failed or is missing:

1. Do not set `passes: true`.
2. Do not commit.
3. Audit session commits.
4. If any session commit exists, the commit gate is blocked.
5. Read `references/progress.md`.
6. Append progress with blocker evidence, failures, session commits, and any commit-gate blocker.
7. Report blocker and stop.

If verification passed and commit is enabled:

1. Read and follow `references/commit.md`.
2. Create exactly one scoped commit for task changes.
3. Audit session commits.
4. If the commit gate is blocked:
   - do not set `passes: true`
   - read `references/progress.md`
   - append progress with verification evidence, failures, commit blocker, and session commits
   - report blocker and stop
5. Read `references/progress.md`.
6. Append progress with verification evidence, failures, task commit, commit-gate result, and session commits.
7. Set the selected task’s `passes` to `true` in `prd_file`.
8. Leave `prd_file` and `progress_file` uncommitted.

If verification passed and commit is disabled:

1. Do not commit.
2. Audit session commits.
3. If any session commit exists, the commit gate is blocked.
4. Read `references/progress.md`.
5. Append progress with verification evidence, failures, `disabled by input`, commit-gate result, and session commits.
6. If the commit gate is blocked:
   - do not set `passes: true`
   - report blocker and stop
7. Set the selected task’s `passes` to `true` in `prd_file`.

### 6. Final response

Before responding, confirm:

- progress was appended for any attempted selected task
- every command/tool failure or timeout was recorded in `progress_file`
- every mistake and/or workaround was recorded in `Learnings`
- verification passed or the task was blocked
- commit gate passed or the task was blocked
- all session commits were recorded in `progress_file`
- if commit was enabled and passed, the commit excludes `prd_file` and `progress_file`
- if commit was disabled and passed, no commit was created

If all `tasks[].passes` are now `true` and commit gate rules are satisfied, output exactly:

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
- session commits
