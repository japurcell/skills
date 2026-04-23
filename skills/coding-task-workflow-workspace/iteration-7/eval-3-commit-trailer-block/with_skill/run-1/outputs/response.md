Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. For GitHub Copilot CLI, include `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

Shape:

```text
<type>(<scope>): <subject>

<body referencing work-item slug 2026-04-23-add-retry-mechanism and parent issue #42>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Rules:

- Subject follows conventional commits (e.g. `feat(retry): add retry mechanism`).
- Body is separated from the subject by one blank line and must link both the work-item slug (`2026-04-23-add-retry-mechanism`) and the parent issue (`#42`).
- Trailer block is separated from the body by one blank line and contains `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` exactly as shown.
