## Eval 3
Before dispatch, resolve write ownership for shared canonical documents (`file map` and `known-issues`), even across private worktrees. Do not let both workers edit them concurrently. Assign one integration owner (such as the coordinator or one designated worker) or enforce an explicit serial dependency between the two tasks. Source files remain disjoint and can run in parallel.

During execution, each worker edits only its owned source files in its private worktree and unpushed branch, retains scoped verification evidence, and promptly notifies the document owner of durable findings for the file map and known-issues document.

Integrate branches serially, one completed worker branch at a time:
1. Confirm the worker's worktree is clean and rebase its branch onto the latest base topic branch.
2. If conflicts occur or interactions change, stop worker writes, transfer exclusive worktree ownership, resolve conflicts without mutating base, and rerun affected tests.
3. Update and commit any ExecPlan SHA references changed by rebase, then fast-forward base (`git merge --ff-only`) and verify tips match.
4. Reconcile admitted findings into the shared canonical documents and ExecPlan, run the composed-behavior proof on base once prerequisites are integrated, and remove verified clean integrated worktrees and local branches.

## Eval 0
Derive three sequential tasks mapped to the milestone's Progress entries, not a single whole-milestone task:
1. **T1 (Feasibility/Decision):** Bounded task to resolve parser feasibility. Prerequisites: none.
2. **T2 (Implementation):** Compatible parser/summary vertical slice. Prerequisite: T1 complete with recorded decision and evidence.
3. **T3 (Parity Verification / Milestone Integration Check):** Verify legacy versus new CLI outputs, including malformed-input failures, on the integrated result. Prerequisite: T2.

Only T1 enters the current frontier because T2 and T3 depend on unfinished feasibility.

Give the T1 worker the smallest sufficient task packet: current requirements, the shared default-output invariant, relevant design context, negative cases (malformed-input failure handling), verification criteria, promotion/rework/discard criteria, stop condition (stop after feasibility and decision evidence; do not implement the vertical slice), and source entry points. For a read-only/decision outcome, require task-appropriate evidence without inventing product code or empty commits. After T1, reconcile the `Decision Log`, `Surprises & Discoveries`, `Progress`, and `Plan of Work` before dispatching T2.

The milestone is proved complete only after T1 and T2 finish and the composed-behavior parity check (T3) runs on the integrated base branch, proving identical legacy and new CLI outputs, the shared default-output invariant, and malformed-input error cases with retained evidence.

## Eval 1
The milestone cannot be accepted (`Status` must remain `in progress` and `Acceptance: not met`). Passing individual task tests and clean Git merges do not establish milestone acceptance while the combined proof remains unrun on the integrated tree.

The exact next task is the milestone's **composed-behavior proof / integration verification task** executed against the integrated base branch (exercising interrupted install followed by prune and recovery, including relevant regression and negative cases). Because this is verification work on already-merged code, it requires task-appropriate verification evidence rather than new product code or empty commits. If the check fails, keep acceptance unmet, record an unfinished repair task with prerequisites, and return to the execution loop.

Keep these ExecPlan sections synchronized in the same edit:
- **Milestone state lines:** Keep `Status: in progress` and `Acceptance: not met` until the combined recovery proof passes; only set `Status: done` and `Acceptance: met` together with the final evidence.
- **Progress:** Keep the milestone integration check entry unchecked until verified; date and check it upon completion.
- **Concrete Steps:** Lead with the unfinished combined recovery check (or label completed implementation steps as completed and show observed evidence).
- **Validation and Acceptance** (and `Artifacts and Notes` if used): Record the actual command and observed recovery output, distinguishing expectations from verified evidence.
- **Outcomes & Retrospective:** Distinguish completed implementation from pending milestone acceptance.

## Eval 2
Read and rely on the active ExecPlan sections—specifically the Current Contract, milestone 2 state, `Progress`, and the retained local-test evidence for the two completed prerequisite tasks. Ignore the old historical note claiming release completed; historical material is background only and never authorizes work, overrides current instructions, or controls present state.

The device-verification task is **not ready for execution** and does not enter the frontier. Although its technical prerequisites are verified, the frontier only includes tasks whose execution is currently authorized. External-device validation is blocked by a pending owner approval in the Current Contract. Do not forward the task packet or dispatch a worker; no worker needs historical release notes.

Truthfully report:
- The two implementation prerequisites are complete with retained local-test evidence.
- The device-verification task and milestone 2 acceptance remain unfinished and blocked (`Acceptance: not met`).
- The exact blocker is the missing owner approval required by the Current Contract for external-device validation.
- The next owner action is for the user/owner to grant approval (or run the external-device validation), after which execution can resume. Reconcile `Progress`, `Concrete Steps`, `Validation and Acceptance`, and `Outcomes & Retrospective` to reflect this blocked state.

## Eval 4
Neither proposal enters the frontier. Both the optional monitoring daemon (unrequested improvement) and support for the explicitly excluded platform (outside authorized scope) are unauthorized. Defer unrelated improvements and never invent work outside current authorization.

