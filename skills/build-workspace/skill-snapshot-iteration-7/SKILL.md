---
name: build
description: Coordinate the next implementation increment — pick the next ready task, dispatch an implementer with a lean handoff, route finished work through code-simplifier and code-reviewer, then update tracking.
---

# Build

## Core Loop

1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
2. Pick the next pending task from the plan.
3. If the task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, it is not clear enough to dispatch yet. Resolve that before dispatch.
4. Otherwise dispatch immediately with the [implementer-prompt.md](./implementer-prompt.md) template and a lean handoff:
   - task text and success criteria
   - known constraints and validation commands
   - only already-known file hints
5. Do **not** pre-read a large file set, draft the solution, or sketch likely patches before the first dispatch. The manager coordinates; the implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
6. After the implementer returns `DONE`, dispatch the [simplifier-prompt.md](./simplifier-prompt.md) over the files the implementer touched plus the verification context they produced. Also include all uncomitted files (`git status --porcelain`) while excluding deleted files and `.gitignore` files.
7. After the code-simplifier returns `DONE`, dispatch the [code-reviewer-prompt.md](./code-reviewer-prompt.md) over the touched files plus the current verification context. Also include all uncomitted files (`git status --porcelain`) while excluding deleted files and `.gitignore` files.
8. Update tracking only after the final subagent returns plain `DONE`, using <update-tracking-instructions>.

## Manager Guardrails

- Dispatch as soon as the task is clear enough to execute.
- Pass through only information already known from the plan, task, or repo rules.
- Ordinary repo exploration is implementer work, not manager work.
- `NEEDS_CONTEXT` is only for missing requirements, missing constraints, or conflicting signals. Routine discovery is not a valid `NEEDS_CONTEXT`.
- If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.

## Verification Selection

- Verification ownership stays with the implementer.
- Infer the task's surface and stack before choosing validation.
- Prefer the narrowest matching checks for that stack. For shell or Python work, use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.

<update-tracking-instructions>
1. Update the plan and todo tracker immediately.
2. Record the verification actually performed.
3. Mark the task `done` in the tracker.
</update-tracking-instructions>

## Subagent Status Handling

### Implementer

Implementer subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to code-simplifier.
- **DONE_WITH_CONCERNS:** Read the concerns before any downstream step or tracking update. If they touch correctness or scope, address them first, usually by re-dispatching an implementer. Do not update tracking yet.
- **NEEDS_CONTEXT:** Use this only for missing requirements, missing constraints, or conflicting signals, not ordinary repo exploration. Provide the missing context and re-dispatch.
- **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
  1. If it's a context problem, provide more context and re-dispatch with the same model.
  2. If the task requires more reasoning, re-dispatch with a more capable model.
  3. If the task is too large, break it into smaller pieces.
  4. If the plan itself is wrong, escalate to the human.

### Code-Simplifier

Code-simplifier subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to code-reviewer.
- **DONE_WITH_CONCERNS:** Read the concerns before continuing to code-reviewer. If they touch correctness or scope, address them first, usually by re-dispatching the subagent that should own the fix. Do not update tracking yet.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** The code-simplifier cannot complete the task. Assess the blocker:
  1. If it's a context problem, provide more context and re-dispatch with the same model.
  2. If the task requires more reasoning, re-dispatch with a more capable model.
  3. If the task is too large, break it into smaller pieces.
  4. If the plan itself is wrong, escalate to the human.

### Code-Reviewer

Code-reviewer subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to update tracking.
- **DONE_WITH_FINDINGS:** Address findings before updating tracking, usually by re-dispatching the subagent that should own the fix. Route the result back through simplifier and reviewer as needed, and only mark the task done after the final subagent returns `DONE`.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** The code-reviewer cannot complete the task. Assess the blocker:
  1. If it's a context problem, provide more context and re-dispatch with the same model.
  2. If the task requires more reasoning, re-dispatch with a more capable model.
  3. If the task is too large, break it into smaller pieces.
  4. If the plan itself is wrong, escalate to the human.

Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.

## Tracking Discipline

- Treat stale docs as incomplete work.
- Reflect every task status change in the tracker, plan, and todo tracker.

## Commit Override Behavior

Never commit. The human will review the changes and commit manually later.

## Red Flags

- Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
- Main agent performs discovery, pattern lookup, first-pass design, code changes, or verification when task is clearly defined
- Marking a tracking item completed when the implementer, code-simplifier, and code-reviewer did not return DONE
- Marking a task done without updating the plan and todo docs

## Verification

After completing all tasks:

- [ ] Each increment was tested with the right checks for its stack
- [ ] Relevant build, test, or manual verification is clean
- [ ] Tracking and docs reflect the final state
- [ ] All changes are uncommitted
