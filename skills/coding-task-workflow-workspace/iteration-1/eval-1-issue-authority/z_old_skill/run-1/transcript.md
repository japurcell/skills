## Eval Prompt

Run only Phase 1 Intake for coding-task-workflow with `ISSUE: 42`. I also typed `WORK_ITEM: maybe clean up auth later`, but the GitHub issue body actually describes a CSV import bug that silently drops rows. Tell me what Intake should do and what it should use as the work item.

## Files Read

- `skills/coding-task-workflow-workspace/skill-snapshot/SKILL.md`
- `skills/coding-task-workflow-workspace/skill-snapshot/references/workflow.md`
- `skills/coding-task-workflow-workspace/skill-snapshot/references/stop-gates.md`
- `skills/coding-task-workflow-workspace/skill-snapshot/references/templates/intake.md`

## Steps

1. Read `SKILL.md` to find the governing Intake authority rule and Phase 1 checklist.
2. Read `references/workflow.md` for the detailed Phase 1 Intake procedure.
3. Read `references/templates/intake.md` to confirm what `00-intake.md` must contain.
4. Applied the issue-authority rule to the prompt: `ISSUE: 42` overrides the separately typed auth-cleanup note.
5. Wrote the final user-facing answer and metrics artifacts in the run directory.

## Final Answer

The GitHub issue title/body is the authoritative WORK_ITEM, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue. For Phase 1 Intake, fetch ISSUE 42 first, infer the work item from its title/body, classify it, assign a `YYYY-MM-DD-<kebab-title>` slug, create `.coding-workflow/work/<slug>/`, write `00-intake.md` from the intake template, and record the issue number/node ID with a comment linking the intake artifact. Here, the work item should be the CSV import bug that silently drops rows; `WORK_ITEM: maybe clean up auth later` is supplemental only and must not override the issue.
