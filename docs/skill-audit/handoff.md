# Skill Authoring Audit Handoff

## Goal and Status

Complete the evidence-backed audit of non-imported maintained skills, then write `docs/skill-audit/audit.md` and a self-contained `docs/skill-audit/ExecPlan.md`. Skill implementation, installation, and publication follow this effort.

The [map](map.md) now has 24 tickets: eight closed and sixteen open. [Review Skill Authoring and Repository Guidance](tickets/review-skill-authoring-and-repository-guidance.md#resolution) is closed after static investigation and live human proposal review. Its exact two blockers were verified closed before claiming. No other primary batch started and no native audit baseline ran.

The current candidate pool is 37: 32 published plus five repository-local skills. Twenty-three configured imports are excluded. Unknown historical origin does not block a candidate; clear additional import evidence removes it. Current scope remains in [the inventory](local-inventory.md#current-audit-scope) and [coverage index](coverage.md).

## Next Focus and Exact Next Step

Next session, claim [Review Repository-local Workflows](tickets/review-repository-local-workflows.md) after verifying both exact blocking filenames are closed. Review its five owned entry points and resources, using the existing 58-check catalog and single findings register; gather source facts before live human disposition. Do not edit repository-local skill sources or launch native baselines. If the human prioritizes one of the four separate decisions, select that ticket instead.

The human answered all three first-batch review questions on 2026-10-05. These answers are recorded in the owning Resolution and finding register:

1. Accepted authoring repairs: SAG-001, 009, 010, 011, 012, 014, plus only SAG-013's documentation cleanup. Preserve names, invocation controls, approval boundaries, required dependencies and output contracts. Actual client enforcement under SAG-012 remains unverified.
2. Accepted evaluation repairs: SAG-004, 005, 006 and 007. Preserve duplicate avoidance and identity, response-only Improve Skill and loaded-target conditions, restored notes fixtures, and meaningful preservation checks. Ground exact fixture/oracle choices in documented current overlap before executable plan readiness.
3. Retained separate pending questions: SAG-002 installer authority, SAG-003 body structure, SAG-008 unknown metric representation, and SAG-013 execution authority. Leave dependent implementation pending and every ID visible in both final documents. This is not a behavior or metric choice, waiver, residual-risk acceptance, or execution approval.

The [single finding register](findings.md) contains the concrete evidence, proposals, validation, recorded human status, exact decisions and linked routes. No proposal was rejected or deferred. Approval concerns later plan scope only; it does not authorize implementation. This logical session resolved only this one non-research ticket. Do not claim or resolve another ticket before a new session.

The four separate decisions are now unblocked by this review ticket, but remain open. Do not silently resolve them from approval of proposal routing. All twelve static scopes must finish before reconciliation and baseline selection.

## Completed Static Evidence

- [Coverage](coverage.md) defines 58 stable checks: 38 authoring checks covering all 36 source bullets, four security checks, twelve repository checks and four client checks. Applicability, adoption disposition, compliance, review completion and runtime evidence are distinct.
- [Batch report](reports/review-skill-authoring-and-repository-guidance.md) records six primary skills, 45 hashed/read bundle files, bounded supporting-source inspection, protected contracts and six complete 58-check matrices (348 rows).
- [Findings](findings.md) owns fourteen records once: seven major, five minor, two observations. These are static evidence and inferred consequences, not observed native skill failures. Ten findings are accepted for later planning, SAG-013 has a split accepted/pending disposition, and SAG-002/003/008 remain pending. Four precise questions have separate open decision tickets.
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

Parent verification confirms all 45 bundle hashes unchanged, six matrices containing exactly the 58 catalog IDs, preserved static/runtime distinctions, JSON parse evidence, and source anchors for consequential findings. No grader, validator, installer, imported refresh, native model test or implementation acceptance run occurred.

Final record checks verify the 24-ticket graph (eight closed, sixteen open), exact dependencies, no cycles or missing blockers, all 348 coverage rows, 45 unchanged source hashes, fourteen unique finding records, local paths/anchors, formatting, and fog delimiters. `rtk git diff --check` passes. These are audit-record checks, not native behavioral evidence.

The formal Update Agent Docs pass added one bounded issue pointer in `.agents/memory/known-issues/skills.md` for the unresolved installer authority conflict. Existing INDEX/FILE_MAP routes cover the new effort records; no new global policy or skill source was chosen. OKF Authoring loaded the profile branch (no source-summary branch), retained Known Issue metadata and file-relative links, and `rtk proxy ./scripts/lint-okf.py` exited 0. Added: None. Changed: skills known-issues pointer. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None.

Source-review settings submitted `gpt-6.1-sol`/`high`; executed settings/usage are unconfirmed. Dispatch started 15:52:49 UTC, with the repository's 20-minute initial limit and five-minute saved checkpoints. At the limit, status checks found active work and usable source/proposal checkpoints. A ten-minute extension through 16:22:49 UTC covered matrix persistence/refinements after diagnosed input limits. Completion was observed 16:19:04 UTC without interruption. Parent verified the output. This delegation is not a native behavioral baseline.

Tool Guardian rejected long prose/table shell inputs. Small direct patches plus disposable helper files and short RTK commands succeeded without approval escalation or weakened settings. Match full current lines when patching long paragraphs; an independent small patch recovered from a stale-context rejection. These lessons reinforce existing guidance rather than creating new global rules. RTK 0.50.0 works; its gain database is unavailable in this sandbox.

## Discussion Surface

[Visual design overview](design-map.html) is a dated 2026-10-05 inline view of the prior agreed design, not live review status or an approval record. No discussion notes were supplied. Host draft restoration is best-effort; exported text supports explicit discussion. Its earlier browser checks are historical, not native audit evidence. Use Codex's visualization surface, not a standalone-page assumption.
