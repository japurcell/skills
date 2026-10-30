---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by co-ordinating subagents. Use when the user explicitly asks to delegate, spawn, dispatch, or fan out subagents.
---

# Delegate to Subagents

You co-ordinate subagents to pursue a long-running goal. This session will run for a long time.

All work should be done in subagents. Protect your context window.

Use background agents so you can stay in active dialogue with the user.

Run independent work in parallel and dependent work in waves. Serialize edits to shared files.

Routine communication to and from subagents should be sparse. Communicate primarily through **context pointers**: research notes, previous commits, knowledge base files, and others. Don't duplicate information already available via pointers. There is an exception: relay every subagent question requiring human input through the parent’s user-facing question tool immediately.

## Dispatch loop

Activate the `subagent-model-router` skill.

While you pursue the long-running goal and maintain dialogue with the user, you will continuously identify subtasks to make progress until the goal is achieved. For each subtask:

- Define scope, file ownership, acceptance criteria, and required completion evidence.
- Determine the most cost-efficient and capable model and reasoning effort for that subtask.
- If you have already dispatched a subagent that has the context needed for this subtask and matches the routed model and reasoning effort, assign the subtask to that subagent. Otherwise, dispatch a fresh subagent by submitting the exact routed model and reasoning effort through dispatch controls. If the router does not return an exact model and reasoning effort or the host does not permit both to be specified, do not dispatch and report the issue. Never fall back to runtime defaults.

**Subagent rules**:

- Enforce runtime limits based on expected effort and complexity. When overdue, request a **progress update** that includes: request status, completed work, blockers, and an updated ETA. Set a new runtime limit based on the **progress update**. If the second runtime limit is exceeded, cancel the subagent and dispatch a fresh **replacement agent**.
- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.
