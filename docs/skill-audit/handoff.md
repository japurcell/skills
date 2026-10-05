# Skill Authoring Audit Handoff

## Goal and Status

Complete the evidence-backed audit of non-imported maintained skills, then write `docs/skill-audit/audit.md` and a self-contained `docs/skill-audit/ExecPlan.md`. Skill implementation, installation, and publication follow this effort.

The [map](map.md) now has 25 tickets: eight closed, sixteen open, and [Review Repository-local Workflows](tickets/review-repository-local-workflows.md) claimed by `subagent-xS437U`. Both exact blockers were verified closed before claiming. The first authoring/guidance batch remains closed with its recorded human dispositions. No native audit baseline ran.

The current candidate pool is 37: 32 published plus five repository-local skills. Twenty-three configured imports are excluded. Unknown historical origin does not block a candidate; clear additional import evidence removes it. Current scope remains in [the inventory](local-inventory.md#current-audit-scope) and [coverage index](coverage.md).

## Next Focus and Exact Next Step

Record the two pending live human answers for the claimed [Review Repository-local Workflows](tickets/review-repository-local-workflows.md), then update the register, report, coverage and owning Resolution. Source investigation and record verification are complete. Do not repeat the audit, edit repository-local skill sources, or launch native baselines.

The questions ask whether to accept RLW-001/RLW-003 as later authoring clarifications, and retain RLW-002 in its separate intended-output decision. Silence is not a decision. If the human accepts both, close only this review ticket; leave the underlying RLW-002 question open and expose its ID/route in both final documents. That acceptance does not expand SAG-007's targets, choose predecessor-plan semantics, waive evidence, accept residual risk or authorize implementation.

After this ticket closes, the next allocated scope is [Review Delegation and Discovery](tickets/review-delegation-and-discovery.md), unless the human prioritizes the new separate decision. Do not claim another non-research ticket in this logical session.

The human answered all three first-batch review questions on 2026-10-05. These answers are recorded in the owning Resolution and finding register:

1. Accepted authoring repairs: SAG-001, 009, 010, 011, 012, 014, plus only SAG-013's documentation cleanup. Preserve names, invocation controls, approval boundaries, required dependencies and output contracts. Actual client enforcement under SAG-012 remains unverified.
2. Accepted evaluation repairs: SAG-004, 005, 006 and 007. Preserve duplicate avoidance and identity, response-only Improve Skill and loaded-target conditions, restored notes fixtures, and meaningful preservation checks. Ground exact fixture/oracle choices in documented current overlap before executable plan readiness.
3. Retained separate pending questions: SAG-002 installer authority, SAG-003 body structure, SAG-008 unknown metric representation, and SAG-013 execution authority. Leave dependent implementation pending and every ID visible in both final documents. This is not a behavior or metric choice, waiver, residual-risk acceptance, or execution approval.

The [single finding register](findings.md) contains the first batch's concrete evidence, proposals, validation, recorded human status, exact decisions and linked routes. No first-batch proposal was rejected or deferred. Approval concerns later plan scope only; it does not authorize implementation. The resumed logical session may resolve only the claimed repository-local review; do not claim another non-research ticket in this session.

The four first-batch separate decisions are unblocked by the closed authoring/guidance review, but remain open. Do not silently resolve them from approval of proposal routing. All twelve static scopes must finish before reconciliation and baseline selection.

The repository-local batch adds RLW-001/002/003 as pending human dispositions in the finding register. The first aligns a conflicting metadata table; the third clarifies reported workflow values versus valid independently checked artifacts. RLW-002 has a separate [ExecPlan reference decision](tickets/resolve-execplan-self-containment-and-prior-plan-references.md), blocked by the current review, because its source clauses conflict. No underlying interpretation or new proposal scope is accepted yet.

## Completed Static Evidence

- [Coverage](coverage.md) defines 58 stable checks: 38 authoring checks covering all 36 source bullets, four security checks, twelve repository checks and four client checks. Applicability, adoption disposition, compliance, review completion and runtime evidence are distinct.
- [First batch report](reports/review-skill-authoring-and-repository-guidance.md) records six primary skills, 45 hashed/read bundle files, protected contracts and six complete matrices (348 rows). [Repository-local report](reports/review-repository-local-workflows.md) records five skills, sixteen unchanged primary files (85,512 bytes), eighteen fixture dependencies, five bounded dependency fingerprints and five complete matrices (290 rows).
- Combined static investigation covers eleven of 37 candidates, 638 check rows and 61 unchanged primary hashes. The first six skills have completed human review; the new five await live dispositions. The other 26 candidates remain unstarted.
- [Findings](findings.md) owns seventeen records once: seven major, seven minor, three observations. These are static evidence and inferred consequences, not observed native failures. Ten SAG findings are accepted for later planning, SAG-013 is split accepted/pending, SAG-002/003/008 remain pending, and RLW-001/002/003 await current-batch review. Five precise questions have separate open decision tickets; the newest is blocked by this review.
- Consequential evidence includes response-only Improve Skill versus file-writing evals, three missing note fixtures, removed planning names in the Create Skill dedupe oracle, weak grader preservation predicates, a capped/unscoped AGENTS discovery command, and conflicting installer authority.
- Exact old planning names have no established one-to-one successor. Bounded inspection identifies current ExecPlans/PRD overlap and downstream Spec to Tasks/To Issues, without auditing those additional primary skills or choosing a new output layout.
- Omitted metric fields can default to zero in the imported consumer; a compatible unknown representation is not established. Keep SAG-008 pending rather than silently using null, omission, or zero.
- Source byte inspection found three whitespace-only violations in the Improve Skill grader (lines 133, 139, 142), recorded as SAG-014. Skill source was not edited.

## Standing Constraints and Owning Decisions

- Keep all map, tickets, research, reports, handoff, audit and ExecPlan in `docs/skill-audit/`. The user waived `domain-modeling`; use Wayfinder and Grilling.
- [Adoption policy](tickets/set-adoption-rules-and-protected-behavior.md#resolution): contextual adopt/adapt/not-applicable/incompatible dispositions, preserved intent/controls/approvals/dependencies/stops/outputs/names, consequence-based severity, explicit evidence and scoped exceptions. Missing evidence is unresolved, not incompatibility or passing compliance. Length alone is not a defect.
- [Ownership](tickets/decide-skill-ownership-and-import-handling.md#resolution): exclude known imports and their maintenance, provenance recovery and new ledgers. Inspect excluded helpers only as necessary dependencies of included skills. Plan accepted improvements in both roots with explicit targets; documentation maintenance remains barred from editing local skill sources.
- [Batch/report rules](tickets/choose-audit-batches-and-evidence-format.md#resolution): twelve bounded scopes, per-check coverage, one finding register, shared-resource owner/consumer checks, live human review after each batch, then reconciliation and sample selection. Split bundles stay partial until all scopes/integration are reviewed.
- [Completion gates](tickets/set-audit-completion-and-implementation-gates.md#resolution): completed audit requires coverage/reconciliation/human dispositions plus required native evidence or exact human waivers. Defects may remain; undisclosed gaps may not. Accepted authoring scope becomes executable plan work only with design prerequisites settled. Both final documents retain every unresolved proposal by ID and route. Deferral does not erase real dependencies or bypass controls.
- The human authorized narrow static paper reading of Dotnet Upgrade for this audit. Preserve both invocation controls and all execution, approval, installation, packaging, validator and live-evaluation restrictions. Reading is not activation. Only bounded dependency content was read in this batch; full owning review remains later.

## Native Evidence Still Outstanding

[Evidence/model contract](tickets/set-audit-evidence-and-model-coverage.md#resolution) requires native Codex CLI, up to three risk-selected fixture-ready skills chosen after full static review, explicit/automatic-where-allowed/adjacent-negative/safe-boundary cases, the same cases across seven models at explicit medium effort, and three fresh runs per configuration. No sample or launch recipe is selected.

Exact targets: `gpt-5.6-sol`, `gpt-6-sol`, `gpt-6.1-sol`, `gpt-5.6-luna`, `gpt-6-luna`, `gpt-6-astra`, `gpt-5.6-terra`. Catalog advertisement in CLI 0.159.3 is evidence of listing, not account access or execution. Copilot/Gemini compatibility remains static. Do not silently substitute models, effort, client or API replay.

Use isolated fixtures with enforced discovery/tool boundaries, unchanged source snapshots, complete records and traces, expected outcomes defined before runs, and separate activation/workflow/output grading. Usable failed runs are diagnostic evidence; unavailable models, unsafe fixtures and missing traces remain required gaps unless specifically waived. Handoff, Spec to Tasks and OKF have promising inputs, not certified fixture readiness. `--ignore-user-config` alone does not prove discovery isolation; current CLI help does not advertise the dated example's `--full-auto`.

## Verification and Documentation Pass

Parent verification confirms 61 unchanged primary hashes, eighteen fixture hashes, eleven matrices each containing exactly the 58 catalog IDs, preserved static/runtime distinctions and consequential source anchors. Source review used non-mutating YAML/JSON parsing. No audited grader, validator, installer, imported refresh, native model test or implementation acceptance run occurred. The formal canonical-document lint below is separate from those audited workflows.

Combined record checks passed for the 25-ticket graph (eight closed, sixteen open, one claimed), exact dependencies, no cycles or missing blockers, all 638 coverage rows, 61 primary hashes, eighteen fixture hashes, seventeen unique findings, local paths/anchors, formatting and fog delimiters. Parent separately verified all five bounded dependency hashes unchanged. `rtk git diff --check` passed, and the protected source diff is empty. These checks verify audit records, not native behavior.

The formal Update Agent Docs pass added one bounded RLW-001 issue pointer in `.agents/memory/known-issues/skills.md`; the earlier installer pointer remains. Existing INDEX/FILE_MAP routes cover the records; no new global policy or protected skill source was chosen. OKF Authoring loaded the profile branch (no source-summary branch), retained Known Issue metadata and file-relative links, and `rtk proxy ./scripts/lint-okf.py` exited 0. Added: None. Changed: skills known-issues pointer. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None.

Current source-review settings selected and submitted `gpt-6.1-sol`/`high`; executed settings/usage are unconfirmed. Dispatch started 16:40:49 UTC, with a twenty-minute initial limit through 17:00:49 UTC and five-minute saved checkpoints. Parent inspected saved progress and requested status. Completion was observed 16:59:03 UTC before the limit, without interruption or extension. Parent verified the output; report ownership was released before reconciliation. The report retains the structured dispatch audit. The earlier dispatch remains recorded in its own report. Neither is a native baseline.

Tool Guardian rejected a long reviewer helper command. Direct helper patches and short RTK commands recovered it without weakening controls. Parent corrected a guessed hook filename through enumeration and fixed a disposable extraction regex before canonical writes; assertions remained. The final finding index is continuous. These are resolved record-processing issues, not skill-source defects. RTK 0.50.0 works; its gain database is unavailable in this sandbox.

## Discussion Surface

[Visual design overview](design-map.html) is a dated 2026-10-05 inline view of the prior agreed design, not live review status or an approval record. No discussion notes were supplied. Host draft restoration is best-effort; exported text supports explicit discussion. Its earlier browser checks are historical, not native audit evidence. Use Codex's visualization surface, not a standalone-page assumption.
