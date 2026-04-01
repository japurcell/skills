Understanding
- Scope: small change touching two files (rate limiting in API handler).
- Track: Light.
- Constraint: 2-hour deadline.

Response
- We should not skip TDD.
- In the feature-dev workflow, Phase 5 requires using TDD (explicit red-green-refactor) on every track, including Light track and urgent work.

Fast Path That Preserves TDD
1. Tighten scope to the smallest viable slice
- Implement only core rate-limit check + deterministic rejection response.
- Defer non-essential enhancements (advanced metrics, configurability) to follow-up.
2. Minimal red phase (targeted failing tests first)
- Add focused tests for:
1. over-limit request returns expected status/body
2. under-limit request passes through
3. boundary case at threshold
3. Green phase
- Implement minimal logic in the two touched files to satisfy tests.
4. Refactor phase
- Small cleanup only (naming/duplication), keep tests green.
5. Phase 6 quality gates (still required)
- Run separate code-simplifier pass.
- Run independent code-reviewer pass.

If timing is still at risk
- Reduce feature scope further (for example fixed window only, single key strategy) rather than bypassing TDD.
- This preserves delivery speed and avoids shipping unverified behavior under pressure.
