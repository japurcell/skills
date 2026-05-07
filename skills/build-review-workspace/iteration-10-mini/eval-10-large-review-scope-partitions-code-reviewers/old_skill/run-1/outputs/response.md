After the wave is fully marked done, I would launch the code-reviewers in parallel using two non-overlapping partitions, reusing the same stable review scope split:

- Auth reviewer: `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
- Billing reviewer: `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Each reviewer gets only its exact file list plus the current verification context. Once both return `DONE`, I would perform the final tracking sync.
