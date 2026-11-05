---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by co-ordinating subagents. Use when the user explicitly asks to delegate, spawn, dispatch, or fan out subagents.
compatibility: Requires subagent dispatch with model and reasoning-effort controls.
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
- Brief exploration workers with the needed context, acceptance criteria, and known negative cases; use context pointers where those facts are already available.
- Determine the most cost-efficient and capable model and reasoning effort for that subtask.
- If you have already dispatched a subagent that has the context needed for this subtask and matches the routed model and reasoning effort, assign the subtask to that subagent. Otherwise, dispatch a fresh subagent by submitting the exact routed model and reasoning effort through dispatch controls. If the router does not return an exact model and reasoning effort or the host does not permit both to be specified, do not dispatch and report the issue. Never fall back to runtime defaults.

**Subagent rules**:

- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.

## Runtime enforcement

For every directly dispatched background assignment, including assignments to reused agents, the parent sets a runtime limit based on expected effort and complexity. Before dispatch, record the selected exact model, reasoning effort, and deadline. In the same record, capture assignment/task ID, agent ID, start time, extension count (zero), and enforcement handle or scheduler entry as they become available; record or confirm armed enforcement before waiting.

Before waiting, arm a host timeout or parent-owned scheduler whose waits are bounded by the nearest assignment or checkpoint deadline. Independently time out operations that would block enforcement. Recheck deadlines whenever control returns, including after user interruptions; worker-prompt deadlines and completion notifications alone are insufficient.

At first expiry, request status, completed work, blockers, and updated ETA by a bounded checkpoint deadline. On a timely checkpoint: confirm completion, stop the worker, or grant at most one ETA-based extension, increment its count, record the new deadline, and re-arm enforcement. Maintain an active deadline for every overdue unfinished assignment; follow-up messages never reset extension counts. Stop the worker if the checkpoint is late or absent, or the extended deadline expires.

Confirm the worker and associated write-producing operations have stopped before transferring ownership; then route and dispatch a fresh replacement. Otherwise, report the blocker and continue independent authorized work without overlapping ownership. Cancel enforcement when the assignment finishes.
