# Skill Authoring Audit Handoff

## Goal and Status

The destination is a completed audit of non-imported maintained skills plus a self-contained implementation ExecPlan. The twenty-ticket map contains seven closed tickets and thirteen open tickets. No ticket remains claimed. [Set Audit Completion and Implementation Gates](tickets/set-audit-completion-and-implementation-gates.md#resolution) is closed after the human accepted all six policies and the explicit proposal-tracking clarification. The current audit pool has 37 candidates: 32 published and five repository-local entry points, after excluding 23 configured imports.

All planning artifacts are feature-scoped under `docs/skill-audit/`, as the user explicitly requested. Resume from [Skill Authoring Audit](map.md).

## Confirmed Constraints

- Review the 32 remaining published candidates and all five repository-local candidates. Remove any additional imports established by clear evidence. The original 60-entry total remains inventory history, not current audit scope. Exclude snapshots, generated benchmark outputs, and fixtures.
- Imported skill bundles, imported-derivative maintenance, historical provenance recovery, and a lasting provenance ledger are outside this effort. Check shared resources only as dependencies of included skills; do not audit or revise excluded bundles.
- Complete static review plus targeted safe OpenAI baselines. The [evidence contract](tickets/set-audit-evidence-and-model-coverage.md#resolution) selects native Codex CLI, up to three risk-selected fixture-ready skills, three fresh runs per model/scenario, separate activation/workflow/output grading, and complete run records. Required missing evidence blocks the completed-audit label unless explicitly waived. Define broader candidate validation in the implementation ExecPlan.
- Preserve intended behavior and approval rules. Present behavior redesigns separately.
- Use the seven exact native IDs in the evidence contract at explicit `medium` effort. The user confirmed Terra means `gpt-5.6-terra`. Local catalog advertisement is verified; account access, effective runtime selection, and baseline execution remain untested. Do not silently substitute configurations.
- The user waived `domain-modeling`. Continue with Wayfinder and Grilling.
- Keep the map, tickets, research, handoff, and final deliverables in `docs/skill-audit/`, not the scratchpad.
- Final deliverables are `docs/skill-audit/audit.md` and `docs/skill-audit/ExecPlan.md`. Skill implementation, installation, and publication follow this effort.
- The [completion-gates decision](tickets/set-audit-completion-and-implementation-gates.md#resolution) separates audit completion, executable plan readiness, and later candidate acceptance. Unresolved redesigns and proposals requiring new approval retain stable finding IDs, exact decisions needed, affected work, decision tickets when precise, and visible pending-decision entries in both final documents. Deferral never removes a genuine dependency or bypasses protected controls.
- The [batch/report decision](tickets/choose-audit-batches-and-evidence-format.md#resolution) defines twelve review scopes, per-check Markdown coverage, one findings register, shared-resource ownership with consumer checks, and human review after each batch. Complete static review before reconciliation and baseline sample selection. No sample is selected yet.
- The human authorized a narrow static paper-reading exception for `dotnet-upgrade` within this audit. Preserve all invocation, migration approval, execution, installation, packaging, validator, and live-evaluation restrictions. This does not activate its upgrade procedure.
- Follow the [canonical subagent checkpoint rule](../../.agents/instructions/repo.md#subagent-checkpoints), approved after repeated premature interruptions. Missed checkpoints trigger status checks. Do not reuse the short historical limits below as defaults.

## Next Focus

Claim [Review Skill Authoring and Repository Guidance](tickets/review-skill-authoring-and-repository-guidance.md), the first allocated review scope. Verify its exact blockers, `choose-audit-batches-and-evidence-format.md` and `set-audit-completion-and-implementation-gates.md`, are closed before assigning a new six-character claim. Review its six primary skills and maintained resources; create the shared check catalog/coverage index, findings register, and batch report when review begins, without prefilled passing claims. Gather source facts, then obtain the human's proposal dispositions through Grilling. Use the approved subagent checkpoint rule for delegated fact gathering. Do not resolve a second non-research ticket in the session that closed completion gates.

[Set Audit Completion and Implementation Gates](tickets/set-audit-completion-and-implementation-gates.md#resolution) records first-round acceptance and the tracking clarification on 2026-10-02, followed by acceptance of all remaining recommendations on 2026-10-04. No gate question remains pending. Ten independent static review scopes are now unblocked; the two resource scopes retain their respective instructions-review blockers. No review ticket is claimed yet.

[Choose Audit Batches and Evidence Format](tickets/choose-audit-batches-and-evidence-format.md#resolution) records all seven human-confirmed policies from four rounds. The two common blockers for all twelve review tickets are closed; the two resource reviews also depend on their corresponding instructions review. [Reconcile Static Findings and Select Baseline Cases](tickets/reconcile-static-findings-and-select-baseline-cases.md) remains blocked by all twelve reviews and now explicitly requires accounting for every proposal under the accepted gates. Those tickets gather source evidence, then require live human disposition decisions; they do not implement changes.

[Batch sizing evidence](batch-sizing-evidence.md) contains all 37 verified measurement rows and a bounded explicit-dependency scan. The second explorer completed without interruption under the longer limit; executed model/effort remain unconfirmed. Parent source checks corrected dependency/role distinctions, an input flag mistaken for a skill dependency, and conditional scope. Complete dependency closure, fixture readiness, and full static compliance remain unverified. Only `dotnet-upgrade/SKILL.md` and its `agents/openai.yaml` were read under the paper exception. No agent remains active and no audit baseline ran.

[Set Audit Evidence and Model Coverage](tickets/set-audit-evidence-and-model-coverage.md#resolution) records nine human-confirmed policies from four rounds. [Model and Baseline Evidence](evidence-model-baselines.md) records the native catalog, help and configuration evidence, limited eval-input checks, delegation timeouts, and unverified prerequisites. Handoff, Spec to Tasks, and OKF Authoring have promising existing inputs; they are not selected or certified fixture-ready. Explore and Create Skill illustrate additional limitations.

No complete isolated native launch recipe or grader compatibility check exists yet. The catalog does not prove account execution. Preserve these gaps when creating later baseline tickets; do not fill them by weakening controls, adding missing fixtures silently, or running a global installer. The actual sample depends on bounded content and fixture review.

[Decide Skill Ownership and Import Handling](tickets/decide-skill-ownership-and-import-handling.md#resolution) records the final scope. The human rejected the lasting provenance proposal and instead excluded imported skills; this supersedes the earlier derivative-maintenance choices in the same exchange. Keep accepted improvements in both roots with exact implementation targets and the existing documentation-maintenance restrictions. Do not resurrect ledger or import-refresh work from earlier answers.

[Current audit scope](local-inventory.md#current-audit-scope) lists all 32 published candidates. Unknown historical origin alone does not block review, but clear additional import evidence removes a candidate. [Import and Packaging Evidence](import-ownership-evidence.md) records the exclusion mappings, read-only delegation, and parent source checks. The original inventory now correctly attributes `show-me` to `humanlayer/skills` and records the four unprefixed Addy state values.

[Set Adoption Rules and Protected Behavior](tickets/set-adoption-rules-and-protected-behavior.md#resolution) holds the human-confirmed rubric, behavior contracts, exception policy, finding severities, and evidence fields. Apply it within the reduced scope.

Final audit and implementation-plan authoring remain in the fog until actual findings and behavioral evidence make their scopes precise. No new baseline sample, launch recipe, or authoring improvement was selected by the gate decision.

Read the [authoring checklist](research/authoring-checklist/findings.md) and [provider comparison](research/provider-compatibility/findings.md) as needed. The latter is dated source research; the newer evidence ticket resolves the Terra identity and native IDs/efforts while retaining the runtime verification gaps.

## Verification

Read-only Python checks pass for the twenty-ticket graph, metadata, exact dependencies, cycles, seven closed-ticket resolutions and named map links, local Markdown links/anchors, whitespace, and fog delimiters. The graph has seven closed tickets, thirteen open tickets, and no claims. Ten independent review scopes are unblocked; both resource reviews and reconciliation remain blocked by their retained dependencies. The next named review is verified eligible. `rtk git diff --check` passes. All six gate policies and the proposal-tracking clarification are confirmed; no human gate answer remains pending. No behavioral baseline, full skill audit, or implementation acceptance run has occurred.

The formal Update Agent Docs pass reviewed the final diff, user clarification, routing, document quality, and indexes. This session changes four effort documents only. Existing canonical workflow guidance and `FILE_MAP.md` routes already cover this effort; feature-specific gate and proposal policies remain in their owning decision. Added: None. Changed: None. Split or moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None. No canonical semantic edit requires an OKF pass in this session. The earlier checkpoint-rule update remains in `.agents/instructions/repo.md`, routed by `.agents/memory/INDEX.md`; its previously recorded OKF result is historical. No skill source or tooling implementation changes.

## Resolved Execution Friction

Tool Guardian rejected an oversized multi-file patch because its input exceeded the command-segment limit. Smaller patches succeeded. The protected scratchpad parent required an approved directory creation; files were subsequently moved into the user-requested docs location. Keep future patches bounded and use the docs location directly.

The resumed session's temporary commit-message replacement used delete and add operations for the same path in one patch. `apply_patch` rejected the duplicate target; a single update operation succeeded. Use one operation per path within a patch.

`rtk --version` reports 0.50.0, and the binary resolves to `/Users/adam/homebrew/bin/rtk`. `rtk gain` cannot open its tracking database in this sandbox; ordinary RTK commands work. This does not block planning.

The provider research reached its 600-second limit before writing findings. The parent interrupted it and resumed the same configured agent for a 180-second recovery limited to saving collected evidence. Findings and a closed resolution were written before the parent stopped the recovery at its next deadline check. Parent source checks corrected the Codex metadata-budget wording: 8,000 characters is the fallback for an unknown context window, not a cap compared with 2%. Preserve source conditions and units when translating numeric rules.

Both research tasks used explicitly submitted `gpt-6-luna` with `max` effort; executed runtime values remain unconfirmed. The parent verified the final artifacts against the tickets and checked key claims against Claude, OpenAI, GitHub, and Gemini primary documentation.

The ownership explorer used explicitly submitted `gpt-6-luna` with `medium` effort and a 300-second parent-enforced limit; completion was checked at 105 seconds. Executed runtime values remain unconfirmed. Parent verification corrected its prefixed state-file wording and unsupported absence inference: all 19 mapped multi-source destinations exist. Preserve the distinction between configured origin, current file presence, and verified historical provenance.

The evidence explorer used explicitly submitted `gpt-6-luna` with `max` effort. The parent interrupted its 360-second fact-collection attempt and its one 90-second report-only recovery at their deadlines. Only partial model facts were returned; the parent verified the native catalog and independently collected the limited help/JSON observations. Fixture readiness remains unknown. Avoid making a broad source-collection report the only durable output before a deadline.

`codex exec --help` for 0.159.3 does not advertise the `--full-auto` flag shown in a dated official eval example. Use current help and configuration evidence, then verify effective permissions and discovery. `--ignore-user-config` does not establish isolated skill loading. A guessed configuration-reference URL returned 404; following the official navigation located `https://learn.chatgpt.com/docs/config-file/config-reference`. Do not infer a broken source from an unverified URL.
