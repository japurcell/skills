## Checklist Gate
- Status: PASS (assumed by task statement)
- Evidence: All checklist files treated as complete; no blocking incompletes.

## Implementation Context Loaded
- Plan source: `.agents/scratchpad/feature-notify/plan.md`
- Required artifacts expected: `tasks.md`, `plan.md` (plus optional research/contracts/data model/quickstart)
- Parsed phases: Setup, Tests, Core, Integration, Polish
- Constraint detected: mixed `[P]` markers with overlapping file paths, so `[P]` is only parallelized when file sets are disjoint.

## Phase Execution
### Phase Handoff Packet (example: Core)
Use this exact handoff format when dispatching the phase subagent.

```text
Phase: Core
Task IDs (ordered): T-C01, T-C02 [P], T-C03 [P], T-C04
Dependency policy:
- Execute non-[P] tasks strictly in listed order.
- `[P]` tasks may run concurrently only if their touched file paths do not overlap.
- If `[P]` tasks overlap on any file, serialize them by task ID order.
TDD requirement:
- For each task: write/fail test -> implement minimal code -> pass tests -> refactor.
Task-state synchronization:
- Mark completed tasks as [X] in tasks.md immediately after verification.
Failure handling:
- Non-[P] failure: stop phase and report blocker.
- [P] failure: continue independent parallel siblings, then report failed task(s) and impact.
Deliverable back to orchestrator:
- Changed files list
- Test commands + pass/fail summary
- Updated task statuses in tasks.md
- Deferred items/blockers with rationale
```

## Code Review Findings
- Not run in this handoff step (execution-format definition only).
- Planned at phase completion: 1 simplification pass + 3 focused parallel review passes (simplicity, correctness, conventions).

## Completion Validation
Checkpoint criteria before moving to next phase:
1. Intended phase tasks are either completed `[X]` or explicitly deferred with reason.
2. `tasks.md` reflects actual completion state (no stale unchecked/completed mismatch).
3. Required tests for the phase were executed and results recorded.
4. No unresolved blocker that invalidates downstream phase assumptions.
5. Any deferred item includes owner + next action.

Checkpoint Decision
- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- Evidence: <tasks completed, tests run, files changed, blockers/deferments>
- Next Action: <advance to next phase | resolve blockers | request user approval>

Advancement rule:
- Advance automatically only on `PASS`.
- On `PASS WITH DEFERRED ITEMS`, advance only if deferments are non-blocking and explicitly logged.
- On `FAIL`, do not advance without user approval.
