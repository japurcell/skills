I’ve extracted the required structure from the authoritative skill and will now provide a concise, ready-to-use single-phase handoff template plus the checkpoint gate required before advancing.

## Phase Execution

### Phase Handoff: Core
- Phase Goal: Implement core domain behavior and service logic for this feature.
- Ordered Tasks:
  - C1 (sequential)
  - C2 (sequential)
  - C3 [P]
  - C4 [P]
- Dependency Rules:
  - Run sequential tasks in listed order.
  - Run [P] tasks in parallel only if their file paths do not overlap.
  - If a sequential task fails, halt the phase.
  - If one parallel task fails, continue other independent parallel tasks, then report failures.
- Required Execution Rules:
  - Apply TDD for each task (write/confirm failing test, implement minimal fix, rerun tests).
  - Update task checkboxes to [X] immediately after verified completion.
- Deliverable for Phase Completion:
  - Files changed
  - Tests executed and results
  - Deferred items/blockers with reason and owner

## Checkpoint Decision

- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- Evidence:
  - All planned phase tasks completed or explicitly deferred
  - Task status is synchronized with actual completion
  - Required phase tests executed (with pass/fail summary)
  - Blockers/deferments documented
- Next Action:
  - advance to next phase (PASS)
  - request user approval to continue (PASS WITH DEFERRED ITEMS)
  - resolve blockers before continuing (FAIL)

Checkpoint Decision
- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- Evidence: <tasks completed, tests run, files changed, blockers/deferments>
- Next Action: <advance to next phase | resolve blockers | request user approval>
