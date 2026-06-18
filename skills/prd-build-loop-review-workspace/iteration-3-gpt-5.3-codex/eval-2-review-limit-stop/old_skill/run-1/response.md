Stop: review-fix iteration limit reached (iteration count is 3), and blocking issues remain.

Reread `prd_file`, append an orchestrator stop-state entry to `progress_file`, and ask the user to decide the blocker.

Do not fix directly and do not dispatch another review-fix implementer unless the user provides an unblocking decision.
