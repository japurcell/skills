Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block.

```text
feat(retry): add retry mechanism

Work item: 2026-04-23-add-retry-mechanism
Parent issue: #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Required shape: `<type>(<scope>): <subject>`. The trailer block must be separated from the body by a blank line. If there are multiple trailers, keep them together in that final trailer block.
