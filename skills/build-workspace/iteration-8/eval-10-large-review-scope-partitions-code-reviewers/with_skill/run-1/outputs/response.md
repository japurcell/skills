The manager should launch **two parallel code-reviewers**, not one, because the deduped `review_scope_files` list has **>5 files** and already falls into **two logical areas**.

1. **Auth reviewer scope**: `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
2. **Billing reviewer scope**: `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Those scopes should be **manager-authored, exhaustive, deduped, stable-order, and non-overlapping**, and the manager should **reuse the same partitions from the code-simplifier wave**. Each reviewer gets **its exact file list** plus the **current verification context**, and reviewers should **not recompute, expand, or narrow scope**. **Tracking stays untouched until both reviewers return `DONE`.**
