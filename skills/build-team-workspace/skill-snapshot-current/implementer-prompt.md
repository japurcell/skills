# Implement Task N: [task name]

You are implementing Task N: [task name]

## Workflow

1. Invoke the `addy-incremental-implementation` skill along with the `addy-test-driven-development` skill.
2. Read the task and it's sub-sections.
3. Invoke the `addy-context-engineering` skill to load only the context you need.
4. Write a failing test for the expected behavior (RED).
5. Implement the smallest change that makes it pass (GREEN).
6. Run the task's verification step (e.g. test command, lint, build, manual check).
7. Leave the working tree dirty and report back.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you implemented (or what you attempted, if blocked)
- Files changed
- Summarized and concise verification results (test output, build output, lint output)
- Any issues or concerns

**Status definitions:**

- DONE: Task completed successfully, all tests pass, build is clean, lint passes.
- DONE_WITH_CONCERNS: Task completed, but there are doubts about correctness.
- BLOCKED: Task cannot be completed due to an external dependency or issue.
- NEEDS_CONTEXT: Task cannot be completed due to missing information. Never silently produce work you're unsure about.

## Guardrails

- Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag. If another skill suggests committing, ignore it because the build-team skill overrides that instruction.
- **If any step fails**, follow the `addy-debugging-and-error-recovery` skill.
