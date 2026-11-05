---
name: execplan-implement
description: ExecPlan implementation workflow. Use when implementing ExecPlans and you are the parent agent. Do not use if you are a subagent being delegated to.
compatibility: Requires subagent dispatch with model controls and effort controls when the route requires explicit effort.
---

You have been provided an ExecPlan. This plan should have tasks and milestones associated with it, describing how to implement the plan.

The goal is the entire plan implemented on a single **integration branch**, with every task and milestone resolved.

The tasks are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tasks which are ready to be grabbed.

**Subagent management rules:**

- Activate the `subagent-model-router` skill.
- For every subagent dispatch, use `subagent-model-router` to obtain its final dispatchable route, and apply its model and effort policy through dispatch controls. Stop on a named blocker.
- **Implementer subagents** should be run in the background where possible for maximum concurrency.
- Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the plan, tasks, research notes, and previous commits. Don't duplicate information already available via pointers.
- Delegate integration to one persistent **integration coordinator** subagent. Reuse it across merge waves, progress updates, and final checks. The coordinator should also handle deterministic commits and status checks directly when safe.

Enforce limits for exploration, implementation, review, and fixes. An agent is idle only with no outstanding assignment; dependency waits remain active.

All commits must follow [commit message guidelines](references/message.md).

## Runtime enforcement

For every directly dispatched background assignment, including assignments to reused agents, the parent sets a runtime limit based on expected effort and complexity. Before dispatch, record the final route’s exact model, effort policy, explicit reasoning effort or host-default omission, and deadline. In the same record, capture assignment/task ID, agent ID, start time, extension count (zero), and enforcement handle or scheduler entry as they become available; record or confirm armed enforcement before waiting.

Before waiting, arm a host timeout or parent-owned scheduler whose waits are bounded by the nearest assignment or checkpoint deadline. Independently time out operations that would block enforcement. Recheck deadlines whenever control returns, including after user interruptions; worker-prompt deadlines and completion notifications alone are insufficient.

At first expiry, request status, completed work, blockers, and updated ETA by a bounded checkpoint deadline. On a timely checkpoint: confirm completion, stop the worker, or grant at most one ETA-based extension, increment its count, record the new deadline, and re-arm enforcement. Maintain an active deadline for every overdue unfinished assignment; follow-up messages never reset extension counts. Stop the worker if the checkpoint is late or absent, or the extended deadline expires.

Confirm the worker and associated write-producing operations have stopped before transferring ownership; then route and dispatch a fresh replacement. Otherwise, report the blocker and continue independent authorized work without overlapping ownership. Cancel enforcement when the assignment finishes.

## Steps

1. Activate the `exec-plans` skill, then read the plan, milestones, and tasks to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tasks - relevant codebase files or external documentation. Brief it with the needed context, acceptance criteria, and known negative cases, using context pointers where those facts are already available. Ensure the exploration subagent can save files - it should save its markdown notes in a directory next to the plan, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. If current branch is `main` or `master`, create a new **integration branch**. Start the **integration coordinator** subagent, instructing it to activate the `exec-plans` skill and reconcile its required plan sections before reporting a checkpoint complete.

4. Use **implementer subagents** to implement each task, each in its own worktree on its own branch. Follow the router’s final dispatchable route and runtime enforcement as specified above. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - calls the Skill tool with `tdd` to build the task;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, have the same **integration coordinator subagent** merge its work to the integration branch.

6. If this changes the **frontier** of available tasks, kick off more **implementer subagents** to work on the new tasks. This allows for maximum concurrency.

7. Once all tickets are complete, follow the [code review fix cycle](#code-review-fix-cycle).

8. Ensure all tasks and milestones are resolved and report the integration branch.

9. Clean up all **implementer subagent** worktrees and their related branches.

## Code review fix cycle

Call the Skill tool with `code-review-biaxis` on the integration branch. Track all issues raised by the code review as new tasks in the ExecPlan **frontier**, then fix them in a single **implementer subagent**. Repeat _code review → fix cycle_ until no issues remain for a maximum of three iterations. Report all unresolved issues.

For each repeat of the cycle, prefer reusing the code review and implementer subagents from the previous iteration when they match the final dispatchable route: the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`. Otherwise, dispatch a fresh agent.

## Gotchas

- Do not create worktrees anywhere within the main project directory because agents will automatically discover files like `AGENTS.md` causing context window bloat. Recommend creating them in `../<project name>.worktrees`.
