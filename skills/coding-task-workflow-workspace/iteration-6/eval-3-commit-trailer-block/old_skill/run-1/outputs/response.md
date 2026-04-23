Use this Phase 11 shape:

```text
<type>(<scope>): <subject>

<summary/body text>
- Work item: 2026-04-23-add-retry-mechanism
- Parent issue: #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Example:

```text
feat(http-client): add retry mechanism with exponential backoff

Implement retry handling for transient HTTP failures.
- Work item: 2026-04-23-add-retry-mechanism
- Parent issue: #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Rules: the subject must be conventional-commits format `<type>(<scope>): <subject>`; the body must reference the work-item slug and parent issue; the `Co-authored-by` trailer must be in a final trailer block separated from the body by a blank line; if there are multiple trailers, keep them together in that final trailer block.
