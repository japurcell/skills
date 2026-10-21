## Eval 3
Before dispatch, assign each task explicit disjoint source write ownership, private worktree, and unpushed branch (`git worktree add -b <worker-branch> <path> <base-branch>`). Shared canonical documents (file map and known-issues document) cannot have concurrent writers, even across private worktrees. Give each shared canonical document one integration owner (such as the coordinator) or an explicit serial dependency between tasks. Exclusive area documentation stays worker-owned.

During execution, workers retain scoped evidence and promptly notify the integration owner of durable findings and critical guidance instead of concurrently editing shared canonical docs.

Integrate one completed worker branch at a time (`references/integration.md`):
1. Confirm worker worktree is clean, stop worker writes, and rebase its branch onto latest base topic branch.
2. Resolve conflicts and rerun affected tests if interactions or tree changed.
3. Update and commit any ExecPlan SHA references changed by rebase; confirm clean worker worktree.
4. Confirm clean base worktree, then run `git merge --ff-only <worker-branch>` and verify base tip matches worker tip.
5. Run composed-behavior proof on base once related prerequisites integrate.
6. Remove verified clean worker worktree (`git worktree remove`) and branch (`git branch -d`).
7. Reconcile admitted findings and complete one final documentation pass after all active tasks finish.

## Eval 0
Derive three distinct tasks mapped to the Progress entries, not one whole-milestone task:
1. Bounded feasibility/decision task for parser unknown (no prerequisites; in-progress frontier).
2. Implementation task for compatible parser/summary vertical slice (prerequisite: feasibility task complete with recorded decision/evidence).
3. Milestone integration/parity verification task comparing legacy and new CLI outputs on the integrated result (prerequisite: implementation task complete).

Only the feasibility task is on the frontier now. Resolve design uncertainty before dependent implementation.

Send the first worker the smallest sufficient task packet:
- Current requirements, shared default-output invariant, and negative cases (malformed-input failures).
- Relevant design context, source entry points, and allowed resources/ownership.
- Deliverable, verification commands/criteria, promotion/rework/discard criteria, and explicit stop boundary (stop after feasibility resolves; do not implement the vertical slice).
- Instruction to use task-appropriate evidence for decision/feasibility work without inventing product tests or code changes if the outcome is read-only.

Milestone acceptance is proven only after the feasibility and vertical-slice tasks complete, changes integrate on base, and the composed-behavior parity check runs on the integrated tree—exercising legacy and new paths on identical valid and malformed-input fixtures—and passes while preserving the shared default-output invariant. Update `Status: done`, `Acceptance: met`, and all `[milestone-X]` Progress entries together with recorded evidence.

## Eval 1
The milestone cannot be accepted. Keep `Acceptance: not met` (and `Status` not `done`). Passing individual task tests and clean Git merges do not establish milestone acceptance while the plan's composed-behavior proof on the integrated base tree remains unrun.

The exact next task is the named milestone integration / composed-behavior verification task on the integrated base branch (exercising interrupted install followed by prune and recovery, plus relevant regression and negative cases, locally on base or delegated as the named integration task). Because it is verification-only, it must produce task-appropriate verification evidence without inventing product code changes or empty commits.

When reconciling and after running the check, keep these ExecPlan sections synchronized in the same edit:
- Milestone state lines (`Status: in progress | done` and `Acceptance: not met | met`).
- `Progress` (keep the combined-proof `[milestone-X]` entry unchecked until verified; date and check it only with actual evidence).
- `Concrete Steps` (lead with the unfinished integration check now; mark completed after it runs).
- `Validation and Acceptance` (distinguish expected results from actual observed evidence on base).
- `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` (distinguish completed implementation from pending milestone acceptance, or record repair tasks if the check fails).

## Eval 2
Read the active ExecPlan's current sections (`Current Contract`, milestone states, `Progress`, `Concrete Steps`, `Validation and Acceptance`, `Decision Log`, `Outcomes & Retrospective`) and retained prerequisite local-test evidence. Ignore the historical note: historical material is background only and never authorizes work, overrides current instructions, or controls present state. Active contract rules and pending owner approvals govern.

Do not forward anything yet because the device-verification task is not ready for execution. Although its two implementation prerequisites have verified evidence, a frontier task requires both verified prerequisites and current authorization. The active contract requires owner approval for external-device validation, and that approval is still pending. Honor explicit stopping points and owner-only actions.

If another task or future dispatch needs context, forward only the smallest sufficient task packet from active sections (current requirements, shared invariants, verified prerequisite evidence paths, negative cases, acceptance, stop condition, and active authorization limits)—never superseded historical claims.

Truthfully report:
- Both implementation prerequisites are complete with retained local-test evidence.
- Milestone 2 acceptance remains `not met` because external-device verification has not run.
- Execution of the device-verification task is blocked on required owner approval per the Current Contract (next owner action: grant approval or run external-device validation).

