## Checklist Gate
- No checklist gate data provided for `.agents/scratchpad/feature-export/checklists/`.
- Proceeding to required artifact loading.

## Implementation Context Loaded
- Base feature directory derived from `plan_file`: `.agents/scratchpad/feature-export/`
- Required artifacts policy at context-load time:
  - Must read `.agents/scratchpad/feature-export/tasks.md` (required)
  - Must read `.agents/scratchpad/feature-export/plan.md` (required)
- Handling behavior for this scenario (plan exists, tasks missing):
  - `tasks.md` is missing
  - `plan.md` is treated as present per scenario assumption
  - Execution **stops immediately** at required-artifact validation
  - User instruction: run `/create-tasks` (or regenerate planning artifacts) to create `tasks.md`, then re-run `/implement-plan`

## Phase Execution
- Not started.
- Reason: required artifact gate failed before task parsing.

## Code Review Findings
- Not started.
- Reason: no implementation phase executed and no touched files.

## Completion Validation
- Result: **FAIL (blocked at required artifacts)**
- Evidence:
  - Missing required file: `.agents/scratchpad/feature-export/tasks.md`
  - Required to continue: both `tasks.md` and `plan.md`
- Next action:
  - Run `/create-tasks` for `.agents/scratchpad/feature-export/plan.md`
  - Re-run `/implement-plan` after `tasks.md` is generated
