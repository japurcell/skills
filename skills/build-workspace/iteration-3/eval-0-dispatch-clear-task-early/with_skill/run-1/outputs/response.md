Manager checklist (before dispatch)
- Invoke addy-context-engineering and subagent-model-selection.
- Verify the task matches the plan; resolve ambiguities or tradeoffs first.
- Collect acceptance criteria, exact validation commands, and only the file paths named in the plan. Do NOT pre-read repository files or draft patches.

Lean handoff contents
- Task text + success criteria (copy acceptance criteria).
- Known constraints (DB, perf, auth, rate limits) and exact validation/CI commands.
- Only plan-named file hints and CI expectations.
- Note: do NOT commit changes.

Implementer-owned work
- Repo discovery, pattern lookup, pick pagination approach (offset vs cursor), param names, defaults, headers.
- Implement code, tests, run validations, ensure full test suite/build pass.
- Return status: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED.

After DONE: dispatch code-simplifier; update tracking only after simplifier returns DONE.
