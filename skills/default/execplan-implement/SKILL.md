---
name: execplan-implement
description: ExecPlan implementation workflow. Use when implementing ExecPlans and you are the parent agent. Do not use if you are a subagent being delegated to.
compatibility: Requires background subagent dispatch with follow-up messaging and Git worktrees.
---

This workflow applies when the parent implements an ExecPlan, whether supplied by the user, created during the session, or resumed from earlier work. This plan should have tasks and milestones associated with it, describing how to implement the plan.

The goal is the entire plan implemented on a single **integration branch**, with every task and milestone resolved.

The tasks are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tasks which are ready to be grabbed.

**Subagent management rules:**

- For each assignment, including reuse, activate the `subagent-model-router` skill. Route once per assignment. Before launch, write the router invocation, unchanged JSON and intended arguments to the assignment record. Dispatch the required worker with the exact eligible model, even if absent from an advisory list. Pass explicit effort only. Append actual arguments and the returned worker ID or blocker. Keep routing metadata out of worker briefs. Continue independent assignments as slots open.
- **Implementer subagents** should run in the background when their tasks can progress independently.
- After the coordinator acknowledges readiness, start one implementer. Assign one task per implementer. For each ready task, reuse an eligible idle implementer or start another when capacity allows.
- Brief each implementer with its task, base revision, acceptance checks and constraints that could invalidate its work. Give it the entry path, a direct link to its assignment, and the specific prerequisite decisions, results or research notes it needs. Send interface changes to affected owners as soon as they are known.
- Delegate integration to one persistent **integration coordinator** subagent in background mode. Before relying on it, obtain its agent ID, send a bounded follow-up readiness request, and observe its acknowledgment. Record the verified follow-up handle. A launch response alone does not prove follow-up delivery.
- Reuse the **integration coordinator** across merge waves, progress updates, and final checks. Give it bounded assignments; leave it idle between waves instead of assigning an indefinite wait. It should handle deterministic commits and status checks directly when safe.

