Manager (before dispatch)
- Invoke addy-context-engineering + subagent-model-selection.
- Confirm the task is unambiguous; resolve missing requirements.
- Do NOT pre-read large file sets, draft patches, or implement.

Handoff (lean)
- Task text + acceptance criteria (exact wording).
- Validation commands, environment, and repo rules.
- Only the known file hints named in the plan and any constraints.

Implementer (must keep)
- Repo discovery, pattern lookup, design choice, code changes, tests, and verification (run the validation commands + full test suite).
- Report status (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED).
- Leave changes uncommitted for human review.
