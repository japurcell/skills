Launch code-simplifiers in parallel, one per logical area, because the deduped review scope has 8 files (>5).

Partitions:
1. auth slice:
   - src/auth/login.ts
   - src/auth/session.ts
   - src/auth/token.ts
   - tests/auth/login.test.ts
2. billing slice:
   - src/billing/invoice.ts
   - src/billing/payment.ts
   - src/billing/refund.ts
   - tests/billing/invoice.test.ts

For each simplifier, pass the exact file list, the accumulated verification context, and the simplifier prompt. Do not recompute scope. After both return DONE, reuse these same partitions for code-review.
