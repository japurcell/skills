# Delegation rules

## Sequential-only phases

- 00 Intake
- 01 Worktree setup
- 04 Clarifications
- 05 Plan
- 09 Verification
- 10 PR open

## Parallel-friendly phases

- 02 Exploration: parallel subagents for module/file analysis
- 03 Research: parallel subagents for official docs and open questions
- 08 Review: parallel specialized reviewers (code/security/tech debt)

## Mixed phase

- 06/07 Task graph + implementation:
  - Respect `depends_on`
  - Tasks marked `parallelizable: true` may run concurrently
  - Red -> Green -> Refactor order must be preserved per dependency chain

## Delegation constraints

1. Every delegated task must cite expected artifact output.
2. Agent output must be merged into canonical artifact files.
3. Conflicts between subagents require explicit decision logging in plan/review artifacts.
