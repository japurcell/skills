---
name: build
description: Implement the next task incrementally — build, test, verify
---

# Build

## Workflow

1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
2. Pick the next pending task from the plan. For each task:
   a. Dispatch an implementer subagent with the [implementer-prompt.md](./implementer-prompt.md) template
   b. Wait for the implementer to report back with status and details
   c. Update tracking using <update-tracking-instructions>
   d. Move to the next pending task

<update-tracking-instructions>
1. Update the human-readable docs immediately:
   - check off completed items in the plan
   - check off completed items in the todo doc
   - note any verification actually performed
2. Mark the task `done` in the tracker
</update-tracking-instructions>

## Handling Implementer Status

Implementer subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to update tracking.
- **DONE_WITH_CONCERNS:** The implementer completed the work but flagged doubts. Read the concerns before proceeding. If the concerns are about correctness or scope, address them before updating tracking by re-dispatching another implementer subagent. If they're observations (e.g., "this file is getting large"), note them and proceed to update tracking.
- **NEEDS_CONTEXT:** The implementer needs information that wasn't provided. Provide the missing context and re-dispatch implementer subagent.
- **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
  1. If it's a context problem, provide more context and re-dispatch with the same model
  2. If the task requires more reasoning, re-dispatch with a more capable model
  3. If the task is too large, break it into smaller pieces
  4. If the plan itself is wrong, escalate to the human

**Never** ignore an escalation or force the same model to retry without changes. If the implementer said it's stuck, something needs to change.

## Tracking Discipline

- Treat stale docs as incomplete work.
- Every task status change must be reflected in:
  1. the tracker
  2. the plan
  3. the todo doc

## Commit Override Behavior

Do NOT commit. The user will review the changes and commit manually later.

## Red Flags

- Not using a subagent for implementation tasks or fixes
- Marking a tracking item completed when the implementer reported concerns that haven't been addressed
- Marking a task done without updating the plan and todo docs

## Verification

After completing all tasks:

- [ ] Each increment was individually tested
- [ ] The full test suite passes
- [ ] The build is clean
- [ ] The feature works end-to-end as specified
- [ ] All relevant docs are updated to reflect the completed work
- [ ] All changes are uncommitted
