---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by co-ordinating subagents. Use when the user explicitly asks to delegate, spawn, dispatch, or fan out subagents.
compatibility: Requires subagent dispatch with model controls and effort controls when the route requires explicit effort.
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
- For every task, use `subagent-model-router` to obtain the final dispatchable route. Apply its model and effort policy through dispatch controls, and stop on a named blocker. Prefer an existing agent only when it has the task context needed by the subtask and matches the final dispatchable route: the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`. Otherwise, dispatch a fresh agent.

**Subagent rules**:

- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.


## Runtime enforcement

1. **Record each background assignment you dispatch**, including reuse. Before dispatch, set a deadline based on expected effort and complexity. Record the routed model and its exact explicit effort or host-default omission. Track task and agent IDs, start time, extension count (initially zero), and enforcement handle as available.
2. **Arm enforcement before waiting.** Use a host timeout or parent-owned scheduler bounded by the nearest assignment or checkpoint deadline. Independently time out blocking operations. Recheck deadlines whenever control returns, including after user interruptions.
3. **At expiry**, request status, completed work, blockers, and updated ETA by a bounded checkpoint deadline. Keep overdue work under a deadline. On timely status, confirm completion, stop the worker, or grant its only ETA-based extension. If extended, record the new deadline, increment the count, and re-arm enforcement. Preserve the count across follow-ups. Stop the worker on a missed checkpoint or expired extension.
4. **Before transferring ownership**, confirm the worker and its write-producing operations have stopped, then route and dispatch a fresh replacement. If shutdown is unconfirmed, report the blocker and continue independent work. Cancel enforcement on completion.
