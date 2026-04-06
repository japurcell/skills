## Checklist Gate
- Context-loading excerpt: this response starts at the point where implementation context loading begins.
- Evidence: no checklist outcome is evaluated in this excerpt.

## Implementation Context Loaded
- Read `.agents/scratchpad/feature-export/plan.md`.
- Required artifact missing: `.agents/scratchpad/feature-export/tasks.md`.
- Stop condition reached: `/implement-plan` requires both `plan.md` and `tasks.md` before execution can continue.
- Action required: run `/create-tasks` or regenerate the planning artifacts, then rerun `/implement-plan`.

## Phase Execution
- Not started.
- Execution is halted before phase execution because `tasks.md` is missing, so task parsing and phase/subagent execution cannot begin.

Checkpoint Decision
- Status: FAIL
- Evidence: `plan.md` available; `tasks.md` missing; no actionable task list could be loaded; no phases executed; no tests run; no files changed
- Next Action: run `/create-tasks` or regenerate planning artifacts, then rerun `/implement-plan`

## Code Review Findings
- Not started.
- Evidence: code review is skipped because implementation did not begin and there are no implementation changes to review.

Review Scope Coverage
- Total Changed (Uncommitted) Files: 0
- Total Reviewed Files: 0
- Missing Files: 0
- Missing File List: none
- Excluded Files: none
- Completion Gate: Missing Files > 0 => INCOMPLETE (requires explicit deferment/approval)

## Completion Validation
- Status: FAIL
- Evidence: prerequisite planning artifacts are incomplete; execution halted before phase execution.
- Required next step: run `/create-tasks` or regenerate planning artifacts, then rerun `/implement-plan`.
