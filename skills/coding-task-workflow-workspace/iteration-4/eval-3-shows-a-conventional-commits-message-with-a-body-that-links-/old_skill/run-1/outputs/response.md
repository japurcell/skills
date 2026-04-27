# Phase 11 Commit Message Format

## Governing Rule

From SKILL.md (Rule 5 - Non-negotiable rules):

> Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. For GitHub Copilot CLI, include `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

## Required Commit Message Shape

```
<type>(<scope>): <subject>

<body with reference to work-item slug and parent issue>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Format Specification

### Subject Line (First Line)
- **Format**: `<type>(<scope>): <subject>`
- **Type**: One of `feat`, `fix`, `refactor`, `chore`, etc. (conventional commits)
- **Scope**: Optional, but recommended (e.g., `http-client`, `retry-logic`)
- **Subject**: Concise description of the change

### Body (After Subject)
- Separated from subject by a blank line
- Must reference:
  - The **work-item slug** (format: `YYYY-MM-DD-<kebab-title>`, e.g., `2026-04-23-add-retry-mechanism`)
  - The **parent issue** (e.g., `#42`)
- Can include additional context, rationale, or change summary

### Trailer Block (After Body)
- **Separated by a blank line** from the body above it
- Starts with: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`
- RFC 2822 trailer format (key-value pairs)

## Example for Work Item `2026-04-23-add-retry-mechanism` on Parent Issue `#42`

```
feat(http-client): add retry mechanism with exponential backoff

Implements exponential backoff and jitter for HTTP client retries.
Retries on status codes 429, 500, 502, 503, and 504.
Maximum of 5 retry attempts.

Work item: 2026-04-23-add-retry-mechanism
Fixes #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Blank Line Rules (Critical Formatting)

1. **After subject** → blank line before body
2. **After body** → blank line before trailer block
3. **Trailer block** → no blank lines within the trailer block itself

This ensures the trailer block is properly recognized by git and GitHub tools that parse trailer metadata.
