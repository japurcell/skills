Follow the build skill: materialize the deduped review_scope_files, partition by logical area, then launch reviewers in parallel (do not update tracking yet).

Concretely:
- Auth partition (4 files): src/auth/login.ts, src/auth/session.ts, src/auth/token.ts, tests/auth/login.test.ts — launch one code-reviewer subagent with that exact file list and the implementer’s verification context.
- Billing partition (4 files): src/billing/invoice.ts, src/billing/payment.ts, src/billing/refund.ts, tests/billing/invoice.test.ts — launch one code-reviewer subagent with that exact file list and the same verification context.
- Invoke addy-context-engineering and subagent-model-selection first, keep partitions stable, run both reviewers in parallel, and only update tracking after every reviewer returns DONE.
