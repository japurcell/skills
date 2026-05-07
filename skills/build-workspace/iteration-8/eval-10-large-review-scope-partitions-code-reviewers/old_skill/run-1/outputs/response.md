Launch **two parallel code-reviewers now**, not tracking. Because the deduped review scope is **8 files (>5)**, the manager should **split the review into manager-authored, non-overlapping partitions** by logical area:

1. **Auth reviewer:** `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
2. **Billing reviewer:** `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Each reviewer should get its **exact file list** via `code-reviewer-prompt.md`, plus the **current verification context** and the **uncommitted-file context** from `git status --porcelain` (excluding deleted entries and `.gitignore`). The reviewers should **not** recompute or narrow scope themselves. Update tracking **only after all reviewer partitions return plain `DONE`**; if any reviewer returns findings, route that back through the fix/simplify/review loop first.
