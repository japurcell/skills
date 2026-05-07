Because the scope is >5 files, the manager should launch code-reviewers in parallel over two stable, non-overlapping partitions before final tracking sync:

- Auth: `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
- Billing: `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Use the exact deduped review scope as provided, keep the partitioning manager-authored, and run the final reviewed sync only after both reviewers return `DONE`.
