---
name: build-team
description: Orchestrates an existing `$plan` through implementation, code simplification, code review, and durable lesson capture while keeping `$plan` as the source of truth. Use when the user wants you to continue an implementation plan, finish ready tasks without repeated check-ins, or run the build-team workflow from a plan file.
---

# Build Team

## Overview

Execute an existing `$plan` continuously. You are the orchestrator: send ready tasks to fresh implementer subagents, record completion in `$plan`, then run one simplification pass and one review pass before stopping.

Use a fresh implementer per task so coordination stays clean and each task gets focused context.

## When to Use

- `$plan` already exists and has pending implementation tasks.
- The user wants execution of an existing plan, not planning from scratch.
- The work should continue through ready tasks without repeated "should I continue?" check-ins.
- Not for creating a plan, writing a spec, or breaking work down from scratch.

## Inputs

- `$plan` (required): path to the implementation plan file, typically `.agents/scratchpad/<feature>/plan.md`. This file must already exist and contain pending tasks.

## Workflow

### Phase 1: Implementation Orchestration

1. Read `$plan` and pick the next ready pending task from the file.
2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the implementer subagent.
3. Dispatch one fresh implementer subagent with the exact task text, the relevant `$plan` excerpt, and the [implementer-prompt.md](./implementer-prompt.md) template.
4. Wait for the implementer to report back.
5. Handle the status exactly:
   - **DONE:** Update the matching task in `$plan`, save it, then re-read `$plan` and verify the completion is visible before starting the next task.
   - **DONE_WITH_CONCERNS:** Treat this as unresolved correctness or scope risk. Read the concerns first and resolve them before marking the task complete. If the implementer only has a non-blocking observation, it should report `DONE` and include the note there instead.
   - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch. Do not mark the task complete.
   - **BLOCKED:** Try to unblock with better context, a smaller slice, or a more capable model. If the blocker remains, stop and escalate to the human. Do not mark the task complete.
6. Continue through ready implementation tasks without pausing for permission.
7. When no ready implementation tasks remain, build one `$review_scope_files` list:
   - Start with every file any implementer reported changing.
   - Add uncommitted files from `git status --porcelain`.
   - Exclude deleted paths, `.gitignore`, and paths ignored by git.
   - Deduplicate the list and keep paths relative to the repository root.
8. Proceed to the next phase. Stop early only when a real blocker remains or the plan itself is wrong.

### Phase 2: Code Simplification

1. Add a "Code Simplification" task to `$plan` with the full `$review_scope_files` list in the description. This makes simplification part of the execution record and ensures it doesn't get lost.
2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the code-simplifier subagent.
3. Dispatch code-simplifier subagents over `$review_scope_files` partitions with the [code-simplifier-prompt.md](./code-simplifier-prompt.md) template. Include the exact file list for each subagent. Scale based on the number of files:
   - **≤5 files**: launch 1 agent covering all changed files
   - **>5 files**: partition files into non-overlapping groups (by module, directory, or logical area) and launch one agent per group in parallel. Each file must appear in exactly one agent's scope — overlapping scopes cause conflicting writes.
4. Wait for all code-simplifier subagents to report back.
5. Handle the statuses exactly:
   - **DONE:** When all subagents report `DONE`, update the code simplification task in `$plan`, save it, then re-read `$plan` and verify the completion is visible.
   - **DONE_WITH_CONCERNS:** If the concern affects correctness or scope, resolve it before marking the task complete. If it's a non-blocking observation, the agent should have reported `DONE` and included the note there instead.
   - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch. Do not mark the task complete.
   - **BLOCKED:** Try to unblock with better context, a smaller slice, or a more capable model. If the blocker remains, stop and escalate to the human. Do not mark the task complete.
6. When the code simplification task is marked complete in `$plan`, proceed to the next phase. Stop early only when a real blocker remains.

### Phase 3: Code Review

1. Add a "Code Review" task to `$plan` with the full `$review_scope_files` list in the description. This makes code review part of the execution record and ensures it doesn't get lost.
2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the code-reviewer subagent.
3. Dispatch code-reviewer subagents over `$review_scope_files` with the [code-reviewer-prompt.md](./code-reviewer-prompt.md) template. Include the exact file list for each subagent. Scale based on the number of files:
   - **≤5 files**: launch 1 agent covering all changed files
   - **>5 files**: launch multiple agents in parallel with different focuses (e.g., correctness, security, performance).
