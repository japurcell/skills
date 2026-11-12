---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by co-ordinating subagents.
compatibility: Requires Python 3 and subagent dispatch with model controls and effort controls when the route requires explicit effort.
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
- Use `subagent-model-router` to obtain the final dispatchable route for the subtask. Apply its model and effort policy through dispatch controls, and stop on a named blocker. Prefer an existing agent only when it has the task context needed by the subtask and matches the final dispatchable route: the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`. Otherwise, dispatch a fresh agent.

**Subagent rules**:

- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.

## Runtime enforcement

Use [`scripts/scheduler.py`](scripts/scheduler.py) with a session-specific state file. Read [`README.md`](README.md) and the CLI's `--help` before first use for commands and state behavior.

1. **Register assignments.** Choose a deadline based on expected effort and complexity before dispatch. Register task and returned agent IDs before waiting, including new assignments to reused agents. Preserve the same assignment record across follow-ups.
2. **Service the scheduler.** Call `tick` whenever control returns, including after user interruptions. Use bounded `wait` calls while awaiting work. Independently time out blocking tools.
3. **Carry out emitted actions.** For status requests, collect status, completed work, blockers, and updated ETA; record a timely `checkpoint`, then choose completion, stopping, or the single ETA-based `extend`. Stop workers when a checkpoint or decision deadline is missed or an extension expires.
4. **Complete ownership transfer.** Verify the worker and its write-producing operations have stopped, then record `confirm-stopped` and `transfer`. Authorization leaves transfer pending: update the parent's actual ownership record, then run `confirm-transfer ID --owner OWNER --evidence REFERENCE --confirmation parent-ownership-updated`. Read back the parent owner and scheduler receipt before reporting reassignment complete or dispatching overlapping replacement work. Cancel the superseded active assignment if needed; route and freshly register the replacement. If shutdown or transfer is blocked, retain it as pending and continue independent work.
5. **Close assignments.** Record verified completion with `complete`, or cancellation with `cancel` after stopping the worker.

Keep dispatch start time, routed model, exact effort or host-default omission, and any host enforcement handle in a separate coordination record keyed by assignment ID; the scheduler lacks structured fields for these. Let the scheduler own deadline transitions and extension state. It advances only when called and emits JSON actions; the parent performs communication, worker control, and shutdown verification.
