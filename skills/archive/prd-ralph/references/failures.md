# Command/tool failures

Use after any command/tool failure or timeout.

## Rule

Every command/tool failure or timeout must be recorded in `progress_file`, even if later fixed, retried, or worked around.

This includes failures/timeouts from:

- shell commands
- tests, lint, typecheck, build, install, git
- file operations
- browser/Playwright checks
- any other tool call

## Record

In the progress block, include:

- exact command/tool call, if applicable
- failure or timeout summary
- concise relevant output/error
- whether it was blocking
- workaround, if used

If a workaround was used, also add it to `Learnings`.

## Before task selection

If failure happens before task selection:

- append a progress block using task ID `PREPARE`
- use `Files changed: none` unless files were changed
