Review-fix iteration limit reached for `story-search-index`.

`prd.json` remains official source of truth and still shows `passes: false`. Latest reviewer still found blocking issue: stale document race after deletes in `src/search_index.py` and `tests/test_search_index.py`. Per loop rules, I will not fix directly and will not dispatch another review-fix implementer.

Human decision required: do you want to allow another review-fix iteration for this blocker, change the requirement/review bar, or stop with this story incomplete?
