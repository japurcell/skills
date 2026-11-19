---
name: execplan-implement
description: ExecPlan implementation workflow. Use when implementing ExecPlans and you are the parent agent. Do not use if you are a subagent being delegated to.
compatibility: Requires background subagent dispatch with follow-up messaging and Git worktrees.
---

This workflow applies when the parent implements an ExecPlan, whether supplied by the user, created during the session, or resumed from earlier work. This plan should have tasks and milestones associated with it, describing how to implement the plan.

The goal is the entire plan implemented on a single **integration branch**, with every task and milestone resolved.

The tasks are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tasks which are ready to be grabbed.

**Subagent management rules:**

- Activate the `subagent-model-router` skill and follow the [pre-dispatch gate](#pre-dispatch-gate) for every subagent dispatch.
- **Implementer subagents** should run in the background when their tasks can progress independently.
- Start with one implementer and assign each implementer one task at a time. Reuse an idle implementer when its model and effort satisfy the pre-dispatch gate and its prior context helps with the task. If no suitable implementer is idle, a single independent ready task is enough to start another when capacity allows.
- Brief each implementer with its task, base revision, acceptance checks and constraints that could invalidate its work. Give it the entry path, a direct link to its assignment, and the specific prerequisite decisions, results or research notes it needs. Send interface changes to affected owners as soon as they are known.
- Delegate integration to one persistent **integration coordinator** subagent in background mode. Before relying on it, obtain its agent ID, send a bounded follow-up readiness request, and observe its acknowledgment. Record the verified follow-up handle. A launch response alone does not prove follow-up delivery.
- Reuse the **integration coordinator** across merge waves, progress updates, and final checks. Give it bounded assignments; leave it idle between waves instead of assigning an indefinite wait. It should handle deterministic commits and status checks directly when safe.

[Enforce limits](#runtime-enforcement) for exploration, implementation, review, and fixes. An agent is idle only with no outstanding assignment; dependency waits remain active.

Before every commit, the commit creator must activate the `commit` skill and follow its message validation workflow.

## Pre-dispatch gate

Before each new assignment, including agent reuse, run the router CLI. Save its invocation, unchanged JSON result, and intended dispatch arguments in the assignment's coordination record.

Apply the selected route within user constraints, host permissions, context limits, and applicable restrictions.

- Require `route_available: true`, except for an exact user-selected model. Apply that override through host controls; leave unknown catalog tier, price, and capability unresolved.
- Dispatch the assignment with the exact model ID, even if omitted from a descriptive model list. Honor enforced allowlists. For `explicit`, pass the user-specified effort or otherwise the CLI effort. For `host_default`, omit effort and leave its capability unverified.
- Use the dispatch result to establish live acceptance. If blocked, identify the specific model, effort, capability, or permission issue. Apply the same checks to any permitted fallback, preserving effort policy and capability floor. A model-wide rejection rules out every effort for that model.

Record actual arguments and the returned agent ID or blocker. Record overrides and fallbacks separately from the CLI result. Routine routing needs no separate user confirmation.

## Runtime enforcement

1. **Record each background assignment**, including reuse. Before dispatch, set a deadline from expected effort and complexity. Record the routed model and explicit effort or host-default omission; track task and agent IDs, start time, extension count (initially zero), and enforcement handle as available.
2. **Arm one nearest wake before waiting.** Keep every active deadline in the parent-owned assignment registry, but set only one wake for the nearest deadline. Independently time out blocking operations. Recheck on control returns, including user interruptions. When a worker completes, consume and verify its result, close its assignment, clear its wake, then arm the nearest remaining deadline. Do no status lookup or new dispatch during quiet time, and do not poll other workers when one completion arrives. Before dispatch, check the task registry for an active assignment; resume or resolve it instead of launching duplicate work.
3. **Enforce real expiry.** At the expired assignment's deadline, request status, completed evidence, blockers, and updated ETA with a bounded checkpoint deadline. Keep overdue work under a deadline. On timely status, confirm completion, stop the worker, or grant its only ETA-based extension. Record an extension's new deadline and increment its count before re-arming. Preserve the count across follow-ups. Stop the worker on missed checkpoint or expired extension. Use the host's current time for live enforcement, not frozen test timestamps.
4. **Preserve continuity.** Keep owner, pinned revision, completed evidence, blocker, deadline, and next action in the assignment record. For a same-worker follow-up, request a relevant fact from its earlier setup and verify the returned value. If transport is unavailable or a replacement is needed, provide the environment, pinned revision, and prior evidence.
5. **Report compactly and transfer safely.** Each status report carries all six assignment fields. Later reports preserve stable evidence references, update changed fields, and add completed evidence without replaying setup or history. Before transferring ownership, confirm the worker and its write-producing operations have stopped, then route and dispatch a fresh replacement. If shutdown is unconfirmed, report the blocker and continue independent work. Cancel enforcement on verified completion.

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

8. Ensure all tasks and milestones are resolved and report the integration branch.

9. Clean up all **implementer subagent** worktrees and their related branches.

## Code review fix cycle

Call the Skill tool with `code-review-biaxis` on the integration branch. Track all issues raised by the code review as new tasks in the ExecPlan **frontier**, then fix them in a single **implementer subagent**. Repeat _code review → fix cycle_ until no issues remain for a maximum of three iterations. Report all unresolved issues.

For a narrow fix, prefer the original implementer when its investigation still applies. A reviewer can resume to recheck a specific finding. When a review calls for independent discovery, start a fresh reviewer with the relevant spec or standards, the diff and verification evidence. Keep the two review axes independent.

Apply the [pre-dispatch gate](#pre-dispatch-gate) to each new assignment. Reuse requires the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`. Otherwise dispatch a fresh agent.

## Gotchas

- Do not allow code reviews result in scope creep. It is your job to keep scope limited to the ExecPlan frontier.
- Do not create worktrees anywhere within the main project directory because agents will automatically discover files like `AGENTS.md` causing context window bloat. Recommend creating them in `../<project name>.worktrees`.
- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.
