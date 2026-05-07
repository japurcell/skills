Launch **2 code-simplifiers in parallel**, one per logical area, because the deduped `review_scope_files` list is **>5 files**.

- **auth-simplifier**: `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
- **billing-simplifier**: `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Keep the manager-owned partitions **non-overlapping, stable, and deduped**, and then reuse the same partitions for code-review once every simplifier returns `DONE`.
