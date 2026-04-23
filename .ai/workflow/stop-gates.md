# Stop gates

A phase cannot advance if its gate fails.

- **G00 Intake complete**: `00-intake.md` exists and acceptance criteria are listed.
- **G01 Worktree ready**: `01-worktree.md` exists and includes branch + path.
- **G02 Exploration done**: `02-exploration-summary.md` exists and includes open questions.
- **G03 Research done**: `03-research-findings.md` exists with dated sources.
- **G04 Clarifications resolved**: `04-clarifications.md` exists and blocking questions are resolved or escalated.
- **G05 Plan approved**: `05-plan.md` exists with verification strategy.
- **G06 DAG complete**: `06-task-graph.yaml` exists with red/green/refactor tasks.
- **G08 Reviews complete**: all three `08-*` review artifacts exist.
- **G09 Verification complete**: `09-verification.md` exists with executed checks and outcomes.

Use `python3 .ai/scripts/validate-artifacts.py --work-id <id>` for lightweight gate checks.
