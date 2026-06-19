I’ll load only the required instructions and fixture inputs, then produce the stop decision file.
Switching to writing the dry-run stop decision artifact in `outputs/decision.md`.
1. State that review-fix iteration limit is reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: ask user to decide blocker.
