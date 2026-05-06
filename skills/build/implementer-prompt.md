# Implement Task N: [task name]

You are implementing Task N: [task name]

## Task Description

[FULL TEXT of task from plan - paste it here, don't make subagent read file]

## Context

[Scene-setting: existing code, patterns, types]

## Workflow

1. Invoke the `addy-incremental-implementation`, `addy-test-driven-development`, and `addy-context-engineering` skills.
2. Write a failing test for the expected behavior (RED)
3. Implement the minimum code to pass the test (GREEN)
4. Run the relevant test suite to check for regressions
5. Run the build to verify compilation
6. Report back

**If any step fails**, follow the `addy-debugging-and-error-recovery` skill.

## Report Format

When done, report:

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you implemented (or what you attempted, if blocked)
- What you tested and test results
- Files changed
- Any issues or concerns

**Status Determination**:

- Use DONE_WITH_CONCERNS if you completed the work but have doubts about correctness.
- Use BLOCKED if you cannot complete the task.
- Use NEEDS_CONTEXT if you need
  information that wasn't provided. Never silently produce work you're unsure about.
