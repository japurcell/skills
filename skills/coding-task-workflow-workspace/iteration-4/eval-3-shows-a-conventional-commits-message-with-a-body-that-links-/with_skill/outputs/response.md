# Phase 11 Commit Message Shape for coding-task-workflow

## Required Format

The `coding-task-workflow` skill specifies the following commit message structure for **Phase 11** (Commit / Push / PR):

### Structure

```
<type>(<scope>): <subject>

<body with reference to work-item slug and parent issue>

Co-authored-by: <NAME> <EMAIL>
```

### Components

1. **Conventional Commits Subject Line** (mandatory)
   - Format: `<type>(<scope>): <subject>`
   - `<type>`: feature, fix, refactor, docs, chore, test, etc.
   - `<scope>`: component or area affected (e.g., `http-client`, `pagination`, etc.)
   - `<subject>`: concise description of the change

2. **Body** (mandatory)
   - References the work-item slug (e.g., `2026-04-23-add-retry-mechanism`)
   - References the parent issue number (e.g., `#42`)
   - Separated from subject line by a single blank line

3. **Trailer Block** (mandatory)
   - Format: `Co-authored-by: <NAME> <EMAIL>`
   - **Separated from the body by a blank line**
   - For GitHub Copilot CLI, use: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`

### Example

For work item `2026-04-23-add-retry-mechanism` on parent issue `#42`:

```
feat(http-client): add retry mechanism with exponential backoff

This implements the retry mechanism for HTTP client as specified in work item
2026-04-23-add-retry-mechanism. The implementation includes exponential backoff
with jitter and caps retries at 5 attempts for 429, 500, 502, 503, 504 status codes.

Closes #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Key Formatting Rules

1. **No blank line between subject and body** — they are separated by a single newline only
2. **Blank line before the trailer block** — this is mandatory and separates body content from co-author information
3. **Conventional Commits compliance** — subject follows the `<type>(<scope>): <subject>` shape
4. **Body must reference both**:
   - The work-item slug (deterministic, YYYY-MM-DD format)
   - The parent issue number (e.g., `#42`)
5. **Co-authored-by trailer uses proper email format** — `NAME <EMAIL>` with angle brackets

## Citation

- **Source**: `coding-task-workflow` skill
- **Reference**: [SKILL.md](../../../SKILL.md#non-negotiable-rules) line 33 and [`references/workflow.md`](../../../references/workflow.md#phase-11--commit--push--pr) Phase 11 specification (lines 310-321)
- **Authoritative text**: "Write a conventional-commits message: `<type>(<scope>): <subject>`. Include a body linking to the work-item slug and parent issue, then append a `Co-authored-by: NAME <EMAIL>` trailer block separated from that body by a blank line using your own known co-author identity."
