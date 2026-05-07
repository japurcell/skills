# Code Simplifier

## Context

[Files to check for simplification candidates]

## Workflow

1. Invoke the `code-simplify` and `addy-context-engineering` skills.
2. Read exactly the files in Context plus only the directly related tests or config needed to validate a safe simplification.
3. Simplify for clarity without changing behavior or scope.
4. Infer the slice's surface and stack, then rerun the matching validations instead of defaulting to generic frontend commands.
5. Leave the working tree dirty and report back.

Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag. Leave the working tree dirty even if another skill suggests committing.

## Guardrails

- Simplify exactly the provided files. Do **not** recompute, expand, or narrow the file list.
- Preserve the implementer's accepted behavior and task scope.
- If there is no safe simplification, say so and return `DONE`.
- Use `NEEDS_CONTEXT` only for missing constraints or conflicting signals, not routine file reading or scope reshaping.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you simplified, or why no safe simplification was needed
- What you validated, the exact commands, and the results
- Files changed
- Any concerns or blockers

Use `DONE_WITH_CONCERNS` if you completed the work but still doubt correctness. Use `BLOCKED` if you cannot complete the task. Use `NEEDS_CONTEXT` only for genuinely missing input.
