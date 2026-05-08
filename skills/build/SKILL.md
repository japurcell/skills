---
name: build
description: Orchestrates execution of an existing `plan.md` by dispatching one fresh implementer subagent per task and persisting completion in `plan.md`. Use when the user wants you to continue an existing implementation plan, work through pending tasks without repeated check-ins, or finish a planned feature continuously.
---

# Build

## Overview

Execute an existing `plan.md` continuously. You are the orchestrator: pick the next pending task, dispatch one fresh implementer subagent with [implementer-prompt.md](./implementer-prompt.md), then update `plan.md` only after the implementer has truly finished.

Use a fresh implementer per task so coordination stays clean and each task gets focused context.

## When to Use

- `plan.md` already exists and has pending implementation tasks.
- The user wants execution, not planning.
- The work should continue through ready tasks without repeated "should I continue?" check-ins.
- Not for creating a plan, writing a spec, or breaking work down from scratch.

## Workflow

1. Read `plan.md` and pick the next pending task from the file.
2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the implementer subagent.
3. Dispatch an implementer subagent with the [implementer-prompt.md](./implementer-prompt.md) template.
4. Wait for the implementer to report back.
5. Handle the status exactly:
   - **DONE:** Update the matching task in `plan.md`, save it, then re-read `plan.md` and verify the completion is visible before starting the next task.
   - **DONE_WITH_CONCERNS:** Treat this as unresolved correctness or scope risk. Read the concerns first and resolve them before marking the task complete. If the implementer only has a non-blocking observation, it should report `DONE` and include the note there instead.
   - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch. Do not mark the task complete.
   - **BLOCKED:** Try to unblock with better context, a smaller slice, or a more capable model. If the blocker remains, stop and escalate to the human. Do not mark the task complete.
6. Continue through ready tasks without pausing for permission. Stop only when all tasks are complete, a real blocker remains, or the plan itself is wrong.
7. Leave all changes uncommitted.

## Specific Techniques

- Treat `plan.md` as the only execution record. Internal todo trackers, memory, scratchpads, chat summaries, and subagent status messages can help coordination but never replace updating `plan.md`.
- A task is complete only after the finished state is written to `plan.md` and then verified by re-reading `plan.md`.
- Send the implementer the exact task text plus the relevant `plan.md` excerpt. Weaker models behave better when task boundaries are explicit.
- Keep the orchestration boundary intact: the implementer does the task work; you coordinate selection, status handling, and `plan.md` updates.
- Reuse [implementer-prompt.md](./implementer-prompt.md) instead of re-explaining implementation details from memory. That prompt already covers incremental implementation, TDD, targeted verification, and debugging when a step fails.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "The implementer said it's done, so I can move on." | `DONE` is not enough by itself. The task is complete only after `plan.md` is updated, saved, and re-read. |
| "I can track completion in my todo list or chat summary." | Those are helpers, not execution records. `plan.md` is the only source of truth. |
| "I'll just do this task myself instead of dispatching a subagent." | This skill is for orchestration. A fresh implementer subagent per task keeps context clean and the workflow consistent. |
| "I'll stop after this task and ask whether to continue." | Keep going through ready tasks. Stop only for a real blocker, genuine ambiguity, or full completion. |
| "DONE_WITH_CONCERNS is close enough to done." | If the concern affects correctness or scope, resolve it before marking the task complete. |

## Red Flags

- Code implemented by the orchestrator instead of an implementer subagent
- Starting the next task before `plan.md` is updated and re-read
- Treating runtime trackers or subagent reports as equivalent to `plan.md`
- Marking `BLOCKED` or `NEEDS_CONTEXT` work complete
- Stopping between ready tasks to ask for permission
- Committing changes or telling the implementer to commit

## Verification

- [ ] `plan.md` existed and provided the task order.
- [ ] Each task was assigned to a fresh implementer subagent.
- [ ] Each completed task was written to `plan.md` only after `DONE` or an acceptable `DONE_WITH_CONCERNS` resolution.
- [ ] After each `plan.md` update, the file was re-read and matched the current execution state before the next task began.
- [ ] Ready tasks ran continuously until completion or a real blocker required escalation.
- [ ] All work remains uncommitted.
