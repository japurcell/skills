---
name: execplan-implement
description: ExecPlan implementation workflow. Use when implementing ExecPlans and you are the parent agent. Do not use if you are a subagent being delegated to.
compatibility: Requires background subagent dispatch with follow-up messaging and Git worktrees.
---

This workflow applies when the parent implements an ExecPlan, whether supplied by the user, created during the session, or resumed from earlier work. This plan should have tasks and milestones associated with it, describing how to implement the plan.

The goal is the entire plan implemented on a single **integration branch**, with every task and milestone resolved.

The tasks are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tasks which are ready to be grabbed.

**Subagent management rules:**

- For every subagent dispatch, use the `subagent-model-router` skill to obtain its final dispatchable route, and apply its model and effort policy through dispatch controls. Stop on a named blocker.
- **Implementer subagents** should be run in the background where possible for maximum concurrency.
- Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the plan, tasks, research notes, and previous commits. Don't duplicate information already available via pointers.
- Delegate integration to one persistent **integration coordinator** subagent in background mode. Before relying on it, obtain its agent ID, send a bounded follow-up readiness request, and observe its acknowledgment. Record the verified follow-up handle. A launch response alone does not prove follow-up delivery.
- Reuse the **integration coordinator** across merge waves, progress updates, and final checks. Give it bounded assignments; leave it idle between waves instead of assigning an indefinite wait. It should handle deterministic commits and status checks directly when safe.

[Enforce limits](#runtime-enforcement) for exploration, implementation, review, and fixes. An agent is idle only with no outstanding assignment; dependency waits remain active.

Before every commit, the commit creator must activate the `commit` skill and follow its message validation workflow.

## Pre-dispatch gate

Before launching an agent or assigning new work to an existing agent, run the router CLI and record its invocation, returned route, and intended dispatch arguments in the assignment's coordination record.

Loading `subagent-model-router` does not complete routing. Proceed only when the record establishes a dispatchable route and the intended arguments match its model and effort policy. If permissions or host restrictions prevent applying the route, report the named blocker instead of silently substituting runtime defaults.

Automatically apply the router's final dispatchable model and effort policy, including verified fallbacks. Do not request separate user confirmation for routine routing choices. Preserve explicit user constraints and required host approval flows.

After dispatch, record the actual arguments and returned agent ID. A successful launch does not replace the required routing evidence.

## Runtime enforcement

1. **Record each background assignment you dispatch**, including reuse. Before dispatch, set a deadline based on expected effort and complexity. Record the routed model and its exact explicit effort or host-default omission. Track task and agent IDs, start time, extension count (initially zero), and enforcement handle as available.
2. **Arm enforcement before waiting.** Use a host timeout or parent-owned scheduler bounded by the nearest assignment or checkpoint deadline. Independently time out blocking operations. Recheck deadlines whenever control returns, including after user interruptions.
3. **At expiry**, request status, completed work, blockers, and updated ETA by a bounded checkpoint deadline. Keep overdue work under a deadline. On timely status, confirm completion, stop the worker, or grant its only ETA-based extension. If extended, record the new deadline, increment the count, and re-arm enforcement. Preserve the count across follow-ups. Stop the worker on a missed checkpoint or expired extension.
4. **Before transferring ownership**, confirm the worker and its write-producing operations have stopped, then route and dispatch a fresh replacement. If shutdown is unconfirmed, report the blocker and continue independent work. Cancel enforcement on completion.

## Steps

1. Activate the `exec-plans` skill, then read the plan, milestones, and tasks to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tasks - relevant codebase files or external documentation. Brief it with the needed context, acceptance criteria, and known negative cases, using context pointers where those facts are already available. Ensure the exploration subagent can save files - it should save its markdown notes in a directory next to the plan, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. If current branch is `main` or `master`, create a new **integration branch**. Start the background **integration coordinator** and verify follow-up messaging as above. Instruct it to activate the `exec-plans` skill and reconcile its required plan sections before reporting a checkpoint complete.

4. Use **implementer subagents** to implement each task, each in its own worktree on its own branch. Follow the router’s final dispatchable route and runtime enforcement above. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, have the same **integration coordinator subagent** merge its work to the integration branch.

6. If this changes the **frontier** of available tasks, kick off more **implementer subagents** to work on the new tasks. This allows for maximum concurrency.

7. Once all tickets are complete, follow the [code review fix cycle](#code-review-fix-cycle).

8. Ensure all tasks and milestones are resolved and report the integration branch.

9. Clean up all **implementer subagent** worktrees and their related branches.

## Code review fix cycle

Call the Skill tool with `code-review-biaxis` on the integration branch. Track all issues raised by the code review as new tasks in the ExecPlan **frontier**, then fix them in a single **implementer subagent**. Repeat _code review → fix cycle_ until no issues remain for a maximum of three iterations. Report all unresolved issues.

For each repeat of the cycle, prefer reusing the code review and implementer subagents from the previous iteration when they match the final dispatchable route: the same model with no original effort override for `host_default`, or the exact model/effort pair for `explicit`. Otherwise, dispatch a fresh agent. Keep the two review axes independent.

## Gotchas

- Do not create worktrees anywhere within the main project directory because agents will automatically discover files like `AGENTS.md` causing context window bloat. Recommend creating them in `../<project name>.worktrees`.
- Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.
