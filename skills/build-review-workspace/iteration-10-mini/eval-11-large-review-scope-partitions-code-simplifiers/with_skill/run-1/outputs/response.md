With 8 files, the manager should partition `review_scope_files` by logical area and launch code-simplifiers once per partition, using the exact manager-authored lists from `simplifier-prompt.md`.

Recommended fanout:
- Auth simplifier: `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
- Billing simplifier: `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Then wait for both simplifiers to return `DONE` before starting code-review, and reuse the same partitions for reviewer fanout.
