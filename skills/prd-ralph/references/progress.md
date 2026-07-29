# Progress file

Append one progress block after every attempted selected task, including failed or blocked attempts.

"Attempted" means implementation or verification began after task selection.

Also append a progress block for any command/tool failure or timeout before task selection, using task ID `PREPARE`.

Use the real date/time and task ID.

## Format

```text
## [Date/Time] - [Task ID]
- Implemented: ...
- Files changed: ...
- Verification:
  - [exact command]: [pass/fail output or concise proof]
- Browser verification:
  - Required: yes/no
  - Evidence: [exact playwright-cli command + pass/fail output, "not required", or "blocked: <reason>"]
- Command/tool failures:
  - [exact command/tool or "none"]: [failure/timeout summary, output, blocking/non-blocking]
- Commit:
  - [hash, "disabled by input", "not attempted: verification failed", or "blocked: <reason>"]
- Assumptions:
  - ...
- Learnings:
  - [workaround used, reusable repo note, or "none"]
---
```

## Rules

- Include every field.
- Include exact verification commands.
- Include pass/fail output or concise proof.
- Include every command/tool failure or timeout, even if retried or worked around.
- If a workaround was used, include it in `Learnings`.
- If browser verification was required, include Playwright evidence or blocker.
- Never treat an unexecuted browser check as passing.
- Confirm the appended block is well formed.
- Add reusable repo-wide notes to top `## Codebase Patterns` only when broadly useful.
