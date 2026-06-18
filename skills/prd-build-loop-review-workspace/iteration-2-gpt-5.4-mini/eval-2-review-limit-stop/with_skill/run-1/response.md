Stop: review-fix iteration limit reached (iteration count is 3), and latest reviewer still found blocking issues.

Do not fix findings directly. Do not dispatch another review-fix implementer.

Reread `prd_file`, append a stop-state entry to `progress_file`, and ask the user to decide the blocker.