## Eval 4
Neither proposal enters the frontier. The optional monitoring daemon is an unauthorized, unrelated improvement and must be deferred. Support for the explicitly excluded platform violates current scope and authorization boundaries and must be rejected. Because every authorized requirement and acceptance check is already met, the frontier is empty. Do not add or reopen tasks. Complete the final documentation pass if needed, reconcile the ExecPlan (`Status: done`, `Acceptance: met`, updated `Progress` and `Outcomes & Retrospective`), clean up only verified integrated worktrees, and report final plan and base state.

If a reproduced failure still violates a current authorized requirement:
- Keep the affected milestone `Acceptance: not met` (and `Status: in progress`).
- Reopen the affected task or add a bounded repair task to the plan with explicit repair prerequisites, negative/reproducer cases, and verification criteria.
- Record the reproducer failure evidence in the plan (`Progress`, `Surprises & Discoveries`, `Validation and Acceptance`, `Concrete Steps`).
- That repair task enters the frontier as ready, authorized work; return to Step 2 to choose local or delegated execution, fix and verify the failure (reproducer fails before, passes after), and rerun the composed-behavior proof on base before marking acceptance met.

## Eval 5
Choose local execution by the coordinator in the base worktree with exclusive file ownership.

Cost and correctness tradeoff:
- Expected completion cost must be minimized without reducing correctness across context loading, startup, routing, tool calls, handback review, integration, and verification.
- The coordinator already holds all required current context, and the task is a bounded single edit with a known verification check. Executing locally avoids copying context into a task packet, running `subagent-model-router`, creating/rebasing/removing a private worktree, and reviewing a worker handback—all of which cost more than doing the edit and check directly.
- Correctness is fully preserved: no independent review or context isolation is required, the coordinator applies the exact current contract directly without handoff loss, uses task-appropriate documentation verification evidence (without inventing product tests), skips unnecessary worktree rebase/merge, and verifies on the base branch before reconciling the ExecPlan.

## Eval 6
Delegate one shared, read-only exploration/investigation task to the cheaper capable worker first, then execute the three source tasks after its findings return.

Why and how:
- Under the execution cost and context rules, share exploration when several tasks need the same context, and delegate when a cheaper capable worker and context isolation save more than dispatch overhead. Keeping the large log investigation out of the coordinator's nearly full context avoids repeated reads and context compaction/overflow.
- Activate `delegate-to-subagents` and route via `subagent-model-router`.
- Because the investigation is read-only, the worker does not need a private worktree, branch, or product code/test changes, and must not create an empty commit.
- Send the smallest sufficient task packet: bounded investigation objective, log/source entry points, current authorization boundaries, shared invariants, required negative cases, deliverable format, verification criteria, and stop condition. Never trim facts required for correctness or authorization.

Handback and shared context handling:
- Request only concise conclusions, exact source/log evidence paths, relevant negative-case findings, and blockers—no raw large logs or full transcripts.
- Retain the reusable findings beside the ExecPlan (or linked task notes) with source and verification evidence, reconcile the plan, and reference or include those verified findings in the task packets for the three ready source tasks.

## Eval 7
Reuse the existing parser worker for the closely related ready parser node, and dispatch a fresh worker for the unrelated payments node.

Parser node (compact, current context):
- Under the execution cost rules, reuse a worker for closely related nodes when retained useful context outweighs contamination and reload costs.
- Before dispatch, revalidate routing (`subagent-model-router`) and explicit file/worktree ownership, and give the second parser node its own explicit task packet, requirements, negative cases, acceptance criteria, stop boundary, and separate result/verification evidence. Integrate one completed branch at a time.

Payments node (unrelated context):
- Use a fresh worker with its own routed model/effort, isolated private worktree/branch, and minimal sufficient task packet. Reusing the parser worker would carry irrelevant parser context and risk cross-task contamination without saving reload cost.

If the parser worker's context is stale or crowded:
- Do not reuse that worker. Before replacing or compacting, retain the completed parser node's state, decisions, verification evidence, and next action in the ExecPlan or linked task notes.
- Dispatch a fresh worker for the second parser node using a clean task packet that references the retained evidence and current contract.

## Eval 8
Honor the user's commit prohibition strictly.

What can be marked complete:
- The local task's implementation and verification Progress entries (and the worker task's implementation/test verification steps, if verified) can be recorded as verified in the plan using their uncommitted diff and test output as evidence.
- However, any commit-dependent branch integration (`git merge --ff-only` onto base) and any milestone acceptance that depends on integrating the worker branch onto base must remain pending (`Acceptance: not met`).

What integration remains pending:
- Rebasing the worker branch onto base, updating/committing rebased SHA references, fast-forwarding base (`git merge --ff-only`), running the composed-behavior proof on the integrated base tree, and cleaning up the worker worktree/branch all depend on commits and must be reported as pending owner commit authorization.

What must be retained:
- All uncommitted changes in the base worktree and the worker's private worktree.
- The worker's private worktree and local branch.
- Verification evidence (test results, diffs, commands) and reconciled ExecPlan state recording that commit-dependent integration is blocked by the user's no-commit instruction.

What must not happen:
- Do not run `git commit` in base or worker worktrees.
- Do not rebase or fast-forward merge uncommitted worker work, and do not delete the worker worktree or branch.