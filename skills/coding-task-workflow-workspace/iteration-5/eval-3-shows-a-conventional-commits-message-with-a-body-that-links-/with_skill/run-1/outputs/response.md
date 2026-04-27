# coding-task-workflow Phase 11 Commit Message Format Evaluation

## Scenario

- **Work item slug**: `2026-04-23-add-retry-mechanism`
- **Parent issue**: `#42`
- **Phase**: 11 (Commit / Push / PR)

## Skill Specification: Phase 11 Commit Message Requirements

**From references/workflow.md, Phase 11 — Commit / Push / PR, Step 2:**

> Write a conventional-commits message: `<type>(<scope>): <subject>`. Include a body linking to the work-item slug and parent issue, then append a `Co-authored-by: NAME <EMAIL>` trailer block separated from that body by a blank line using your own known co-author identity. For GitHub Copilot CLI, use `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

**From SKILL.md, Non-negotiable rule #7:**

> Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. For GitHub Copilot CLI, include `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

## Required Commit Message Shape

### Structure

```
<type>(<scope>): <subject>

<body-content>

Co-authored-by: NAME <EMAIL>
```

### Components

#### 1. **First Line (Conventional-Commits Subject)**

Format: `<type>(<scope>): <subject>`

- **`<type>`**: One of `feat`, `fix`, `docs`, `refactor`, `chore`, etc. (determined by work classification)
- **`<scope>`**: Optional narrowing of impact (e.g., `http-client`, `auth`, `csv-import`)
- **`<subject>`**: Imperative, present-tense description without period (e.g., "add retry mechanism with exponential backoff")

#### 2. **Blank Line**

One blank line separates the subject from the body.

#### 3. **Body**

Contains:
- **Work-item slug** reference: `2026-04-23-add-retry-mechanism`
- **Parent issue** reference: `#42`
- Free-form description of changes
- May include technical rationale or migration notes

The specification states the body must link to both the work-item slug and parent issue.

#### 4. **Blank Line**

One blank line separates the body from the trailer block.

#### 5. **Trailer Block**

Format: `Co-authored-by: NAME <EMAIL>`

For GitHub Copilot CLI, use exactly:
```
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Example Commit Message

For the scenario with `2026-04-23-add-retry-mechanism` and parent issue `#42`:

```
feat(http-client): add retry mechanism with exponential backoff and jitter

Implements retry logic for HTTP client as specified in work item
2026-04-23-add-retry-mechanism (fixes #42). Includes exponential
backoff with jitter, capped at 5 retries, for status codes 429,
500, 502, 503, 504.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

### For a bug fix example:

```
fix(csv-import): prevent silent row drops during import

Fixes regression in csv-import where rows are silently dropped when
total_count is a multiple of page_size. Work item:
2026-04-23-add-retry-mechanism (resolves #42). Adds regression test
with reproduction case for page_size=10, total_count=20.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Trailer Formatting Rules

1. **Blank line separation**: The trailer block MUST be separated from the body by exactly one blank line
2. **Format**: `Co-authored-by: NAME <EMAIL>` (not `Co-Author` or other variants)
3. **For GitHub Copilot CLI**: Use the exact identity: `Copilot <223556219+Copilot@users.noreply.github.com>`
4. **No extra content after trailer**: The trailer block is the final element of the commit message
5. **Single trailer**: Only one `Co-authored-by` trailer is required by the workflow specification

## Additional Context: PR Body

While the commit message is the main artifact, note that Phase 11 also opens a PR with:

- **Title**: Same as the conventional-commits subject
- **Body**: Must include `Fixes #<parent issue number>` (e.g., `Fixes #42`), summary of changes, and any follow-up items

PR Body Example:
```
Fixes #42

## Summary

Implements retry mechanism with exponential backoff and jitter for the HTTP client.
Retries on 429, 500, 502, 503, 504 with exponential backoff capped at 5 attempts.

## Changes

- Added retry handler to HTTP client
- Implemented exponential backoff with jitter
- Added tests for single and max retry scenarios

## Follow-up Items

- None
```

## Summary Table

| Element | Requirement |
|---------|-------------|
| **Subject line format** | `<type>(<scope>): <subject>` using conventional commits |
| **Body content** | Must reference work-item slug (`2026-04-23-add-retry-mechanism`) and parent issue (`#42`) |
| **Body-to-trailer separation** | Exactly one blank line |
| **Trailer format** | `Co-authored-by: NAME <EMAIL>` |
| **GitHub Copilot CLI trailer** | `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` |
| **Trailer separation** | Blank line before trailer block (not after subject) |
| **Message flow** | Subject → blank line → body → blank line → trailer |

This format ensures the commit is both human-readable (conventional commits) and machine-parseable (structured trailer), while preserving the durable link to the GitHub parent issue (#42) and the workflow's internal work-item tracking.
