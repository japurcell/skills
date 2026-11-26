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

Activate the `subagent-model-router` skill once per session, before the first routing evaluation.

For each assignment, including reuse:

- Assign a new ID for status updates. Define scope, ownership, acceptance criteria, and required completion evidence.
- Put constraints and known negative cases that change the worker's decisions in the brief. Point to the relevant file, section, commit or research note for supporting detail.
- Run `route.py` once for this assignment. Before launch, record its invocation, unchanged JSON and intended arguments. Use the exact eligible model and pass effort only when explicitly routed. Keep routing metadata outside worker briefs.
- Before spawning, run `scheduler.py --state <file> reusable --model MODEL --profile PROFILE`; add `--effort LEVEL` only for explicit effort. For independent review, exclude every author with repeatable `--exclude AGENT` and check the remaining workers’ assignment histories for conflicts. Use a fresh context when the task requires one.
- Prefer an eligible worker when its context fits, or when capacity is full and the brief can stand alone. Confirm host availability before sending a follow-up. When a fresh context is necessary and capacity is exhausted, wait for capacity or report the host limit. Retry spawning after capacity changes. Inherit the parent transcript only when reconstructing its observations would be costly.
- Register the returned host ID with its actual `--model`, `--profile` and explicit effort, if any. Record the context choice, actual dispatch arguments and worker ID or blocker. Validate structured records before dispatch and after recording the result. Continue independent assignments as slots open.
- Ask for the result, evidence pointer and any open decision that affects another task. Retrieve the underlying evidence when verifying a claim or resolving a disagreement.

## Runtime enforcement

Use [`scripts/scheduler.py`](scripts/scheduler.py) with a session-specific state file. Read the CLI's `--help` before first use for commands and state behavior.

Use the host's result channel. In Copilot, keep a cursor per worker starting at 0. Pass it as `since_turn` on every `read_agent`, including blocking waits, follow-ups and deadline checks. After verifying and recording complete turns, advance to the last consumed index plus one. An empty timeout leaves the cursor unchanged. In Codex, consume delivered messages after a bounded `wait_agent` or yield. In Claude Code, consume the background completion notification. In Gemini CLI, consume the named subagent tool's returned result. If the host offers only synchronous calls, report the missing background/deadline control before assigning background work.

1. **Register and wait.** Choose the assignment ID and absolute deadline before dispatch. Register ordinary work without `--checkpoint`; opt in only when scheduled reminders are needed. Register immediately after dispatch, including follow-ups. Run `scheduler.py --state <file> next-wake`: `wake` is null or contains `assignment`, `agent`, absolute `due`, and `reason`. Calculate remaining time from the live clock and attend immediately if due. Use a host wait for any eligible completion capped at that remaining time, or arm one one-shot timer and yield if independent notifications arrive only on yield. Codex `wait_agent` is an any-completion wait. Where Copilot `read_agent(agent_id=worker, since_turn=cursor, wait=true, timeout=remaining)` waits on only one worker and no independent notification is available, wait on the selected worker; another worker's completion may be consumed only when the wait returns, up to its remaining timeout plus host scheduling overhead. No native latency bound has been verified here. `scheduler.py wait --max-wait` alone cannot observe native completion. Omit `--now` in live enforcement and independently time out blocking tools.
2. **Act on events.** Drain delivered completions before expiring assignments: consume and verify each result, then record `complete`. Call `tick` for due actions and perform each emitted action. Refresh after completion, a registry mutation, a deadline or an interruption: query `next-wake` again and re-arm the single wake. The scheduler does not wake a native wait when its state file changes, so its owner must re-arm after changes. Do not poll other workers when one completes. Before dispatch, check whether that task already has an active assignment; resume or resolve it instead of launching duplicate work. During quiet time, wait through the host completion channel or yield for host notifications with the one-shot deadline timer.
3. **Enforce expiry.** When the deadline wins, first consume any delivered result and check only the due worker for completed work. Request status, completed evidence, blockers, and ETA only if it remains active, within the scheduler's bounded checkpoint deadline. Record a timely response with `checkpoint`; then complete or stop the worker, or use the single `extend` if the worker supplied an ETA later than both the current deadline and now. An unknown ETA cannot justify an extension. Stop the worker if the checkpoint or decision deadline is missed or the extension expires. Keep the watchdog armed until verified completion or shutdown.
4. **Preserve continuity and transfer safely.** Keep owner, pinned revision, completed evidence, blocker, deadline, and next action in the assignment record. When a follow-up depends on an earlier observation, ask the worker for it and verify it before relying on it. Verify a standalone assignment against its own acceptance criteria. If transport is unavailable or a new worker is needed, give the replacement the environment, pinned revision, and prior evidence. Confirm both worker and write-producing operations have stopped before `confirm-stopped` and `transfer`; if unconfirmed, report the blocker and continue independent work.
5. **Report compactly.** Each status report carries those six fields. On the next report, preserve stable evidence references, update changed fields, and add newly completed evidence without replaying setup or history.

Keep dispatch start time and the host enforcement handle in the coordination record keyed by assignment ID. Let the scheduler own deadline transitions and extension state. It advances only when called and emits JSON actions; the parent performs communication, worker control, and shutdown verification.

Native observations are not latency guarantees: in one Codex inverse trial, expiry was processed about 11 seconds late. In a Copilot trial, a stop message did not stop the worker's launcher, which wrote after the request. Keep ownership until the worker and its writes are independently confirmed stopped; report any missing control or observation.