4. Wait for all code-reviewer subagents to report back.
5. Handle the statuses exactly:
   - **DONE:** When all subagents report `DONE`, update the code review task in `$plan`, save it, then re-read `$plan` and verify the completion is visible.
   - **DONE_WITH_FINDINGS:** Re-open the affected task in `$plan` and route the fix to a fresh implementer subagent instead of patching inline. Include the finding, affected files, and original task context. After the fix lands, add any newly changed files to `$review_scope_files`, return to Phase 2 for the affected files, then repeat code review. Do not mark the code review task complete.
   - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch. Do not mark the code review task complete.
   - **BLOCKED:** Try to unblock with better context, a smaller slice, or a more capable model. If the blocker remains, stop and escalate to the human. Do not mark the code review task complete.
6. When the code review task is marked complete in `$plan`, proceed to the next phase. Stop early only when a real blocker remains.

### Phase 4: Self-Improve

Before stopping, invoke the `self-improve` skill when the session produced durable, reusable learnings. Do not record one-off task trivia.

## Specific Techniques

- Treat `$plan` as the only execution record. Internal todo trackers, memory, scratchpads, chat summaries, and subagent status messages can help coordination but never replace updating `$plan`.
- A task is complete only after the finished state is written to `$plan` and then verified by re-reading `$plan`.
- Send the implementer the exact task text plus the relevant `$plan` excerpt. Weaker models behave better when task boundaries are explicit.
- Keep the orchestration boundary intact: the implementer does the task work; you coordinate selection, status handling, and `$plan` updates.
- Reuse [implementer-prompt.md](./implementer-prompt.md) instead of re-explaining implementation details from memory. That prompt already covers incremental implementation, TDD, targeted verification, and debugging when a step fails.
- Reuse the simplifier and reviewer prompt templates instead of improvising status names or report formats.
- Leave all repository changes uncommitted.

## Common Rationalizations

| Rationalization                                                    | Reality                                                                                                                  |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| "The implementer said it's done, so I can move on."                | `DONE` is not enough by itself. The task is complete only after `$plan` is updated, saved, and re-read.                  |
| "Implementation tasks are done, so I can skip review."             | The workflow includes simplification and code review tasks before the final handoff.                                     |
| "I can track completion in my todo list or chat summary."          | Those are helpers, not execution records. `$plan` is the only source of truth.                                           |
| "I'll just do this task myself instead of dispatching a subagent." | This skill is for orchestration. A fresh implementer subagent per task keeps context clean and the workflow consistent.  |
| "I'll stop after this task and ask whether to continue."           | Keep going through ready tasks. Stop only for a real blocker, genuine ambiguity, or full completion.                     |
| "Review findings are faster to patch inline."                      | Re-open the affected task in `$plan` and send the fix to a fresh implementer so the orchestration record stays complete. |
| "The plan is done, so the skill is done."                          | Not yet. First capture durable reusable lessons with `self-improve`, if any exist.                                       |

## Red Flags

- Code implemented by the orchestrator instead of an implementer subagent
- Starting the next task before `$plan` is updated and re-read
- Treating runtime trackers or subagent reports as equivalent to `$plan`
- Marking `BLOCKED` or `NEEDS_CONTEXT` work complete
- Stopping between ready tasks to ask for permission
- Skipping the simplification or code review phase after implementation tasks finish
- Patching review findings inline instead of reopening the affected `$plan` task
- Committing changes or telling the implementer to commit
- Finishing all plan tasks but skipping `self-improve` when durable lessons exist
- Recording one-off task trivia as durable lessons

## Verification

- [ ] `$plan` existed and provided the task order.
- [ ] Each task was assigned to a fresh implementer subagent.
- [ ] Each completed task was written to `$plan` only after `DONE` or an acceptable `DONE_WITH_CONCERNS` resolution.
- [ ] After each `$plan` update, the file was re-read and matched the current execution state before the next task began.
- [ ] Ready tasks ran continuously until completion or a real blocker required escalation.
- [ ] `$review_scope_files` included touched files plus filtered uncommitted files, with deleted, ignored, and `.gitignore` paths excluded.
- [ ] A "Code Simplification" task was added to `$plan`, completed, saved, and verified by re-reading `$plan`.
- [ ] A "Code Review" task was added to `$plan`, completed, saved, and verified by re-reading `$plan`.
- [ ] Any review findings re-opened the affected `$plan` task and were routed to a fresh implementer subagent.
- [ ] All work remains uncommitted.
- [ ] Before stopping, `self-improve` was invoked if the session produced durable, reusable learnings worth preserving.
- [ ] Any captured lessons were durable and reusable, not one-off task trivia.
