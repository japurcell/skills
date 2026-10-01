# Review Routing

This file owns capability floors for code review, PR review, change auditing, and security review.

## Routing order

1. Use **Premium** for security-sensitive or high-stakes review, or after a prior important miss on materially similar review work.
2. Otherwise, use **Fast** only for mechanical or non-semantic changes with straightforward verification.
3. Otherwise, use **Standard**.
4. Apply [`escalation-policy.md`](escalation-policy.md) if verification reveals a reasoning gap or risk increases.

## Floors

### Fast

Examples:

- whitespace or formatting
- non-behavioral comments or documentation
- reproducible generated output
- mechanical renames or transformations

File count does not determine the floor. A mechanical multi-file change may remain Fast, while a substantive one-file change is at least Standard.

### Standard

Use for ordinary substantive review, including:

- features and bug fixes
- behavioral configuration
- tests or guard logic
- cross-file interactions
- meaningful refactoring
- ordinary correctness and maintainability analysis

Use the budget-review default for a bounded, clear-scope diff and the general-work default for broader behavioral or cross-component reasoning.

### Premium

Use for:

- security review or security-sensitive changes
- authentication, authorization, secrets, credentials, cryptography, or trust boundaries
- high-stakes correctness
- subtle concurrency, cache-consistency, or false-pass risk
- a prior important miss on materially similar review work
- repeated reasoning failures
- user-requested best-quality review
- unusually difficult review over a large or highly connected codebase

A prior important review miss establishes a Premium floor, not merely a one-tier suggestion.

## Fallback and verification

Preserve the review floor when a configuration is unavailable. Never substitute the bounded-work default for substantive review or lower Premium review to Standard.

If no same-tier configuration is available, use the lowest-cost available higher-tier configuration that satisfies current-request constraints. If no exact configuration satisfies the review floor, return `dispatchable: false`.

Model selection does not replace verification. Use checks appropriate to the review, such as tracing affected behavior and callers, checking tests and failure paths, validating trust boundaries, reproducing generated output, running focused checks, or obtaining independent high-stakes review.

For unvalidated model-and-task combinations, state the uncertainty and require verification appropriate to the stakes.
