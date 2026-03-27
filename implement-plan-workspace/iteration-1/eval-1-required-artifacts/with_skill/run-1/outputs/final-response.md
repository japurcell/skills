## Checklist Gate
- Checklist scan status: not evaluated in this scenario output.
- Gate decision: proceed to implementation context loading.

## Implementation Context Loaded
- Loaded plan artifact: .agents/scratchpad/feature-export/plan.md (present).
- Required artifact check: .agents/scratchpad/feature-export/tasks.md (missing).
- Handling behavior (exact per skill): stop execution and instruct user to run /create-tasks or regenerate planning artifacts.

Blocking message:
Required planning artifact missing: tasks.md. Cannot continue /implement-plan because both plan.md and tasks.md are required. Run /create-tasks for .agents/scratchpad/feature-export/plan.md (or regenerate planning artifacts), then rerun /implement-plan.

## Phase Execution
- Not started.
- Reason: context loading failed at required artifact validation.

## Code Review Findings
- Not started.
- Reason: no implementation changes were executed.

## Completion Validation
- Final status: BLOCKED.
- Preconditions to continue:
  - tasks.md exists under .agents/scratchpad/feature-export/
  - rerun /implement-plan with the same plan_file
