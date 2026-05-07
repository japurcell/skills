Use **two parallel code-reviewer subagents**, not one, because `review_scope_files` has **8 files (>5)**. Partition by logical area, keep scopes non-overlapping, and reuse the same partitions used for simplifiers:

1. **auth reviewer**: `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
2. **billing reviewer**: `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Launch both with the `code-reviewer-prompt.md` template in parallel, pass the exact file list for that partition plus the current verification context, wait for both to return `DONE`, then run the final post-review tracking sync.
