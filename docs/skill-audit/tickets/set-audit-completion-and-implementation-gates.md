# Set Audit Completion and Implementation Gates

**Type:** grilling
**Status:** closed
**Blocked By:** set-adoption-rules-and-protected-behavior.md, choose-audit-batches-and-evidence-format.md
**Research Dir:** not applicable

## Question

What conditions make the audit complete and the implementation ExecPlan ready to execute, given the accepted consequence-based rubric and the eventual evidence contract?

Distinguish audit coverage and honest reporting from repaired skill behavior. Decide how blocker and major findings, unavailable model runs, unverified client behavior, approved exceptions, and separate behavior proposals affect each gate. Define when an unresolved item can be explicitly deferred, which implementation milestones must remain blocked by a human decision or missing evidence, and what the final audit and self-contained ExecPlan must contain.

The destination remains a completed audit of every in-scope maintained skill plus an implementation plan. Imported skill bundles and their maintenance are excluded by the ownership decision. Resolving this ticket does not authorize implementation, installation, or publication. Use the evidence/model and batch/report decisions before selecting concrete acceptance requirements; do not invent universal model or provider claims.

---

## Resolution

The human accepted the first three policies and the unresolved-proposal tracking clarification on 2026-10-02, then accepted all three remaining recommendations together on 2026-10-04. This resolution records the six policies and the shared understanding. It authorizes the next audit review sessions, not skill implementation, installation, or publication.

### Completed audit gate

