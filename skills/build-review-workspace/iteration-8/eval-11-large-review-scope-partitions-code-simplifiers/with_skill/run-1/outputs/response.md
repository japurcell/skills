Launch **2 code-simplifier subagents in parallel**, not 1. Under the build skill’s fanout rule, `review_scope_files` with **more than 5 files** must be split into **non-overlapping logical partitions**, and those same partitions are later reused for code-review.

1. **Auth simplifier** — `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
2. **Billing simplifier** — `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Each launch should use `simplifier-prompt.md`, pass **only** that exact stable file list plus the implementer’s context, and instruct the simplifier not to recompute or narrow scope. Use the specialized `code-simplifier` agent on a fast/cheap model by default. Begin code-review only after **both** simplifiers return `DONE`, reusing these exact two partitions.
