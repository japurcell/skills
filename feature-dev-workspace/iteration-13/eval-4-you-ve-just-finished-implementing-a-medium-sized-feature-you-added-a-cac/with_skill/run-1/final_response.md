Understanding
- This is Phase 6 (Quality Review) after implementation of a medium-sized caching feature across three Python service files.
- Track context: Standard.

Phase 6 Runbook (Order + Exact Subagents)
1. Launch `code-simplifier` subagent first
- Prompt focus:
"Review the caching-layer implementation across the three modified service files. Identify simplifications that preserve behavior: duplicated cache-key construction, repeated TTL/default handling, repeated error/fallback branches, and opportunities to extract shared helper functions without changing public APIs. Propose low-risk refactors in priority order."
- Output expected:
1. Refactor opportunities ranked by impact/risk.
2. Concrete code-level suggestions for clarity/DRY improvements.

2. Apply selected simplifications and keep tests green
- Integrate only low-risk, high-value simplifier recommendations.
- Re-run relevant tests before reviewer pass.

3. Launch independent `code-reviewer` subagent A (correctness/risk)
- Prompt focus:
"Independently review the caching changes for functional correctness and regression risk: cache invalidation behavior, stale data risk, race/concurrency edge cases, fallback-on-cache-failure behavior, and correctness of cache miss/hit branching. Identify high-severity defects first."
- Output expected:
1. Correctness defects and severity.
2. Required fixes before merge.

4. Launch independent `code-reviewer` subagent B (conventions/maintainability)
- Prompt focus:
"Independently review the same changes for Python conventions and maintainability: naming consistency, module boundaries, logging/error style, test readability, and long-term operability of the caching abstraction. Flag style/convention drift and unclear code paths."
- Output expected:
1. Maintainability and convention findings.
2. Suggested cleanups ranked by priority.

5. Consolidate and fix
- Address high-severity findings first, then medium issues with strong ROI.
- Re-run tests and summarize residual trade-offs.

Why this structure
- Refactoring and quality review are separate by design in feature-dev.
- `code-simplifier` runs before (or at least alongside) reviewer passes so independent reviewers evaluate a cleaner near-final code state.
- A single merged step is not used because it reduces independence and coverage.
