## Eval 3
Before dispatch, apply `delegate-to-subagents` ownership rules to the canonical file map and known-issues document, even across private worktrees. Serialize edits to shared canonical documents by assigning one integration owner (such as the coordinator) or an explicit serial dependency. Do not allow both workers to edit shared canonical docs concurrently.

Give each subtask an identifier, objective, context, constraints, deliverable, verification criteria, allowed resources, disjoint source write ownership, dependencies, and runtime limit. Each worker operates in its own private worktree and branch, retains scoped evidence for its findings, and promptly notifies the owner of durable findings for the canonical docs.

Integrate completed branches into the base topic branch one at a time (serialized):
1. Confirm the implementer worktree is clean and rebase its branch onto the latest base topic branch.
2. Resolve any conflicts (using a merger subagent with exclusive ownership of the implementer worktree if conflict-prone) and run affected checks covering the resulting tree and interactions.
3. Update and commit any ExecPlan SHA references changed by the rebase.
4. Confirm the base worktree is clean, fast-forward base (`git merge --ff-only`), verify the base tip matches, and remove the integrated worktree and branch.
5. Reconcile admitted canonical-doc findings in the designated owner pass and run the milestone composed-behavior proof on base.

## Eval 0
Derive three distinct tasks in the task graph with explicit prerequisites rather than inferring order from the checklist:
1. **T1 (Feasibility/decision task):** Resolve parser feasibility first. Prerequisites: none.
2. **T2 (Implementation task):** Implement the compatible parser/summary vertical slice. Prerequisite: T1 complete with recorded evidence.
3. **T3 (Parity/milestone integration task):** Verify legacy versus new CLI outputs, including malformed-input failures and the shared default-output invariant. Prerequisite: T2 integrated on base.

Only T1 is in the current frontier. Assign T1 to a fresh subagent with its full task and current plan context, the shared default-output invariant, required inputs, explicit file ownership, verification criteria, and stopping boundary (stop after feasibility evidence is recorded; do not start T2). Instruct it to use task-appropriate feasibility evidence rather than inventing product code or empty commits, or if prototyping in a worktree, state promotion/discard criteria and follow commit message guidelines.

Milestone acceptance is proven only after T1 and T2 are completed, integrated onto the base branch, and the composed-behavior parity check (T3) runs against the integrated base tree—verifying matching legacy and new CLI stdout, stderr, exit codes, malformed-input negative cases, and the default-output invariant—with actual evidence recorded and `Status: done`, `Acceptance: met`, and Progress updated together.

## Eval 1
The milestone **cannot** be accepted (`Status` remains `in progress`/`open` and `Acceptance: not met`). Passing individual task tests and clean Git merges do not establish milestone acceptance while the composed-behavior proof on the integrated base tree is unrun.

The exact next task is a **milestone integration / verification task** (composed-behavior proof) executed on the base topic branch—either run directly by the coordinator or delegated as the named integration task to a fresh subagent. It must exercise an interrupted install followed by prune and recovery against the integrated base tree, including relevant regression and negative cases, and retain concise evidence of the actual result. If the check fails, keep milestone acceptance unmet, record a repair task in the ExecPlan with prerequisites, and delegate the repair through Step 5.

Reconcile and keep these ExecPlan sections synchronized in the same edit:
- **Milestone state lines** (`Status: done | in progress | open` and `Acceptance: met | not met`)
- **Progress** (the milestone-tagged checklist entry for the combined recovery proof, dated when verified)
- **Concrete Steps** (lead with the next unfinished action or label completed steps)
- **Validation and Acceptance** (record actual integrated test evidence vs expectations)
- **Outcomes & Retrospective** (distinguish completed implementation from pending/completed acceptance)
- **Surprises & Discoveries** and **Decision Log** (if integration reveals findings or scope/repair decisions).

## Eval 2
Read and reconcile the active ExecPlan (`Current Contract`, milestone state, `Progress`, `Validation and Acceptance`, `Concrete Steps`, `Decision Log`, and `Outcomes & Retrospective`) alongside the retained local-test evidence from the two implementation prerequisites. Ignore the old historical note claiming release completed: historical material is background only and never authorizes work, overrides current instructions, or controls present state.

The device-verification task is **not ready for execution** and does not enter the execution frontier. Although its prerequisites have retained evidence, a ready task requires current authorization, and the active `Current Contract` explicitly requires owner approval for external-device validation, which is still pending. Honor required approvals and owner-only actions. Do not dispatch the verification subagent or invent substitute work.

If other independent, authorized tasks exist in the frontier, continue them; otherwise pause and reconcile the plan. Report truthfully:
1. The two implementation tasks are complete and integrated on the base branch with retained local-test evidence (including actual base branch state).
2. Milestone 2 acceptance remains **not met** (`Status: in progress`, `Acceptance: not met`) because external-device verification has not run.
3. The exact blocker and next owner action: owner approval is required to authorize external-device validation before the verification task can be dispatched.

## Eval 4
Neither proposal enters the execution frontier. Under Step 5, add or reopen a task only to satisfy an authorized requirement or repair a reproduced failure within authorized scope. Record the optional monitoring daemon as a deferred improvement outside the execution frontier. Reject or record the excluded platform proposal as out of scope per the active plan's constraints. Since every authorized requirement and acceptance check is met, do not dispatch new implementer subagents; proceed to Step 8 to reconcile the ExecPlan (`Status: done`, `Acceptance: met`, checked `Progress` entries, `Outcomes & Retrospective`) and report completion along with the base branch's actual state.

