---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by delegating work to subagents.
compatibility: Requires Python 3, subagent dispatch with model controls and effort controls when the route requires explicit effort, worker cancellation, and worker/write shutdown verification.
---

# Delegate to Subagents

You coordinate subagents to pursue a long-running goal.

You - the parent - owns routing, scheduling, user questions, and completion verification; delegate all other work to subagents. Protect your context window.

Use background agents so you can stay in active dialogue with the user.

Run independent work in parallel and dependent work in waves. Serialize edits to shared files.

Routine communication to and from subagents should be sparse. Communicate primarily through **context pointers**: research notes, previous commits, knowledge base files, and others. Don't duplicate information already available via pointers. There is an exception: relay every subagent question requiring human input through the parent's user-facing question tool immediately.

## Dispatch loop

Activate the `subagent-model-router` skill to learn how to use the router CLI.

While you pursue the long-running goal and maintain dialogue with the user, you will continuously identify subtasks to make progress until the goal is achieved. For each subtask:

- Define scope, file ownership, acceptance criteria, and required completion evidence.
- Brief exploration workers with the needed context, acceptance criteria, and known negative cases; use context pointers where those facts are already available.
- Follow the [pre-dispatch gate](#pre-dispatch-gate). Prefer an existing agent only when it has the task context needed by the subtask and matches the final dispatchable route: the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`. Otherwise, dispatch a fresh agent.

### Pre-dispatch gate

Before each new assignment, including agent reuse, run the router CLI. Save its invocation, unchanged JSON result, and intended dispatch arguments in the assignment's coordination record.

Use a new assignment ID for each new subtask; retain it for status updates and clarifications.

Apply the selected route within user constraints, host permissions, context limits, and applicable restrictions.

- Require `route_available: true`, except for an exact user-selected model. Apply that override through host controls; leave unknown catalog tier, price, and capability unresolved.
- Dispatch the assignment with the exact model ID, even if omitted from a descriptive model list. Honor enforced allowlists. For `explicit`, pass the user-specified effort or otherwise the CLI effort. For `host_default`, omit effort and leave its capability unverified.
- Use the dispatch result to establish live acceptance. If blocked, identify the specific model, effort, capability, or permission issue. Apply the same checks to any permitted fallback, preserving effort policy and capability floor. A model-wide rejection rules out every effort for that model.

Record actual arguments and the returned agent ID or blocker. Record overrides and fallbacks separately from the CLI result. Routine routing needs no separate user confirmation.

## Runtime enforcement

Use [`scripts/scheduler.py`](scripts/scheduler.py) with a session-specific state file. Read the CLI's `--help` before first use for commands and state behavior.

1. **Register assignments.** Choose and record the assignment ID and deadline based on expected effort and complexity before dispatch. Immediately after dispatch, register the task and returned agent ID before waiting.
2. **Service the scheduler.** Call `tick` whenever control returns, including after user interruptions. Use bounded `wait` calls while awaiting work. Independently time out blocking tools.
3. **Carry out emitted actions.** For status requests, collect status, completed work, blockers, and updated ETA; record a timely `checkpoint`, then choose completion, stopping, or the single ETA-based `extend`. Stop workers when a checkpoint or decision deadline is missed or an extension expires.
4. **Verify shutdown before transfer.** Confirm the worker and its write-producing operations have stopped before recording `confirm-stopped` and `transfer`; then route and dispatch a fresh replacement. If shutdown is unconfirmed, report the blocker and continue independent work.
5. **Close assignments.** Record verified completion with `complete`, or cancellation with `cancel` after stopping the worker.

Keep dispatch start time, routed model, exact effort or host-default omission, and any host enforcement handle in a separate coordination record keyed by assignment ID; the scheduler lacks structured fields for these. Let the scheduler own deadline transitions and extension state. It advances only when called and emits JSON actions; the parent performs communication, worker control, and shutdown verification.

## Gotchas

- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.
