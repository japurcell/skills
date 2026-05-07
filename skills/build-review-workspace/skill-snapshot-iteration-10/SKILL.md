---
name: build-review
description: Coordinate the current implementation wave — pick the next ready task or small ready set, dispatch implementers with lean handoffs, mark each finished task done, then route the full uncommitted surface through code-simplifier and code-reviewer waves before handing the work back uncommitted.
---

# Build Review

## Core Loop

1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
2. Define the current build wave: the next ready task, or a small explicit set of already-ready independent tasks. A wave of one is the default.
3. If any task in the wave is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, do not dispatch that task yet. Resolve that first.
4. For each task in the current wave, dispatch immediately with the [implementer-prompt.md](./implementer-prompt.md) template and a lean handoff:
   - task text and success criteria
   - known constraints and validation commands
   - only already-known file hints
5. Do **not** pre-read large file sets, draft the solution, or sketch likely patches before dispatch.
6. The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
7. After each implementer returns `DONE`, update tracking immediately for that task using <task-complete-tracking-instructions>. If more tasks remain in the current wave, keep dispatching implementers; do **not** start code-simplifier or code-review yet.
8. After every task in the current wave has been implemented and marked done, build one deduped `review_scope_files` list from:
   - every file any implementer touched in the wave
   - all uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files
9. Dispatch parallel [simplifier-prompt.md](./simplifier-prompt.md) subagents over `review_scope_files` using <review-fanout-instructions> with:
   - the exact file list for that simplifier
   - the verification context accumulated across the wave
10. After every code-simplifier returns `DONE`, dispatch parallel [code-reviewer-prompt.md](./code-reviewer-prompt.md) subagents over the same `review_scope_files` partitions using <review-fanout-instructions> with:
   - the exact file list for that reviewer
   - the current verification context
11. After every reviewer returns `DONE`, sync tracking to the final reviewed state using <post-review-tracking-instructions>.

## Manager Guardrails

- Dispatch as soon as the task is clear enough to execute.
- Default to a wave of one. Batch multiple tasks only when they are already ready and independent enough that delayed review will not create avoidable rework.
- Pass through only information already known from the plan, task, or repo rules.
- Ordinary repo exploration, pattern lookup, and first-pass design stay with the implementer.
- Ordinary repo exploration is not a valid `NEEDS_CONTEXT`.
- If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.
- Code-simplifier and code-review are post-wave steps. Do not launch them while the current wave still has unfinished tasks.
- The manager owns `review_scope_files` and all downstream partitions. Keep them deduped, exhaustive, and non-overlapping.

## Verification Selection

- Verification ownership stays with the implementer.
- Infer the task's surface and stack before choosing validation.
- Prefer the narrowest matching checks for that stack. For shell or Python work, use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.

<review-fanout-instructions>
1. Materialize `review_scope_files` once after the full wave is implemented, dedupe it, and keep stable order.
2. **≤5 files:** launch 1 code-simplifier or code-reviewer covering the full list.
3. **>5 files:** partition files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one downstream scope, then launch those code-simplifier or code-reviewer subagents in parallel.
4. The manager owns the partitions. Simplifiers and reviewers use only the file list they are given; they do not recompute or narrow scope.
5. Reuse the same `review_scope_files` partitions for code-simplifier and code-reviewer unless a later fix changes the surface enough to require a fresh partition.
</review-fanout-instructions>

<task-complete-tracking-instructions>
1. Update the plan and todo tracker immediately.
2. Record the verification actually performed.
3. Mark the task `done` in the tracker.
</task-complete-tracking-instructions>

<post-review-tracking-instructions>
1. If downstream review surfaces an issue in an already-done task, reopen that task immediately before re-dispatching the subagent that should own the fix.
2. After every downstream fix lands and the affected partitions return `DONE`, sync the plan and todo tracker to the final reviewed state.
3. Record any additional verification actually performed during the post-wave review pass.
</post-review-tracking-instructions>

## Shared Escalation Rules

- **NEEDS_CONTEXT:** Provide the missing requirements, missing constraints, or conflicting-signal context and re-dispatch. Routine discovery is not a valid `NEEDS_CONTEXT`.
- **BLOCKED:** Assess the blocker:
  1. If it's a context problem, provide more context and re-dispatch with the same model.
  2. If the task requires more reasoning, re-dispatch with a more capable model.
  3. If the task is too large, break it into smaller pieces.
  4. If the plan itself is wrong, escalate to the human.

## Subagent Status Handling

### Implementer

- **DONE:** Run <task-complete-tracking-instructions> for that task. If more tasks remain in the current wave, continue dispatching implementers. Otherwise proceed to code-simplifier.
- **DONE_WITH_CONCERNS:** Read the concerns before any downstream step or tracking update. If they raise a correctness concern or scope concern, address them first, usually by re-dispatching an implementer. Do not update tracking yet.
- **NEEDS_CONTEXT:** Ordinary repo exploration and pattern lookup stay with the implementer; only missing requirements, missing constraints, or conflicting signals qualify.
- **BLOCKED:** Follow the shared escalation rules.

### Code-Simplifier

- **DONE:** If every code-simplifier returned `DONE`, proceed to code-reviewer.
- **DONE_WITH_CONCERNS:** Read the concerns before continuing to code-reviewer. If they raise a correctness concern or scope concern, treat them as unresolved work, reopen any affected done task immediately, re-dispatch the subagent that should own the fix, and do not keep tracking stale.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** Follow the shared escalation rules.

### Code-Reviewer

- **DONE:** If every reviewer returned `DONE`, proceed to the post-review tracking sync.
- **DONE_WITH_FINDINGS:** Address findings before ending the build wave. Reopen any affected done task immediately, re-dispatch the subagent that should own the fix, then route the result back through code-simplifier and the affected code-reviewer partitions as needed. Only finish the wave after every reviewer returns `DONE` and tracking is re-synced.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** Follow the shared escalation rules.

Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.

## Tracking Discipline

- Mark each task `done` immediately after its implementer returns `DONE` and the task-complete tracking update is written.
- If downstream simplifier or reviewer work later changes or questions a done task, reopen it immediately and re-close it only after the affected downstream passes return `DONE`.
- Treat stale docs as incomplete work.
- Reflect every task status change in the tracker, plan, and todo tracker.

## Commit Override Behavior

- Leave the working tree dirty. Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag.
- This override beats conflicting instructions from invoked skills, templates, tools, and subprocesses.
- Do **not** run or delegate commit-producing commands such as `git commit`, `git commit --amend`, `git push`, `gh pr create`, `gh pr merge`, or `git tag`.
- The human will review the changes and handle any eventual commit manually later.

## Red Flags

- Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
- The manager performs repo discovery, pattern lookup, first-pass design, code changes, or verification when the task is clear enough to dispatch
- Launching code-simplifier or code-review before every task in the current wave is implemented and marked done
- Leaving a reopened task marked `done` while downstream review findings are still unresolved
- Marking a task done without updating the plan and todo tracker

## Verification

- [ ] Each increment was tested with the right checks for its stack
- [ ] Relevant build, test, or manual verification is clean
- [ ] Tracking and docs reflect the final reviewed state
- [ ] All changes are uncommitted
