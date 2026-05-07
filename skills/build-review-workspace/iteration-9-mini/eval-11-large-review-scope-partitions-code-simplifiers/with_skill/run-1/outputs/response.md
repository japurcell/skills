Launch **two parallel code-simplifier subagents** after the wave is fully done and `review_scope_files` is materialized once, deduped, and kept stable.

**Partition the 8 files by logical area:**

1. **auth-simplifier**
   - `src/auth/login.ts`
   - `src/auth/session.ts`
   - `src/auth/token.ts`
   - `tests/auth/login.test.ts`

2. **billing-simplifier**
   - `src/billing/invoice.ts`
   - `src/billing/payment.ts`
   - `src/billing/refund.ts`
   - `tests/billing/invoice.test.ts`

Then wait for **both** simplifiers to return `DONE` before starting code-review, and reuse the **same partitions** for the reviewer wave.
