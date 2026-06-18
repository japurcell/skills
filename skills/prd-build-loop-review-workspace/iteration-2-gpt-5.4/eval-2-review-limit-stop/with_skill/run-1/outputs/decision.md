1. Stop. The review-fix iteration limit is reached: iteration count is 3 and the latest review still has blocking issues.
2. Do not fix findings directly or dispatch another review-fix implementer.
3. Reread `prd_file`.
4. Append a stop-state entry to `progress_file`.
5. Ask the user to decide the blocker: `story-search-index` still has an unresolved stale document race after the capped review-fix loop.
