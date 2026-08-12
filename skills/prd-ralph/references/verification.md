# Verification

Use before deciding whether the selected task can pass.

## Goal

Run the smallest check that proves the selected task’s acceptance criteria.

Prefer filtered checks over full-suite checks.

## Sources

Determine required verification from:

- selected task acceptance criteria
- existing repo scripts
- documented repo commands
- relevant test/typecheck/lint/build commands
- browser requirements, if applicable

Never invent commands or acceptance criteria.

## Rules

- If acceptance criteria name a command, run it unless unsafe or impossible.
- For code changes, executable verification is required.
- If code verification is unavailable, missing, failing, or unsafe, block.
- For doc/config-only work, deterministic inspection is allowed if no relevant command exists.
- Do not treat an unexecuted check as passing.
- Capture:
  - exact command or inspection performed
  - exit code, if applicable
  - concise relevant output/evidence
  - pass/fail result

## Browser-visible behavior

If the task mentions or implies browser/UI/auth/routing/DOM/interactive behavior, read `references/browser-verification.md`.

Browser verification is required unless the PRD explicitly says otherwise.

## Failure

If any command/tool fails or times out:

1. read `references/failures.md`
2. record the failure in the progress block
3. retry only if the retry is reasonable and task-scoped
4. block if required verification still does not pass
