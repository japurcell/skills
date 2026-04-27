## Eval Prompt

Phase 11 is ready for work item `2026-04-23-add-retry-mechanism` on parent issue `#42`. Show the required commit message shape that coding-task-workflow expects, including any trailer formatting rules.

## Files Read

- `skills/coding-task-workflow-workspace/skill-snapshot/SKILL.md`
- `skills/coding-task-workflow-workspace/skill-snapshot/references/workflow.md`

## Steps

1. Read `SKILL.md` for the top-level Phase 11 priority rule and checklist entry.
2. Read the Phase 11 section in `references/workflow.md` for the exact commit message and trailer requirements.
3. Composed a concise user-facing answer showing the required shape for work item `2026-04-23-add-retry-mechanism` and parent issue `#42`.
4. Wrote the transcript, final answer, user notes, and metrics in the run directory.

## Final Answer

Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. Shape:

```text
fix(retry): add retry mechanism

Work-item: 2026-04-23-add-retry-mechanism
Parent: #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

If there are multiple trailers, keep them together in that final trailer block.
