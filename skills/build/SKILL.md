---
name: build
description: Implement the next task incrementally — build, test, verify
argument-hint: <plan:.agents/scratchpad/<feature>/plan.md>
---

# Build

## Inputs

- `$plan`: the implementation plan containing the tasks, typically `.agents/scratchpad/<feature>/plan.md`.

## Workflow

1. Invoke the `addy-incremental-implementation` skill alongside `addy-test-driven-development`.
2. Pick the next pending task from `$plan`. For each task:
   a. Read the task's acceptance criteria
   b. Load relevant context (existing code, patterns, types)
   c. Write a failing test for the expected behavior (RED)
   d. Implement the minimum code to pass the test (GREEN)
   e. Run the relevant test suite to check for regressions
   f. Run the build to verify compilation
   g. check off completed items in `$plan` immediately and note any verification actually performed
   h. Mark the task `done` in the tracker
   i. Move to the next pending task

**If any step fails**, follow the `addy-debugging-and-error-recovery` skill.

## Tracking Discipline

- Treat `$plan` as the only execution record. Internal todo trackers, memory, scratchpads, and chat summaries can help coordination but never replace updating `$plan`.
- A task is complete only after the finished state is written to `$plan` and then verified by re-reading `$plan`.

## Commit Override Behavior

Do NOT commit. The user will review the changes and commit manually later.

## Red Flags

- Starting the next task before `$plan` is updated and re-read
- Treating runtime trackers as equivalent to `$plan`
- Stopping between ready tasks to ask for permission
- Committing changes

## Verification

After completing all tasks:

- [ ] Each increment was individually tested and verified
- [ ] The full test suite passes
- [ ] The build is clean
- [ ] The feature works end-to-end as specified
- [ ] Each completed task was written to `$plan`.
- [ ] After each `$plan` update, the `$plan` was re-read and matched the current execution state before the next task began.
- [ ] Ready tasks ran continuously until completion or a real blocker required escalation.
- [ ] All work remains uncommitted.
