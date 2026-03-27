# Checklist Gate
- Status: PASS (assumed per prompt)
- Evidence: All checklist files have 0 incomplete items.
- Decision: Proceed to implementation context loading.

# Implementation Context Loaded
- plan_file: `.agents/scratchpad/feature-notify/plan.md`
- Required artifacts: `plan.md` and `tasks.md` (assumed present and valid per prompt)
- Parsed phases from `tasks.md`: Setup, Tests, Core, Integration, Polish
- Execution rule acknowledged: `[P]` tasks run in parallel only when file paths do not overlap.

# Phase Execution
## Phase Handoff: Core (example)
- Phase goal: Deliver core feature behavior after Setup and Tests prerequisites are complete.
- Ordered task IDs: `C1`, `C2 [P]`, `C3 [P]`, `C4`
- Dependency policy:
  - `C1` must finish before `C2/C3`.
  - `C2` and `C3` may run concurrently only if touched files do not overlap.
  - `C4` starts only after required predecessors succeed (or are explicitly deferred).
- TDD requirement: For each task, write/fail test first, implement, then pass tests.
- Required task bookkeeping: Mark completed task lines as `[X]` in `tasks.md`.

### Subagent Prompt Template (for this phase)
```text
Execute phase: Core
Tasks (in order): C1, C2 [P], C3 [P], C4
Rules:
1) Respect sequential dependencies.
2) Run [P] tasks in parallel only when touched file paths do not overlap.
3) Apply TDD per task (red -> green -> refactor).
4) If a non-parallel task fails, halt the phase and report blocker.
5) If one [P] task fails, continue independent [P] tasks and report partial completion.
6) Update tasks.md checkboxes to [X] for completed tasks.
Deliverables:
- Changed files list
- Test results (per task and phase summary)
- Unresolved issues/blockers with impact
```

# Code Review Findings
- Post-phase review gate (required before next phase):
  - Run code-simplifier pass on touched files (excluding ignore files)
  - Run 3 focused reviews: simplicity/DRY, correctness/bugs, conventions/abstractions
- Consolidate to highest-severity findings and resolve required fixes before advancing.

# Completion Validation
## Checkpoint Criteria Before Moving to Next Phase
A phase checkpoint passes only if all criteria below are satisfied (or explicit user approval is captured for exceptions):
1. Scope completion:
   - All intended phase tasks are either completed or explicitly deferred with rationale.
2. Task-state integrity:
   - `tasks.md` checkbox state matches actual completion state.
3. Test validation:
   - Required tests for the phase were executed and results recorded.
   - New/changed behavior has passing tests.
4. Parallel safety audit:
   - Any `[P]` concurrency respected non-overlapping file-path constraint.
5. Failure handling compliance:
   - Non-parallel failure halted phase appropriately.
   - Parallel failure handling preserved independent progress and reported partials.
6. Review gate:
   - Code review findings triaged; blocking/high severity issues addressed or explicitly accepted.

Checkpoint decision format:
- Status: `PASS` | `PASS WITH DEFERRED ITEMS` | `FAIL`
- Evidence: tasks completed, tests run, files changed, issues/deferments
- Next action:
  - `PASS` -> start next phase
  - `PASS WITH DEFERRED ITEMS` -> start next phase with tracked follow-ups
  - `FAIL` -> stop and resolve blockers (or request user approval to continue)