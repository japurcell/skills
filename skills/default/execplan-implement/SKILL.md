---
name: execplan-implement
description: Implement an ExecPlan in code.
disable-model-invocation: true
---

You have been provided an ExecPlan with milestone acceptance and a Progress checklist.

The goal is to implement and verify the authorized ExecPlan work on one branch, with commits for implementation changes and evidence for milestone acceptance.

Before creating any commit, read and follow [commit message guidelines](references/message.md). Apply them to every commit created by the primary agent or a subagent.

The **frontier** of the plan's task graph contains unfinished tasks whose prerequisites are verified and whose execution is authorized. If none are ready, report the blockers and next owner action instead of inventing work.

Run independent **implementer subagents** concurrently when useful. Serialize shared files, shared state, and integration.

## Steps

1. Activate the `exec-plans` and `delegate-to-subagents` skills.

2. Read and reconcile the ExecPlan using `exec-plans`, then select the frontier.

3. (optional) Use an **exploration subagent** to conduct any exploration required by the progress checklist items - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes beside the ExecPlan, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

4. If current branch is `main` or `master`, create a new **base topic branch**.

5. Repeat steps 5-7 while authorized tasks are ready. You - the primary agent - coordinate this loop; subagents perform implementation. When integration or validation reveals additional work, record it in the ExecPlan by reopening an existing task or adding a bounded one with prerequisites, then delegate it through this step.

   Assign each distinct task to a fresh implementer subagent. Do not reuse an implementer for a different node, even with a new worktree. Reuse is allowed only for repairs or follow-up work on that implementer's original node. This preserves context isolation, ownership clarity, and independent task results.

   Pass each implementer its full task and current plan context as required by `exec-plans`, plus prerequisite evidence and explicit file ownership. Instruct it to:
   1. Activate the `tdd` skill for source changes. Use task-appropriate evidence for decision, verification, integration, or documentation work; do not invent product tests or code changes for a read-only outcome.
   2. Make repository changes in its own worktree and branch (see [Working with Worktrees](#working-with-worktrees)). A read-only task needs a retained evidence result, not an empty commit.
   3. Follow [commit message guidelines](references/message.md).
   4. Keep its branch private and unpushed because integration rebases it.

6. Integrate completed **implementer subagent** branches into the **base topic branch** one at a time:
   1. Confirm the implementer's worktree is clean, then rebase its branch onto the latest **base topic branch**.
   2. If there are conflicts, resolve them and rerun the affected tests. For a conflict-prone rebase, stop the implementer and give a **merger subagent** exclusive ownership of the existing implementer's worktree before the rebase starts. The merger rebases the implementer branch and does not mutate the base branch. A conflict-free rebase does not waive required integration checks: reuse evidence only when it covers the resulting tree and relevant interactions; otherwise run the affected checks.
      If affected tests fail, pause integration of that branch. Record the required repair as unfinished work in the ExecPlan and delegate it to an **implementer subagent** through step 5. Resume integration after the repair passes the affected tests.
   3. Update and commit any ExecPlan references to SHAs changed by the rebase, then confirm the implementer's worktree is clean.
   4. Confirm the base worktree is clean, then fast-forward the base branch with `git merge --ff-only <implementer-branch>`.
   5. Confirm the base branch tip matches the verified implementer branch tip. Once related prerequisites are integrated, execute the plan's composed-behavior proof on base, or delegate it as the named integration task. If it fails or remains unrun, keep milestone acceptance unmet and record the repair or blocker.
   6. After each fast-forward, remove clean worktrees and local branches for the integrated node, including superseded repair/merger branches once their changes are verified on base. Preserve base and unrelated worktrees.

   Serialize this integration sequence so concurrent completions cannot race to update the base branch.

7. After each task result or integration, reconcile the plan using `exec-plans`; verify retained evidence for read-only tasks before marking them complete. Reassess the **frontier**, including repairs, and return to step 5 for ready items. Independent authorized work may continue while repairs or owner actions are pending.

8. When authorized work is complete or blocked, reconcile and report the plan using `exec-plans`, including the base branch's actual state. Preserve unfinished work and evidence; clean up only verified clean integrated worktrees.

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

# After integration, clean up the worktree and it's associated branch
git worktree remove ../project-feature-a
git branch -d feature/task-creation
git worktree remove ../project-feature-b
git branch -d feature/user-settings
```

Benefits:

- Multiple agents can work on different features simultaneously
- No branch switching needed (each directory has its own branch)
- Preserve unfinished changes and evidence before removing an experimental worktree
- Changes are isolated until explicitly fast-forwarded into the base branch
