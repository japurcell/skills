---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by co-ordinating subagents.
compatibility: Requires Python 3, subagent dispatch with model controls and effort controls when the route requires explicit effort, worker cancellation, and worker/write shutdown verification.
---

# Delegate to Subagents

You co-ordinate subagents to pursue a long-running goal.

You - the parent - owns routing, scheduling, user questions, and completion verification; delegate all other work to subagents. Protect your context window.

Use background agents so you can stay in active dialogue with the user.

Run independent work in parallel and dependent work in waves. Serialize edits to shared files.

Routine communication to and from subagents should be sparse. Communicate primarily through **context pointers**: research notes, previous commits, knowledge base files, and others. Don't duplicate information already available via pointers. There is an exception: relay every subagent question requiring human input through the parent's user-facing question tool immediately.

## Dispatch loop

Activate the `subagent-model-router` skill.

While you pursue the long-running goal and maintain dialogue with the user, you will continuously identify subtasks to make progress until the goal is achieved. For each subtask:

- Define scope, file ownership, acceptance criteria, and required completion evidence.
- Brief exploration workers with the needed context, acceptance criteria, and known negative cases; use context pointers where those facts are already available.
- Use `subagent-model-router` to obtain the final dispatchable route for the subtask. Apply its model and effort policy through dispatch controls, and stop on a named blocker. Prefer an existing agent only when it has the task context needed by the subtask and matches the final dispatchable route: the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`. Otherwise, dispatch a fresh agent.

### Pre-dispatch gate

Before launching an agent or assigning new work to an existing agent, run the router CLI and record its invocation, returned route, and intended dispatch arguments in the assignment's coordination record.

A new subtask requires a new assignment ID and route, even when reusing an agent. Retain the assignment ID for same-subtask status updates or clarifications.

Loading `subagent-model-router` does not complete routing. Proceed only when the record establishes a dispatchable route and the intended arguments match its model and effort policy. If permissions or host restrictions prevent applying the route, report the named blocker instead of silently substituting runtime defaults.

Automatically apply the router's final dispatchable model and effort policy, including verified fallbacks. Do not request separate user confirmation for routine routing choices. Preserve explicit user constraints and required host approval flows.

After dispatch, record the actual arguments and returned agent ID. A successful launch does not replace the required routing evidence.

## Runtime enforcement

Use [`scripts/scheduler.py`](scripts/scheduler.py) with a session-specific state file. Read [`README.md`](README.md) and the CLI's `--help` before first use for commands and state behavior.

1. **Register assignments.** Choose and record the assignment ID and deadline based on expected effort and complexity before dispatch. Immediately after dispatch, register the task and returned agent ID before waiting.
2. **Service the scheduler.** Call `tick` whenever control returns, including after user interruptions. Use bounded `wait` calls while awaiting work. Independently time out blocking tools.
3. **Carry out emitted actions.** For status requests, collect status, completed work, blockers, and updated ETA; record a timely `checkpoint`, then choose completion, stopping, or the single ETA-based `extend`. Stop workers when a checkpoint or decision deadline is missed or an extension expires.
4. **Verify shutdown before transfer.** Confirm the worker and its write-producing operations have stopped before recording `confirm-stopped` and `transfer`; then route and dispatch a fresh replacement. If shutdown is unconfirmed, report the blocker and continue independent work.
5. **Close assignments.** Record verified completion with `complete`, or cancellation with `cancel` after stopping the worker.

Keep dispatch start time, routed model, exact effort or host-default omission, and any host enforcement handle in a separate coordination record keyed by assignment ID; the scheduler lacks structured fields for these. Let the scheduler own deadline transitions and extension state. It advances only when called and emits JSON actions; the parent performs communication, worker control, and shutdown verification.

## Gotchas

- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.