**If a reproduced failure violates a current authorized requirement:**
The milestone acceptance is **not met** (keep or revert milestone `Acceptance: not met` and `Status: in progress`). Add or reopen a repair task in the ExecPlan with explicit prerequisites and failure evidence, update `Progress`, `Concrete Steps`, and `Validation and Acceptance`, and place the repair task into the execution frontier. Delegate the repair through Step 5 (either reusing the original node's implementer subagent if it belongs to that node, or a fresh implementer subagent in its own worktree), then re-integrate and rerun the affected tests and composed-behavior proof on the base branch before finishing.

## Eval 5
Under `delegate-to-subagents`, delegation is justified only when parallel execution, specialized expertise, or context isolation outweighs coordination overhead. However, `execplan-implement` Step 5 states that the primary agent coordinates the loop while subagents perform implementation, and assigns each ready task to a fresh subagent (instructing it to use task-appropriate evidence for documentation work and follow commit message guidelines in its own worktree/branch).

**Tradeoff and Decision:**
- **Cost tradeoff:** Executing a one-line/small documentation edit directly in the coordinator is much cheaper in tokens and latency because the coordinator already holds all required context, avoiding `subagent-model-router` routing, worktree creation, context copying, subagent startup, and rebase/fast-forward integration.
- **Strict workflow vs efficiency:** If strictly bound by `execplan-implement` Step 5 ("You - the primary agent - coordinate this loop; subagents perform implementation. Assign each distinct task to a fresh implementer subagent"), dispatch a single low-cost routed subagent with explicit file ownership for the doc file and the known check. If applying `delegate-to-subagents` threshold rules to coordinator-owned plan/doc reconciliation, the coordinator should execute the small doc edit and known check directly on the base branch because coordination overhead exceeds task cost and no context isolation or independent review is needed.

## Eval 6
Dispatch **one exploration subagent** first (per `execplan-implement` Step 3 and `delegate-to-subagents` Section 1: "consider one exploration worker when several workers need the same context"), routed via `subagent-model-router` to the cheaper capable model.

**Execution and Shared Context Handling:**
1. **Exploration phase:** Give the exploration subagent the bounded log-investigation objective, current authorization boundaries, required negative cases, runtime limit, and write permission to save its concise markdown notes beside the ExecPlan so all future implementer subagents can access them without bloating the coordinator's near-limit context.
2. **Handback:** The exploration subagent returns a concise conclusion and retained evidence reference to the coordinator and writes the shared markdown artifact beside the ExecPlan. The coordinator reconciles the ExecPlan if needed without reading the raw large logs.
3. **Implementation fan-out:** Once the shared exploration artifact is saved, dispatch **three fresh, independent implementer subagents** in parallel (one per ready source task), each in its own git worktree and private branch. Pass each implementer its full task context, the path/content of the exploration notes, prerequisite evidence, explicit file ownership, `tdd` activation instruction, and commit message guidelines, preserving all current authorization limits and required negative test cases. Serialize any shared files and integrate completed branches one at a time into the base topic branch.

## Eval 7
Under `execplan-implement` Step 5: **"Assign each distinct task to a fresh implementer subagent. Do not reuse an implementer for a different node, even with a new worktree. Reuse is allowed only for repairs or follow-up work on that implementer's original node. This preserves context isolation, ownership clarity, and independent task results."**

1. **Closely related ready parser node:** Assign to a **fresh implementer subagent** in its own worktree and branch. Even though the existing parser worker has compact, current context and reuse appears cheaper, `execplan-implement` explicitly prohibits reusing an implementer for a different task node. Pass the required context and prerequisite evidence from the completed parser node (after integrating or recording its evidence) into the fresh parser implementer's prompt. *(Reuse of the first parser worker is permitted only if the work is a repair or direct follow-up on that worker's original parser node.)*
2. **Ready payments node:** Assign to a **fresh implementer subagent** in its own worktree and branch (can run in parallel with the new parser subagent if file ownership and state are disjoint).
3. **If the parser context is stale or crowded:** The rule is unchanged—never reuse an implementer for a new node, and even for a same-node repair, if the worker's context is stale, crowded, or failed/terminated, retain its findings/artifacts and dispatch a fresh replacement implementer with clean, reconciled ExecPlan context.

## Eval 8
Honor the user's explicit constraint ("do not commit yet") as a current authorization boundary in the active ExecPlan (`exec-plans`: honor explicit stopping points and user instructions; `execplan-implement`: execute only authorized work).

1. **What can be marked complete:** Nothing requiring a committed/integrated implementation deliverable can be marked milestone-accepted or fully integrated. Record in the ExecPlan that local edits and verification checks were run and passed in the worker worktree (updating `Surprises & Discoveries`, `Validation and Acceptance`, or partial `Progress` notes by splitting the entry into completed local verification and remaining commit/integration steps), while keeping the task/milestone uncommitted and `Acceptance: not met`.
2. **What integration remains pending:** Committing the worker's changes using `references/message.md`, confirming a clean worktree, rebasing onto the base topic branch, updating any SHA references, fast-forwarding the base topic branch (`git merge --ff-only`), running the composed-behavior proof on base, and cleaning up the worktree/branch.
3. **What must be retained:** Preserve the worker's dirty worktree, uncommitted edits, branch, and verification evidence intact (`Step 8`: "Preserve unfinished work and evidence; clean up only verified clean integrated worktrees").
4. **What must not happen:** Do not run `git commit`, do not rebase or fast-forward merge into the base branch, do not delete the worker worktree or branch, and do not mark the milestone `Status: done` or `Acceptance: met`. Reconcile the plan and report the blocker (awaiting user authorization to commit).