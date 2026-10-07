# Review Execution and Handoff

**Type:** grilling
**Status:** closed
**Blocked By:** choose-audit-batches-and-evidence-format.md, set-audit-completion-and-implementation-gates.md
**Research Dir:** not applicable

## Question

Which authoring improvements and adaptations does this scope justify, which contracts must they preserve, and which findings should the human accept, defer, reject, or resolve as separate behavior decisions?

Review each maintained entry point and bundled resources under `skills/prd-ralph/`, `skills/prd-ralph-loop/`, `skills/execplan-implement/`, `skills/commit/`, `skills/handoff/`. Include evaluation definitions as static evidence; exclude generated outputs, snapshots, and fixture entry points from the primary inventory.

Specific review concerns: Prerequisites, execution/approval gates, stopping and failure recovery, commit contracts, handoff triggers, and artifact ownership. Input flags do not by themselves establish skill dependencies.

Carry forward the bounded delegation consumer check: `skills/prd-ralph-loop/SKILL.md:20-22,34-35` starts successive task runs and stops after three consecutive failures; `skills/delegate-to-subagents/SKILL.md:246` permits at most one replacement unless the user authorizes more retries. Verify task/run/replacement counting and whether actual invocation supplies the permitted authorization. A consumer check is outstanding, not an established contradiction or approved policy change. Preserve both limits. If full review exposes a protected-contract ambiguity, record the finding and create its precise separate decision before proposing dependent wording.

