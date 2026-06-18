1. State that the review-fix iteration limit is reached (`count = 3`) and blocking review issues remain.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file` (`evals/files/review-limit-fixture/prd.json`) as the official source of truth (`progress.txt` is supplemental only).
5. Append an orchestrator stop-state entry to `progress_file` (`evals/files/review-limit-fixture/progress.txt`).
6. Ask user to decide the blocker so work can continue.

Required stop response:

Review-fix iteration limit reached at 3, and latest review still reports blocking issues for `story-search-index` (story remains `passes: false` in `prd_file`). I will not apply direct fixes and will not dispatch another review-fix implementer. Please decide how to unblock: provide a human decision on the blocking review finding (or explicitly authorize a policy change such as raising the iteration cap).
