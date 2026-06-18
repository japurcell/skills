1. Invoke `subagent-model-router` and `addy-code-review-and-quality`, make a todo list, and lock the review target to **PR #482**.
2. Do GitHub intake through fast subagents only: the main agent must not read PR or issue content directly, and subagents must use `gh` to capture PR eligibility, title/body summary, branch info, changed files, linked issues/specs, and compact issue summaries.
3. Stop early if intake says the PR is `closed`, `draft`, `review not needed`, or `already reviewed by you`; otherwise continue in PR comment mode.
4. Gather only relevant standards/context files from the repo root and touched paths, then find the spec in the required order; if none is found, record `no spec available` and skip spec review.
5. Preflight the required distinct review roles: `addy-code-reviewer`, `addy-security-auditor`, `addy-test-engineer`, maintainability review using `MAINTAINABILITY_CRITERIA.md` with a thermonuclear lens, standards review limited to explicit documented rules, plus spec/history/related-PR/code-comment review where required for a PR.
6. Run the required review roles in parallel, keeping maintainability findings high-conviction and focused on complexity, wrong-layer logic, duplication, flags, casts, and other regressions introduced by the change.
7. Filter candidate findings with `FALSE_POSITIVE_RUBRIC.md`, keep only scores `75` or `100`, and require concrete file evidence plus explicit standards-file support for any standards finding.
8. Prepare the final PR comment exactly per `OUTPUT_FORMATS.md`, keeping it brief, evidence-backed, and limited to issues introduced by or clearly reachable through the PR.
9. Repeat the PR eligibility check immediately before `gh pr comment`; if still eligible, post the final comment, otherwise stop without commenting.
