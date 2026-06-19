Reading benchmark instructions and fixture inputs, then I’ll write the required stop decision file.
I found the stop condition; next I’m writing the exact dry-run stop response into `outputs/decision.md`.
1. State that review-fix iteration limit is reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: ask the user to decide blocker.
