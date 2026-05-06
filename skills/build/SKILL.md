---
name: build
description: Implement the next task incrementally — build, test, verify
---

# Build

## Workflow

1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
2. Pick the next pending task from the plan. For each task:
   a. If the task text is ambiguous, conflicts with the plan, or the human asked for tradeoff analysis first, resolve that before dispatch.
   b. Otherwise send a lean handoff: task text, success criteria, known constraints, validation commands, and only already-known file hints.
   c. Dispatch an implementer subagent immediately with the [implementer-prompt.md](./implementer-prompt.md) template.
   d. Let the implementer own discovery, pattern lookup, first-pass design, code changes, and verification.
   e. Update tracking using <update-tracking-instructions> after the implementer finishes.

## Dispatch Rule

The main agent coordinates. It does not pre-implement.

- Dispatch as soon as the task is clear enough to execute.
- Do **not** pre-read a large file set, draft the solution, or sketch likely patches before the first dispatch.
- Pass through only information already known from the plan, task, or repo rules.
- If the implementer needs more than the lean handoff, let it ask via `NEEDS_CONTEXT`.

<update-tracking-instructions>
1. Update the plan and todo doc immediately.
2. Record the verification actually performed.
3. Mark the task `done` in the tracker.
</update-tracking-instructions>

## Handling Implementer Status

Implementer subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to update tracking.
- **DONE_WITH_CONCERNS:** Read the concerns before updating tracking. If they touch correctness or scope, address them first, usually by re-dispatching another implementer.
- **NEEDS_CONTEXT:** Use this only for missing requirements, constraints, or conflicting signals, not ordinary repo exploration. Provide the missing context and re-dispatch.
- **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
  1.  If it's a context problem, provide more context and re-dispatch with the same model
  2.  If the task requires more reasoning, re-dispatch with a more capable model
  3.  If the task is too large, break it into smaller pieces
  4.  If the plan itself is wrong, escalate to the human

Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.

## Tracking Discipline

- Treat stale docs as incomplete work.
- Reflect every task status change in the tracker, plan, and todo doc.

## Commit Override Behavior

Do NOT commit. The user will review the changes and commit manually later.

## Red Flags

- Not using a subagent for implementation tasks or fixes
- Main agent performs discovery, pattern lookup, first-pass design, code changes, or verification when task is clearly defined
- Marking a tracking item completed when the implementer did not return DONE
- Marking a task done without updating the plan and todo docs

## Verification

After completing all tasks:

- [ ] Each increment was individually tested
- [ ] The full test suite passes
- [ ] The build is clean
- [ ] The feature works end-to-end as specified
- [ ] All relevant docs are updated to reflect the completed work
- [ ] All changes are uncommitted
