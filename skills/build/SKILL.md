---
name: build
description: Coordinate the next implementation increment — pick the next ready task, dispatch an implementer with a lean handoff, route finished work through one or more code-simplifiers and code-reviewers, then update tracking.
---

# Build

## Core Loop

1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
2. Pick the next pending task from the plan.
3. If the task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, do not dispatch yet. Resolve that first.
4. Otherwise dispatch immediately with the [implementer-prompt.md](./implementer-prompt.md) template and a lean handoff:
   - task text and success criteria
   - known constraints and validation commands
   - only already-known file hints
5. Do **not** pre-read large file sets, draft the solution, or sketch likely patches before dispatch.
6. The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
7. After the implementer returns `DONE`, build one deduped `review_scope_files` list from:
   - the files the implementer touched
   - all uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files
8. Dispatch parallel [simplifier-prompt.md](./simplifier-prompt.md) subagents over `review_scope_files` using <review-fanout-instructions> with:
   - the exact file list for that simplifier
   - the implementer's verification context
9. After every code-simplifier returns `DONE`, dispatch parallel [code-reviewer-prompt.md](./code-reviewer-prompt.md) subagents over the same `review_scope_files` partitions using <review-fanout-instructions> with:
   - the exact file list for that reviewer
   - the current verification context
10. Update tracking only after every reviewer returns `DONE`, using <update-tracking-instructions>.

## Manager Guardrails

- Dispatch as soon as the task is clear enough to execute.
- Pass through only information already known from the plan, task, or repo rules.
- Ordinary repo exploration, pattern lookup, and first-pass design stay with the implementer.
- Ordinary repo exploration is not a valid `NEEDS_CONTEXT`.
- If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.
- The manager owns `review_scope_files` and all downstream partitions. Keep them deduped, exhaustive, and non-overlapping.

## Verification Selection

- Verification ownership stays with the implementer.
- Infer the task's surface and stack before choosing validation.
- Prefer the narrowest matching checks for that stack. For shell or Python work, use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.

<review-fanout-instructions>
1. Materialize `review_scope_files` once, dedupe it, and keep stable order.
2. **≤5 files:** launch 1 code-simplifier or code-reviewer covering the full list.
3. **>5 files:** partition files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one downstream scope, then launch those code-simplifier or code-reviewer subagents in parallel.
4. The manager owns the partitions. Simplifiers and reviewers use only the file list they are given; they do not recompute or narrow scope.
5. Reuse the same `review_scope_files` partitions for code-simplifier and code-reviewer unless a later fix changes the surface enough to require a fresh partition.
</review-fanout-instructions>

<update-tracking-instructions>
1. Update the plan and todo tracker immediately.
2. Record the verification actually performed.
3. Mark the task `done` in the tracker.
</update-tracking-instructions>

## Shared Escalation Rules

- **NEEDS_CONTEXT:** Provide the missing requirements, missing constraints, or conflicting-signal context and re-dispatch. Routine discovery is not a valid `NEEDS_CONTEXT`.
- **BLOCKED:** Assess the blocker:
  1. If it's a context problem, provide more context and re-dispatch with the same model.
  2. If the task requires more reasoning, re-dispatch with a more capable model.
  3. If the task is too large, break it into smaller pieces.
  4. If the plan itself is wrong, escalate to the human.

## Subagent Status Handling

### Implementer

- **DONE:** Proceed to code-simplifier.
- **DONE_WITH_CONCERNS:** Read the concerns before any downstream step or tracking update. If they raise a correctness concern or scope concern, address them first, usually by re-dispatching an implementer. Do not update tracking yet.
- **NEEDS_CONTEXT:** Ordinary repo exploration and pattern lookup stay with the implementer; only missing requirements, missing constraints, or conflicting signals qualify.
- **BLOCKED:** Follow the shared escalation rules.

### Code-Simplifier

- **DONE:** If every code-simplifier returned `DONE`, proceed to code-reviewer.
- **DONE_WITH_CONCERNS:** Read the concerns before continuing to code-reviewer. If they raise a correctness concern or scope concern, treat them as unresolved work, address them first, usually by re-dispatching the subagent that should own the fix, and do not update tracking yet.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** Follow the shared escalation rules.

### Code-Reviewer

- **DONE:** If every reviewer returned `DONE`, proceed to update tracking.
- **DONE_WITH_FINDINGS:** Address findings before updating tracking. Re-dispatch the subagent that should own the fix, then route the result back through code-simplifier and the affected code-reviewer partitions as needed. Only mark the task done after every reviewer returns `DONE`.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** Follow the shared escalation rules.

Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.

## Tracking Discipline

- Treat stale docs as incomplete work.
- Reflect every task status change in the tracker, plan, and todo tracker.

## Commit Override Behavior

Never commit. The human will review the changes and commit manually later.

## Red Flags

- Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
- The manager performs repo discovery, pattern lookup, first-pass design, code changes, or verification when the task is clear enough to dispatch
- Marking a tracking item completed when the implementer, every code-simplifier, and every code-reviewer did not return `DONE`
- Marking a task done without updating the plan and todo tracker

## Verification

- [ ] Each increment was tested with the right checks for its stack
- [ ] Relevant build, test, or manual verification is clean
- [ ] Tracking and docs reflect the final state
- [ ] All changes are uncommitted
