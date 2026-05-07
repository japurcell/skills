---
name: build-review
description: Coordinate the next planned implementation task incrementally — choose the next ready task, dispatch an implementer with a lean handoff, run a code-simplifier pass, run a code-reviewer pass, verify, then update tracking.
---

# Build Review

## Workflow

1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
2. Pick the next pending task from the plan.
3. If the task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, it is not clear enough to dispatch yet. Resolve that before dispatch.
4. Otherwise dispatch immediately with the [implementer-prompt.md](./implementer-prompt.md) template and a lean handoff:
   - task text and success criteria
   - known constraints and validation commands
   - only already-known file hints
5. Do **not** pre-read a large file set, draft the solution, or sketch likely patches before the first dispatch.
6. The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
7. After the implementer returns `DONE`, dispatch the [simplifier-prompt.md](./simplifier-prompt.md) template over the files the implementer touched.
8. After the code-simplifier returns `DONE`, dispatch the [code-reviewer-prompt.md](./code-reviewer-prompt.md) template over the files the implementer touched.
9. Update tracking only after the final subagent returns `DONE`, using <update-tracking-instructions>.

## Implementer Dispatch Rule

The main agent coordinates. It does not pre-implement.

- Dispatch as soon as the task is clear enough to execute.
- Do **not** pre-read a large file set, draft the solution, or sketch likely patches before the first dispatch.
- Pass through only information already known from the plan, task, or repo rules.
- Ordinary repo exploration is implementer work, not manager work.
- `NEEDS_CONTEXT` is for missing requirements, missing constraints, or conflicting signals — routine discovery is not a valid `NEEDS_CONTEXT`.
- If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.

<update-tracking-instructions>
1. Update the plan and todo doc immediately.
2. Record the verification actually performed.
3. Mark the task `done` in the tracker.
</update-tracking-instructions>

## Subagent Status Handling

### Implementer

Implementer subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to code-simplifier.
- **DONE_WITH_CONCERNS:** Read the concerns before code-simplifier. If they touch correctness or scope, address them first, usually by re-dispatching another implementer. Do not update tracking yet.
- **NEEDS_CONTEXT:** Use this only for missing requirements, constraints, or conflicting signals, not ordinary repo exploration. Provide the missing context and re-dispatch.
- **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
  1.  If it's a context problem, provide more context and re-dispatch with the same model
  2.  If the task requires more reasoning, re-dispatch with a more capable model
  3.  If the task is too large, break it into smaller pieces
  4.  If the plan itself is wrong, escalate to the human

### Code-Simplifier

Code-simplifier subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to code-reviewer.
- **DONE_WITH_CONCERNS:** Read the concerns before code-reviewer. If they touch correctness or scope, address them before continuing with code-reviewer, usually by re-dispatching the subagent that should own the fix.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** The code-simplifier cannot complete the task. Assess the blocker:
  1.  If it's a context problem, provide more context and re-dispatch with the same model
  2.  If the task requires more reasoning, re-dispatch with a more capable model
  3.  If the task is too large, break it into smaller pieces
  4.  If the plan itself is wrong, escalate to the human

### Code-Reviewer

Code-reviewer subagents report one of four statuses. Handle each appropriately:

- **DONE:** Proceed to update tracking.
- **DONE_WITH_FINDINGS:** Address findings before update tracking, usually by re-dispatching the subagent that should own the fix.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** The code-reviewer cannot complete the task. Assess the blocker:
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

- Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
- Main agent performs discovery, pattern lookup, first-pass design, code changes, or verification when task is clearly defined
- Marking a tracking item completed when the implementer, code-simplifier, and code-reviewer did not return DONE
- Marking a task done without updating the plan and todo docs

## Verification

After completing all tasks:

- [ ] Each increment was individually tested
- [ ] The full test suite passes
- [ ] The build is clean
- [ ] The feature works end-to-end as specified
- [ ] All relevant docs are updated to reflect the completed work
- [ ] All changes are uncommitted
