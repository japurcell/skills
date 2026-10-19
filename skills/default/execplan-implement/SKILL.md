---
name: execplan-implement
description: Implement an ExecPlan in code.
disable-model-invocation: true
---

Implement authorized ExecPlan tasks on one base branch, retaining verification evidence and committing implementation changes when permitted.

Honor user restrictions on commits and branches. Before any permitted commit, every author must read [commit message guidelines](references/message.md).

The **frontier** of the plan's task graph contains unfinished tasks whose prerequisites are verified and whose execution is authorized. If none are ready, report the blockers and next owner action instead of inventing work.

## Steps

1. Activate the `exec-plans` skill for task boundaries, prerequisites, context, reconciliation, and acceptance. Read and reconcile the plan; select the frontier.

2. Choose local execution or delegation for each ready task using [Execution cost and context](#execution-cost-and-context). Share exploration only when several tasks need it; retain reusable findings beside the ExecPlan with source and verification evidence.

3. If current branch is `main` or `master`, create a new **base topic branch**.

4. Execute ready tasks locally or through implementers. Add or reopen tasks only for authorized requirements or reproduced in-scope failures; record repair prerequisites. Defer unrelated improvements. Finish when authorized acceptance is met.

   Before delegating, activate the `delegate-to-subagents` skill for routing, ownership, dispatch, and monitoring. Give shared canonical documents one integration owner or serial dependency, including across private worktrees. Run independent tasks concurrently when cost-effective; serialize shared files, state, and integration.

   Give workers explicit file ownership and the task packet below. All executors must:
   1. Activate the `tdd` skill for source changes. Use task-appropriate evidence for decision, verification, integration, or documentation work; do not invent product tests or code changes for a read-only outcome.
   2. Delegated edits use a private worktree and unpushed branch because integration rebases it. Local edits may use the base worktree with exclusive ownership. Read-only tasks retain evidence without an empty commit or unnecessary worktree.
   3. If commits are prohibited, retain changes and evidence; report commit-dependent integration as pending.

5. Before integrating a worker branch, read and follow [branch integration](references/integration.md). Local changes skip rebase/merge, but require verification and the plan's composed-behavior proof on base. Keep acceptance unmet when that proof fails or remains unrun.

6. After each result or integration, verify evidence and reconcile the plan. Return to step 2 for ready tasks, including repairs. Continue independent authorized work while blockers remain.

7. After all active tasks finish, coordinate one final documentation pass across their findings. When complete or blocked, reconcile and report the plan and actual base state, including owner actions. Preserve unfinished work and evidence; remove only verified clean integrated worktrees.

## Execution cost and context

Minimize expected completion cost without reducing correctness: context loading, repeated turns, startup, routing, tools, handback review, integration, verification, and retries. Model price or parallelism alone does not establish savings. Use measured usage when available; otherwise state material assumptions briefly.

- Work locally when the coordinator already has the needed context and a bounded task costs less than dispatch and review.
- Delegate when a cheaper capable worker, independent exploration, or context isolation is likely to save more than its overhead. Keep large searches and transcripts out of the coordinator's context; request conclusions, evidence paths, test results, and blockers.
- Send the smallest sufficient task packet: current requirements, relevant design and shared invariants, prerequisites, negative cases, acceptance, stop condition, and source entry points. Reference bulky evidence; do not forward whole conversations or unrelated plan history. Never trim information required for correctness or authorization.
- Prefer a fresh worker for unrelated tasks or stale, crowded context. Reuse a worker for same-task repairs or closely related nodes only when useful context outweighs contamination and reload costs. Revalidate routing and ownership, and give each node its own acceptance and result.
- Before compaction or worker replacement, retain current task state, decisions, evidence, and next action in the plan or linked task notes. Reuse valid evidence; recheck changed inputs and integrated interactions.
