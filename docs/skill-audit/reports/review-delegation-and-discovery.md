# Review Delegation and Discovery

Started 2026-10-05. Source baseline: `991b14b86440dab452ac28312c5f05a2b4a42266`. Static source investigation complete; human proposal review and all runtime evidence remain pending. Source-review ownership was released before parent reconciliation.

## Scope and evidence boundary

Primary scope is every maintained file under `skills/{delegate-to-subagents,subagent-model-router,explore,official-sources,explain-your-thinking}/`, including evaluation definitions and graders. Fixture inputs are recorded separately. Generated output, snapshots and fixture entry points are excluded as primary skills. No skill source, canonical `.agents/` document, installer or imported helper was changed. No grader, validator, packaging, native baseline, installer/importer or migration was executed. JSON/YAML were parsed as data. Source facts do not confirm runtime model settings, native discovery or behavior.

The [58-check catalog](../coverage.md#check-catalog), [adoption policy](../tickets/set-adoption-rules-and-protected-behavior.md#resolution), [report contract](../tickets/choose-audit-batches-and-evidence-format.md#report-contract), and [evidence contract](../tickets/set-audit-evidence-and-model-coverage.md#resolution) govern this review. Audit baselines, when selected later, use native Codex CLI only; Copilot CLI/VS Code and Gemini remain static compatibility comparisons, and desktop behavior is untested. Create Skill and Skill Creator were loaded solely as planning/review guidance; their execution workflows were not activated. Domain-modeling is waived only for this effort. Existing accepted contracts and five separately pending decisions remain unchanged.

## Exact reviewed inventory

All fifteen primary files and seven fixture dependencies have been read in full as static source. All twenty-two files are byte-identical to the declared Git baseline. Evaluation Python was not imported or run. Hashes are source evidence, not model-run snapshots.

| File | Bytes | Lines | SHA256 | Role | Reading status |
| --- | --- | --- | --- | --- | --- |
| [skills/delegate-to-subagents/SKILL.md](../../../skills/delegate-to-subagents/SKILL.md) | 12184 | 308 | `670318c390b55da662f617e2e1d2538da299f4f151b3c82f03bb9443ffa9ef32` | maintained entry/resource | read |
| [skills/subagent-model-router/SKILL.md](../../../skills/subagent-model-router/SKILL.md) | 8127 | 168 | `7de60f23f3152164ee4b9dd0c7caa329b9aa42f57f44677c14f54b26b61a5ac1` | maintained entry/resource | read |
| [skills/subagent-model-router/reference/escalation-policy.md](../../../skills/subagent-model-router/reference/escalation-policy.md) | 3110 | 74 | `daa87e78bda5bfb9b5eeca56005886636a1086ee2a791e0b1c804518d44c1e77` | maintained entry/resource | read |
| [skills/subagent-model-router/reference/model-catalog.md](../../../skills/subagent-model-router/reference/model-catalog.md) | 8249 | 138 | `49a4f81bace60ad3d68842e677e6163789813572366adf55cee9e76e8697a3b7` | maintained entry/resource | read |
| [skills/subagent-model-router/reference/patterns.md](../../../skills/subagent-model-router/reference/patterns.md) | 2811 | 61 | `3c93cdc50f214b5d8831c3b4bc5139127278b97fcf99ca4f270aa34a210bbbe9` | maintained entry/resource | read |
| [skills/subagent-model-router/reference/pricing.md](../../../skills/subagent-model-router/reference/pricing.md) | 6318 | 106 | `d7ac81879a09a460f842a3fa86889313c3adb1ac4719c0876e53419f913d203e` | maintained entry/resource | read |
| [skills/subagent-model-router/reference/review-routing.md](../../../skills/subagent-model-router/reference/review-routing.md) | 2609 | 61 | `8da047069ddf7db33243a4d4c9253525e999977f30aa9135a8fec9b17135fd1f` | maintained entry/resource | read |
| [skills/explore/SKILL.md](../../../skills/explore/SKILL.md) | 1305 | 38 | `5fefe9f992e78ddac3642698d1ea824f54e1216c7b63b42441640b02b826f83b` | maintained entry/resource | read |
| [skills/explore/evals/evals.json](../../../skills/explore/evals/evals.json) | 3304 | 61 | `6b76f05ed6e048e26f5a176d28bf25cc72d1dd63ee091bd5117666745bf8fb25` | static evaluation | read |
| [skills/explore/evals/grade_benchmark.py](../../../skills/explore/evals/grade_benchmark.py) | 7147 | 192 | `6b0ee92507345c118322e75ddc7445f2c9afda67f8da7887e2adab187f213f64` | static evaluation | read |
| [skills/official-sources/SKILL.md](../../../skills/official-sources/SKILL.md) | 3121 | 55 | `593ff089223b7f86ef6966a9e361780065ffca5bc65b7039855c3966137d05b0` | maintained entry/resource | read |
| [skills/official-sources/evals/evals.json](../../../skills/official-sources/evals/evals.json) | 8436 | 124 | `12059958abbb9a58861a23a219911a7aca13909e119b54d621285a25b2dd6d3f` | static evaluation | read |
| [skills/official-sources/evals/grade_benchmark.py](../../../skills/official-sources/evals/grade_benchmark.py) | 12661 | 348 | `c1000dc4488f11778cec2c28f2f8bd9310924329d86d4dc1bf4e80b13a14fbd1` | static evaluation | read |
| [skills/explain-your-thinking/SKILL.md](../../../skills/explain-your-thinking/SKILL.md) | 588 | 14 | `547eb3a080dd96180f52d4b63c63aa07dc2ad7ebd8252cc711a91a18318c98b9` | maintained entry/resource | read |
| [skills/explain-your-thinking/agents/openai.yaml](../../../skills/explain-your-thinking/agents/openai.yaml) | 43 | 2 | `a1499d95abd8447558c535fe5554adcc3c9b988a0a39264a6283d430effe1e94` | maintained entry/resource | read |

### Fixture dependencies

| File | Bytes | Lines | SHA256 | Role | Reading status |
| --- | --- | --- | --- | --- | --- |
| [skills/official-sources/evals/files/agnostic-fixture/README.md](../../../skills/official-sources/evals/files/agnostic-fixture/README.md) | 92 | 1 | `e81248d7bf670c20bb4b609c5726f48fb4e64806350778d70a7f571c77a2e661` | fixture dependency | read |
| [skills/official-sources/evals/files/missing-version-fixture/requirements.txt](../../../skills/official-sources/evals/files/missing-version-fixture/requirements.txt) | 7 | 1 | `68f552418963a8100befe5a0664747d95d9a9a4b4a4c30546576f80c1c87598a` | fixture dependency | read |
| [skills/official-sources/evals/files/missing-version-fixture/src/auth_flow.py](../../../skills/official-sources/evals/files/missing-version-fixture/src/auth_flow.py) | 68 | 5 | `4d74dc9e13b0340536a77d6d50e8f1d01c250e64c8049b6d9fa187e1b83be29c` | fixture dependency | read |
| [skills/official-sources/evals/files/next-conflict-fixture/package.json](../../../skills/official-sources/evals/files/next-conflict-fixture/package.json) | 127 | 8 | `2198e35bb6eba25facf54178136330a4024237809ce537e43e212fb9d64e1cdf` | fixture dependency | read |
| [skills/official-sources/evals/files/next-conflict-fixture/src/use-dashboard-router.ts](../../../skills/official-sources/evals/files/next-conflict-fixture/src/use-dashboard-router.ts) | 105 | 5 | `f6e2b4b6fc8de47f490e080c0122e54aee9feee7587c2ce21370f7364332b1fe` | fixture dependency | read |
| [skills/official-sources/evals/files/react-router-fixture/package.json](../../../skills/official-sources/evals/files/react-router-fixture/package.json) | 137 | 8 | `bce7bc8882a84e348964dad089f38ba1687ff37ba8f388a73bdeb28ca5fbf744` | fixture dependency | read |
| [skills/official-sources/evals/files/react-router-fixture/src/nav.ts](../../../skills/official-sources/evals/files/react-router-fixture/src/nav.ts) | 159 | 6 | `56b41733d8d37a604a60ec96f5da9e1d8f87cbd0ec3e3658a50708c73cdd3323` | fixture dependency | read |

### Metadata and source checks

All five entry records parse with the checked-in vendored YAML runtime, have string name/description, and use directory-matching lowercase kebab-case names shorter than 64 characters. All descriptions are nonempty and below the source-specific 1,024-character advice, with no XML tags. Body lengths are facts, not defects.

| Skill | Name characters | Description characters | Body lines | Frontmatter keys |
| --- | --- | --- | --- | --- |
| delegate-to-subagents | 21 | 251 | 303 | name, description |
| subagent-model-router | 21 | 202 | 163 | name, description |
| explore | 7 | 157 | 33 | name, description |
| official-sources | 16 | 272 | 50 | name, description |
| explain-your-thinking | 21 | 49 | 8 | name, description, disable-model-invocation |

Formatting observations: skills/explore/evals/grade_benchmark.py:116 trailing whitespace; skills/explore/evals/grade_benchmark.py:121 trailing whitespace; skills/explore/evals/grade_benchmark.py:143 trailing whitespace; skills/explore/evals/grade_benchmark.py:145 trailing whitespace; skills/explore/evals/grade_benchmark.py:156 trailing whitespace. No CR bytes detected.

Body line counts exclude YAML frontmatter, delimiter lines and leading blank lines after frontmatter.

## Purpose and protected contracts

| Skill | Purpose and preserved contracts | Source anchors |
| --- | --- | --- |
| delegate-to-subagents | Delegate only when benefit justifies coordination; mandatory router; preserve prior constraints and route-before-approval sequence; exact explicit model/effort, no implicit defaults; dispatched runtime limit; prompt isolation; selected/submitted/executed distinction; no self-report confirmation; ownership/dependency waves; limited replacements and fail-closed routing. | SKILL.md:8-59,65-110,152-177,181-248,258-308 |
| subagent-model-router | Minimize expected completion cost among exact dispatchable configurations above the capability floor; preserve prior user constraints; no model-permission question; Standard substantive review/Premium sensitive review; evidence hierarchy; same-tier fallback before promotion; concrete route or dispatchable false. | SKILL.md:8-48,50-108,112-158; reference/review-routing.md:3-61; reference/escalation-policy.md:5-74 |
| explore | Produce concise code map before editing; reuse relevant session/current notes; narrow scope uses direct reads without subagents; otherwise one code-explorer per 1-3 independent areas through delegation; synthesize then save topic notes; bounded direct dependencies; no raw dumps or repeated exploration. | SKILL.md:8-17,21-38 |
| official-sources | Detect stack/version, clarify material uncertainty, prefer version-matching official authorities, stop once verified, avoid weak primary sources, surface conflicts for human choice, explicitly mark UNVERIFIED, conditional exact-match cache, useful delegation through required helper. | SKILL.md:10-55 |
| explain-your-thinking | Explicit invocation controls retained; arguments request explanation of prior action only, never redo/reverse/execute; concise decision, rationale and applicable rules; ask if the action is unclear. | SKILL.md:2-14; agents/openai.yaml:1-2 |

## Dependencies, ownership and consumer navigation

This batch owns delegation, routing, exploration, official-source procedure and explanation source. Router catalog owns tier membership/task defaults; review-routing owns review floors; escalation-policy owns escalation. Patterns are explicitly non-authoritative. The entry links all five references with selection criteria (router SKILL.md:73-79,162-168). Pricing and catalog are 106/138 lines with descriptive section headings and tables; no concrete navigation failure is established from their lack of a table of contents. Price and retirement facts remain the 2026-09-29 snapshot, including already-past scheduled dates. They were not fetched or refreshed, and do not establish current prices, availability or provider-supported effort. Catalog :13,19-28,115-138 explicitly separates local configuration choices from runtime support and requires rechecking.

Delegation requires router at :17,85 and isolates routing/audit metadata from task prompts (:168-175). Exploration and official-sources require activation/loading of delegation (:15 and :48); no new optionality is proposed. The canonical `agents/code-explorer.md:1-20` exists for the named exploration role; this bounded existence/mission check does not prove installation or supported assignment in each host. Published consumer skills checked at their call sites include `code-review/SKILL.md:21,25-28`, `adversarial-review/SKILL.md:9-15`, `code-simplify/SKILL.md:10`, `techdebt/SKILL.md:13`, `prd/SKILL.md:29-31`, `spec-to-tasks/SKILL.md:35-40`, `architecture-design-contest/SKILL.md:140-142`, `execplan-implement/SKILL.md:19-44`, and `prd-ralph-loop/SKILL.md:19-39`. Quality, requirements and execution batches own their full consumer contracts. Consumer instructions preserve distinct review roles, fresh implementer nodes, blind PRD task selection and ordered integration. Imported `grilling/SKILL.md:28` is only a bounded consumer call, not a new audited primary skill.

The execution owner should reconcile retry counting when reviewing `prd-ralph-loop/SKILL.md:34`: the loop counts three consecutive failed agent runs, while delegation :246 limits replacements of a failed compliant subtask unless the user authorizes more. This does not establish a contradiction without resolving whether each loop run is a new node or a replacement, and whether explicit loop invocation authorizes its documented retry budget. Both contracts are retained; no new behavior choice is proposed from this ambiguity alone. Parent has added this exact consumer check to the [owning execution review](../tickets/review-execution-and-handoff.md) for visible later reconciliation.

Exploration notes and official cache use exact scratchpad paths; repository-promoted artifact locations take precedence under `.agents/instructions/repo.md:13-16`. The short outputs have no schema enforcement claim. Cache freshness for unchanged versions/current guidance and source-data trust are runtime evidence gaps; missing chronology alone does not prove stale advice. Explanation's `$ARGUMENTS` binding is host-specific; [SAG-012](../findings.md#sag-012-argument-binding-and-control-adapter-evidence-gaps) owns the analogous evidence concern. Its prior accepted target scope is not expanded by this link.

`scripts/install.sh:40-55` and `install.ps1:251-269` copy non-eval source and prune per-skill evals/README/licenses. All eleven non-eval primary files here ship; four evaluation files and seven fixtures do not. Installed source/resource access remains untested. Explanation's sidecar is a Codex adapter; the frontmatter control is preserved separately. Neither proves equivalent Copilot VS Code or Gemini behavior. The documented required-client constraints remain the dated [provider comparison](../research/provider-compatibility/findings.md), not fresh runtime evidence. Activation consent and tool permissions remain independent. Delegate/router's no-extra-model-confirmation rule does not bypass prior human-requested approval or actual host permission (:25,181-189).

Excluded helper `skill-creator/scripts/quick_validate.py:42-50` rejects explanation's retained control. The repository [known issue](../../../.agents/memory/known-issues/skills.md) and [SAG-001](../findings.md#sag-001-validation-prerequisites-and-retained-control-exceptions) explain that tooling limitation. No validator was run, no control removed, and no excluded-helper redesign proposed. [SAG-002](../findings.md#sag-002-installer-ownership-conflict) remains the pending installer-authority decision; no installation occurred.

An initial consumer search used a glob that did not exclude nested workspace paths. Its generated matches were discarded and a corrected bounded search excluded `**/*-workspace/**`, `**/evals/**` and `**/archive/**`; no generated artifact informs the findings or coverage. This is audit process evidence, not a skill defect.

## Findings and live review

The single [finding register](../findings.md) owns all five records once. Static investigation is complete; the human has not reviewed their proposals. [DD-001](../findings.md#dd-001-explore-spawn-grading-omits-independent-area-assertions), [DD-002](../findings.md#dd-002-evaluation-setup-does-not-establish-required-prior-context-or-cache-hit), [DD-003](../findings.md#dd-003-official-source-graders-equate-text-mentions-with-citation-and-cache-evidence), [DD-004](../findings.md#dd-004-graders-can-announce-success-without-grading-runs-and-do-not-validate-json-shape), [DD-005](../findings.md#dd-005-explore-grader-contains-prohibited-blank-line-whitespace). DD-004's exact incomplete/invalid outcome protocol has a separate [failure-outcome decision](../tickets/define-benchmark-grader-failure-outcomes.md), blocked by this batch review. Existing five decision routes remain open and unblocked.

Two newly evidenced zero-filling producers are recorded under [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero): Explore grader :49,59-70 and Official Sources grader :38,47-58. Including these targets in the existing [metric decision](../tickets/choose-unknown-benchmark-metric-representation.md) awaits human disposition; the representation remains unchosen. Analogous SAG-001/SAG-012 consumer links do not expand earlier accepted targets.

## Positive results and unresolved evidence

Delegation already separates selected, submitted and runtime-confirmed execution values, rejects implicit defaults, prints routes before approval, limits nesting/retries and defines failure records. Router already distinguishes capability from price/family/recency, preserves floors on unavailable models, diagnoses environment problems before escalation, dates provisional sources and checks accepted runtime values. Explore has a small core, direct-read narrow branch and context reuse. Official Sources has version-sensitive questions, bounded relevant URLs and explicit gaps/conflicts. Explanation preserves both controls and only explains prior actions. These static strengths do not prove behavior.

Explore's three and Official Sources' six evals are inspectable scenario definitions; no grader was executed and no native run was selected. Delegation, router and explanation have no bundled evals. Missing baselines, model coverage, fresh-session iteration, team-use evidence, installed-file traces, consent enforcement and argument binding remain unresolved evidence gaps, not invented defects or an incompatible disposition. The Next fixture lacks router-mode/layout context beyond the helper import; version alone and its expected oracle do not certify which framework pattern is appropriate. That scenario requires qualified native/version evidence before current guidance is claimed; this review does not choose a migration.

## Static completion checkpoint

Source reads/hashes, contracts, bounded consumer checks, candidate records and five independent 58-check matrices are complete. Static source investigation is complete with disclosed defects and evidence gaps. Human disposition and runtime evidence remain pending.

Non-mutating record verification independently counted all five matrices as 58 unique catalog IDs in catalog order, 290 rows total, and rechecked all twenty-two hashes against current bytes. Both evaluation Python files parse as AST without importing or executing them. JSON/YAML data parsing and source whitespace inspection were scoped to this inventory. Parent independently checked the declared Git baseline; no primary source changed. Final report whitespace/table-shape checks passed. These checks verify the saved audit record, not grader behavior or native skill compliance. Parent owns shared finding/coverage/ticket reconciliation, human review, and the single end-of-session canonical document pass.

## Per-skill coverage matrices

Each matrix contains every stable catalog ID exactly once. The catalog owns criteria, strength, applicability and source provenance. Evidence anchors are relative to the named skill unless a dependency path is named. `adapt` translates advice to required hosts and preserves the contract; it is never a passing result. Static completion does not close human disposition or native evidence gaps. No row selects incompatibility merely from absent evidence. The single findings register owns reconciled DD records; cross-links to SAG records preserve their accepted/pending scope.


### delegate-to-subagents

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: concrete task purpose and procedure | SKILL.md:8-59,65-110,152-248,258-308 |  | Context cost unmeasured |
| A02 | Exact route/dispatch gate | adapt | Static: precise gate; runtime enforcement needs host mechanism | SKILL.md:40-59,152-156,193-210 |  | Supported timeout/control mechanism untested |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | Shared evidence contract; reviewed inventory |  | No selected native baseline or model runs |
| A04-F | Entry YAML | adapt | Static: parsed required string name/description | SKILL.md:1-5; metadata checkpoint |  | Native parser/discovery untested |
| A04-N | Name format | adapt | Static: directory match, lowercase kebab-case, <=64 chars | SKILL.md:2; metadata checkpoint |  | Required-client native enforcement untested |
| A04-D | Description bounds | adapt | Static: nonempty, <1024 chars, no XML tags | SKILL.md:3; metadata checkpoint |  | 1024 is source-specific advice |
| A05 | Preserved meaningful identity | adopt | Static: name denotes stated purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Capability and trigger description | adapt | Static: bounded declared purpose | SKILL.md:3; SKILL.md:8-59,65-110,152-248,258-308 |  | Activation outcome requires traces |
| A07 | Focused entry | adapt | Static: entry stays within stated task | SKILL.md:8-59,65-110,152-248,258-308; metadata checkpoint |  | Length alone is not a defect |
| A08 | Required router dependency | adapt | Static: direct named call with inputs | SKILL.md:17,85-110 |  | Native dependent skill load untested |
| A09 | Approval/reuse/fallback branches | adapt | Static: conditional gates preserve prior constraints | SKILL.md:25-36,110,179-248 |  | No runtime branch trace |
| A10 | Named router navigation | adapt | Static: required skill named at exact route step | SKILL.md:17,85 |  | Named skill resolution untested |
| A11 | No >100-line procedure reference | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A12 | Dispatch values and allowed resources | adapt | Static: exact values and ownership specified | SKILL.md:65-75,98-110,152-177 |  | Actual runtime dispatch interface untested |
| A13 | Workflow order | adopt | Static: concrete procedure ordering | SKILL.md:8-59,65-110,152-248,258-308 |  | Native sequencing untested |
| A14 | Coordinator verification/audit | adapt | Static: mismatch recovery and output checks explicit | SKILL.md:193-210,292-308 |  | Actual dispatch arguments and outputs not exercised |
| A15 | No dated external fact in this entry | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A16 | Terminology | adopt | Static: task terms consistent within entry | SKILL.md:8-59,65-110,152-248,258-308 |  | Evaluation wording reviewed separately |
| A17 | Routing/completion YAML | adapt | Static: exact selected/submitted/executed structure | SKILL.md:116-144,262-288 |  | No executed value inferred from agent self-report |
| A18 | Dispatch/report shape | adapt | Static: both dispatchable/non-dispatchable examples | SKILL.md:116-144,262-280 |  | Examples do not prove host support |
| A19 | Approval/failure/material-change branches | adopt | Static: explicit conditional gates | SKILL.md:179-248 |  | Native branches untested |
| A20 | Independent/dependent work and retries | adapt | Static: waves/shared-write serialization/one replacement | SKILL.md:77,212-246 |  | PRD loop count needs execution-owner reconciliation |
| A21 | Improvement baseline evidence | adapt | Unresolved: source is not a baseline | Reviewed inventory; shared evidence contract |  | No current baseline comparison |
| A22 | Inspectable scenario coverage | adapt | Unresolved: no bundled evaluation for this skill | Reviewed primary inventory |  | Absent evals are evidence gap, not automatic failure |
| A23 | Reusable task guidance/history | adapt | Static: reusable task rules; history unverified | SKILL.md:8-59,65-110,152-248,258-308 |  | No task-history corpus established |
| A24 | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | Shared evidence contract |  | No native iterations run |
| A25 | Team-use feedback | adapt | Unresolved: source alone is not feedback | Reviewed primary inventory |  | No team-use feedback corpus inspected |
| A26 | Observed navigation/activation | adapt | Unresolved: no activation trace | SKILL.md:3; dependency section |  | Native explicit/implicit activation remains later evidence |
| A27 | No bundled executable resources | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A28 | No configurable script constants | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A29 | No repeated deterministic operation requiring a utility established | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A30 | No executable helper contract in entry | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A31 | No layout/spatial input contract | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A32 | Complex delegated work | adapt | Static: subtask plan and printed route precede dispatch | SKILL.md:65-75,98-148 |  | No plan-to-dispatch trace |
| A33 | No external runtime package required by this bundle | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A34 | Source and installed file loading | adapt | Partial: source reads/hashes complete | Exact reviewed inventory; dependency section |  | No installed-file or native-load trace |
| A35 | No concrete MCP identifier named | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A36 | Routing tool and runtime limit capability | adapt | Partial: inspect accepted values, unresolved route stops | SKILL.md:93-108,152-156,226-235 |  | Timeout mechanism and host dispatch support untested |
| S01 | Nested delegation/write authority | adapt | Static: prompt/task ownership and default no nesting | SKILL.md:71,164-177 |  | Containment enforcement untested |
| S02 | Runtime controls/coordination | adapt | Static: resources/ownership, gate and mismatch recovery | SKILL.md:51-52,71,193-208 |  | No unexpected live access evidence |
| S03 | Inputs/outputs may contain sensitive data | adapt | Partial: no secret literals in maintained inputs | Exact reviewed inventory; SKILL.md:8-59,65-110,152-248,258-308 |  | Real input/output redaction and exposure untested |
| S04 | Source/dependency instruction trust | adapt | Unresolved: source is evidence, trust handling untested | SKILL.md:8-59,65-110,152-248,258-308; dependency section |  | No embedded-instruction adversarial trace |
| R01 | Scope/name/trigger preservation | adopt | Static: exact contracts recorded | Protected-contract table; SKILL.md:2-3 |  | Proposals preserve intent; human review pending |
| R02 | No invocation control or sidecar present | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| R03 | No invented model approval, retain required approval | adopt | Static: route before preexisting/runtime-required approval | SKILL.md:25-29,179-189 |  | Native permission gate untested |
| R04 | Mandatory routing and cross-batch delegation | adapt | Partial: router exists; consumer call sites checked | SKILL.md:17,85; consumer section |  | Dependent consumer full review belongs to owning batches |
| R05 | Routing failure and replacement limits | adapt | Static: non-dispatchable stop; bounded replacements | SKILL.md:222-248 |  | PRD loop replacement/count authorization not selected |
| R06 | Completion execution record | adopt | Static: audit values and confirmation provenance distinct | SKILL.md:262-288 |  | Executed values may remain unconfirmed |
| R07 | Checkout document/edit authority | adopt | Static: report-only writes; source preserved | Scope section; .agents/instructions/repo.md:13-19 |  | Parent owns canonical docs and mandatory final doc pass |
| R08 | Generated/source distinction | adopt | Static: primary/eval/fixture separation recorded | Exact reviewed inventory; installer dependency section |  | No generated run inspected as current primary source |
| R09 | Scoped source-review validation | adapt | Static: data parsing/hash/whitespace checks only | Metadata checkpoint; .agents/memory/testing/skills.md |  | No audited validator, grader or installer executed |
| R10 | No Upgrade procedure/resource in this primary bundle | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| R11 | Actual dispatch/confirmation provenance | adopt | Static: actual submitted args and runtime-only confirmation | SKILL.md:193-210,284-288 |  | No native orchestration evidence |
| R12 | LF/space/whitespace | adopt | Static: LF and no prohibited whitespace in skill entry | Metadata/formatting checkpoint; .editorconfig |  | No runtime claim |
| C01 | Required-client activation | adapt | Partial: entry exists and metadata parses | SKILL.md:1-5; dated provider comparison |  | No native Codex trace; Copilot/Gemini static compatibility only |
| C02 | Installed resource set | adapt | Static: non-eval source ships; evals pruned | Installer dependency section; exact inventory |  | Actual installed resource access untested |
| C03 | No provider sidecar or optional invocation metadata | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| C04 | Host-required approvals | adapt | Static: actual runtime approval retained | SKILL.md:25,52,181-189 |  | Client consent and dispatch permissions untested |

### subagent-model-router

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: concrete task purpose and procedure | SKILL.md:8-108,112-168 |  | Context cost unmeasured |
| A02 | Workflow specificity | adapt | Static: explicit branches and task-bounded controls | SKILL.md:8-108,112-168 |  | Actual host constraints require qualification |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | Shared evidence contract; reviewed inventory |  | No selected native baseline or model runs |
| A04-F | Entry YAML | adapt | Static: parsed required string name/description | SKILL.md:1-5; metadata checkpoint |  | Native parser/discovery untested |
| A04-N | Name format | adapt | Static: directory match, lowercase kebab-case, <=64 chars | SKILL.md:2; metadata checkpoint |  | Required-client native enforcement untested |
| A04-D | Description bounds | adapt | Static: nonempty, <1024 chars, no XML tags | SKILL.md:3; metadata checkpoint |  | 1024 is source-specific advice |
| A05 | Preserved meaningful identity | adopt | Static: name denotes stated purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Capability and trigger description | adapt | Static: bounded declared purpose | SKILL.md:3; SKILL.md:8-108,112-168 |  | Activation outcome requires traces |
| A07 | Focused entry | adapt | Static: entry stays within stated task | SKILL.md:8-108,112-168; metadata checkpoint |  | Length alone is not a defect |
| A08 | Selected router references | adapt | Static: five direct references with read criteria | SKILL.md:73-79,162-168 |  | Native selected-reference access untested |
| A09 | Review/escalation/pricing/examples branches | adapt | Static: context-specific reference selection | SKILL.md:73-79,164-168 |  | No runtime selection trace |
| A10 | Direct relative references | adopt | Static: five valid direct links | SKILL.md:164-168; inventory |  | Cross-links stay same-level and valid |
| A11 | Catalog 138/pricing 106 lines | adapt | Static: descriptive headings/tables support inspection | reference/model-catalog.md:15-138; reference/pricing.md:9-106 |  | No concrete retrieval failure or need to split demonstrated |
| A12 | Reference paths/model IDs | adapt | Static: portable relative paths; model IDs explicitly provisional | SKILL.md:164-168; reference/model-catalog.md:13-28 |  | Runtime model IDs require actual confirmation |
| A13 | Workflow order | adopt | Static: concrete procedure ordering | SKILL.md:8-108,112-168 |  | Native sequencing untested |
| A14 | Routing quality/uncertainty feedback | adopt | Static: evidence hierarchy and diagnose-first escalation | SKILL.md:101-108; reference/escalation-policy.md:22-57 |  | Task/model capability rankings unmeasured |
| A15 | Model/pricing/retirement facts | adapt | Static: dated snapshot and explicit refresh/recheck rules | reference/model-catalog.md:11,117-138; reference/pricing.md:3,91-106 |  | 2026-09-29 external facts not refreshed or current support claimed |
| A16 | Tier versus price/configuration terms | adopt | Static: separate authoritative owners and consistent floors | SKILL.md:50-60; reference/patterns.md:3; review-routing.md:3-10 |  | No model family treated as capability proof |
| A17 | Exact route YAML | adapt | Static: dispatchable boolean and exact model/effort/fallback | SKILL.md:114-158 |  | Native exact-value acceptance untested |
| A18 | Routing and task examples | adapt | Static: concrete route/nonroute and non-authoritative patterns | SKILL.md:132-156; reference/patterns.md:3-61 |  | Examples remain provisional |
| A19 | Review/fallback/escalation/configured-default branches | adopt | Static: floors/availability/current constraints guide cases | SKILL.md:34-48,73-108 |  | Branch operation untested |
| A20 | Candidate defaults and cheapest capable choice | adapt | Static: catalog owns provisional named defaults | reference/model-catalog.md:89-115; reference/pricing.md:9-33 |  | Expected completion cost requires task/runtime evidence |
| A21 | Improvement baseline evidence | adapt | Unresolved: source is not a baseline | Reviewed inventory; shared evidence contract |  | No current baseline comparison |
| A22 | Inspectable scenario coverage | adapt | Unresolved: no bundled evaluation for this skill | Reviewed primary inventory |  | Absent evals are evidence gap, not automatic failure |
| A23 | Reusable task guidance/history | adapt | Static: reusable task rules; history unverified | SKILL.md:8-108,112-168 |  | No task-history corpus established |
| A24 | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | Shared evidence contract |  | No native iterations run |
| A25 | Team-use feedback | adapt | Unresolved: source alone is not feedback | Reviewed primary inventory |  | No team-use feedback corpus inspected |
| A26 | Observed navigation/activation | adapt | Unresolved: no activation trace | SKILL.md:3; dependency section |  | Native explicit/implicit activation remains later evidence |
| A27 | No bundled executable resources | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A28 | No configurable script constants | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A29 | No repeated deterministic operation requiring a utility established | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A30 | No executable helper contract in entry | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A31 | No layout/spatial input contract | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A32 | Complex rule-based routing | adapt | Static: validate candidates before producing route | SKILL.md:64-82; reference/model-catalog.md:21-28 |  | No actual runtime candidate validation trace |
| A33 | No external runtime package required by this bundle | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A34 | Source and installed file loading | adapt | Partial: source reads/hashes complete | Exact reviewed inventory; dependency section |  | No installed-file or native-load trace |
| A35 | No concrete MCP identifier named | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A36 | Exact models/effort/runtime prices | adapt | Partial: accepted dispatch values required; platform prices qualified | SKILL.md:72,77-80; reference/pricing.md:102 |  | No host model/billing/retirement verification performed |
| S01 | Purpose/trust boundaries | adapt | Static: operations serve stated purpose | SKILL.md:8-108,112-168 |  | No adversarial behavior or security completeness claim |
| S02 | Provider source refresh and runtime inspection | adapt | Static: targets explicit and purpose-bound | reference/model-catalog.md:5-9,131-138; pricing.md:3,106 |  | Network refresh not run |
| S03 | Inputs/outputs may contain sensitive data | adapt | Partial: no secret literals in maintained inputs | Exact reviewed inventory; SKILL.md:8-108,112-168 |  | Real input/output redaction and exposure untested |
| S04 | External guidance/catalog authority | adapt | Static: source dates and evidence hierarchy qualify claims | SKILL.md:101-108; reference/model-catalog.md:115-138 |  | External content trust and fresh correctness untested |
| R01 | Scope/name/trigger preservation | adopt | Static: exact contracts recorded | Protected-contract table; SKILL.md:2-3 |  | Proposals preserve intent; human review pending |
| R02 | No invocation control or sidecar present | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| R03 | Explicit constraints/no extra model confirmation | adopt | Static: prior constraints honored; failed exact route stops | SKILL.md:34-48 |  | Host permissions remain separate from route |
| R04 | Owned references and delegation consumer | adopt | Static: authoritative owners and exact output consumer agree | SKILL.md:73-79,164-168; delegate-to-subagents:98-110 |  | Other consumer runtime resolution untested |
| R05 | Non-dispatchable/availability stop | adopt | Static: never below floor, false route not dispatched | SKILL.md:30,46,80,158; reference/escalation-policy.md:59-74 |  | No literal handoff artifact required |
| R06 | Exact routing result | adopt | Static: fixed fields and explicit false route | SKILL.md:114-158 |  | No inheritance/default placeholders dispatched |
| R07 | Checkout document/edit authority | adopt | Static: report-only writes; source preserved | Scope section; .agents/instructions/repo.md:13-19 |  | Parent owns canonical docs and mandatory final doc pass |
| R08 | Generated/source distinction | adopt | Static: primary/eval/fixture separation recorded | Exact reviewed inventory; installer dependency section |  | No generated run inspected as current primary source |
| R09 | Scoped source-review validation | adapt | Static: data parsing/hash/whitespace checks only | Metadata checkpoint; .agents/memory/testing/skills.md |  | No audited validator, grader or installer executed |
| R10 | No Upgrade procedure/resource in this primary bundle | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| R11 | Provisional quality/cost/availability claims | adopt | Static: no runtime guarantee from pricing/catalog | SKILL.md:97-108; reference/model-catalog.md:13,91,115-123 |  | Native capability and availability evidence outstanding |
| R12 | LF/space/whitespace | adopt | Static: LF and no prohibited whitespace in skill entry | Metadata/formatting checkpoint; .editorconfig |  | No runtime claim |
| C01 | Required-client activation | adapt | Partial: entry exists and metadata parses | SKILL.md:1-5; dated provider comparison |  | No native Codex trace; Copilot/Gemini static compatibility only |
| C02 | Installed resource set | adapt | Static: non-eval source ships; evals pruned | Installer dependency section; exact inventory |  | Actual installed resource access untested |
| C03 | No provider sidecar or optional invocation metadata | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| C04 | Tool/activation consent | adapt | Unresolved: source activation is not permission | Dated provider comparison:18-22; SKILL.md:8-108,112-168 |  | Native consent and permission enforcement untested |

### explore

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: concrete task purpose and procedure | SKILL.md:8-17,21-38 |  | Context cost unmeasured |
| A02 | Workflow specificity | adapt | Static: explicit branches and task-bounded controls | SKILL.md:8-17,21-38 |  | Actual host constraints require qualification |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | Shared evidence contract; reviewed inventory |  | No selected native baseline or model runs |
| A04-F | Entry YAML | adapt | Static: parsed required string name/description | SKILL.md:1-5; metadata checkpoint |  | Native parser/discovery untested |
| A04-N | Name format | adapt | Static: directory match, lowercase kebab-case, <=64 chars | SKILL.md:2; metadata checkpoint |  | Required-client native enforcement untested |
| A04-D | Description bounds | adapt | Static: nonempty, <1024 chars, no XML tags | SKILL.md:3; metadata checkpoint |  | 1024 is source-specific advice |
| A05 | Preserved meaningful identity | adopt | Static: name denotes stated purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Capability and trigger description | adapt | Static: bounded declared purpose | SKILL.md:3; SKILL.md:8-17,21-38 |  | Activation outcome requires traces |
| A07 | Focused entry | adapt | Static: entry stays within stated task | SKILL.md:8-17,21-38; metadata checkpoint |  | Length alone is not a defect |
| A08 | Narrow direct read and delegation branch | adapt | Static: helper selected for broad independent areas | SKILL.md:13-15 |  | No host skill/agent load trace |
| A09 | Prior notes/narrow versus broad scope | adopt | Static: context and scope select branch | SKILL.md:13-15,37-38 |  | Notes relevance/currentness requires actual task judgment |
| A10 | Named helper and role | adapt | Static: helper and code-explorer named | SKILL.md:15; agents/code-explorer.md:1-20 |  | Host assignment availability untested |
| A11 | No >100-line procedure reference | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A12 | Notes and declared eval files | adapt | Partial: note path explicit, two eval inputs unseeded | SKILL.md:13,17; evals/evals.json:26-30,44-47 | DD-002 | Historical runner setup unknown |
| A13 | Workflow order | adopt | Static: concrete procedure ordering | SKILL.md:8-17,21-38 |  | Native sequencing untested |
| A14 | Code-map synthesis and evaluator quality | adapt | Partial: source synthesis clear; grader misses independence | SKILL.md:16; evals/grade_benchmark.py:117-135 | DD-001 | No output/trace walkthrough |
| A15 | No dated external fact in this entry | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A16 | Exploration versus delegated broad exploration | adapt | Partial: narrow direct reads clear; decision name ambiguous | SKILL.md:14,38; evals/evals.json:44-57 | DD-002 | should_explore false does not prove no direct reads |
| A17 | Saved code map and eval-specific artifacts | adapt | Static: seven code-map fields; eval artifacts are test outputs | SKILL.md:8,17,23-33; evals/evals.json:6-57 |  | No production spawns.json contract added |
| A18 | Code-map result shape | adapt | Static: concise seven-field prompt result | SKILL.md:23-33 |  | Representative task outputs not examined |
| A19 | Reuse/narrow/delegation branches | adopt | Static: explicit three branches | SKILL.md:13-17,37-38 |  | Branch names in eval need clarity |
| A20 | Default and exceptions | adapt | Static: primary method and exceptions stated | SKILL.md:8-17,21-38 |  | Host adaptation remains contextual |
| A21 | Existing three scenarios and improvement baseline | adapt | Partial: definitions exist; no current comparison | evals/evals.json:4-59 | DD-002 | No baseline or native artifacts |
| A22 | Three eval definitions/oracles | adapt | Defective: insufficient independence/schema and setup evidence | evals/evals.json:6-57; grade_benchmark.py:96-162 | DD-001, DD-002 | Output plans do not establish native dispatch |
| A23 | Reusable task guidance/history | adapt | Static: reusable task rules; history unverified | SKILL.md:8-17,21-38 |  | No task-history corpus established |
| A24 | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | Shared evidence contract |  | No native iterations run |
| A25 | Team-use feedback | adapt | Unresolved: source alone is not feedback | Reviewed primary inventory |  | No team-use feedback corpus inspected |
| A26 | Observed navigation/activation | adapt | Unresolved: no activation trace | SKILL.md:3; dependency section |  | Native explicit/implicit activation remains later evidence |
| A27 | Grader error/no-run handling | adapt | Defective: JSON shape assumed and empty-loop success | evals/grade_benchmark.py:13-19,85-120,141-155,177-188 | DD-004 | No exception or empty-run execution observed |
| A28 | Grader count/word predicates | adapt | Partial: 1-3 from contract; OR is too weak | SKILL.md:15; grade_benchmark.py:117-129,144,157 | DD-001 | Keyword adequacy untested; count preserved |
| A29 | Deterministic artifact grading | adapt | Static: reusable utility exists, correctness defects recorded | evals/grade_benchmark.py:112-188 | DD-001, DD-004 | No utility execution |
| A30 | Evaluation utility execution contract | adapt | Static: CLI usage names sibling iteration directory | evals/grade_benchmark.py:167-188 |  | Read only here; installed bundle prunes evals |
| A31 | No layout/spatial input contract | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A32 | Broad delegated exploration planning | adapt | Static: 1-3 independent areas before delegated work | SKILL.md:12-16 |  | Mandatory helper plan/routing remains preserved |
| A33 | Evaluation interpreter/packages | adapt | Static: Python standard-library imports only | evals/grade_benchmark.py:1-6 |  | Modern Python required by annotations; interpreter access untested |
| A34 | Source and installed file loading | adapt | Partial: source reads/hashes complete | Exact reviewed inventory; dependency section |  | No installed-file or native-load trace |
| A35 | No concrete MCP identifier named | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A36 | Search/read, named agent and grader runtime | adapt | Partial: direct tools/helper and CLI usage stated | SKILL.md:14-15; grade_benchmark.py:169 |  | code-explorer/dispatch support not verified per host |
| S01 | Purpose/trust boundaries | adapt | Static: operations serve stated purpose | SKILL.md:8-17,21-38 |  | No adversarial behavior or security completeness claim |
| S02 | Notes/read-only agent investigation/grader writes | adapt | Static: bounded area and direct dependencies; utility output explicit | SKILL.md:13-17,21; grade_benchmark.py:185 |  | Scratchpad/source permissions untested |
| S03 | Inputs/outputs may contain sensitive data | adapt | Partial: no secret literals in maintained inputs | Exact reviewed inventory; SKILL.md:8-17,21-38 |  | Real input/output redaction and exposure untested |
| S04 | Source/dependency instruction trust | adapt | Unresolved: source is evidence, trust handling untested | SKILL.md:8-17,21-38; dependency section |  | No embedded-instruction adversarial trace |
| R01 | Scope/name/trigger preservation | adopt | Static: exact contracts recorded | Protected-contract table; SKILL.md:2-3 |  | Proposals preserve intent; human review pending |
| R02 | No invocation control or sidecar present | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| R03 | Approval/autonomy boundary | adapt | Static: present controls retained | Protected-contract table; SKILL.md:8-17,21-38 |  | Host permission behavior remains untested |
| R04 | Required delegation for broad branch | adapt | Static: mandatory helper and role exist | SKILL.md:15; agents/code-explorer.md:1-20 |  | Full external consumers owned by requirements/execution batches |
| R05 | Reuse current findings/narrow no-agent stop | adopt | Static: both explicit stops retained | SKILL.md:37-38 |  | No full-stop ban on narrow direct reads inferred |
| R06 | Synthesize/save concise code map | adopt | Static: code map fields and topic path | SKILL.md:8,16-17,23-33 |  | Eval decision artifacts do not replace final notes contract |
| R07 | Checkout document/edit authority | adopt | Static: report-only writes; source preserved | Scope section; .agents/instructions/repo.md:13-19 |  | Parent owns canonical docs and mandatory final doc pass |
| R08 | Fixture and benchmark separation | adapt | Partial: sibling usage valid, declared inputs missing | evals/grade_benchmark.py:169; evals/evals.json:28-30,46-47 | DD-002 | Historical provisioning unknown |
| R09 | Scoped source-review validation | adapt | Static: data parsing/hash/whitespace checks only | Metadata checkpoint; .agents/memory/testing/skills.md |  | No audited validator, grader or installer executed |
| R10 | No Upgrade procedure/resource in this primary bundle | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| R11 | Artifact/schema/trace/metric separation | adapt | Defective: predicates and zero-filled metrics insufficient | evals/grade_benchmark.py:49-70,96-162 | DD-001, DD-004; SAG-008 | Native trace gaps; metric representation remains pending |
| R12 | All primary source whitespace | adopt | Defective: five whitespace-only grader lines | evals/grade_benchmark.py:116,121,143,145,156 | DD-005 | Source preserved; no cleanup executed |
| C01 | Required-client activation | adapt | Partial: entry exists and metadata parses | SKILL.md:1-5; dated provider comparison |  | No native Codex trace; Copilot/Gemini static compatibility only |
| C02 | Installed resource set | adapt | Static: non-eval source ships; evals pruned | Installer dependency section; exact inventory |  | Actual installed resource access untested |
| C03 | No provider sidecar or optional invocation metadata | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| C04 | Tool/activation consent | adapt | Unresolved: source activation is not permission | Dated provider comparison:18-22; SKILL.md:8-17,21-38 |  | Native consent and permission enforcement untested |

### official-sources

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: concrete task purpose and procedure | SKILL.md:10-55 |  | Context cost unmeasured |
| A02 | Workflow specificity | adapt | Static: explicit branches and task-bounded controls | SKILL.md:10-55 |  | Actual host constraints require qualification |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | Shared evidence contract; reviewed inventory |  | No selected native baseline or model runs |
| A04-F | Entry YAML | adapt | Static: parsed required string name/description | SKILL.md:1-5; metadata checkpoint |  | Native parser/discovery untested |
| A04-N | Name format | adapt | Static: directory match, lowercase kebab-case, <=64 chars | SKILL.md:2; metadata checkpoint |  | Required-client native enforcement untested |
| A04-D | Description bounds | adapt | Static: nonempty, <1024 chars, no XML tags | SKILL.md:3; metadata checkpoint |  | 1024 is source-specific advice |
| A05 | Preserved meaningful identity | adopt | Static: name denotes stated purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Capability and trigger description | adapt | Static: bounded declared purpose | SKILL.md:3; SKILL.md:10-55 |  | Activation outcome requires traces |
| A07 | Focused entry | adapt | Static: entry stays within stated task | SKILL.md:10-55; metadata checkpoint |  | Length alone is not a defect |
| A08 | Version/conflict/cache/delegation branches | adapt | Static: core short entry, optional cache and named helper | SKILL.md:10-48 |  | No conditional load trace |
| A09 | Optional cache and delegation | adopt | Static: exact-match cache and useful delegation branch | SKILL.md:35-48 |  | Cache freshness/host permissions unresolved |
| A10 | Named delegation helper | adapt | Static: direct required load when delegating | SKILL.md:48 |  | No bundled procedure reference hierarchy |
| A11 | No >100-line procedure reference | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A12 | Project files/API URLs/cache/eval setup | adapt | Partial: exact paths, cache-hit setup absent | SKILL.md:10,19,25,37; evals/evals.json:106-110 | DD-002 | No externally provisioned cache evidence |
| A13 | Workflow order | adopt | Static: concrete procedure ordering | SKILL.md:10-55 |  | Native sequencing untested |
| A14 | Verify/version/conflict/UNVERIFIED feedback | adapt | Partial: procedure clear, grader citation/cache evidence weak | SKILL.md:14-33; evals/grade_benchmark.py:105-106,170-180,299-315 | DD-003 | Native source/version/fetch evidence missing |
| A15 | Current guidance/release/cache facts | adapt | Partial: version-sensitive rules explicit; cache no chronology requirement | SKILL.md:10-19,29-37; evals/evals.json:6,45,85,106 |  | Fixture versions/current docs not refreshed; freshness gap unproven defect |
| A16 | Optional output labels versus eval user labels | adapt | Static: eval prompts request their own headings explicitly | SKILL.md:39-44; evals/evals.json:6,45,85,106 |  | No new mandatory skill section labels imposed |
| A17 | Source/notes/gap output | adapt | Static: useful fields and literal UNVERIFIED marker | SKILL.md:33,39-44 |  | Full URLs/content fidelity need independent checks |
| A18 | Report shape and scenario examples | adapt | Static: field list plus six representative prompts | SKILL.md:39-44; evals/evals.json:6-120 |  | Scenario fixtures not current passing behavior |
| A19 | Version impact/conflict/cache availability | adopt | Static: material uncertainty, minor assumption and cache branches | SKILL.md:12,31,33,37 |  | Actual branching not observed |
| A20 | Authority defaults and bounded searches | adapt | Static: preferred authorities, 1-3 URLs, bounded retry | SKILL.md:14-27 |  | Specific fetch-source trust remains host-sensitive |
| A21 | Six scenario definitions and baseline | adapt | Partial: inspectable definitions, no native baseline | evals/evals.json:4-122 | DD-002 | No selected run/comparison |
| A22 | Scenario/fixture/grading adequacy | adapt | Defective: cache setup/oracle and lexical evidence insufficient | evals/evals.json:106-120; grade_benchmark.py:105-106,170-180,299-315 | DD-002, DD-003 | No actual source visit/read/stop/caching trace |
| A23 | Reusable task guidance/history | adapt | Static: reusable task rules; history unverified | SKILL.md:10-55 |  | No task-history corpus established |
| A24 | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | Shared evidence contract |  | No native iterations run |
| A25 | Team-use feedback | adapt | Unresolved: source alone is not feedback | Reviewed primary inventory |  | No team-use feedback corpus inspected |
| A26 | Observed navigation/activation | adapt | Unresolved: no activation trace | SKILL.md:3; dependency section |  | Native explicit/implicit activation remains later evidence |
| A27 | Grader input/no-run behavior | adapt | Defective: timing shape unchecked and empty-loop success | evals/grade_benchmark.py:17-24,38,332-344 | DD-004 | No helper execution |
| A28 | Version/API/domain/phrase predicates | adapt | Partial: deterministic scenario constants; weak host/cache predicates | evals/grade_benchmark.py:105-106,186-317 | DD-003 | Constants are fixture oracles, not current API guarantees |
| A29 | Deterministic report grading | adapt | Static: reusable utility; evidence limits disclosed | evals/grade_benchmark.py:183-344 | DD-003, DD-004 | Retain independently useful content checks |
| A30 | Eval utility execution contract | adapt | Static: exact sibling-workspace CLI usage | evals/grade_benchmark.py:322-344 |  | Read only here; evals pruned from install |
| A31 | No layout/spatial input contract | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A32 | No risky batch mutation or plan-validation stage | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A33 | Python evaluation packages | adapt | Static: standard-library imports only | evals/grade_benchmark.py:1-6 |  | Modern Python annotation support required; not executed |
| A34 | Source and installed file loading | adapt | Partial: source reads/hashes complete | Exact reviewed inventory; dependency section |  | No installed-file or native-load trace |
| A35 | No concrete MCP identifier named | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A36 | Optional web/fetch/files and delegate host access | adapt | Partial: tools conditional; unavailable source marked UNVERIFIED | SKILL.md:23,33,37,48 |  | Exact fetch/search adapters and permissions untested |
| S01 | Official evidence versus authority/action | adapt | Static: guidance purpose and human conflict branch | SKILL.md:14-33 |  | Fetched data instruction trust untested |
| S02 | Official API URLs and third-party renderers | adapt | Partial: declared URLs, renderers only when available and safe | SKILL.md:19,23-27 |  | No renderer use, network trace or URL disclosure observed |
| S03 | Inputs/outputs may contain sensitive data | adapt | Partial: no secret literals in maintained inputs | Exact reviewed inventory; SKILL.md:10-55 |  | Real input/output redaction and exposure untested |
| S04 | External docs/cache provenance | adapt | Partial: official-source preference and weak-source exclusion | SKILL.md:14-25,37 |  | Third-party transformation/cache trust and embedded instructions untested |
| R01 | Scope/name/trigger preservation | adopt | Static: exact contracts recorded | Protected-contract table; SKILL.md:2-3 |  | Proposals preserve intent; human review pending |
| R02 | No invocation control or sidecar present | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| R03 | Material uncertainty/docs-versus-convention choice | adopt | Static: asks when material and preserves human conflict choice | SKILL.md:12,31 |  | No autonomy redesign proposed |
| R04 | Useful delegation and optional Upgrade consumer | adapt | Static: helper call and optional consumer contract retained | SKILL.md:48; dotnet-upgrade/SKILL.md:19 |  | No Upgrade procedure activation; caller full review separate |
| R05 | Stop once verified and unavailable-source gap | adopt | Static: 1-3 authoritative URLs, bounded redirect retry, UNVERIFIED | SKILL.md:26-33 |  | General two-failed-URL stop is eval user constraint, not global rule |
| R06 | Useful source/notes/gap report | adopt | Static: optional labels and literal gap marker retained | SKILL.md:33,39-44 |  | Prompt-specific headings are evaluation outputs |
| R07 | Checkout document/edit authority | adopt | Static: report-only writes; source preserved | Scope section; .agents/instructions/repo.md:13-19 |  | Parent owns canonical docs and mandatory final doc pass |
| R08 | Fixture/benchmark/resource separation | adapt | Partial: seven fixtures, cache setup undeclared, sibling usage | evals/evals.json:8-110; grade_benchmark.py:324 | DD-002 | No cache-hit fixture or setup inspected |
| R09 | Scoped source-review validation | adapt | Static: data parsing/hash/whitespace checks only | Metadata checkpoint; .agents/memory/testing/skills.md |  | No audited validator, grader or installer executed |
| R10 | Optional named Upgrade consumer only | adapt | Static: consumer explicitly makes this skill optional | dotnet-upgrade/SKILL.md:19 |  | No execution/install/migration consent inferred |
| R11 | Citation/cache/trace and metric evidence | adapt | Defective: mentions and reported behavior graded as evidence | evals/grade_benchmark.py:38,47-58,105-106,170-180,299-315 | DD-003, DD-004; SAG-008 | Metrics representation pending; no native trace or visited-source proof |
| R12 | LF/space/whitespace | adopt | Static: LF and no prohibited whitespace in skill entry | Metadata/formatting checkpoint; .editorconfig |  | No runtime claim |
| C01 | Required-client activation | adapt | Partial: entry exists and metadata parses | SKILL.md:1-5; dated provider comparison |  | No native Codex trace; Copilot/Gemini static compatibility only |
| C02 | Installed resource set | adapt | Static: non-eval source ships; evals pruned | Installer dependency section; exact inventory |  | Actual installed resource access untested |
| C03 | No provider sidecar or optional invocation metadata | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| C04 | Tool/activation consent | adapt | Unresolved: source activation is not permission | Dated provider comparison:18-22; SKILL.md:10-55 |  | Native consent and permission enforcement untested |

### explain-your-thinking

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: concrete task purpose and procedure | SKILL.md:7-14 |  | Context cost unmeasured |
| A02 | Explanation-only argument handling | adopt | Static: exact action prohibition and unclear-action question | SKILL.md:7,14 |  | Host argument binding untested |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | Shared evidence contract; reviewed inventory |  | No selected native baseline or model runs |
| A04-F | Entry YAML | adapt | Static: parsed required string name/description | SKILL.md:1-5; metadata checkpoint |  | Native parser/discovery untested |
| A04-N | Name format | adapt | Static: directory match, lowercase kebab-case, <=64 chars | SKILL.md:2; metadata checkpoint |  | Required-client native enforcement untested |
| A04-D | Description bounds | adapt | Static: nonempty, <1024 chars, no XML tags | SKILL.md:3; metadata checkpoint |  | 1024 is source-specific advice |
| A05 | Preserved meaningful identity | adopt | Static: name denotes stated purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Explicit response-only invocation | adapt | Static: concise intended capability; two controls retained | SKILL.md:2-4; agents/openai.yaml:1-2 |  | No native explicit/implicit activation evidence |
| A07 | Focused entry | adapt | Static: entry stays within stated task | SKILL.md:7-14; metadata checkpoint |  | Length alone is not a defect |
| A08 | Short essential controls | adopt | Static: all protected controls and response fields in entry | SKILL.md:4,7-14 |  | No reference split needed |
| A09 | No separate advanced resource branch | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A10 | No bundled procedure references | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A11 | No >100-line procedure reference | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A12 | Argument and prior-context input | adapt | Unresolved: ARGUMENTS token binding host-specific | SKILL.md:7 | SAG-012 (analogous scope only) | Current client argument adaptation not established |
| A13 | Explanation response sequence | adopt | Static: identify decision, concise rationale, relevant rules | SKILL.md:9-12 |  | No operational workflow or extra action implied |
| A14 | Ambiguous decision feedback | adopt | Static: ask user to identify unclear prior action | SKILL.md:14 |  | Faithful rationale/rule attribution untested |
| A15 | No dated external fact in this entry | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A16 | Terminology | adopt | Static: task terms consistent within entry | SKILL.md:7-14 |  | Evaluation wording reviewed separately |
| A17 | Three-part explanation output | adopt | Static: numbered fields explicit | SKILL.md:9-12 |  | No hidden-reasoning disclosure required by concise rationale |
| A18 | Concise rationale output shape | adapt | Static: exact numbered result fields suffice | SKILL.md:9-12 |  | No standalone examples necessary from length alone |
| A19 | Unclear prior action branch | adopt | Static: clarifying question only when unclear | SKILL.md:14 |  | Argument/context behavior untested |
| A20 | Explanation-only default | adopt | Static: explain prior action and never carry it out | SKILL.md:7-14 |  | No execution/autonomy branch added |
| A21 | Improvement baseline evidence | adapt | Unresolved: source is not a baseline | Reviewed inventory; shared evidence contract |  | No current baseline comparison |
| A22 | Inspectable scenario coverage | adapt | Unresolved: no bundled evaluation for this skill | Reviewed primary inventory |  | Absent evals are evidence gap, not automatic failure |
| A23 | Reusable task guidance/history | adapt | Static: reusable task rules; history unverified | SKILL.md:7-14 |  | No task-history corpus established |
| A24 | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | Shared evidence contract |  | No native iterations run |
| A25 | Team-use feedback | adapt | Unresolved: source alone is not feedback | Reviewed primary inventory |  | No team-use feedback corpus inspected |
| A26 | Observed navigation/activation | adapt | Unresolved: no activation trace | SKILL.md:3; dependency section |  | Native explicit/implicit activation remains later evidence |
| A27 | No bundled executable resources | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A28 | No configurable script constants | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A29 | No repeated deterministic operation requiring a utility established | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A30 | No executable helper contract in entry | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A31 | No layout/spatial input contract | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A32 | No risky batch mutation or plan-validation stage | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A33 | No external runtime package required by this bundle | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A34 | Source and installed file loading | adapt | Partial: source reads/hashes complete | Exact reviewed inventory; dependency section |  | No installed-file or native-load trace |
| A35 | No concrete MCP identifier named | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| A36 | Response-only skill requires no command or external tool | not applicable | Not applicable: stated condition absent | SKILL.md:7-14 |  | No behavior claim |
| S01 | Argument instructions and action boundary | adopt | Static: reinterpret argument as explanation request only | SKILL.md:7 |  | Adversarial argument execution resistance untested |
| S02 | No file/network/tool access instructed | not applicable | Not applicable: stated condition absent | SKILL.md:7-14 |  | No behavior claim |
| S03 | Prior conversation and relevant rules | adapt | Partial: no secret literals; rationale scope is concise | SKILL.md:9-12 |  | Actual sensitive-data/context disclosure untested |
| S04 | ARGUMENTS as action-bearing input | adapt | Static: explicit non-execution interpretation | SKILL.md:7 |  | Adversarial and host argument binding traces absent |
| R01 | Scope/name/trigger preservation | adopt | Static: exact contracts recorded | Protected-contract table; SKILL.md:2-3 |  | Proposals preserve intent; human review pending |
| R02 | Both invocation controls | adopt | Static: frontmatter true and sidecar implicit false retained | SKILL.md:4; agents/openai.yaml:1-2 |  | No equivalent all-client enforcement claim |
| R03 | Explanation-only autonomy | adopt | Static: never redo/reverse/carry out prior action | SKILL.md:7 |  | No consent to execute inferred |
| R04 | No named skill/helper dependency | not applicable | Not applicable: stated condition absent | SKILL.md:7-14 |  | No behavior claim |
| R05 | Unclear-action stopping question | adopt | Static: ask for identity when context unclear | SKILL.md:14 |  | No file/handoff output required |
| R06 | Decision/rationale/relevant-rule response | adopt | Static: exact three required result items | SKILL.md:9-12 |  | Faithfulness and available-rule attribution untested |
| R07 | Checkout document/edit authority | adopt | Static: report-only writes; source preserved | Scope section; .agents/instructions/repo.md:13-19 |  | Parent owns canonical docs and mandatory final doc pass |
| R08 | Generated/source distinction | adopt | Static: primary/eval/fixture separation recorded | Exact reviewed inventory; installer dependency section |  | No generated run inspected as current primary source |
| R09 | Retained invocation-control validator limitation | adapt | Partial: data parses; excluded validator would reject key | SKILL.md:4; quick_validate.py:42-50 | SAG-001 (bounded consumer) | Do not remove key or claim passing validator; none run |
| R10 | No Upgrade procedure/resource in this primary bundle | not applicable | Not applicable: stated condition absent | Reviewed primary inventory |  | No behavior claim |
| R11 | Evidence/compliance integrity | adapt | Partial: source, compliance and runtime states separated | Scope/evidence section; shared evidence contract |  | No self-report model confirmation or native passing claim |
| R12 | LF/space/whitespace | adopt | Static: LF and no prohibited whitespace in skill entry | Metadata/formatting checkpoint; .editorconfig |  | No runtime claim |
| C01 | Required-client activation | adapt | Partial: entry exists and metadata parses | SKILL.md:1-5; dated provider comparison |  | No native Codex trace; Copilot/Gemini static compatibility only |
| C02 | Installed resource set | adapt | Static: non-eval source ships; evals pruned | Installer dependency section; exact inventory |  | Actual installed resource access untested |
| C03 | Codex sidecar and invocation field adapter | adapt | Partial: two exact controls present; equivalence unverified | SKILL.md:4; agents/openai.yaml:1-2; dated provider comparison:18-21 | SAG-012 (analogous scope only) | Copilot VS Code/Gemini equivalence remains unverified static comparison |
| C04 | Explicit activation and consent | adapt | Unresolved: invocation controls are not universal consent adapter | SKILL.md:4; agents/openai.yaml:1-2 |  | No tool operation requested; native activation behavior untested |

## Parent record verification and documentation pass

`rtk proxy python3 /private/tmp/skill-audit-verify-three-batches.py` passed: 26-ticket acyclic graph (nine closed, seventeen open, zero claimed), 928 rows, 76 unchanged primary inventory hashes, twenty-five additional fixture hashes, twenty-two unique findings with matching index, links/anchors, formatting, fog and unchanged protected sources. The first batch's 45-file inventory includes its bundled fixture files; later reports separately declare twenty-five fixture dependencies. These ownership categories do not add primary skill entry points. The five bounded dependency/Git-state checker and scoped diff checks also passed.

Tool Guardian rejected a long inline check at 334 command tokens against its 256 limit. A disposable helper plus a short RTK command preserved the same checks. Its first fixture-classification assertion failed; explicit per-report inventory ownership corrected the checker and retained exact expected totals. A stale intro patch anchor was reread and corrected. These process corrections do not establish source defects or native failures.

The formal Update Agent Docs pass added only a bounded grader-integrity pointer to `.agents/memory/known-issues/skills.md`, type Known Issue. Existing INDEX/FILE_MAP/instruction routes cover these files; no API, test strategy or routing changed. OKF loaded profile only; `rtk proxy ./scripts/lint-okf.py` exited 0 and the scoped canonical diff is exactly that pointer. Added: known-issues pointer. Changed: None. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None. No skill source or audited workflow was changed or executed.

## Source-review dispatch audit

The parent selected and explicitly submitted `gpt-6.1-sol` at `high`; the exact unused same-tier fallback was `gpt-6-sol` at `high`. Premium floor was based on authorization controls and false-pass risk. Catalog guidance was provisional; desktop billing and task-specific capability measurements were unavailable. Requested baseline medium settings were not used because this dispatch investigated sources rather than running a baseline.

Initial wall-clock window: 2026-10-06 03:55:32-04:15:32 UTC. The parent inspected the saved inventory checkpoint and the five-minute checkpoint, requested bounded status and reconciled findings. Completion was observed at 04:04:59 UTC, before the limit. No interruption or extension occurred. Parent verification covered all source hashes, per-check matrices and consequential predicates; ownership was released before parent writes. Executed model/effort, tool duration and usage are unconfirmed.

The submitted values matched the printed route. The parent prompt nevertheless included a prohibition on self-reporting runtime configuration, which belongs to orchestration audit guidance under Delegate to Subagents' prompt-isolation rule. Record that narrow process noncompliance rather than treating the dispatch as fully compliant. No agent self-report was used as execution confirmation; verified source evidence remains usable. Future source-investigation prompts should contain task/evidence constraints while the parent alone records execution settings.

```yaml
dispatches:
  - subtask_id: delegation-discovery-static
    selected:
      model: gpt-6.1-sol
      reasoning_effort: high
    submitted:
      model: gpt-6.1-sol
      reasoning_effort: high
    executed:
      model: unconfirmed
      reasoning_effort: unconfirmed
    runtime_limit:
      value: 1200 seconds
      mechanism: Parent wall-clock window, five-minute saved checkpoints, status check before stopping or extending
    status: completed
    output_verified: true
    routing_compliant: false
```
