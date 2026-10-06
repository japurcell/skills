# Skill Authoring Audit Handoff

## Goal and Status

Complete the evidence-backed audit of non-imported maintained skills, then write `docs/skill-audit/audit.md` and self-contained `docs/skill-audit/ExecPlan.md`. Neither final document exists. Implementation, installation and publication follow this effort.

The [map](map.md) has 33 tickets: eleven closed and twenty-two open, with no claims. [Review Quality and Harness Skills](tickets/review-quality-and-harness-skills.md#resolution) is closed after the human accepted all three planning questions on 2026-10-06. All four static review tickets are closed. No native audit baseline ran.

Scope remains 37 candidates: 32 published plus five repository-local skills; 23 configured imports excluded. [Inventory](local-inventory.md#current-audit-scope) and [coverage](coverage.md) own history. Static investigation and human proposal review cover twenty-three candidates, 1,334 rows, 102 primary hashes and all thirty-two findings, plus twenty-five separately declared fixture hashes. Fourteen candidates remain unstarted.

## Next Focus and Exact Next Step

Continue static review with [Review Requirements and Task Planning](tickets/review-requirements-and-task-planning.md): PRD, Spec to Tasks, To Issues and Architecture Design Contest. Both exact blockers, `choose-audit-batches-and-evidence-format.md` and `set-audit-completion-and-implementation-gates.md`, were verified closed during this closure; recheck them, claim this open ticket before work, and gather bounded static facts before live proposal review. Do not claim or start it as part of the completed quality/harness session. At most one non-research ticket may close per logical session.

## Findings and Pending Routes

The [single register](findings.md) owns thirty-two findings: eighteen major, eleven minor and three observations. All thirty-two findings have recorded dispositions; underlying choices remain pending. Static evidence and predicted consequences are not observed native failures.

Earlier accepted scopes remain unchanged: SAG-001/009/010/011/012/014 plus SAG-013 documentation cleanup; SAG-004 through SAG-007 evaluation repairs; RLW-001/RLW-003 authoring clarifications; DD-001/DD-002/DD-003/DD-005 repairs. Preserve contracts, useful predicates, direct narrow reads, optional cache and dependencies. Exact SAG-004 and other accepted fixture/oracle choices precede executable readiness; do not invent successor names or make dependencies optional. RLW-003 does not expand SAG-007. SAG-012 enforcement remains unverified.

Six earlier underlying questions remain open and unblocked:

- SAG-002: [Resolve Installer Authority for Skill Authoring](tickets/resolve-installer-authority-for-skill-authoring.md).
- SAG-003: [Define Create Skill Body Contract](tickets/define-create-skill-body-contract.md).
- SAG-008: [Choose Unknown Benchmark Metric Representation](tickets/choose-unknown-benchmark-metric-representation.md).
- SAG-013: [Set Safe Command Validation Scope for Agents Authoring](tickets/set-safe-command-validation-scope-for-agents-authoring.md).
- RLW-002: [Resolve ExecPlan Self-containment and Prior-plan References](tickets/resolve-execplan-self-containment-and-prior-plan-references.md).
- DD-004: [Define Benchmark Grader Failure Outcomes](tickets/define-benchmark-grader-failure-outcomes.md).

Seven quality/harness routes are now open and unblocked:

- QH-002: [Resolve Code Review Generalist Role Portability](tickets/resolve-code-review-generalist-role-portability.md).
- QH-003: [Resolve Code Review Verification Routing Floor](tickets/resolve-code-review-verification-routing-floor.md).
- QH-004: [Resolve Techdebt Validation and Rollback](tickets/resolve-techdebt-validation-and-rollback.md).
- QH-005/QH-006: [Resolve Techdebt Required Helper Contracts](tickets/resolve-techdebt-required-helper-contracts.md).
- QH-008: [Resolve Harness Analysis Report Capture](tickets/resolve-harness-analysis-report-capture.md).
- QH-009: [Define Improve Repo Harness Intent](tickets/define-improve-repo-harness-intent.md).
- QH-010: [Resolve Adversarial Trivial Review Intent](tickets/resolve-adversarial-trivial-review-intent.md).

All thirteen routes and owning IDs must appear in both final documents. Accepting retention chooses no behavior, evidence waiver or residual-risk acceptance. Genuinely dependent work stays pending. Deferral requires rationale, affected work, remaining risk and revisit trigger.

QH-001/QH-007 are accepted later evaluation repairs: current Code Review intake/references/80+/PR stops and Harness claim-polarity/recommendation/section grading. Preserve useful checks, four roles, controls, approvals, read-only intent, names and outputs. Exact fixture/oracle choices and genuine protocol prerequisites remain readiness gates. SAG-011 now includes only Harness Analysis sidecar wording plus original Create AgentsMD target. SAG-008 now has eight approved metric producers; DD-004 has five protocol graders, adding exactly Adversarial Review, Code Review and Harness Analysis while retaining original scope. Representation, status, exit, schema and compatibility remain unresolved. Improve Repo Harness sidecar stays pending QH-009; SAG-001/SAG-012 analogies do not expand scope. No proposal was rejected/deferred or implemented. All thirteen routes stay pending; acceptance grants no evidence waiver or residual-risk acceptance.

The bounded retry-counting check remains in [Review Execution and Handoff](tickets/review-execution-and-handoff.md): distinguish successive task runs from failed-subtask replacements and verify authorization under the loop's three-failure budget and delegation's one-replacement exception. No contradiction or behavior selection is established yet.

## Source Evidence and Dispatch

Four reports own baselines and inventory categories: [authoring/guidance](reports/review-skill-authoring-and-repository-guidance.md), six skills/45 primary files/348 rows; [repository-local workflows](reports/review-repository-local-workflows.md), five skills/sixteen primary files/eighteen separately declared fixtures/290 rows; [delegation/discovery](reports/review-delegation-and-discovery.md), five skills/fifteen primary files/seven fixtures/290 rows; [quality/harness](reports/review-quality-and-harness-skills.md), seven skills/twenty-six primary files/no fixtures/406 rows plus eighteen bounded dependencies. The first report's 45-file inventory includes bundled fixtures; twenty-five later declared fixtures are not the audit's whole fixture total.

Quality/harness baseline is `72a3ae956e3533aaddf33eb1e8d8ecf30b69d08f`. All 44 primary/dependency fingerprints match it. Nineteen primary files ship; four eval definitions and three graders are pruned. No entry requires a stripped eval. Six custom-agent bodies were read and nineteen names parsed. No repository generalist definition exists; host availability remains unverified. Imported Addy/TDD reads were bounded dependencies. Remote Improve Repo Harness content/version/trust remains unverified.

Source reviewer selected/submitted `gpt-6.1-sol`/`high`; unused fallback `gpt-6-sol`/`high`. Executed model/effort/usage remain unconfirmed. Routing metadata stayed outside its prompt. Initial window: 2026-10-06 15:40:09-16:00:09 UTC. Saved checkpoints/status were inspected; completion notification preceded the 16:00:30 UTC parent clock check. Exact completion time is unknown. Limit check was 21 seconds late during parent reconciliation preparation; no interruption or extension occurred. Keep future checks independent of long parent writes. The report owns structured details. Prior dispatches, including the previous prompt-isolation lapse, stay in their reports; none is native evidence.

## Standing Constraints and Native Evidence

Keep artifacts under `docs/skill-audit/`. Domain-modeling remains waived. Apply Wayfinder/Grilling, Create Skill/Skill Creator for authoring/evaluation decisions and ExecPlans before plan authoring. Preserve intended triggers, controls, approvals, dependencies/delegation, stops, outputs and names. Missing evidence is unresolved, not incompatibility or passing compliance. Length alone is not a defect.

Exclude imports, provenance recovery and ledgers. Check imported/shared resources only as necessary dependencies. Static batches permit no implementation, installer/import refresh, packaging, audited grader/validator execution or native baseline. Documentation maintenance cannot edit local skill bundles. Dotnet Upgrade has only its narrow paper-reading exception; all other restrictions remain. Finish twelve scopes/reconciliation before sample selection; split bundles remain partial until both parts and integration are covered.

[Native evidence contract](tickets/set-audit-evidence-and-model-coverage.md#resolution): native Codex CLI; up to three safe risk-selected skills after static review; explicit/automatic-where-allowed/adjacent-negative/safe-boundary cases; identical cases across seven models at medium; three fresh runs per configuration. Models: `gpt-5.6-sol`, `gpt-6-sol`, `gpt-6.1-sol`, `gpt-5.6-luna`, `gpt-6-luna`, `gpt-6-astra`, `gpt-5.6-terra`. Dated catalog advertising does not prove access or execution; no substitutions. Copilot/Gemini compatibility stays static.

Require isolated discovery/tools, snapshots, prompt/config/hash/version/permission/timing/usage records and usable traces. Define outcomes before launch; grade activation/workflow/output separately. Self-reports do not prove compliance. Usable failed runs are diagnostic evidence; unavailable models, unsafe fixtures and missing traces block completion unless explicitly waived. No sample/launch recipe exists. Handoff/Spec to Tasks/OKF inputs are promising, not certified fixtures. `--ignore-user-config` alone does not prove isolation; dated help lacks `--full-auto`.

## Verification and Documentation Pass

`rtk proxy python3 /private/tmp/skill-audit-verify-four-batches.py` passed: 33-ticket acyclic graph (eleven closed/twenty-two open/no claims), 1,334 rows, 102 primary hashes, twenty-five additional fixture hashes, eighteen quality/harness dependency fingerprints, thirty-two unique findings/index, preserved existing decisions/scopes, links/anchors, formatting, fog and unchanged protected sources. The four-batch verifier now expects the closed batch and all recorded dispositions/accepted target scopes, retaining its source and record checks. Earlier three-batch totals are superseded. Source inspection and JSON/YAML/AST parsing do not execute graders or prove native behavior.

Closure Update Agent Docs changes only the existing grader-integrity scope pointer in `.agents/memory/known-issues/skills.md`, type Known Issue, distinguishing accepted targets from pending representation/outcome choices. Existing INDEX/FILE_MAP/instruction routes suffice; no API, test strategy or skill changed. OKF loaded profile only; `rtk proxy ./scripts/lint-okf.py` exited 0 across both bundles. Scoped canonical diff is exactly this authorized pointer. Added: None. Changed: grader-integrity scope pointer. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None. The bounded dependency/Git-state check and scoped diff checks also passed. Source-checkpoint documentation pass remains in the owning report.

Process notes: reviewer replaced a Tool Guardian-rejected long write with an inspectable patch before execution. Parent corrected a guessed commit-reference filename and stale append anchor by reading exact paths/text, then replaced an invalid same-file delete/add patch with an inspectable exact-path write. Prior command-token and dynamic `exec(compile(...))` inspection failures remain in earlier reports; use inspectable helpers and short RTK calls. RTK works; gain database is unavailable. Do not rerun old hardcoded totals as current. `design-map.html` remains dated discussion material; no annotations supplied or approval recorded.
