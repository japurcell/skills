1. State that review-fix iteration limit is reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: ask the user to decide blocker.

Human decision required: latest reviewer still finds stale document race after latest fix for `story-search-index` in `src/search_index.py` and `tests/test_search_index.py`. Decide blocker: authorize another review-fix cycle despite limit, change requirements, or stop with issue unresolved.
