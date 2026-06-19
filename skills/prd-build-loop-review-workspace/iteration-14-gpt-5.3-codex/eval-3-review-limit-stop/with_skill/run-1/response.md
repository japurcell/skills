Loading required instructions, then I’ll read the benchmark skill file and fixture progress to produce `outputs/decision.md`.

Reading exact benchmark rule and fixture state, then writing required stop decision file.

1. State that review-fix iteration limit is reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: ask user to decide blocker.
