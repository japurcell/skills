## Checklist Gate
- No checklist gate found for this feature directory, so execution proceeds to context loading.

## Implementation Context Loaded
- Plan artifact from the provided plan_file was loaded.
- Required task breakdown artifact is missing.
- Exact handling: stop implementation immediately and instruct the user to run /create-tasks (or regenerate planning artifacts), then rerun /implement-plan.

## Phase Execution
- Not started due to missing required planning artifact.

## Code Review Findings
- Not started because implementation did not begin.

## Completion Validation
- Status: FAIL
- Blocker: missing required task breakdown artifact.
- Next action: generate tasks, then rerun implementation.
