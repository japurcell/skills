Launch **parallel code-reviewer subagents** split by logical area, because the deduped scope is **>5 files**.

1. **Auth reviewer scope:** `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
2. **Billing reviewer scope:** `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Give each reviewer the **exact file list** plus the **current verification context**, keep the partitions **non-overlapping**, and **do not run the final tracking sync until both reviewers return `DONE`**.
