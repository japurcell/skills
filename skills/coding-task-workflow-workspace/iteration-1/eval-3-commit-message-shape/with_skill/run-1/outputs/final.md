Phase 11 requires a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. Shape:

```text
<type>(<scope>): <subject>

Work item: 2026-04-23-add-retry-mechanism
Parent issue: #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

If there is more than one trailer, keep all trailers together in that final trailer block.
