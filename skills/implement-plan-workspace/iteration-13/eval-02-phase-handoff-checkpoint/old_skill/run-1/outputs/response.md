## Phase Execution

Phase Handoff: Tests
- Ordered tasks: execute the unchecked Tests-phase tasks in declared order, but run any test-writing work before its paired implementation work.
- Dependency rules: sequential tasks stay in order; `[P]` tasks may run in parallel only when their touched file paths do not overlap.
- Overlap rule: any `[P]` tasks that touch the same file path are forced back to sequential execution for this phase.
- Touched file paths: include only the files listed for the Tests phase tasks.
- Resumption state: skip any tasks already marked `[X]`; execute only remaining unchecked Tests-phase tasks.
- Planning context passed to the phase subagent: `plan.md`, `tasks.md`, plus any available `data-model.md`, `contracts/`, `research.md`, and `quickstart.md`.
- Verification expectations:
  - TDD RED tasks: run the new tests and accept a clean RED for the intended reason.
  - Code changes: build/lint changed files and run related tests before any task is marked `[X]`.

Required phase subagent report
- Tasks attempted
- RED / GREEN / REFACTOR progress
- Files changed
- Validations run
- Failures or deferments
- Tasks ready to mark `[X]`

Checkpoint Decision
- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- Evidence: <tasks completed, tests run, files changed, blockers/deferments>
- Integrity check: <any `[X]` tasks whose expected outputs are missing or whose tests now fail>
- Next Action: <advance to next phase | resolve blockers | request user approval>

The controller updates `tasks.md` checkmarks only after the phase report includes verification evidence. If checkpoint validation finds a broken `[X]` task, that task is reverted to `[ ]` before moving to the next phase.
