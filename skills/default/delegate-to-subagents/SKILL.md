---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by co-ordinating subagents. Use when the user explicitly asks to delegate, spawn, dispatch, or fan out subagents.
compatibility: Requires subagent dispatch with model controls and effort controls when task policy requires explicit effort.
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

- Define scope, file ownership, acceptance criteria, and required completion evidence. Classify effort as explicit only for dedicated material planning or architecture, substantive review, security review, or an explicit user effort request. Coding, tests, debugging, local design, exploration, coordination, and mechanical review use host default even when risk or failure raises the tier. Split material planning from coding when both can stand alone.
- Before routing, confirm model-control support and permission. Preflight effort-control support and permission before routing only when effort is required. Report the specific failed check; permission failure is not evidence of unavailable capability.
- Brief exploration workers with the needed context, acceptance criteria, and known negative cases; use context pointers where those facts are already available.
- Determine the most cost-efficient and capable model and reasoning effort for that subtask.
- If you have already dispatched a subagent that has the context needed for this subtask and matches the routed model and effort policy, assign the subtask to that subagent. Reuse for host-default work only when the original spawn omitted effort; for explicit effort, require the exact model/effort pair. Otherwise, dispatch a fresh subagent with the exact routed model and effort policy: submit effort only for `explicit`, and omit the effort argument for `host_default`. If the router lacks an exact model or required effort, or the host lacks support or permission for a required control, do not dispatch and name that blocker. Never invent an effort value.

**Subagent rules**:

- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.

## Runtime enforcement

For every directly dispatched background assignment, including assignments to reused agents, the parent sets a runtime limit based on expected effort and complexity. Before dispatch, record the selected exact model, effort policy, explicit reasoning effort or host-default omission, and deadline. In the same record, capture assignment/task ID, agent ID, start time, extension count (zero), and enforcement handle or scheduler entry as they become available; record or confirm armed enforcement before waiting. Verify live acceptance separately after routing and before dispatch; a missing recommendation is not a live-availability result.

Before waiting, arm a host timeout or parent-owned scheduler whose waits are bounded by the nearest assignment or checkpoint deadline. Independently time out operations that would block enforcement. Recheck deadlines whenever control returns, including after user interruptions; worker-prompt deadlines and completion notifications alone are insufficient.

At first expiry, request status, completed work, blockers, and updated ETA by a bounded checkpoint deadline. On a timely checkpoint: confirm completion, stop the worker, or grant at most one ETA-based extension, increment its count, record the new deadline, and re-arm enforcement. Maintain an active deadline for every overdue unfinished assignment; follow-up messages never reset extension counts. Stop the worker if the checkpoint is late or absent, or the extended deadline expires.

Confirm the worker and associated write-producing operations have stopped before transferring ownership; then route and dispatch a fresh replacement. Otherwise, report the blocker and continue independent authorized work without overlapping ownership. Cancel enforcement when the assignment finishes.
