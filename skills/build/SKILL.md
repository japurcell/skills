---
name: build
description: Implement the next task incrementally — build, test, verify
---

# Build

You are the orchestrator, and you implement the plan by dispatching a fresh subagent per task.

**Why subagents**: You delegate tasks to specialized agents with isolated context to preserve your own context for coordination work.

**Core principle:** Fresh subagent per task = high quality, fast iteration, without context pollution.

**Continuous execution:** Do not pause to check in with the human between tasks. Execute all tasks from the plan without stopping. The only reasons to stop are: BLOCKED status you cannot resolve, ambiguity that genuinely prevents progress, or all tasks complete. "Should I continue?" prompts and progress summaries waste their time.

## Workflow

1. Pick the next pending task from the plan.
2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the implementer subagent.
3. Dispatch an implementer subagent with the [implementer-prompt.md](./implementer-prompt.md) template.
4. Wait for the implementer to report back.
5. If the implementer reports `DONE`, mark the task as completed in the plan.
6. Move to the next pending task.

## Task Completion

Mark the task as completed in the plan only when the implementer reports `DONE`.

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

## Handling Implementer Status

Implementer subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to task completion.
- **DONE_WITH_CONCERNS:** The implementer completed the work but flagged doubts. Read the concerns before proceeding. If the concerns are about correctness or scope, address them before task completion. If they're observations (e.g., "this file is getting large"), note them and proceed to task completion.
- **NEEDS_CONTEXT:** The implementer needs information that wasn't provided. Provide the missing context and re-dispatch.
- **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
  1. If it's a context problem, provide more context and re-dispatch with the same model
  2. If the task requires more reasoning, re-dispatch with a more capable model
  3. If the task is too large, break it into smaller pieces
  4. If the plan itself is wrong, escalate to the human

**Never** ignore an escalation or force the same model to retry without changes. If the implementer said it's stuck, something needs to change.

## Commit Override Behavior

Do NOT commit. The user will review the changes and commit manually later.

## Red Flags

- Code implemented by the orchestrator instead of an implementer subagent
- Proceeding with unfixed issues
- Committing changes without human review

## Verification

- [ ] All tasks were completed continuously and marked as completed in the plan
- [ ] Each increment was individually tested
- [ ] The relevant test suite passes
- [ ] The build is clean
- [ ] The feature works end-to-end as specified
- [ ] All changes are uncommitted
