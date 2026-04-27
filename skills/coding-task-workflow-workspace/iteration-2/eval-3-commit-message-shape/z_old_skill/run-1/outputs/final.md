Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block.

```text
feat: add retry mechanism

Work-item: 2026-04-23-add-retry-mechanism
Parent: #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

The required shape is: conventional-commits subject first, then a body that links the work item and `#42`, then a **blank line**, then the trailer block with the Copilot `Co-authored-by` line.
