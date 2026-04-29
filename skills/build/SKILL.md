---
name: build
description: Implement the next task incrementally — build, test, verify, commit
---

# Build

## Workflow

1. Invoke the `addy-incremental-implementation` skill alongside `addy-test-driven-development`.
2. Pick the next pending task from the plan. For each task:
   a. Read the task's acceptance criteria
   b. Load relevant context (existing code, patterns, types)
   c. Write a failing test for the expected behavior (RED)
   d. Implement the minimum code to pass the test (GREEN)
   e. Run the full test suite to check for regressions
   f. Run the build to verify compilation
   g. Mark the task complete and move to the next one

**If any step fails**, follow the `addy-debugging-and-error-recovery` skill.

## Commit Override Behavior

Do NOT commit. The user will review the changes and commit manually later.

## Subagent Guidance

When using subagents:

- Invoke the `subagent-model-selection` skill.

## Verification

After completing all tasks:

- [ ] Each increment was individually tested and committed
- [ ] The full test suite passes
- [ ] The build is clean
- [ ] The feature works end-to-end as specified
- [ ] All changes are uncommitted
