Source of truth: `prd_file` official; `progress_file` supplemental resume data only.

1. Review-fix iteration limit is reached for `story-search-index`.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. `prd_file` reread confirms `story-search-index` still has `passes: false`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: latest review still finds stale document race after latest fix. Should we allow another review-fix iteration beyond cap, change the requirements, or stop with this blocker?
