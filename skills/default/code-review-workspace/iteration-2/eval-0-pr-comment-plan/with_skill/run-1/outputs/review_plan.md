1. Lock the review target to PR #482 and review only that PR's changes.
2. Invoke `subagent-model-router` and `addy-code-review-and-quality`, then make a todo list.
3. Do GitHub intake through fast subagents only with `gh`; the main agent must not read PR or issue content directly.
4. Gather only relevant standards/context files, then find the spec; if none exists, record `no spec available` and skip spec review.
5. Preflight the required review roles: `addy-code-reviewer`, `addy-security-auditor`, `addy-test-engineer`, maintainability review using `MAINTAINABILITY_CRITERIA.md`, and standards review limited to explicit documented rules.
6. Run the required review roles in parallel and keep each role distinct.
7. Filter findings with `FALSE_POSITIVE_RUBRIC.md`; keep only scores `75` or `100`.
8. Prepare PR-comment output with `OUTPUT_FORMATS.md`, including concrete file links and brief evidence-backed findings.
9. Before `gh pr comment`, repeat the PR eligibility check; if the PR is still open and eligible, post the comment.
10. Use the PR-comment format exactly, including the required footer if findings remain, or the no-issues template if none do.
