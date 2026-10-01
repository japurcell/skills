# Review Routing

This file owns the capability floors for:

- code review
- pull-request review
- change auditing
- security review

Use [`escalation-policy.md`](escalation-policy.md) after establishing the initial review floor.

## Routing order

1. Use **Premium** if the review is security-sensitive, high-stakes, or follows a prior important miss on materially similar review work.
2. Otherwise, use **Fast** only when the changes are mechanical or non-semantic and correctness is straightforward to verify.
3. Otherwise, use **Standard**.
4. Escalate under [`escalation-policy.md`](escalation-policy.md) if verification exposes a reasoning gap or the task's risk materially increases.

## Review floors

### Fast review

Fast is permitted only for changes such as:

- whitespace or formatting
- comments or documentation with no behavioral claims requiring substantive validation
- deterministic generated output that can be reproduced
- mechanical renames or transformations with straightforward verification
- similarly non-semantic changes

File count alone does not determine eligibility. A mechanical change may span multiple files and remain Fast.

Do not use Fast merely because:

- the diff is small
- only one file changed
- the implementation is bounded
- the cheaper model appears adequate
- the review is expected to be quick

A substantive one-file change is at least Standard.

### Standard review

Standard is the floor for ordinary substantive review, including:

- bounded feature changes
- bug fixes
- behavioral configuration changes
- test or guard-logic changes
- cross-file changes
- backend and frontend interactions
- meaningful refactoring
- ordinary correctness and maintainability review

Use the budget-review default for a bounded, clear-scope substantive diff. Use the general-work default when review requires broader behavioral or cross-component reasoning.

### Premium review

Premium is the floor for:

- security review or security-sensitive changes
- authentication or authorization behavior
- secrets, credentials, cryptography, or trust boundaries
- high-stakes correctness
- subtle concurrency, cache-consistency, or false-pass risk
- a prior important miss on materially similar review work
- repeated reasoning failures
- user-requested best-quality review
- unusually difficult review over a large or highly connected codebase

A prior important review miss establishes a Premium floor; it is not merely a one-tier suggestion.

## Fallback rules

When the preferred review configuration is unavailable:

1. Preserve the review floor.
2. Choose another available model-and-effort configuration in the same tier.
3. Do not substitute the bounded-work default for substantive review.
4. Do not lower Premium review to Standard because the preferred Premium configuration is unavailable.
5. Report the availability-driven fallback.

If no available configuration satisfies the review floor, report that limitation rather than silently lowering the tier.

## Verification

Model selection does not replace review verification.

Use verification appropriate to the review, which may include:

- reading the affected implementation and callers
- checking tests and failure paths
- reproducing generated changes
- tracing data and control flow
- checking authorization and trust boundaries
- comparing behavior against stated requirements
- running focused static or dynamic checks
- obtaining an independent review for high-stakes findings

For unvalidated model-and-task combinations, state the uncertainty and require independent verification appropriate to the stakes.
