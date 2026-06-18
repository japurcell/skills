Source of truth: `prd_file` official; `progress_file` supplemental resume data only.

Stop. `story-search-index` still has `passes: false`. Latest reviewer still found a blocking stale document race after the latest fix, and `progress.txt` shows `review-fix iteration count = 3`, so the review-fix iteration limit is reached.

Please decide the blocker: what should the next attempt change about delete/index race handling to satisfy the story requirements?
