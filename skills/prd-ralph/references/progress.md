# Progress file

Append progress after every attempted selected task, including blocked or failed attempts.

Use the real date/time and selected task ID.

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
- Assumptions:
  - ...
- Learnings:
  - ...
---
```

## Rules

- Include every field.
- Include exact verification commands.
- Include pass/fail output or concise proof.
- If browser verification was required, include Playwright evidence or blocker.
- Never write “browser check listed but not executed” as acceptable verification.
- Confirm the appended block is well formed.
- Add reusable repo-wide notes to top `## Codebase Patterns` only when broadly useful.
