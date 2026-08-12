# Progress file

Read before appending progress.

Append one progress block after every attempted selected task, including failed or blocked attempts.

Also append a progress block for any command/tool failure or timeout before task selection, using task ID `PREPARE`.

"Attempted" means implementation or verification began, or the selected task was blocked after inspection.

Use real date/time and task ID.

## Format

```text
## [Date/Time] - [Task ID]
- Implemented: ...
- Files changed: ...
- Verification:
  - [exact command/check]: [PASS/FAIL/BLOCKED + concise evidence]
- Browser verification:
  - Required: yes/no
  - Evidence: [exact playwright-cli command + result, "not required", or "blocked: <reason>"]
- Command/tool failures:
  - [exact command/tool or "none"]: [failure/timeout summary, output, blocking/non-blocking]
- Commit:
  - Mode: [enabled/disabled]
  - Task commit: [hash, "disabled by input", "not attempted: verification failed", or "blocked: <reason>"]
  - Gate: [PASS/BLOCKED + reason]
  - Session start HEAD: [hash or "unavailable: <reason>"]
  - Session commits:
    - [hash subject]: [changed files or "none"; scope note]
- Assumptions:
  - ...
- Learnings:
  - [mistakes, workaround used, reusable repo note, or "none"]
---
```

## Rules

- Include every field.
- Include exact verification commands/checks and concise pass/fail evidence.
- Include every command/tool failure or timeout, even if later fixed.
- Include browser verification evidence when required.
- Never treat an unexecuted browser check as passing.
- Include every session commit in `session_start_head..HEAD`.
- For each session commit, include hash, subject, changed files, and scope note.
- If verification failed or is missing, expected session commits: none.
- If commit is enabled and verification passed, expected session commits: exactly one task-scoped commit.
- If commit is disabled, expected session commits: none.
- If a session commit includes `prd_file`, `progress_file`, unrelated changes, or blocked/failing work, record a commit-gate blocker.
- Confirm the appended block is well formed.
- Add reusable repo-wide notes to top `## Codebase Patterns` only when broadly useful.
- If session commit audit fails, record the failure and treat the task as blocked.
