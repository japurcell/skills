---
name: execplan-implement
description: Implement an ExecPlan in code.
disable-model-invocation: true
---

You have been provided an ExecPlan. This plan should have tasks and milestones associated with it, describing how to implement the plan.

The goal is the entire plan implemented on a single **integration branch**, with every task and milestone resolved.

The tasks are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tasks which are ready to be grabbed.

**Subagent management rules:**

- Activate the `subagent-model-router` skill. Route each subtask to the most cost-efficient and capable model and reasoning effort for that subtask. Submit the exact routed model and reasoning effort through dispatch controls when dispatching a subagent. If the router does not return an exact model and reasoning effort or the host does not permit both to be specified, do not dispatch and report the issue. Never fall back to runtime defaults.
- Give every subagent a runtime limit. Treat runtime limits as warning thresholds; lateness alone does not justify interruption, cancellation, or replacement.
- **Implementer subagents** should be run in the background where possible for maximum concurrency.
- Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the plan, tasks, research notes, and previous commits. Don't duplicate information already available via pointers.
- Keep one persistent **integration coordinator** subagent across merge waves, progress updates, and final checks to reduce coordination overhead. The coordinator should also handle deterministic commits and status checks directly when safe.

All commits must follow [commit message guidelines](references/message.md).

## Steps

1. Activate the `exec-plans` skill, then read the plan, milestones, and tasks to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tasks - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory next to the plan, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. If current branch is `main` or `master`, create a new **integration branch**. Start the **integration coordinator** subagent.

4. Use **implementer subagents** to implement each task, each in its own worktree on its own branch. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - calls the Skill tool with `tdd` to build the task;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, have the same **integration coordinator** merge its work to the integration branch.

6. If this changes the **frontier** of available tasks, kick off more **implementer subagents** to work on the new tasks. This allows for maximum concurrency.

7. Once all tickets are complete, call the Skill tool with `code-review-biaxis` on the integration branch. Track all issues raised by the code review as new tasks in the ExecPlan **frontier**, then fix them in a single **implementer subagent**. Repeat _code review → fix cycle_ until no issues remain for a maximum of three iterations. Report all unresolved issues.

8. Ensure all tasks and milestones are resolved and report the integration branch.

9. Clean up all **implementer subagent** worktrees.
