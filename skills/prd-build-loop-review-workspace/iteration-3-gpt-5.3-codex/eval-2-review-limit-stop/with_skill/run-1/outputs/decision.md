1. Stop: review-fix iteration limit reached at `3`, and latest reviewer still reports blocking issues.
2. Do not fix findings directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file` as official source of truth.
5. Append orchestrator stop-state entry to `progress_file`.
6. Ask user to decide blocker (`story-search-index` still has stale delete-race issue) and provide unblock direction before continuing.
