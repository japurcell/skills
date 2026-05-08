---
name: build
description: Implement the next task incrementally — build, test, verify
---

# Build

You are the orchestrator, and you implement the plan by dispatching a fresh subagent per task.

**Why subagents**: You delegate tasks to specialized agents with isolated context to preserve your own context for coordination work.

**Core principle:** Fresh subagent per task = high quality, fast iteration, without context pollution.

**Continuous execution:** Do not pause to check in with the human between tasks. Execute all tasks from the plan without stopping. The only reasons to stop are: BLOCKED status you cannot resolve, ambiguity that genuinely prevents progress, or all tasks complete. "Should I continue?" prompts and progress summaries waste their time.

## Source of Truth

`plan.md` is the authoritative record of task status.

Internal todo trackers, memory, scratchpads, runtime task lists, and chat status messages are non-authoritative and must never be treated as substitutes for updating `plan.md`.

A task is considered completed only when its completion is persisted in `plan.md`.

## Workflow

1. Read `plan.md` and pick the next pending task from the file.
2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the implementer subagent.
3. Dispatch an implementer subagent with the [implementer-prompt.md](./implementer-prompt.md) template.
4. Wait for the implementer to report back.
5. If the implementer reports `DONE`, update `plan.md` immediately to mark the task as completed.
6. Save the change to `plan.md`.
7. Verify directly in `plan.md` that the task now appears completed.
8. Only after that verification, move to the next pending task.

## Task Completion

Mark the task as completed in `plan.md` only when the implementer reports `DONE`.

A task is not complete until the completion state is written to `plan.md`.

**Examples of completed tasks**:

1. A simple task: `- [x] Task 1: Add user registration endpoint`
2. A task with subtasks:

   ```markdown
   ## Task [N]: [Short descriptive title]

   **Description:** One paragraph explaining what this task accomplishes.

   **Acceptance criteria:**

   - [x] [Specific, testable condition]
   - [x] [Specific, testable condition]

   **Verification:**

   - [x] Tests pass: `npm test -- --grep "feature-name"`
   - [x] Build succeeds: `npm run build`
   - [x] Manual check: [description of what to verify]
   ```

**Examples of pending or incomplete tasks**:

1. A simple task: `- [ ] Task 1: Add user registration endpoint`
2. A task with subtasks:

   ```markdown
   ## Task [N]: [Short descriptive title]

   **Description:** One paragraph explaining what this task accomplishes.

   **Acceptance criteria:**

   - [ ] [Specific, testable condition]
   - [x] [Specific, testable condition]

   **Verification:**

   - [x] Tests pass: `npm test -- --grep "feature-name"`
   - [x] Build succeeds: `npm run build`
   - [x] Manual check: [description of what to verify]
   ```

## Completion Gate

After any implementer reports `DONE`, do not begin the next task until all of the following are true:

1. `plan.md` has been updated
2. The updated completion status is visible in `plan.md`
3. `plan.md` matches the current execution state

If `plan.md` is not updated, the task remains incomplete regardless of internal tracker state.

## Post-Task Reconciliation

After each completed task:

- confirm the correct task is marked completed in `plan.md`
- confirm no unrelated tasks were changed incorrectly
- confirm any required subtasks or verification checkboxes were updated appropriately

## Handling Implementer Status

Implementer subagents report one of four statuses. Handle each appropriately:

- **DONE:** Update `plan.md`, verify the update, then proceed.
- **DONE_WITH_CONCERNS:** Read the concerns before proceeding. If the concerns are about correctness or scope, address them before task completion. If they're observations (e.g., "this file is getting large"), note them, update `plan.md`, verify the update, and proceed.
- **NEEDS_CONTEXT:** The implementer needs information that wasn't provided. Provide the missing context and re-dispatch.
- **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
  1. If it's a context problem, provide more context and re-dispatch with the same model
  2. If the task requires more reasoning, re-dispatch with a more capable model
  3. If the task is too large, break it into smaller pieces
  4. If the plan itself is wrong, escalate to the human

**Never** ignore an escalation or force the same model to retry without changes. If the implementer said it's stuck, something needs to change.

## Prohibited Behavior

Do not treat any of the following as equivalent to updating `plan.md`:

- runtime todo trackers
- internal state
- memory
- subagent status reports
- chat summaries

These can assist coordination but are not execution records.

Failure to persist completion to `plan.md` is a workflow error.

## Commit Override Behavior

Do NOT commit. The user will review the changes and commit manually later.

## Red Flags

- Code implemented by the orchestrator instead of an implementer subagent
- Proceeding with unfixed issues
- Committing changes without human review
- Starting the next task before `plan.md` is updated and verified

## Verification

- All tasks were completed continuously and marked as completed in `plan.md`
- Each increment was individually tested
- The relevant test suite passes
- The build is clean
- The feature works end-to-end as specified
- All changes are uncommitted

## Final Audit

Before declaring the plan complete:

- audit `plan.md` against actual completed work
- ensure every finished task is marked complete in `plan.md`
- ensure no unfinished task is marked complete
- fix any discrepancy before reporting completion
