## Checklist Gate

- Status: PASS
- Evidence: `checklists/` assumed complete with 0 incomplete items; no checklist blocker for `.agents/scratchpad/feature-notify/plan.md`.

## Implementation Context Loaded

- Files read: `.agents/scratchpad/feature-notify/plan.md`, derived `.agents/scratchpad/feature-notify/tasks.md`.
- Optional context to load if present: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`.
- Parsed execution phases: Setup, Tests, Core, Integration, Polish.
- Scheduling rule: `[P]` tasks may run in parallel only when their target file paths do not overlap; any overlap forces sequential execution.

## Phase Execution

Phase Handoff: Tests
- Current Phase: Tests
- Ordered Task IDs: `<tests-phase task IDs from tasks.md in listed order>`
- Dependency Rules: run non-`[P]` tasks in order; run `[P]` tasks concurrently only when their file sets are disjoint; serialize any `[P]` tasks that touch overlapping paths.
- TDD Requirement: write or update failing tests first, then implement the minimum code needed to make them pass.
- Task Tracking: mark completed items as `[X]` in `tasks.md`; record any deferments explicitly.
- Expected Deliverable: changed files, tests run with results, unresolved issues or deferments.

Checkpoint Decision
- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- Evidence: all intended Tests tasks completed or explicitly deferred; `tasks.md` matches actual completion; required phase tests executed and reported; changed files and blockers captured.
- Next Action: advance to Core if PASS or PASS WITH DEFERRED ITEMS; otherwise resolve blockers or request user approval before continuing.

## Code Review Findings

- Review status: not started for this handoff.
- Evidence: after phase completion, compute review scope from uncommitted changed files, exclude deleted files and `.gitignore`, then run coverage and reviewer checks before reporting findings.

## Completion Validation

- Current scope: phase handoff only; final completion validation occurs after all phases finish.
- Exit criteria before overall completion: all required tasks complete, implementation matches the plan, required tests pass, and the final checkpoint permits closure.