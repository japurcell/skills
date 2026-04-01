Phase 6 Quality Review (Feature-Dev Workflow)

Order Of Execution
1. Launch `code-simplifier` first.
2. Launch independent `code-reviewer` agents after simplification pass (or with final simplification diff in hand).
3. Consolidate findings, fix high-severity items, then report residual risks.

Subagents And Focus Prompts
1. `code-simplifier` (dedicated refactor pass)
- Focus:
  - Remove duplication introduced across the three caching-related service files.
  - Simplify cache key construction and invalidation flow for readability.
  - Reduce branching complexity while preserving behavior.
  - Keep public interfaces and semantics unchanged.

2. `code-reviewer` - Correctness focus (independent reviewer)
- Focus:
  - Validate cache-hit/miss correctness and stale-data edge cases.
  - Check invalidation paths and race-condition risks.
  - Verify error handling/fallback behavior under cache backend failures.

3. `code-reviewer` - Conventions & maintainability focus (independent reviewer)
- Focus:
  - Confirm Python style/conventions and module boundaries.
  - Assess naming clarity, test readability, and long-term maintainability.
  - Flag unnecessary coupling between service files.

Why This Split Matters
- Refactoring (`code-simplifier`) and independent quality judgment (`code-reviewer`) are distinct controls.
- Keeping them separate preserves reviewer independence and improves defect detection.

Deliverable From Phase 6
- Consolidated issue list prioritized by severity.
- Applied fixes for obvious high-severity issues.
- Clear summary of any remaining trade-offs and follow-up tasks.