Apply the [batch/report contract](choose-audit-batches-and-evidence-format.md#resolution), [adoption policy](set-adoption-rules-and-protected-behavior.md#resolution), and [evidence contract](set-audit-evidence-and-model-coverage.md#resolution). Consult [sizing and dependency evidence](../batch-sizing-evidence.md) as a bounded inventory, not proof of dependency closure or skill quality. Account for every check and reviewed file; give shared resources an owner and check consumers across batches. Static coverage is separate from compliance and runtime evidence.

Write the scope's evidence to `docs/skill-audit/reports/review-execution-and-handoff.md`; update the shared coverage index and findings register through coordinated writes. Gather source facts, then review proposed dispositions with the human through Grilling. The ticket closes only after that live review and its recorded decision. Do not implement skill or tooling changes, run installers or imported refreshes, or launch behavioral baselines in this static review. Surface ambiguous scope and behavior as separate decisions.

---

## Source Checkpoint

This section records the proposed 2026-10-06 checkpoint. The subsequent Resolution owns the 2026-10-07 human decisions and supersedes its pending-review instructions.

Static investigation and parent source reconciliation are complete; live human proposal review remains pending. The [report](../reports/review-execution-and-handoff.md) records five skills, 22 primary files, 20 fixtures, nine bounded source dependencies, seventeen checkpoint-only support hashes and five exact 58-check matrices (290 rows). All 51 source/fixture/dependency fingerprints match unchanged baseline `8d563fae209c5b3583eacb7e7f4056783279aff0`; checkpoint records can change during reconciliation. Sixteen primary files ship under both inspected selection routines; six eval resources and twenty fixtures are pruned. Installed access and native behavior remain untested.

The [single register](../findings.md#eh-001-loop-paper-grader-does-not-establish-blind-orchestration) owns EH-001 through EH-010. EH-002 is an observation about missing default-title coverage behind a valid explicit override; EH-009 owns the separate concrete unrelated-source predicate problem. Five precise behavior questions have proposed tickets blocked by this unclosed batch. No authoring or evaluation repair, behavior choice, grader addition, implementation, evidence waiver or residual risk has been approved in this checkpoint.

The next live Grilling round has three independent recommendations:

1. Accept EH-001/EH-002/EH-003/EH-004/EH-009 for later evaluation repair or coverage. Preserve live blindness, explicit user overrides, supplied path precedence, useful checks, approvals, required dependencies, stopping rules and output contracts. Exact simulation schemas, fixture/oracle facts, source identity and genuine shared protocol prerequisites must be resolved before executable readiness. No blanket anatomy rule or expansion of SAG-003/SAG-007 is implied.
2. Retain EH-005/EH-006/EH-007/EH-008/EH-010 in their five proposed precise routes: failure/replacement counting and terminal maintenance, TDD seam/refactor ordering, integration validation, published ExecPlans helper supply, and Commit dry-run inspection/mutation/output authority. Keep genuinely dependent work pending and expose all earlier and new IDs/routes in both final documents. Retention selects no behavior.
3. Add exactly `skills/prd-ralph-loop/evals/grade_benchmark.py`, `skills/commit/evals/grade_benchmark.py` and `skills/handoff/evals/grade_benchmark.py` to SAG-008 metric-producer and DD-004 protocol scope, retaining all earlier targets. Accepted scope is still nine producers/six protocol graders; accepting these three would make twelve/nine. Unknown representation, outcomes, exits, schemas and consumer compatibility remain unresolved. Preserve computed character counts and independently useful predicates; no excluded helper edits or execution authority is proposed.

The reviewer released report ownership before the twenty-minute limit. Status checks inspected usable saved progress; no interruption, replacement or extension occurred. Selected/submitted `gpt-6.1-sol`/`high`, executed settings and usage unconfirmed. Dispatch evidence belongs in the report, not native baseline evidence. Both exact blockers were verified closed before claiming this ticket. Keep this claim until live answers are recorded; do not resolve another non-research ticket in this logical session.

---

## Resolution

On 2026-10-07 the human explicitly accepted all three Execution and Handoff recommendations, first with “accept all” and then through the matching question reply. This closes the batch's live proposal review. Source evidence remains static at `8d563fae209c5b3583eacb7e7f4056783279aff0`; human approval does not establish passing native behavior. The [report](../reports/review-execution-and-handoff.md) owns the five-skill inventory, protected contracts, 290 checklist rows and bounded source/dispatch evidence. The [single register](../findings.md#eh-001-loop-paper-grader-does-not-establish-blind-orchestration) owns the ten findings once.

### Accepted evaluation repairs and coverage

EH-001/EH-003/EH-004/EH-009 are accepted evaluation repairs for later planning. EH-002 is an accepted evaluation-coverage proposal, retaining its Observation severity and the valid higher-priority PR-title override. No wrong native PR behavior is established.

- Loop: distinguish paper simulations from performed native orchestration, model worker responses explicitly, preserve blind parent selection and exact completion identity, and align active fixture requirements with the current Ralph contract. Keep useful status/output predicates; route mentions are not dispatch proof.
- Commit: retain the explicit title-override case and add default full-first-line title coverage. Repair unrelated current-source heading checks against identified requested artifacts and applicable source metadata; preserve useful message/body/trailer predicates.
- Handoff: honor the explicitly requested path, define genuinely invalid/ambiguous fallback fixtures separately, provision the two declared missing logs as deliberately synthetic inputs, and cover current trigger/error/fallback behavior with independent expected facts. Preserve named-path precedence, root/feature defaults, inherited next step, concision, source anchors and redaction.

Known owning evaluation files are `skills/prd-ralph-loop/evals/evals.json`, `skills/prd-ralph-loop/evals/grade_benchmark.py`, `skills/commit/evals/evals.json`, `skills/commit/evals/grade_benchmark.py`, `skills/handoff/evals/evals.json` and `skills/handoff/evals/grade_benchmark.py`. The missing declared log targets are `skills/handoff/evals/files/root-create-fixture/logs/test-failure.txt` and `skills/handoff/evals/files/fallback-noise-fixture/logs/retry.log`; their synthetic bytes and expected facts remain to be designed, not recovered or fabricated as history. Current criteria-bearing fixture repairs and any additional fixture paths must be specified from these accepted proposals before executable plan readiness. Exact paper schemas, fixture/oracle mappings, provisioning/source identity and genuinely dependent shared protocol choices remain prerequisites for affected executable work.

Preserve triggers, invocation controls, required dependencies/delegation, approvals, stopping rules, names and output contracts. Do not change production instructions to satisfy stale evaluator rules. EH-009 does not create a global body-heading requirement, expand SAG-003's Create Skill question or automatically expand SAG-007's accepted targets. Artifact text does not prove actual loading, routing, tool use or permission containment. Baseline selection and launch remain later work.

### Retained separate behavior decisions

The human accepted retaining five precise routes, now open and unblocked by this batch closure:

- EH-005: [Resolve Ralph Loop Failure Counting and Retry Consent](resolve-ralph-loop-failure-counting-and-retry-consent.md), including blocked/failed/replacement categories, identity/reset/consent and terminal maintenance after failure stop.
- EH-006: [Resolve Ralph TDD Approval and Refactor Ordering](resolve-ralph-tdd-approval-and-refactor-ordering.md), preserving required TDD and confirmed seams before tests.
- EH-007: [Resolve ExecPlan Integration Validation](resolve-execplan-integration-validation.md), including conflict-free rebase, tested state and plan-only SHA updates.
- EH-008: [Resolve Published ExecPlans Helper Supply](resolve-published-execplans-helper-supply.md), retaining mandatory helper supply and repository-local protection.
- EH-010: [Resolve Commit Dry-run Mutation and Output Boundaries](resolve-commit-dry-run-mutation-and-output-boundaries.md), without inferring inspection, staging, branch, commit or publication authority.

All sixteen earlier routes remain pending as well, making 21 underlying decisions. Both final audit and ExecPlan must expose every unresolved ID and route; genuinely dependent work stays pending. Retention does not select behavior or count as rejection, deferral, evidence waiver, implementation approval or residual-risk acceptance. No proposal was rejected or deferred in this review. Imported TDD/Skill Creator helpers remain excluded from primary audit and edit scope.

### Accepted shared grader scope

Add exactly `skills/prd-ralph-loop/evals/grade_benchmark.py`, `skills/commit/evals/grade_benchmark.py` and `skills/handoff/evals/grade_benchmark.py` to [Choose Unknown Benchmark Metric Representation](choose-unknown-benchmark-metric-representation.md) and [Define Benchmark Grader Failure Outcomes](define-benchmark-grader-failure-outcomes.md), retaining every earlier accepted target. SAG-008 now covers twelve metric producers; DD-004 covers nine protocol graders.

Unknown representation, failure statuses, exits, schemas, eligible-run/output/source identity and consumer compatibility remain unresolved. Preserve computed output/transcript character counts and independently useful predicates. This scope acceptance does not choose null, omitted keys, zeros or a result/exit protocol, expand excluded-helper scope, authorize edits or execute graders. Exact dependent design and necessary compatibility evidence precede executable readiness.

The approved destination, import exclusions, static-first twelve-scope sequence, native seven-model medium-effort matrix, three fresh repetitions and completion gates remain unchanged. This review accepts later planning scope and visible routes only. No implementation, installer/import refresh, packaging, audited validator/grader, native baseline, publication, evidence waiver or residual risk was authorized or performed.
