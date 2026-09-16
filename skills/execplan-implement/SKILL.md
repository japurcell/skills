---
name: execplan-implement
description: Implement an ExecPlan in code.
disable-model-invocation: true
---

You have been provided an ExecPlan. This ExecPlan should have a milestone progress checklist section, describing how to implement the ExecPlan.

The goal is a set of commits which implement the entire ExecPlan on a single branch.

The progress checklist items are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of progress checklist items which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the ExecPlan, progress checklist items, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for **maximum concurrency**.

## Steps

1. Activate the `exec-plans` and `delegate-to-subagents` skills.

2. Read the ExecPlan and progress checklist items. Read enough to understand the task graph.

3. (optional) Use an **exploration subagent** to conduct any exploration required by the progress checklist items - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes beside the ExecPlan, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

4. If current branch is `main` or `master`, create a new **base topic branch**.

5. Use **implementer subagents** to implement each progress checklist item. Instruct each implementer subagent to:
   1. Activate the `tdd` skill.
   2. Work in its own worktree, on its own branch (see [Working with Worktrees](#working-with-worktrees)).
   3. Keep its branch private and unpushed because integration rebases it.

6. Integrate completed **implementer subagent** branches into the **base topic branch** one at a time:
   1. Confirm the implementer's worktree is clean, then rebase its branch onto the latest **base topic branch**.
   2. Resolve conflicts there and rerun the affected tests. For a conflict-prone rebase, stop the implementer and give a **merger subagent** exclusive ownership of the existing implementer's worktree before the rebase starts. The merger rebases the implementer branch and does not mutate the base branch.
   3. Update and commit any ExecPlan references to SHAs changed by the rebase, then confirm the implementer's worktree is clean.
   4. Confirm the base worktree is clean, then fast-forward the base branch with `git merge --ff-only <implementer-branch>`.
   5. Confirm the base branch tip matches the tested implementer branch tip.

   Serialize this integration sequence so concurrent completions cannot race to update the base branch.

7. If this changes the **frontier** of available progress checklist items, kick off more **implementer subagents** to work on the new progress checklist items. This allows for maximum concurrency.

8. Once all progress checklist items are complete, clean up all **implementer subagent** worktrees and report that **base topic branch** is ready for human review.

## Working with Worktrees

For parallel AI agent work, use git worktrees to run multiple branches simultaneously:

```bash
# Create a worktree for a feature branch
git worktree add ../project-feature-a feature/task-creation
git worktree add ../project-feature-b feature/user-settings

# Each worktree is a separate directory with its own branch
# Agents can work in parallel without interfering
ls ../
  project/              ← main branch
  project-feature-a/    ← task-creation branch
  project-feature-b/    ← user-settings branch

# After integration, clean up the worktree
git worktree remove ../project-feature-a
```

Benefits:
- Multiple agents can work on different features simultaneously
- No branch switching needed (each directory has its own branch)
- If one experiment fails, delete the worktree — nothing is lost
- Changes are isolated until explicitly fast-forwarded into the base branch
