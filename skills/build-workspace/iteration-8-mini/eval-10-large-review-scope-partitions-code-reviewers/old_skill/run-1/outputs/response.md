Summary of actions the manager should take (per the build SKILL):

1) Invoke addy-context-engineering and subagent-model-selection to pick reviewer models.  
2) Launch code-reviewers in parallel, one per logical area:
   - Auth reviewer: src/auth/{login.ts,session.ts,token.ts} + tests/auth/login.test.ts
   - Billing reviewer: src/billing/{invoice.ts,payment.ts,refund.ts} + tests/billing/invoice.test.ts
3) For each reviewer include (exactly): the touched files list, the implementer’s verification context (what tests/commands were run and results), the full output of git status --porcelain (exclude deleted files and .gitignore), and clear success criteria + allowed responses (DONE, DONE_WITH_FINDINGS, NEEDS_CONTEXT, BLOCKED). Ask them to run the narrow stack checks (only the relevant tests/lints).
4) Do NOT update tracking yet — update only after reviewer(s) return DONE (handle DONE_WITH_FINDINGS per workflow).
