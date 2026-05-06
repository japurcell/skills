Manager (before dispatch)
- Invoke addy-context-engineering and subagent-model-selection.
- Confirm the task is unambiguous vs. plan (resolve conflicts first).
- Pick implementer model and dispatch immediately. Do NOT pre-read large file sets, draft designs, or sketch patches.

Handoff (lean)
- Task text + acceptance criteria (exact).
- Known constraints and validation commands (how to verify).
- Only the file hints already named in the plan (paths).
- Repo rules (e.g., "do not commit; leave changes uncommitted").

Implementer (must keep)
- Repo discovery, pattern lookup, first-pass design.
- All code changes, tests, and verification (narrow checks then full suite).
- Produce verification context: commands run, results, and touched-file list.
- Return one of: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED.
