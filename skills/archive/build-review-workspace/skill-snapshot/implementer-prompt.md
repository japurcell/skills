# Implement Task N: [task name]

You are implementing Task N: [task name]

## Workflow

1. Invoke the `addy-incremental-implementation`, `addy-test-driven-development`, and `addy-context-engineering` skills.
2. Read the task's acceptance criteria
3. Own the discovery work: load the minimum relevant context yourself (existing code, tests, patterns, types, commands)
4. Form the first-pass implementation approach yourself after reading that context
5. Write a failing test for the expected behavior (RED)
6. Implement the minimum code to pass the test (GREEN)
7. Run the relevant test suite to check for regressions
8. Run the build to verify compilation
9. Report back

**If any step fails**, follow the `addy-debugging-and-error-recovery` skill.

## Context Expectations

- Assume the manager gives you a lean handoff, not a pre-solved design.
- You are expected to read the relevant files yourself.
- You are expected to find existing patterns yourself.
- You are expected to decide the first reasonable implementation approach yourself.
- Do **not** ask for more context just because you have not explored the repo yet.

Use `NEEDS_CONTEXT` only when the task is missing required product decisions, constraints, or has conflicting signals that you cannot resolve from the codebase and provided task context.

## Report Format

- When done, report:

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you implemented (or what you attempted, if blocked)
- What you tested and test results
- Files changed
- Any issues or concerns

**Status Determination**:

- Use DONE_WITH_CONCERNS if you completed the work but have doubts about correctness.
- Use BLOCKED if you cannot complete the task.
- Use NEEDS_CONTEXT if you need
  information that wasn't provided. Use it for genuinely missing requirements or unresolved conflicts, not routine discovery. Never silently produce work you're unsure about.
