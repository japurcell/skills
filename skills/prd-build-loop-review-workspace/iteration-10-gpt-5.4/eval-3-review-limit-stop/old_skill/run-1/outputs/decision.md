1. State that review-fix iteration limit is reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: ask the user to decide blocker.

Blocking issue: latest reviewer still finds stale document race after latest fix for `US-001` ("Search index stays consistent after deletes"), so PRD cannot be completed without a human decision on how to proceed.
