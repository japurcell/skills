# Implement Task N: [task name]

You are implementing Task N: [task name]

## Workflow

1. Invoke the `addy-incremental-implementation`, `addy-test-driven-development`, and `addy-context-engineering` skills.
2. Read the task and acceptance criteria.
3. Load the minimum context yourself: code, tests, patterns, types, and commands.
4. Form the first-pass approach from that context.
5. Write a failing test for the expected behavior (RED).
6. Implement the minimum change to pass it (GREEN).
7. Infer the slice's surface and stack first, then run the matching tests, build checks, or manual verification instead of defaulting to generic frontend commands.
8. Report back.

**If any step fails**, follow the `addy-debugging-and-error-recovery` skill.

## Context Expectations

- Assume the manager gives you a lean handoff, not a pre-solved design.
- Read the relevant files and find patterns yourself.
- Do **not** ask for more context just because you have not explored the repo yet.
- Treat "run the relevant validations" as a selection task: choose the narrowest checks that match the files and stack in this slice.
- Use `NEEDS_CONTEXT` only for missing product decisions, missing constraints, or conflicting signals you cannot resolve from the codebase and task context.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you implemented (or what you attempted, if blocked)
- What you tested, the exact commands, and the results
- Files changed
- Any issues or concerns

**Status Determination**:

- Use DONE_WITH_CONCERNS if you completed the work but have doubts about correctness.
- Use BLOCKED if you cannot complete the task.
- Use NEEDS_CONTEXT if you need information that wasn't provided. Use it for genuinely missing requirements or unresolved conflicts, not routine discovery. Never silently produce work you're unsure about.
