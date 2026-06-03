---
name: build-review
description: Implement the next task incrementally — build, test, verify
---

# Build Review

## Workflow

1. Invoke the `addy-context-engineering` and `subagent-model-router` skills.
2. Pick the next pending task from the plan. For each task:
   a. Prepare a lean handoff: task text, acceptance criteria, known constraints, relevant commands, and file hints only if they are already obvious from the task or plan
   b. Dispatch an implementer subagent immediately with the [implementer-prompt.md](./implementer-prompt.md) template
   c. Let the implementer own repo discovery, pattern lookup, first-pass solution design, code changes, and verification
   d. Wait for the implementer to report back with status and details
   e. Update tracking using <update-tracking-instructions>
   f. Move to the next pending task

## Dispatch Early

The main agent is the coordinator, not the pre-implementer.

- Dispatch as soon as the task is clear enough to execute.
- Do **not** pre-read a stack of source files just to "prepare" the implementer.
- Do **not** draft the solution, patch plan, or likely code changes before the first dispatch.
- Do pass through constraints that are already known: plan text, acceptance criteria, repo rules, validation commands, and any file paths already named by the task.
- Keep the main-agent context focused on task selection, tracking, ambiguity resolution, and escalation handling.

Push work into the implementer subagent unless one of these is true:

1. The task text is ambiguous or conflicts with the plan.
2. The human asked for tradeoff analysis before implementation.
3. A previous implementer run returned `NEEDS_CONTEXT` or `BLOCKED`.
4. You need to update tracking artifacts after completed work.

If none of those are true, dispatch first and let the implementer gather its own working context.

## Context Handoff Rules

Provide enough context to avoid hallucination, but not so much that you solve the task in the manager.

- Include: the task, success criteria, known constraints, relevant commands, and explicit file hints that are already known.
- Exclude by default: exploratory file reads, speculative architecture analysis, and hand-written solution proposals.
- If the implementer needs more than the lean handoff, let it ask for it explicitly via `NEEDS_CONTEXT`.

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
- **NEEDS_CONTEXT:** The implementer needs information that was genuinely missing from the handoff. This is for missing requirements, constraints, or conflicting signals, not for ordinary codebase exploration. Provide the missing context and re-dispatch implementer subagent.
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
