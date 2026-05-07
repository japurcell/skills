---
name: build
description: Coordinate the current implementation wave. Use when the plan already has the next ready task or small ready set and you need a manager-led workflow that dispatches implementers with lean handoffs, then runs code-simplifier and code-reviewer waves over the full uncommitted surface before handing the work back uncommitted.
---

# Build

## Overview

Use this skill to run a manager-led implementation wave: pick the next ready task, dispatch subagents with lean handoffs, then route the resulting surface through simplifier and reviewer waves before handing the work back uncommitted. It matters because the manager must coordinate progress and tracking without stealing repo discovery, design, implementation, or verification work from the subagents.

## When to Use

- Use when the plan already has a next ready task or small ready set and you need to execute that wave through implementation, simplification, review, and tracking.
- Use when you need a manager/subagent boundary: the manager coordinates, while implementers own repo discovery, first-pass design, code changes, and validation.
- Use when downstream review must cover the full uncommitted surface, not just the file from one finished task.
- Do **not** use this skill for planning, specs, or unresolved tradeoff analysis. Resolve ambiguity first.

## Workflow

1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
2. Define the current build wave: the next ready task, or a small explicit set of already-ready independent tasks. A wave of one is the default.
3. If any task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, resolve that before dispatch.
4. For each task in the wave, dispatch immediately with [implementer-prompt.md](./implementer-prompt.md) and only:
   - task text and success criteria
   - known constraints and validation commands
   - already-known file hints
5. When an implementer returns `DONE`, immediately update the plan and todo tracker, record the verification actually performed, and mark that task `done`.
6. If any task in the current wave is still unfinished, keep dispatching implementers. Do **not** start code-simplifier or code-review yet.
7. After every task in the wave has been implemented and marked done, build one deduped `review_scope_files` list from:
   - every file any implementer touched in the wave
   - all uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files
8. Dispatch code-simplifier subagents over manager-authored `review_scope_files` partitions using [simplifier-prompt.md](./simplifier-prompt.md).
9. After every code-simplifier returns `DONE`, dispatch code-reviewer subagents over the same partitions using [code-reviewer-prompt.md](./code-reviewer-prompt.md), unless a later fix changes the surface enough to require fresh partitions.
10. After every reviewer returns `DONE`, sync the plan and todo tracker to the final reviewed state and record any additional verification actually performed during review.

## Specific Techniques

### Role Boundaries

- The manager owns wave selection, dispatch, tracking, `review_scope_files`, review partitions, and the final reviewed sync.
- The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
- Dispatch as soon as the task is clear enough. Do **not** pre-read large file sets, draft the solution, sketch likely patches, or run verification on the implementer's behalf.
- Ordinary repo exploration is never a valid `NEEDS_CONTEXT`. Only missing requirements, missing constraints, or conflicting signals qualify.
- Leave the working tree dirty. Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag.

### Review Fanout

1. Materialize `review_scope_files` once after the full wave is implemented, dedupe it, and keep stable order.
2. **<=5 files:** launch one code-simplifier or code-reviewer over the full list.
3. **>5 files:** partition files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one downstream scope.
4. The manager owns the partitions. Simplifiers and reviewers use only the exact file list they are given; they do not recompute or narrow scope.
5. Reuse the same partitions for code-simplifier and code-review unless a later fix changes the touched surface.

### Verification Selection

- Verification ownership stays with the implementer.
- Infer the task's surface and stack before choosing validation.
- Prefer the narrowest matching checks for that stack. Shell or Python work should use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.

### Status Handling

#### Implementer

- **DONE:** run the task-complete tracking update immediately. If more tasks remain in the wave, keep dispatching implementers; otherwise start code-simplifier.
- **DONE_WITH_CONCERNS:** read the concerns before any tracking update. If they raise correctness or scope risk, address them first, usually by re-dispatching an implementer. Do **not** mark the task done yet.
- **NEEDS_CONTEXT:** only valid for missing requirements, missing constraints, or conflicting signals. Routine discovery stays with the implementer.
- **BLOCKED:** follow the escalation ladder.

#### Code-Simplifier

- **DONE:** when every simplifier is `DONE`, proceed to code-review.
- **DONE_WITH_CONCERNS:** treat correctness or scope concerns as unresolved work. Reopen any affected done task immediately, route the fix to the subagent that should own it, and do **not** proceed to code-review yet.
- **NEEDS_CONTEXT:** provide the missing context and re-dispatch.
- **BLOCKED:** follow the escalation ladder.

#### Code-Reviewer

- **DONE:** when every reviewer is `DONE`, run the final reviewed tracking sync.
- **DONE_WITH_FINDINGS:** address findings before ending the wave. Reopen any affected done task immediately, route the fix to the subagent that should own it, then rerun the affected code-simplifier and reviewer partitions as needed. Re-sync tracking only after every reviewer returns `DONE`.
- **NEEDS_CONTEXT:** provide the missing context and re-dispatch.
- **BLOCKED:** follow the escalation ladder.

### Escalation Ladder

When a subagent returns `BLOCKED`:

1. If it is a context problem, provide more context and re-dispatch with the same model.
2. If it needs more reasoning, re-dispatch with a more capable model.
3. If the task or partition is too large, split it into smaller pieces.
4. If the plan itself is wrong, escalate to the human.

Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.

### Tracking Discipline

- Reopen any done task immediately if downstream simplifier or reviewer work changes it or questions its correctness or scope.
- Re-close that task only after the affected downstream passes return `DONE`.
- Treat stale docs or stale tracking as incomplete work.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "I should read the repo and sketch the patch before I dispatch." | That steals implementer work and pushes the manager out of coordination mode. Dispatch once the task is clear enough. |
| "The implementer has not explored the repo yet, so `NEEDS_CONTEXT` is fine." | Ordinary repo discovery, pattern lookup, and first-pass design belong to the implementer. `NEEDS_CONTEXT` is only for missing requirements, constraints, or conflicting signals. |
| "One task in the wave is done, so I can start code-simplifier now." | Downstream review starts only after every task in the current wave is implemented and marked done. |
| "Once review is done I can commit or open the PR for the human." | This skill explicitly leaves the work dirty and unpublished. The human handles any commit or PR later. |

## Red Flags

- The manager reads large file sets, proposes a patch, or runs validation before dispatching a clear task.
- An implementer asks for `NEEDS_CONTEXT` just to avoid ordinary repo exploration.
- A simplifier or reviewer recomputes scope instead of using the exact manager-authored file list.
- A downstream concern or finding surfaces, but the affected task stays marked `done`.
- Any step creates or publishes a commit, PR, or tag.

## Verification

After completing the build wave, confirm:

- [ ] Each implementer `DONE` updated the plan and todo tracker immediately and recorded the verification actually performed.
- [ ] `review_scope_files` was deduped, filtered, manager-authored, and reused across simplifier/reviewer waves unless the touched surface changed.
- [ ] Code-simplifier and code-review started only after the full wave was implemented and marked done.
- [ ] Any reopened task was re-closed only after the affected downstream passes returned `DONE`.
- [ ] The final reviewed sync is complete and the working tree remains dirty and unpublished.