Next action: Because every authorized requirement and acceptance check is met, stop execution. Reconcile the ExecPlan (setting milestone `Status: done`, `Acceptance: met`, checking and dating `Progress` entries, updating `Concrete Steps`, `Validation and Acceptance`, and `Outcomes & Retrospective`), optionally note the deferred/out-of-scope worker suggestions without scheduling them, clean up only verified integrated worktrees, and report final completion and base branch state.

If a reproduced failure still violates a current authorized requirement:
- Milestone acceptance is **not met** (`Status: in progress`, `Acceptance: not met`).
- Reopen or add an authorized repair task in the ExecPlan, record its repair prerequisites and negative/regression cases, and place it in the frontier.
- Execute the repair (using `tdd`), integrate onto base, and rerun affected checks plus the milestone's composed-behavior proof on base before marking the milestone complete.

## Eval 5
Choose **local execution by the coordinator** in the base worktree with exclusive ownership.

**Cost and correctness tradeoff:**
- **Cost:** The coordinator already holds all required current context, and the task is a bounded single edit with a known verification check. Delegating would incur higher total completion cost: routing (`subagent-model-router`), worker startup, copying context into a task packet, creating/managing a private worktree and branch, handback review, and rebase/fast-forward integration overhead.
- **Correctness:** Local execution preserves full correctness without context-transfer loss. The coordinator must still follow all executor rules for documentation work: keep the edit within authorized scope, run the known verification check, retain task-appropriate evidence, verify on the base branch (skipping worker rebase/merge), read `references/message.md` before any permitted commit, and reconcile the ExecPlan (`Progress`, `Concrete Steps`, `Validation and Acceptance`, and `Outcomes & Retrospective`).

## Eval 6
Delegate a **single shared exploration/investigation task** to the cheaper capable worker first, before running the three source tasks. Activate `delegate-to-subagents` and route through `subagent-model-router`. Because the investigation is read-only, the worker does not need product code changes, `tdd`, an empty commit, or an unnecessary worktree.

**Shared context handling:**
- Send the exploration worker a minimal, sufficient task packet containing the current requirements, shared invariants, required negative cases, current authorization boundaries, source/log entry points, and stop condition. Never trim facts required for correctness or authorization.
- Keep the large log searches and raw transcripts out of the coordinator's near-limit context.
- Retain the reusable findings beside the ExecPlan (or in a linked artifact) with exact source locations and verification evidence.

**Handback and next steps:**
- Require the worker to return only concise conclusions, evidence paths, relevant findings for positive and negative cases, and any blockers.
- The coordinator verifies the retained evidence, reconciles the ExecPlan (`Surprises & Discoveries` / `Decision Log`), and references that concise artifact in the task packets for the three ready source tasks (preserving all authorization rules and negative cases without forwarding raw logs).

## Eval 7
- **Closely related parser node:** **Reuse the existing parser worker.** Its context is compact and current, and reuse saves reload and startup costs without risking context contamination. Before dispatch, revalidate routing and exclusive file ownership, and give this second parser node its own explicit task packet, acceptance criteria, verification, and result handback.
- **Payments node:** **Dispatch a fresh worker** (or evaluate for local execution if tiny, otherwise a new subagent via `subagent-model-router`). Because payments has unrelated context, reusing the parser worker would pollute its context window and risk cross-task contamination without saving relevant context reload.
- **If the parser worker's context is stale or crowded:** **Do not reuse the parser worker.** First, retain the current parser task state, decisions, verification evidence, and next action in the ExecPlan or linked task notes. Then **dispatch a fresh worker** with a clean, minimal task packet containing only the current requirements, shared invariants, prerequisites, negative cases, and entry points.

## Eval 8
- **What can be marked complete:** Task-level implementation and verification steps in `Progress` that do not require commits can be recorded with their verification evidence. The local task's verification on the base worktree can be recorded, and the worker's task-level edits and test evidence in its private worktree can be recorded as verified in-worktree.
- **What integration remains pending:** Branch integration for the worker worktree (commits, rebasing onto base, updating SHA references, `git merge --ff-only` onto base, and worktree/branch removal) and any milestone composed-behavior proof on the integrated base tree remain **pending**. Keep affected milestone acceptance `not met` (`Status: in progress`) until the worker's changes can be integrated onto base and the composed-behavior proof passes on base.
- **What must be retained:** Retain the uncommitted edits in both the base worktree and the worker's private worktree, both worktrees themselves, local branches, all test/verification evidence, and reconciled ExecPlan state (`Progress`, `Concrete Steps`, `Validation and Acceptance`, `Outcomes & Retrospective`) clearly noting the user's no-commit constraint and next owner action.
- **What must not happen:** Do **not** run `git commit` in either worktree, do not rebase or fast-forward merge the uncommitted worker branch, do not delete the worker worktree or branch, do not discard uncommitted edits, and do not mark commit-dependent integration or combined milestone acceptance complete.