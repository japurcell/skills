Manager pre-steps:
- Run addy-context-engineering and subagent-model-selection, confirm task is unambiguous.
- Ensure acceptance criteria, validation commands, and any repo rules are available.
- Do NOT pre-read files, sketch patches, or explore the repo.

Handoff must include (lean):
- Task text + success criteria (exact acceptance criteria).
- Known constraints and validation commands (how to verify).
- Only already-known file hints named in the plan.

Implementer owns:
- Repo discovery, pattern lookup, first-pass design.
- All code changes, tests, and running the validation commands.
- Verification evidence and uncommitted changes.
- Return DONE and touched files (manager then builds review_scope_files).
