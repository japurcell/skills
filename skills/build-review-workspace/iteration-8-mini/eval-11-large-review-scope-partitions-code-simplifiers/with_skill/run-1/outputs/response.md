Steps (concise):

1. Invoke addy-context-engineering and subagent-model-selection.
2. Materialize and keep the deduped, stable-ordered review_scope_files list.
3. Partition because total >5 by logical area (manager-owned, non-overlapping):
   - Auth scope (4 files): src/auth/login.ts, src/auth/session.ts, src/auth/token.ts, tests/auth/login.test.ts
   - Billing scope (4 files): src/billing/invoice.ts, src/billing/payment.ts, src/billing/refund.ts, tests/billing/invoice.test.ts
4. Dispatch parallel code-simplifier subagents (one per scope) using simplifier-prompt.md, passing the exact file list and the implementer’s verification context. Do not pre-read or alter scope.
5. After every simplifier returns DONE, launch parallel code-reviewers using the same partitions.
