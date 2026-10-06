# Skill Authoring Audit Handoff

## Goal and Status

Complete the evidence-backed audit of non-imported maintained skills, then write `docs/skill-audit/audit.md` and a self-contained `docs/skill-audit/ExecPlan.md`. Neither final document exists. Skill implementation, installation and publication follow this effort.

The [map](map.md) has 26 tickets: nine closed, seventeen open and zero claimed. [Review Delegation and Discovery](tickets/review-delegation-and-discovery.md) has complete static investigation, with its claim released for live human review continuation. The source reviewer released file ownership before parent reconciliation. The two earlier reviews remain closed. No native audit baseline ran.

Scope remains 37 candidates: 32 published plus five repository-local skills; 23 configured imports excluded. [Inventory](local-inventory.md#current-audit-scope) and [coverage](coverage.md) own candidate/exclusion history. Static investigation now covers sixteen candidates, 928 check rows and 76 unchanged primary hashes, plus twenty-five fixture hashes. Human proposal review is complete for eleven candidates and seventeen findings; five new findings await review. Twenty-one candidates remain unstarted.

## Next Focus and Exact Next Step

Resume only [Review Delegation and Discovery](tickets/review-delegation-and-discovery.md). Claim it before recording answers, verifying both exact blockers remain closed: `choose-audit-batches-and-evidence-format.md` and `set-audit-completion-and-implementation-gates.md`. The ticket's Prepared Live Review owns three concrete dispositions:

1. Accept DD-001/DD-002/DD-003/DD-005 for later planning: independent-area grading, explicit prior-context/cache fixtures and hit/miss oracles, real citation identity and separately reported/trace-backed workflow evidence, and five whitespace-only line repairs. Preserve valid checks, 1-3 allowed areas, direct narrow reads, optional cache, dependencies, controls, names and approval rules. Exact fixture/oracle choices and genuine DD-004 dependencies precede affected executable work.
2. Retain DD-004 in [Define Benchmark Grader Failure Outcomes](tickets/define-benchmark-grader-failure-outcomes.md). Do not choose status, exit code or result schema in batch disposition.
3. Add Explore and Official Sources' two zero-filling producers to SAG-008's existing [metric decision](tickets/choose-unknown-benchmark-metric-representation.md), while retaining its original three targets and unchosen representation. Preserve all earlier routes and expose every underlying decision in both final documents.

No live answer has been recorded for this round. A human “accept all” accepts these three recommended dispositions only; it does not select failure/metric protocols, authorize implementation, waive evidence, or accept residual risk. Record the actual answers, resolve remaining frontier questions, then close only this batch with Resolution, map gist, coverage/findings/handoff synchronization and one docs commit. Do not begin another non-research ticket in the same logical session.

## Findings and Pending Routes

The [single finding register](findings.md) owns all twenty-two findings: eleven major, eight minor and three observations. Static observations and predicted consequences are not observed native failures.

The human's prior answers remain unchanged: accepted SAG-001/009/010/011/012/014 plus only SAG-013 documentation cleanup; accepted SAG-004 through SAG-007 evaluation repairs; accepted RLW-001/RLW-003 authoring clarifications. Exact SAG-004 fixture/oracle mapping must follow current documented overlap, not invented successor names. RLW-003 retains valid independent output/lint/diff checks and does not expand SAG-007's targets. Actual required reads, order and SAG-012 client enforcement stay unverified.

Six separate underlying questions remain pending and must appear by finding ID and route in both final documents:

- SAG-002: [Resolve Installer Authority for Skill Authoring](tickets/resolve-installer-authority-for-skill-authoring.md).
- SAG-003: [Define Create Skill Body Contract](tickets/define-create-skill-body-contract.md).
- SAG-008: [Choose Unknown Benchmark Metric Representation](tickets/choose-unknown-benchmark-metric-representation.md).
- SAG-013: [Set Safe Command Validation Scope for Agents Authoring](tickets/set-safe-command-validation-scope-for-agents-authoring.md).
- RLW-002: [Resolve ExecPlan Self-containment and Prior-plan References](tickets/resolve-execplan-self-containment-and-prior-plan-references.md).
- DD-004: [Define Benchmark Grader Failure Outcomes](tickets/define-benchmark-grader-failure-outcomes.md), blocked by current batch review; the other five remain open and unblocked.

DD-001/002/003/005 are proposed, not accepted. DD-004 remains pending in full until live disposition and its separate protocol decision. Additional SAG-008 targets are proposed, not automatic scope expansion. Analogous SAG-001/SAG-012 links do not add new accepted targets. No proposal has been rejected or deferred. Null, omitted fields and zero are not established compatible unknown metrics; imported consumers can default omissions to zero.

The bounded retry-counting check is now explicit in [Review Execution and Handoff](tickets/review-execution-and-handoff.md): distinguish successive task runs from failed-subtask replacements and check actual authorization under the loop's three-failure budget and delegation's one-replacement exception. This is a consumer check, not an established contradiction or selected behavior.

## Evidence and Verification

The [first report](reports/review-skill-authoring-and-repository-guidance.md) owns six skills/45 primary files/348 rows. The [repository-local report](reports/review-repository-local-workflows.md) owns five skills/sixteen primary files/eighteen fixture files/290 rows and five bounded dependency fingerprints. The [delegation/discovery report](reports/review-delegation-and-discovery.md) owns five skills/fifteen primary files/seven fixtures/290 rows, baseline `991b14b86440dab452ac28312c5f05a2b4a42266`.

All reviewed primary files remain unchanged. Source inspection, JSON/YAML parsing, AST parsing, hashes and record checks do not execute audited graders or prove native behavior. Five Explore grader whitespace violations remain unimplemented at lines 116,121,143,145,156; three Improve Skill violations at 133,139,142 remain recorded separately.

Current source-review dispatch selected/submitted `gpt-6.1-sol`/`high`; executed settings/usage are unconfirmed. Initial window 2026-10-06 03:55:32-04:15:32 UTC; saved inventory/five-minute checkpoints inspected; completion observed 04:04:59 UTC before limit, with no interruption or extension. The report retains structured dispatch audit and a narrow prompt-isolation noncompliance: parent included runtime self-report prohibition in the task prompt. Selected/submitted routing matched; no self-report was used as runtime confirmation. Keep orchestration audit instructions with the parent in future prompts.

Earlier source-review dispatches are recorded in their owning reports; none is a native baseline. Current record verification and canonical docs lint are described below and must not be relabeled as baseline tests. The earlier two-report temporary verifier hardcodes seventeen findings and is superseded for whole-audit checks; do not treat its old totals as current.

## Standing Constraints and Gates

Keep all maps, tickets, research, reports, handoff and final documents under `docs/skill-audit/`. Domain-modeling remains waived. Use Wayfinder and Grilling; Create Skill/Skill Creator for authoring/evaluation decisions, ExecPlans for final plan authoring. At most one non-research ticket closes per logical session.

[Adoption](tickets/set-adoption-rules-and-protected-behavior.md#resolution) requires contextual dispositions, consequence-based findings, scoped exceptions and preserved intent/controls/approvals/dependencies/stops/outputs/names. Missing evidence is unresolved, not incompatibility or passing compliance. Length alone is not a defect.

[Ownership](tickets/decide-skill-ownership-and-import-handling.md#resolution) excludes imports, provenance recovery and ledgers; inspect excluded helpers only as necessary dependencies. Planned accepted targets can include both roots, but documentation maintenance cannot edit local skill bundles. No implementation, installers, import refreshes, audited validator/grader execution or native baselines during static review.

[Batch rules](tickets/choose-audit-batches-and-evidence-format.md#resolution) require twelve scopes, 58 checks per skill, one finding owner, consumer reconciliation and live review. All static reviews finish before sample selection. Split bundles remain partial until both scopes and integration are reviewed.

[Completion gates](tickets/set-audit-completion-and-implementation-gates.md#resolution) distinguish completed audit, executable plan and implementation acceptance. Required evidence gaps need exact human waivers. Pending proposals retain IDs/routes and genuinely dependent work stays pending; deferral does not erase dependencies or bypass controls.

The user authorized only static paper reading of Dotnet Upgrade for this audit. Retain invocation, approval, execution, installation, packaging, validator and live-evaluation restrictions. Reading is not activation.

## Native Evidence Outstanding

[Evidence contract](tickets/set-audit-evidence-and-model-coverage.md#resolution): native Codex CLI; up to three safe risk-selected skills after all static reviews; explicit/automatic-where-allowed/adjacent-negative/safe-boundary cases; identical cases across seven models at explicit medium; three fresh runs per configuration. Copilot/Gemini compatibility stays static. No sample or launch recipe exists.

Exact targets: `gpt-5.6-sol`, `gpt-6-sol`, `gpt-6.1-sol`, `gpt-5.6-luna`, `gpt-6-luna`, `gpt-6-astra`, `gpt-5.6-terra`. CLI 0.159.3 catalog listing does not prove access or execution. No silent substitutions.

Require isolated discovery/tools, unchanged snapshots, full prompt/config/hash/version/permission/timing/usage/run records and usable traces; define expected outcomes before launching; grade activation/workflow/output separately. Self-reports do not prove compliance. Usable failed runs are diagnostic evidence; unavailable models, unsafe setup and missing traces block completion unless scoped waiver. Handoff/Spec to Tasks/OKF inputs are promising, not certified fixtures. `--ignore-user-config` alone does not prove isolation; current help lacks dated `--full-auto`.

## Documentation Pass and Process Notes

Formal Update Agent Docs pass added only a bounded grader-integrity pointer in `.agents/memory/known-issues/skills.md`, derived type Known Issue. Existing INDEX/FILE_MAP/instructions routes cover unchanged scope; no API/test strategy/routing change. OKF loaded profile only. `rtk proxy ./scripts/lint-okf.py` exited 0 across canonical bundles; scoped `.agents/` diff is exactly that pointer. Added: known-issues pointer. Changed: None. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None.

Current verification passed: `rtk proxy python3 /private/tmp/skill-audit-verify-three-batches.py` verifies the 26-ticket graph, 928 rows, 76 primary hashes, twenty-five additional fixture hashes, twenty-two unique findings, links/anchors, formatting, fog and unchanged protected sources. The five bounded dependency/Git-state checker and `rtk git diff --check` also passed. First-batch 45-file inventory includes its bundled fixtures; the twenty-five separately declared fixtures belong to later reports, not every fixture in the whole audit.

Record-processing corrections: source reviewer discarded accidental generated consumer matches and reran bounded discovery; body-line counts exclude YAML delimiters/leading blanks; parent corrected a stale patch anchor. Tool Guardian rejected the long inline checker (334 command tokens versus limit 256); a disposable helper and short RTK call retained all checks. Its first classification assertion failed because the first batch counts bundled fixtures within its 45-file inventory; corrected explicit report ownership passed without weakening totals. Earlier long-helper, guessed hook filename and extraction-regex corrections remain in prior reports. Use small patches, enumeration and asserted boundaries. RTK works; gain database is unavailable.

[Design overview](design-map.html) is dated discussion material, not live status or approval. No annotations supplied. Host draft restoration is best-effort; exported text supports discussion.
