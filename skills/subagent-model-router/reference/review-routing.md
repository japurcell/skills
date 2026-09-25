# Review Routing

Use for code review, PR review, auditing, or security review. Use named defaults from
[the catalog](model-catalog.md#task-defaults).

## Order

1. Use Premium for security-sensitive or high-stakes review, subtle correctness,
   or a prior missed issue in the same task class.
2. Use Fast only for a tiny, single-file, low-risk style or comment diff with no
   logic, test, API, data, policy, or security change.
3. Use Standard for ordinary meaningful code review, including bounded code
   diffs, changed behavior, tests, and multi-file work.

For bounded ordinary reviews, start with the budget-review default. Use the
general-work default for broader reviews. If a model is unavailable, choose a
capable model in the same tier first. Apply the demanding-review default or
another suitable Premium model for Premium review. Explain uncertainty and
verification when review quality for the task class is unmeasured.