[Enforce limits](#runtime-enforcement) for exploration, implementation, review, and fixes. An agent is idle only with no outstanding assignment; dependency waits remain active.

Before every commit, the commit creator must activate the `commit` skill and follow its message validation workflow.

## Runtime enforcement

1. **Register a live deadline before launch.** For each background assignment, including reuse, estimate duration from task complexity, read live host time, and register one absolute deadline before launch. If its budget starts at actual launch, re-anchor the deadline once to the host-reported start time when the worker ID returns. Record the routed model and explicit effort or host-default omission; track task and agent IDs, start time, extension count (initially zero), and enforcement handle as available.
2. **Wait for completion or the nearest deadline.** Keep every active timer in the parent-owned assignment registry, including reservations whose worker handle has not yet returned. For each assignment, select its phase expiry if already due, even if a reminder is overdue; otherwise select the earlier timer, preferring expiry on a tie. Across assignments select the earliest due time, then expiry before reminder, then assignment ID. Arm one wake for that timer. For example, a reservation due at 10 remains the next wake while its launch is delayed, even if an attached worker is due at 20. Calculate `remaining` from live host time; handle a due deadline immediately, otherwise wait for any eligible completion capped at `remaining`, such as Codex `wait_agent`, or arm one one-shot timer and yield for independent notifications. If Copilot `read_agent(wait=true, timeout=remaining)` only waits on one worker and independent notifications are unavailable, use the selected worker when its handle exists; another completion may be consumed only when that wait returns, up to the remaining timeout plus host scheduling overhead. If the selected reservation has no handle, retain its timer and use a bounded host wait on an attached worker if available, or a timer until launch returns. No native latency bound has been verified here. A foreground timer-only helper wait cannot receive native completion. Time out blocking operations. Drain delivered completions before expiring assignments: consume and verify each result and close its assignment. Refresh after completion, a registry mutation, a deadline or an interruption: recalculate and re-arm the single wake. Registry changes do not independently wake a native wait; its owner must re-arm. During quiet time, make no status lookup or new dispatch, and do not poll other workers when one completion arrives. Before dispatch, check the task registry for an active assignment; resume or resolve it instead of launching duplicate work.
3. **Enforce real expiry.** When the deadline wins, consume any delivered result and check only the due assignment for completed work before requesting status, completed evidence, blockers, and updated ETA with a bounded checkpoint deadline. Keep overdue work under a deadline. On timely status, confirm completion or stop the worker, or grant its only extension if the worker supplied an ETA later than both the current deadline and now. An unknown ETA cannot justify an extension. Record an extension's new deadline and increment its count before re-arming. Preserve the count across follow-ups. Stop the worker on missed checkpoint or expired extension. Use the host's current time for live enforcement, not frozen test timestamps.
4. **Preserve continuity.** Keep owner, pinned revision, completed evidence, blocker, deadline, and next action in the assignment record. In the parent registry, keep a cursor per reused Copilot agent (initially `0`). On completion or a due check, pass it as `read_agent(since_turn=...)`. After recording verified results, set it to the highest fully consumed turn index plus one; leave it unchanged if none was consumed. For a same-worker follow-up, request a relevant fact from its earlier setup and verify the returned value. If transport is unavailable or a replacement is needed, provide the environment, pinned revision, and prior evidence.
5. **Report compactly and transfer safely.** Each status report carries all six assignment fields. Later reports preserve stable evidence references, update changed fields, and add completed evidence without replaying setup or history. Before transferring ownership, confirm the worker and its write-producing operations have stopped, then route and dispatch a fresh replacement. If shutdown is unconfirmed, report the blocker and continue independent work. Cancel enforcement on verified completion.

Native observations are not latency guarantees: in one Codex standalone inverse trial, a status request followed the deadline by about 12 seconds. In one Copilot standalone inverse candidate, the parent consumed QUICK about 46 seconds after its native completion event; in a baseline trial a single-worker wait delayed reading QUICK by at least 80 seconds. In a Copilot delegate trial, a stop message did not stop the worker's launcher, which wrote after the request. Keep ownership until the worker and its writes are independently confirmed stopped; report any missing control or observation.

## Steps

1. Activate the `exec-plans` skill and identify the next authorized action from the entry file. If the graph spans files, consult only the linked index sections needed to schedule affected tasks. Open implementation detail only for selected work and its explicit prerequisites. Apply the skill's size check at each checkpoint.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tasks - relevant codebase files or external documentation. Brief it with the needed context, acceptance criteria, and known negative cases, using context pointers where those facts are already available. Ensure the exploration subagent can save files - it should save its markdown notes in a directory next to the plan, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. If current branch is `main` or `master`, create a new **integration branch**. Start the background **integration coordinator** and verify follow-up messaging as above. Instruct it to activate the `exec-plans` skill. For a split plan, include each worker's task file in its integration base revision before dispatch.

4. Use **implementer subagents** to implement each task, each in its own worktree on its own branch. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - merges the integration branch tip into its own branch before reporting done

5. Each implementer records results, evidence and blockers in its assigned file when the plan is split. Send the tested base and task revisions, checks and interface changes to the coordinator for integration. For a single-file plan, the coordinator reconciles the required sections and records the integration revision, verification results and unresolved dependencies in the checkpoint. For a split plan, it reports that evidence to the parent, who reconciles the milestone and shared entry together at the checkpoint. A replacement coordinator resumes from the checkpoint and the links for its assignment.

6. Recompute the **frontier** after each merge. Start ready tasks that unblock dependent work first. If completed branches are accumulating faster than integration or CI can verify them, slow new starts until verification catches up.

7. Once all tickets are complete, follow the [code review fix cycle](#code-review-fix-cycle).

8. Before closing the plan, verify all tasks and milestones are resolved. Record the integration branch and exact revision with the build and test commands required by the plan and repository, their outcomes, and evidence. Report local verification separately from CI. A local handoff may report CI pending or unavailable; leave any milestone that requires CI open until the matching revision passes.

9. Clean up all **implementer subagent** worktrees and their related branches.

## Code review fix cycle

Call the Skill tool with `code-review-biaxis` on the integration branch. Track all issues raised by the code review as new tasks in the ExecPlan **frontier**, then fix them in a single **implementer subagent**. Repeat _code review → fix cycle_ until no issues remain for a maximum of three iterations. Report all unresolved issues.

For a narrow fix, prefer the original implementer when its investigation still applies. A reviewer can resume to recheck a specific finding. When a review calls for independent discovery, start a fresh reviewer with the relevant spec or standards, the diff and verification evidence. Keep the two review axes independent.

## Gotchas

- Do not allow code reviews result in scope creep. It is your job to keep scope limited to the ExecPlan frontier.
- Do not create worktrees anywhere within the main project directory because agents will automatically discover files like `AGENTS.md` causing context window bloat. Recommend creating them in `../<project name>.worktrees`.
