---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by delegating work to subagents.
compatibility: Requires Python 3, subagent dispatch with model controls and effort controls when the route requires explicit effort, worker cancellation, and worker/write shutdown verification.
---

# Delegate to Subagents

You coordinate subagents to pursue a long-running goal.

You - the parent - owns routing, scheduling, user questions, and completion verification; delegate all other work to subagents. Protect your context window.

Use background agents so you can stay in active dialogue with the user.

Keep steps that depend on the same working context in one bounded assignment. Split independent slices when they can run concurrently or need separate judgments. Serialize edits to shared files.
If workers cover different slices, verify every required slice. If they attempt the same problem, decide before dispatch whether to accept the first verified result or compare all candidates.

Keep routine messages sparse. When one worker produces an artifact another consumes, have them exchange a sample and flag interface changes to the affected owner. Relay every question requiring human input through the parent's user-facing question tool immediately.

## Dispatch loop

Activate the `subagent-model-router` skill to learn how to use the router CLI.

While you pursue the long-running goal and maintain dialogue with the user, you will continuously identify subtasks to make progress until the goal is achieved. For each subtask:

- Define scope, file ownership, acceptance criteria, and required completion evidence.
- Put constraints and known negative cases that change the worker's decisions in the brief. Point to the relevant file, section, commit or research note for supporting detail.
- Follow the [pre-dispatch gate](#pre-dispatch-gate). Reuse requires the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`.
- Resume an eligible worker when its prior investigation helps with the next decision. For independent work, a second opinion or stale history, start a fresh worker with only the task brief and pointers. Inherit the parent transcript only when the worker needs a sequence of observations that would be costly to reconstruct. Record the context choice in the existing assignment record.
- Ask for the result, evidence pointer and any open decision that affects another task. Retrieve the underlying evidence when verifying a claim or resolving a disagreement.

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

1. **Register and wait.** Choose the assignment ID and absolute deadline before dispatch. Register ordinary work without `--checkpoint`; opt in only when scheduled reminders are needed. Register the returned agent ID immediately after dispatch. Keep every deadline in the scheduler. Prefer a host completion wait capped at the nearest real deadline: use Codex `wait_agent` or Copilot `read_agent(wait=true, timeout=remaining)` for the nearest pending assignment when the host waits on one worker at a time. If the host delivers notifications only while yielded, arm one one-shot host timer for the nearest deadline and yield for notifications. Use `scheduler.py wait --max-wait` alone only when completion is independently observable during that wait; it sees scheduler state and time, not native host notifications. Omit `--now` in live enforcement and independently time out blocking tools.
2. **Act on events.** When a worker completes, consume and verify its result, record `complete`, clear its wake, then arm the nearest remaining deadline. Do not poll other workers when one completes. Before dispatch, check whether that task already has an active assignment; resume or resolve it instead of launching duplicate work. During quiet time, wait through the host completion channel or yield for host notifications with the one-shot deadline timer; do not run a foreground timer-only helper wait that prevents delivery. Call `tick` on other control returns, including user interruptions, and perform only its emitted action.
3. **Enforce expiry.** When the deadline wins, first consume any delivered result and check only the due worker for completed work. Request status, completed evidence, blockers, and ETA only if it remains active, within the scheduler's bounded checkpoint deadline. Record a timely response with `checkpoint`; then complete, stop, or use the single ETA-based `extend`. Stop the worker if the checkpoint or decision deadline is missed or the extension expires. Keep the watchdog armed until verified completion or shutdown.
4. **Preserve continuity and transfer safely.** Keep owner, pinned revision, completed evidence, blocker, deadline, and next action in the assignment record. For same-worker follow-up, request a relevant fact from its earlier setup and check the returned value before continuing. If transport is unavailable or a new worker is needed, give the replacement the environment, pinned revision, and prior evidence. Confirm both worker and write-producing operations have stopped before `confirm-stopped` and `transfer`; if unconfirmed, report the blocker and continue independent work.
5. **Report compactly.** Each status report carries those six fields. On the next report, preserve stable evidence references, update changed fields, and add newly completed evidence without replaying setup or history.

Keep dispatch start time, routed model, exact effort or host-default omission, and any host enforcement handle in a separate coordination record keyed by assignment ID; the scheduler lacks structured fields for these. Let the scheduler own deadline transitions and extension state. It advances only when called and emits JSON actions; the parent performs communication, worker control, and shutdown verification.

## Gotchas

- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.