The audit can be complete while the reviewed skills still contain defects. Completion requires complete static coverage of every included skill under the [batch/report contract](choose-audit-batches-and-evidence-format.md#resolution), shared-resource and split-bundle reconciliation, human disposition of findings, and the required native baselines under the [evidence contract](set-audit-evidence-and-model-coverage.md#resolution), or explicit scoped evidence waivers. Account for every required check, reviewed file, candidate, and exclusion. Undisclosed review gaps prevent completion.

Blocker and major findings do not by themselves prevent a completed diagnostic audit. Report their evidence, consequences, confidence, proposal status, and remaining validation. They do not become passing compliance merely because review is complete, and the audit does not require implementing their fixes first.

An unavailable required model, unsafe fixture setup, missing usable trace, or other missing required evidence remains blocking unless the human explicitly waives that exact requirement. Preserve the seven-model medium-effort matrix, repetitions, failure records, and distinction between a usable failed skill run and an incomplete harness or infrastructure attempt. Record an approved omission as a waiver or scope change; never describe the omitted review or run as performed.

Disclosed uncertainty outside required audit evidence can remain, including untested Copilot/Gemini enforcement and deferred behavior questions. State which claims it limits and what later validation or decision is needed. Static comparison does not establish runtime enforcement, and incomplete evidence does not establish incompatibility.

### Unresolved proposals remain visible

The human specifically required that unresolved redesigns and proposals requiring new approval must not be missed. Keep each proposal in the single findings register with a stable finding ID, rationale, exact decision or approval needed, affected work, and current human disposition. Create a linked Wayfinder decision ticket as soon as its question is precise. Until then, retain the finding and its unresolved question visibly; do not manufacture a premature ticket or lose the proposal in generic fog.

The final audit and the ExecPlan's pending-decisions section must expose every such proposal by stable ID. Link to the one owning finding and decision ticket rather than copying competing records. Reconciliation must account for every proposal, including accepted, rejected, deferred, and unresolved items. An accepted authoring proposal maps to executable plan work; a pending redesign never silently enters that work.

Dependent implementation remains blocked until the human approves, rejects, or explicitly defers the proposal and the resulting accepted scope is independent of it. A deferral does not remove a genuine technical dependency. Unrelated accepted work can proceed without waiting for unrelated redesign decisions.

### Deferrals, waivers, and severity gates

Record the human decision, rationale, residual risk, affected skill/check/scenario/model or work, and revisit trigger for every deferral or waiver. Keep a proposal deferral, an evidence waiver, and acceptance of remaining risk distinct. None establishes successful behavior, passing validation, or permission to bypass a protected contract.

Blocker and major findings affecting implementation work prevent acceptance of the affected milestone until resolved or the human explicitly accepts the stated remaining risk within its exact scope. This does not block all independent milestones. Binding controls remain binding; a residual-risk decision alone does not redesign approval rules, invocation controls, required dependencies, or other protected behavior. Such a redesign still requires its separate decision under the [adoption policy](set-adoption-rules-and-protected-behavior.md#resolution).

Missing required audit evidence still needs an explicit scoped waiver before the completed-audit label. Later candidate-validation gaps must remain visible in the plan's acceptance state; an audit waiver is not automatically a waiver for implementation acceptance.

### Executable implementation-plan gate

The final ExecPlan must be fully executable for accepted authoring improvements. Resolve design choices for that scope before finalizing it. Name exact targets in both approved roots and preserve the intended contracts and documentation-maintenance boundaries. Concrete validation prerequisites may be executable steps when their procedure, expected outcome, failure handling, and effect on acceptance are specified.

Keep unresolved redesigns and proposals needing new approval outside executable scope, in the visible pending-decisions section. If accepted work genuinely depends on one, resolve the prerequisite before including that work in the executable scope, or explicitly leave that dependent work pending. Do not label an unresolved design choice a validation step or silently choose behavior for the human. The plan must distinguish executable work from pending work and state every relevant approval and evidence gate.

Follow the repository [ExecPlans contract](../../../.agents/skills/exec-plans/SKILL.md). Required knowledge and decisions must be embedded in the plan; links provide evidence and navigation, not a substitute for the instructions a novice needs. Readiness of the plan is separate from authorization to execute, install, or publish it.

### Candidate acceptance

For each accepted change, define observable expected outcomes before candidate testing. Require preserved contracts, applicable static and tooling checks, matched baseline-versus-candidate cases for affected tested behavior, and finding-specific validation for other accepted changes. Match the scenarios, fixtures, clients, models, efforts, and relevant permissions to the unchanged pre-edit snapshot. Justify broader validation from the actual findings; do not claim the small audit sample covers every skill or setting.

Retain failures and variation and grade activation, workflow/approval behavior, and output separately where relevant. Approval or control violations and unresolved blocker/major regressions block affected acceptance. Apply the scoped residual-risk policy above without converting failed checks into passing results or bypassing protected controls. An average score cannot erase a serious observed regression.

Keep `dotnet-upgrade` acceptance document-only. Do not run its rejecting validator, packaging, installer, live models, or migration procedure as an acceptance gate. Preserve the existing control/tooling incompatibility as a recorded limitation. Do not claim untested provider enforcement or remove a control to produce a passing tool result. Exact change-specific commands and cases belong in the later plan once findings make them concrete.

### Final document requirements and reconciliation

`docs/skill-audit/audit.md` must identify the audited scope and source revision, exclusions and changes to scope, static coverage, findings and human decisions, native baseline results, exceptions and waivers, pending proposals, and evidence limits. Link the batch reports, coverage index, single findings register, and run artifacts. State completion against the gates above without implying that defects were repaired or untested behavior passed.

`docs/skill-audit/ExecPlan.md` must contain exact accepted targets, repository context and protected contracts, ordered milestones, working directories and commands, expected observable outcomes, approval and evidence gates, validation, and recovery. Include and maintain `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective`, with synchronized milestone state. Embed the knowledge needed to execute the accepted scope. Include a pending-decisions section linking every unresolved proposal by ID and explaining the work each decision blocks.

Final reconciliation checks that every finding and proposal has a visible disposition and route, that accepted improvements map to implementation work, and that rejected, deferred, or unresolved proposals remain accounted for. Resolve duplicate records through links without losing evidence or stable IDs. Required audit evidence gaps still block completion unless explicitly waived. Do not substitute a clean plan or a closed decision map for the required audit evidence.

This decision unblocks the ten independent static review scopes. The two resource scopes retain their respective instructions-review blockers, and [Reconcile Static Findings and Select Baseline Cases](reconcile-static-findings-and-select-baseline-cases.md) remains blocked by all twelve reviews. No audit baseline or implementation acceptance run occurred while resolving these gates.
