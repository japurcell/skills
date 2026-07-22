1. State that review-fix iteration limit is reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: ask user to decide blocker.

Latest reviewer still finds stale document race after latest delete-path fix, and `progress.txt` shows `review-fix iteration count = 3`. Human decision required on blocker for `US-001`: how should stale search-index delete race be resolved before finalization can continue?
