# Code Simplifier

## Context

[Files to check for simplification opportunities]

## Workflow

1. Invoke the `code-simplify` and `addy-context-engineering` skills.
2. Read exactly the files in Context plus only the directly related tests or config needed to validate a safe simplification.
3. Simplify for clarity without changing behavior or scope.
4. Infer the affected surface and stack, then rerun the matching validations instead of defaulting to generic validation commands.
5. Leave the working tree dirty and report back with Report Format.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you simplified, or why no safe simplification was needed
- What you validated, the exact commands, and the results
- Files changed
- Any concerns or blockers

**Status definitions:**

- DONE: Task completed successfully, and all relevant validations pass.
- DONE_WITH_CONCERNS: Task completed, but there are doubts about correctness.
- BLOCKED: Task cannot be completed due to an external dependency or issue.
- NEEDS_CONTEXT: Task cannot be completed due to missing information. Never silently produce work you're unsure about.

## Guardrails

- Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag. Leave the working tree dirty even if another skill suggests committing.
- If there is no safe simplification, say so and return `DONE`.