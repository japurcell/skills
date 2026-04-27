Rule: Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block.

```text
<type>(<scope>): <subject>

Work-item: 2026-04-23-add-retry-mechanism
Parent: #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

The blank line before `Co-authored-by:` is required; the trailer block must be separated from the body.