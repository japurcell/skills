---
name: build
description: Implement the next task incrementally — build, test, verify
---

# Build

## Workflow

1. Invoke the `addy-context-engineering`, `subagent-model-selection`, `addy-incremental-implementation`, and `addy-test-driven-development` skills.
2. Pick the next pending task from the plan.
3. Dispatch an implementer subagent with the [implementer-prompt.md](./implementer-prompt.md) template.
4. Wait for the implementer to report back.
5. If the implementer reports success, mark the task as completed in the plan.
6. Move to the next pending task.

## Commit Override Behavior

Do NOT commit. The user will review the changes and commit manually later.

## Verification

After completing all tasks:

- [ ] Each increment was individually tested
- [ ] The relevant test suite passes
- [ ] The build is clean
- [ ] The feature works end-to-end as specified
- [ ] All tasks in the plan are marked as completed
- [ ] All changes are uncommitted
