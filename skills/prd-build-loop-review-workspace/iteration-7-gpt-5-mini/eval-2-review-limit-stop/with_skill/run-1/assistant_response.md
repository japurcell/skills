Review-fix iteration limit reached.

Context:
- Story: story-search-index (Search index stays consistent after deletes)
- Latest reviewer: review still finds stale document race after latest fix
- review-fix iteration count: 3

Action (dry-run):
1. State: review-fix iteration limit reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread prd_file.
5. Append orchestrator stop-state entry to progress_file (dry-run).

Decision required from user:
Choose one:
A) Provide additional context/tests to unblock and allow another review-fix iteration.
B) Escalate to maintainer for manual resolution.
C) Declare issue non-blocking and proceed, with justification.
D) Stop work and leave PRD incomplete.

Stop-state recorded in progress_file (dry-run). Awaiting user decision.
