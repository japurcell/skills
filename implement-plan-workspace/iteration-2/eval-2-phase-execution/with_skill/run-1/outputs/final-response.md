## Checklist Gate
| Checklist | Total | Completed | Incomplete | Status |
|-----------|-------|-----------|------------|--------|
| ux.md | 12 | 12 | 0 | PASS |
| test.md | 8 | 8 | 0 | PASS |
| security.md | 6 | 6 | 0 | PASS |

All checklist gates passed; proceed.

## Implementation Context Loaded
- plan_file: .agents/scratchpad/feature-notify/plan.md
- Required artifacts assumed present and parsed: plan.md, tasks.md
- Task model detected: phases Setup, Tests, Core, Integration, Polish with mixed [P] markers
- Parallel rule enforced: [P] tasks may run concurrently only when file paths do not overlap

## Phase Execution
### Phase: Core
Ordered tasks for this phase (example handoff): T301, T302 [P], T303 [P], T304

Subagent handoff prompt (concise):
1. Execute Core phase tasks in order: T301 -> (T302 [P] + T303 [P] if no file overlap) -> T304.
2. Apply TDD per task: add/fail tests first, implement, then pass tests.
3. For [P] tasks, run concurrently only when touched files are disjoint; if overlap exists, serialize.
4. If a non-parallel task fails, halt the phase immediately and report blocker.
5. If one [P] task fails, continue other independent [P] tasks, then report failed task IDs.
6. Mark completed tasks as [X] in tasks.md.
7. Return deliverables: changed files, test commands/results, deferred tasks/issues.

Expected phase evidence:
- Changed files list with ownership per task ID
- Test run log for phase-relevant suites
- Updated tasks.md status for T301-T304
- Explicit unresolved issues/blockers

## Code Review Findings
- Pending post-phase checkpoint.
- On completion of Core phase changes, run:
  - code-simplifier pass on touched non-ignore files
  - 3 parallel reviews: (simplicity/DRY), (bugs/correctness), (conventions/abstractions)
- Record highest-severity findings and required fixes before completion validation.

## Completion Validation
Checkpoint criteria required before moving Core -> Integration:
1. Scope completion: Every intended Core task is either [X] complete or explicitly deferred with reason.
2. Status sync: tasks.md checkboxes match actual implementation state.
3. Test integrity: Required Core tests executed; failures triaged and linked to task IDs.
4. Dependency integrity: Any failed non-[P] task blocks phase promotion.
5. Parallel safety: [P] execution log confirms no overlapping file writes during concurrent runs.
6. Artifacts integrity: Changed files, commands, and outcomes are captured in phase report.
7. Approval rule: Move to Integration only if checkpoint passes, or user explicitly approves continuation with known failures.

Final phase status (this exercise): READY-FOR-HANDOFF TEMPLATE PROVIDED.
