Understanding
- Track: Standard (medium-sized feature, ~3 files, then review).

How The Workflow Enforces Requirements Across Tracks
- Implementation requirement (all tracks): Phase 5 requires using `tdd` with an explicit red-green-refactor loop.
- Refactor quality requirement: run a dedicated `code-simplifier` subagent to identify and apply safe simplifications.
- Review requirement (all tracks): Phase 6 requires independent `code-reviewer` subagent(s); Standard/Deep use multiple reviewers with distinct focus areas.

Execution Plan For This Request
1. Discovery + focused exploration to confirm touched files and conventions.
2. Implement via `tdd`:
- Red: add failing tests for the feature behavior.
- Green: implement minimal code changes across the three files.
- Refactor: clean up while preserving behavior.
3. Launch `code-simplifier` subagent:
- Focus: duplication removal, readability, API clarity, complexity reduction.
4. Launch independent `code-reviewer` subagent(s):
- Reviewer A focus: functional correctness, regressions, edge cases.
- Reviewer B focus: maintainability, conventions, clarity.
5. Consolidate findings, fix high-severity issues, summarize residual risks.

Exact Quality Review Roles
- `code-simplifier` (refactoring opportunities, no independent sign-off authority).
- `code-reviewer` (independent quality gate; one or more reviewers depending on track).

Recommendation
- Proceed on Standard track with the sequence above; it is calibrated for a medium-sized three-file change and satisfies implementation + review constraints without unnecessary escalation.
