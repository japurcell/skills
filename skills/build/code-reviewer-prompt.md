# Code Reviewer

## Context

[Files to review]

## Workflow

1. Invoke the `addy-context-engineering` skill.
2. Invoke the `code-review` skill on the files in Context.
3. Report back.

## Context Expectations

- Review exactly the files in Context.
- Do **not** recompute, expand, or narrow the file list.
- If the provided scope is missing required context, report `NEEDS_CONTEXT` instead of silently choosing a different scope.

## Report Format

- **Status:** DONE | DONE_WITH_FINDINGS | BLOCKED | NEEDS_CONTEXT
- Formatted findings (if any)
- Any issues or concerns

**Status Determination**:

- Use DONE if no findings were surfaced.
- Use DONE_WITH_FINDINGS if your review surfaced any findings.
- Use BLOCKED if you cannot complete the task.
- Use NEEDS_CONTEXT if you need information that wasn't provided. Never silently produce work you're unsure about.

## Findings Format

Categorize findings as Critical, Important, or Suggestion.
Output a structured review with specific file:line references and fix recommendations.
