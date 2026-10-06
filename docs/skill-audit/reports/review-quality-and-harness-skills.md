# Review Quality and Harness Skills

Status: full static investigation complete; parent reconciliation complete; human proposal review pending. No audited workflows or helpers executed. Parent owns shared records and final documentation pass.

Source baseline: `72a3ae956e3533aaddf33eb1e8d8ecf30b69d08f`. All listed file bytes compared directly with the Git baseline.

## Exact reviewed inventory

All 26 maintained files listed below were read in full. JSON, YAML and Python AST parsing completed without importing or executing audited helpers. Hashes identify source bytes, not runtime evidence. No bundled fixture files are present; every eval `files` array is empty.

| File | Bytes | Lines | SHA256 | Baseline | Classification |
| --- | --- | --- | --- | --- | --- |
| [skills/adversarial-review/SKILL.md](../../../skills/adversarial-review/SKILL.md) | 659 | 19 | `1b6224846f812975215a357017333c0a9c2a88854fce888ba799fb64cc5865f1` | unchanged | primary skill entry |
| [skills/adversarial-review/agents/openai.yaml](../../../skills/adversarial-review/agents/openai.yaml) | 199 | 5 | `6468de7b98ec25e090e15a22c605719656a9fc09240fcc685cb006d6c0adfcc9` | unchanged | client metadata adapter |
| [skills/adversarial-review/evals/evals.json](../../../skills/adversarial-review/evals/evals.json) | 1974 | 51 | `16e9d33f6f17dde0c3ac87ef06f60f694b1e5f52e4fc14f616a22fcd21a39001` | unchanged | static eval resource |
| [skills/adversarial-review/evals/grade_benchmark.py](../../../skills/adversarial-review/evals/grade_benchmark.py) | 4798 | 105 | `ffe05b4ab34d245a3bbe4b094dec00dd3cd4efa0f71870846f324ddaa6eefc7b` | unchanged | static eval resource |
| [skills/code-review/SKILL.md](../../../skills/code-review/SKILL.md) | 5934 | 117 | `0e0ec7d4d90cc1132aebe965583ba605a4b397b5b3802b463cd1d535ed31550b` | unchanged | primary skill entry |
| [skills/code-review/agents/openai.yaml](../../../skills/code-review/agents/openai.yaml) | 164 | 5 | `a3d3369895e1d9daa327008631a32a4870b54856dd945523f8771e92464390ae` | unchanged | client metadata adapter |
| [skills/code-review/evals/evals.json](../../../skills/code-review/evals/evals.json) | 5192 | 69 | `8baeadaccafb3b283f0c1ba64e8b4e2bb8391705db5aa45dc7b2573d66a60679` | unchanged | static eval resource |
| [skills/code-review/evals/grade_benchmark.py](../../../skills/code-review/evals/grade_benchmark.py) | 9105 | 246 | `2bf76aa887069f7f23659162d8c84313ad5eff33ecd18ccea131c7347f023f39` | unchanged | static eval resource |
| [skills/code-review/references/code-smells.md](../../../skills/code-review/references/code-smells.md) | 1625 | 25 | `951e417cf8b13c3e32eec1d07fa6c5cb0b3a25a39679df433466a9c7e65df160` | unchanged | bundled reference |
| [skills/code-review/references/false-positive-rubric.md](../../../skills/code-review/references/false-positive-rubric.md) | 841 | 26 | `759e321cb52b644f77decccd7c9763c12ab1da2328941afcea59eeace74c31b6` | unchanged | bundled reference |
| [skills/code-review/references/large-change-triage.md](../../../skills/code-review/references/large-change-triage.md) | 1168 | 41 | `14c90ec4668ee978a2095db87bc2edd8f8d8751ad7d5d0905afe4bc01179460d` | unchanged | bundled reference |
| [skills/code-review/references/maintainability-criteria.md](../../../skills/code-review/references/maintainability-criteria.md) | 1596 | 45 | `6fc8e8412fe12b0c7d1d7e47778a8cf2a2cff0eab5cff00ef7c71d3a0f9906d4` | unchanged | bundled reference |
| [skills/code-review/references/output-formats.md](../../../skills/code-review/references/output-formats.md) | 1568 | 68 | `087673ca9dae17ce2088bd8547088f3b748b767d01b20c3bf67c3ccb02f837d3` | unchanged | bundled reference |
| [skills/code-review/references/pr-protocol.md](../../../skills/code-review/references/pr-protocol.md) | 717 | 33 | `4c6cedd958eaea1a7d64e6e96f6f4ed24941357a7e16ecddcb293c9781dc664b` | unchanged | bundled reference |
| [skills/code-review/references/standards-files.md](../../../skills/code-review/references/standards-files.md) | 550 | 25 | `37081fec16e5ff606b26bb5636374b72c5c15736e31648fc1ca2d364859c6398` | unchanged | bundled reference |
| [skills/code-simplify/SKILL.md](../../../skills/code-simplify/SKILL.md) | 1087 | 22 | `0053af3efb0e1d9ed9a8dae0fdf0d869694d3b86be0167934bf96c4a2a2dd638` | unchanged | primary skill entry |
| [skills/fixing-accessibility/SKILL.md](../../../skills/fixing-accessibility/SKILL.md) | 4718 | 136 | `549261e8a53b53a1a20c0ddbf736821e5fc0876ad82eee76e0efab8e9ee9dadf` | unchanged | primary skill entry |
| [skills/techdebt/SKILL.md](../../../skills/techdebt/SKILL.md) | 3048 | 98 | `06ea757e4dcba76379dc5f383d5a2272cbc1ce6f52d1e56bff4802f00cab389e` | unchanged | primary skill entry |
| [skills/techdebt/agents/openai.yaml](../../../skills/techdebt/agents/openai.yaml) | 210 | 5 | `4439d4cca9a0667b6f79724df292c79a10100e68f927c1a68dfcea213934cec3` | unchanged | client metadata adapter |
| [skills/techdebt/evals/evals.json](../../../skills/techdebt/evals/evals.json) | 2152 | 38 | `0163531f270dc50eca35b843b8285714b0814bf38f8c7d3a2feaa0244b0ec414` | unchanged | static eval resource |
| [skills/harness-analysis/SKILL.md](../../../skills/harness-analysis/SKILL.md) | 12973 | 235 | `4cd128eefdda1e049e2cb9d8ee04872f09e6770880a598a9d79972f2cd4172c7` | unchanged | primary skill entry |
| [skills/harness-analysis/agents/openai.yaml](../../../skills/harness-analysis/agents/openai.yaml) | 182 | 5 | `ed9f60789a874f7b663eaa12f2e8dfeff9d361b14a5046bd3a9ea736a76ff0d1` | unchanged | client metadata adapter |
| [skills/harness-analysis/evals/evals.json](../../../skills/harness-analysis/evals/evals.json) | 6544 | 93 | `bf70b138bc520a7ae710441e0ca4edfc72719f7e7fa323abd08834cc557f6f46` | unchanged | static eval resource |
| [skills/harness-analysis/evals/grade_benchmark.py](../../../skills/harness-analysis/evals/grade_benchmark.py) | 9591 | 222 | `044a73b91a9bcbc16ab066232166c2938b6a32b9ea8381cdb3689e2b683d831d` | unchanged | static eval resource |
| [skills/improve-repo-harness/SKILL.md](../../../skills/improve-repo-harness/SKILL.md) | 404 | 9 | `3edf309432f61754046eb9d791f6c620d5c0da06a0a6efedff19c2703f5aa595` | unchanged | primary skill entry |
| [skills/improve-repo-harness/agents/openai.yaml](../../../skills/improve-repo-harness/agents/openai.yaml) | 202 | 5 | `96cd740230b80cae0359386d95f5c3e6c9edb1d4a924efacb227711f5cb96d6c` | unchanged | client metadata adapter |

## Progress

Seven entry points, seven Code Review references, five sidecars, four eval definitions and three graders fully read. All unchanged at baseline. Seven complete matrices contain 406 rows; matrix and inventory record checks passed. Dependencies are bounded consumer evidence, not imported-skill primary audits.

## Protected contracts

The line anchors below identify each named skill's SKILL.md unless the sidecar is named. Preserve all seven directory and frontmatter names.

| Skill | Purpose and triggers | Controls, approvals and dependencies | Stop, output and validation contracts |
| --- | --- | --- | --- |
| adversarial-review | Explicit adversarial review of code/plans (:2-3) | Both invocation controls; Delegate and fresh subagent (:4,9; agents/openai.yaml:4-5) | Issues and suggested fixes only; no implementation or other changes (:11-19) |
| code-review | Requested PR/diff/fixed point/local changes (:3,9,14,30-38) | Both controls; required Addy quality and Delegate (:27-28); four concurrent responsibilities (:54-66); security helper (:57) | Unclear target/missing dependency stop (:15,21,35); no unsolicited validation (:16); exact change linkage and 80+ (:79-85); normal/PR/YAML output and no-op (:87-100); PR eligibility/recheck |
| code-simplify | Recently changed or specified scope; exact behavior (:8,12-20) | Required Addy simplification (:6), Delegate with useful delegation (:10), project rules (:11) | Understand callers/edges/tests first (:13); incremental tests; passing tests/build/clean diff (:21-22) |
| fixing-accessibility | HTML names/keyboard/focus/forms and UI requests (:3,10-31) | File invocation is review/report; bare invocation applies constraints (:12-19); minimal targeted changes (:21,111-113) | Exact offending snippet, impact and small fix; native semantics before ARIA; no unrequested UI-library migration (:111-136) |
| techdebt | Current/provided scope duplication removal (:3,9,21-26,49-63) | Both controls; Delegate (:13), Explore/code-explorer (:30); refactor/validator roles (:69-76); public API/architecture/UI/naming/unrelated work asks (:81-87) | Provided candidates skip discovery (:17); no changes/duplication stop (:23-24,45); safest 1-3 default (:63); validation/rollback wording unresolved (:77); concise scope/action/result/candidate summary (:91-98) |
| harness-analysis | Explicit process/session/hook/agent guidance audit; exclude normal coding (:3,15-17) | Both controls; read-only, no hook execution, no sensitive body disclosure (:21-26,52,94,106) | 14 days, 10 sessions/20 hooks defaults (:32-34); cheap inventory first; bounded failures (:89-94); Evidence/Uncertainty before candidate recommendations; exact final read-only statement (:130-202,235) |
| improve-repo-harness | Repository harness improvement based on named external repo (:2-9) | Both controls; remote source is a bounded dependency | Description says add/fix/improve; body asks how to improve. Recommendations versus execution remains unresolved |

No audited procedure was activated. No implementation, installer, refresh, packaging, grader, validator or native model evaluation ran. Parent owns canonical finding reconciliation and the final documentation pass.

## Bounded dependency and consumer evidence

The Delegation and Discovery batch owns Delegate, Router, Explore and their references. This report checks these consumers only. Imported Addy and TDD bundles remain excluded; selected helper sections were read as dependency contracts, not primary audits. Six custom-agent definitions were read in full: `agents/{addy-code-reviewer,addy-security-auditor,addy-test-engineer,code-explorer,code-simplifier,code-reviewer}.md`. These are roles, not skill entry points. No fixture entry points were discovered in these seven bundles.

| Consumer/dependency | Exact evidence | Static result and boundary |
| --- | --- | --- |
| Adversarial -> Delegate -> Router | adversarial-review/SKILL.md:9; delegate-to-subagents/SKILL.md:17,85-110,152-177; router/reference/review-routing.md:7-9,40-49 | Required delegation/routing exists; expert choice remains task-sensitive; explicit read-only prompt preserved. Premium auth example agrees with security floor. Actual loading/dispatch untested |
| Code Review -> Addy quality/security and Delegate | code-review/SKILL.md:25-28,54-66; addy-code-review-and-quality/SKILL.md:142-203,232-248,304-358; addy-security-and-hardening/SKILL.md:21-75 | All named skill entry points exist. Consumer narrows scope, excludes style/unrelated work and unrequested validation. Delegate remains mandatory. Helper approval or security rules are not silently removed |
| Four Code Review roles | code-review/SKILL.md:54-66; agents/addy-code-reviewer.md:1-5,52-107; agents/addy-security-auditor.md:1-5,82-112; agents/addy-test-engineer.md:1-5,66-95; agents/ top-level inventory | Three Addy role names exist; no `generalist` source definition exists. No claim that every host rejects that name; exact required-host mapping is unresolved. Caller must constrain personas to review-only and scoped findings |
| Code Review -> routing floor | code-review/SKILL.md:79-85; router/reference/review-routing.md:7-9,27-34,40-49 | Fast verification instruction can conflict with substantive/security floor. Literal tier and mandatory router contract cannot both be assumed satisfied; separate behavior choice |
| Code Simplify -> Addy simplification and Delegate | code-simplify/SKILL.md:6-14,21-22; addy-code-simplification/SKILL.md:32-59,101-105,157-185; agents/code-simplifier.md:10-36,52-69 | Exact behavior/default changed scope/incremental tests align. Existing helper revert and separation rules remain relevant; no helper edits proposed |
| Techdebt -> Explore/code-explorer | techdebt/SKILL.md:17-30; explore/SKILL.md:13-15,32-33; agents/code-explorer.md:7-55 | Same 1-3 broad-area count, but narrow direct-read branch conflicts with unconditional dispatch wording. Do not silently select which contract overrides |
| Techdebt -> TDD | techdebt/SKILL.md:69-77; tdd/SKILL.md:3,18-24,35-38 | Conditional test-edit activation differs from helper's mandatory source-edit activation. TDD's existing seam approval remains protected; changing its dependency scope is a separate choice |
| Fixing Accessibility file argument | fixing-accessibility/SKILL.md:12-19 | Explicit source argument/mode exists; actual host argument binding and invocation trace untested. SAG-012 is an analogous consumer limitation, not an automatic expansion of accepted targets |
| Harness Analysis and Improve Repo Harness sidecars | harness-analysis/agents/openai.yaml:2-5; improve-repo-harness/agents/openai.yaml:2-5; harness-analysis/SKILL.md:3,9-17; improve-repo-harness/SKILL.md:3,9 | Both sidecars say test harness. Harness Analysis actually audits agent/session process. Improve Repo Harness's desired meaning is unresolved. SAG-011 owns the existing analogous issue; proposed additions require parent/human reconciliation |
| Installed skill file selection | scripts/install.sh:40-55; scripts/install.ps1:251-276 | 19 of these 26 files ship by source selection: seven entries, seven review references and five sidecars. Four eval definitions and three graders are pruned. None of the entries requires a stripped eval file. Actual installed access untested |
| Custom-agent installation | scripts/install.sh:58-61; scripts/install.ps1:279-281; scripts/install-codex-agents.py:174-187,280-291 | Top-level Markdown is copied to Copilot/Gemini and converted to Codex TOML. Source definition absence cannot be repaired by a skill sidecar. No installer execution or full installer audit |
| Other maintained consumers | tdd/SKILL.md:38; dotnet/SKILL.md:3 | TDD places refactoring in Code Review stage; .NET consumer says load .NET context before review. Imported TDD is not primary audit scope. No code-review bypass of framework dependencies proposed |
| External harness-engineering source | improve-repo-harness/SKILL.md:9 | URL is an unbundled external dependency. Remote content/version, retrieval, trust handling and applicability not established by local source. No upstream import/history investigation; no external instructions activated |

Consumer searches excluded `**/*-workspace/**`, `**/evals/**` and `**/archive/**`. Generated artifacts do not support these conclusions. Shared-root reference existence was checked as navigation only; this batch does not own imported helpers or redesign their shared material.

## Findings and proposed additions

The [single finding register](../findings.md) owns all ten findings below and the additional SAG-008, DD-004 and SAG-011 evidence. Human dispositions and target expansions remain pending. No native behavior was observed. This report retains source coverage and links the owning records.

- [QH-001: Code Review eval oracles disagree with the maintained contract](../findings.md#qh-001-code-review-eval-oracles-disagree-with-the-maintained-contract).
- [QH-002: Required generalist role lacks a repository source definition](../findings.md#qh-002-required-generalist-role-lacks-a-repository-source-definition).
- [QH-003: Fast verification tier conflicts with required review routing floors](../findings.md#qh-003-fast-verification-tier-conflicts-with-required-review-routing-floors).
- [QH-004: Techdebt rollback condition has competing readings](../findings.md#qh-004-techdebt-rollback-condition-has-competing-readings).
- [QH-005: Techdebt unconditional exploration conflicts with Explore's narrow branch](../findings.md#qh-005-techdebt-unconditional-exploration-conflicts-with-explores-narrow-branch).
- [QH-006: Techdebt limits TDD activation contrary to its required helper](../findings.md#qh-006-techdebt-limits-tdd-activation-contrary-to-its-required-helper).
- [QH-007: Harness grader uses lexemes where assertion polarity and meaning matter](../findings.md#qh-007-harness-grader-uses-lexemes-where-assertion-polarity-and-meaning-matter).
- [QH-008: Harness eval artifact writes conflict with the absolute read-only statement](../findings.md#qh-008-harness-eval-artifact-writes-conflict-with-the-absolute-read-only-statement).
- [QH-009: Improve Repo Harness has unresolved recommendation versus execution intent](../findings.md#qh-009-improve-repo-harness-has-unresolved-recommendation-versus-execution-intent).
- [QH-010: Adversarial typo oracle leaves explicit invocation versus need assessment unresolved](../findings.md#qh-010-adversarial-typo-oracle-leaves-explicit-invocation-versus-need-assessment-unresolved).

The existing SAG-008 metric and DD-004 protocol decisions may add Adversarial Review, Code Review and Harness Analysis graders only after live scope review. SAG-011 may add only Harness Analysis sidecar wording; Improve Repo Harness sidecar meaning stays with QH-009. Existing accepted scopes remain unchanged.

## Positive results and evidence limits

Code Review separates changed-line evidence from nearby context, cites explicit standards, preserves spec absence, uses conditional references and has compact output templates. Its seven references are 25-68 lines, so no long-reference navigation condition occurs. Adversarial Review keeps a small suggestions-only core. Code Simplify retains exact behavior, caller understanding and incremental verification. Accessibility provides native HTML examples, concrete priority rules and clear minimal-change/migration boundaries. Techdebt has bounded changed scope, duplication classes, safe ordering and explicit risky-change approvals. Harness Analysis has strong sanitized evidence, cheap inventory, failure limits and uncertainty rules. All seven names/frontmatter parse; all five sidecars retain false implicit invocation. None of those static strengths proves activation or task success.

Four evaluation files contain fifteen scenarios and no bundled fixture references. They are inspectable paper inputs; Adversarial and Code Review ask for planned/checklist artifacts, Harness uses supplied synthetic evidence, and Techdebt relies on unprovisioned current repository context. No reproducible native discovery, fixture state, external-source retrieval, executed role availability, enforced read-only behavior, timed hook behavior or successful refactor is established. Code Simplify, Accessibility and Improve Repo Harness have no bundled eval definitions; this is an evidence gap, not an automatic authoring defect.

No required-client incompatibility is selected merely from missing runtime evidence. Required later native Codex cases/models/repeats follow the approved evidence contract. Copilot/Gemini comparisons remain static; no desktop or universal enforcement claim. Proposed intent resolutions remain outside executable authoring scope until human disposition.

## Per-skill coverage matrices

Each matrix contains the exact 58 catalog IDs in catalog order. Criterion sources, strength and applicability conditions are owned by [coverage.md](../coverage.md#check-catalog). Evidence paths are relative to the skill unless another root is named. A disposition selects a criterion, not passing behavior. QH IDs link the canonical findings above; existing finding producer additions require parent/human reconciliation. Static investigation can finish with defective, partial or unresolved compliance. Native evidence remains unrun.

### adversarial-review

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: bounded task purpose | SKILL.md:9-19 |  | Context cost unmeasured |
| A02 | Expert review with suggestions-only boundary | adapt | Static: narrow expert remit; no implementation | SKILL.md:9-19 |  | Expert suitability and issue verification untested |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | SKILL.md:2-4; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No selected native cases or seven-model runs |
| A04-F | Entry and required YAML | adapt | Static: parsed string name and description | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N | Name syntax and directory match | adapt | Static: matching lowercase kebab-case; under 64 characters | SKILL.md:2 |  | Required-host discovery not exercised |
| A04-D | Description bounds | adapt | Static: nonempty; 140 characters; no XML tags | SKILL.md:3 |  | 1024-character advice is source-specific |
| A05 | Preserved meaningful identity | adopt | Static: name matches declared purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Purpose and trigger metadata | adapt | Static: declared scope in description | SKILL.md:2-4 |  | Activation requires later native traces |
| A07 | Focused entry body | adapt | Static: task-focused entry; length is review signal | SKILL.md:9-19 |  | No automatic defect from line count |
| A08 | Required delegated review | adapt | Static: direct Delegate activation | SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | Native helper/role load untested |
| A09 | No optional advanced branch | not applicable | Not applicable: condition absent | SKILL.md:9-19 |  | No behavior claim |
| A10 | Dependency/reference navigation | adapt | Static: named dependency or resource present | SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | Installed/named resolution untested |
| A11 | No bundled reference over 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-19 |  | No behavior claim |
| A12 | Documented paths/resources | adapt | Static: scoped path or dependency names | SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | Actual path access untested |
| A13 | Multi-step workflow | adopt | Static: ordered task method | SKILL.md:9-13 |  | Native sequencing untested |
| A14 | Review result quality | adapt | Partial: independent review requested; no finding-verification loop specified | SKILL.md:9-15 |  | Issue quality and independence are untested; no mandatory new filter inferred |
| A15 | No dated or historical factual instructions | not applicable | Not applicable: condition absent | SKILL.md:1-19 |  | No behavior claim |
| A16 | Consistent task terminology | adopt | Static: source terminology follows task purpose | SKILL.md:9-19 |  | Execution artifacts not observed |
| A17 | Issues and suggested fixes | adapt | Static: explicit list and suggestions-only output | SKILL.md:11-13 |  | No produced review result |
| A18 | Prompt strength/decision examples | adapt | Partial: three paper examples, not performed reviews | evals/evals.json:5-49 | QH-010 | Typo negative classification versus invocation unresolved |
| A19 | Trivial versus substantive case | adapt | Unresolved: eval skip policy not specified in procedure | SKILL.md:9-13; evals/evals.json:38-47 | QH-010 | Exact intent decision required |
| A20 | Required default delegation | adopt | Static: fresh expert subagent default; trivial-case oracle unresolved | SKILL.md:9-15; evals/evals.json:38-47 | QH-010 | No inferred global skip exception |
| A21 | Baseline-driven improvement claims | adapt | Unresolved: source snapshot is not behavioral baseline | SKILL.md:1-19; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No current baseline/candidate comparison |
| A22 | Three plan/decision evaluations | adapt | Partial: parsed cases, boolean/string predicates grade plans | evals/evals.json:5-49; evals/grade_benchmark.py:60-85 | QH-010 | No read-only/real-review trace; typo intent unresolved |
| A23 | Reusable task knowledge/history | adapt | Static: reusable instructions; provenance of task learning unverified | SKILL.md:9-19 |  | No real-task history corpus established |
| A24 | Fresh-session iteration evidence | adapt | Unresolved: no fresh-session runs | SKILL.md:2-4; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No matched fresh-state iterations |
| A25 | Team-use feedback evidence | adapt | Unresolved: source alone is not team feedback | SKILL.md:1-19 |  | No team-use corpus inspected |
| A26 | Observed activation/navigation | adapt | Unresolved: no native activation/load trace | SKILL.md:2-4; SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | Explicit and permitted implicit activation remain later work |
| A27 | Bundled evaluator error handling | adapt | Partial: static CLI/error branches; shape/no-run gap | evals/grade_benchmark.py:10-12,26-44,60-102 | DD-004 (proposed producer addition) | Existing failure-outcome protocol pending; no grader executed |
| A28 | Evaluator constants/defaults | adapt | Partial: literal thresholds/metric defaults inspectable | evals/grade_benchmark.py:10-12,26-44,60-102 | SAG-008 (proposed producer addition) | Unknown metric representation pending |
| A29 | Repeated deterministic evaluation | adapt | Static: reusable grader utility exists | evals/grade_benchmark.py:10-12,26-44,60-102 |  | Utility correctness untested |
| A30 | Bundled evaluator versus task procedure | adapt | Static: evaluator separate from entry; read only in audit | evals/grade_benchmark.py:10-12,26-44,60-102; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No execution permission inferred |
| A31 | No layout/spatial input contract | not applicable | Not applicable: condition absent | SKILL.md:1-19 |  | No behavior claim |
| A32 | Read-only review result before fixes | adapt | Static: suggestions only, no implementation | SKILL.md:11-13 |  | No review-to-fix approval inferred |
| A33 | Evaluator imports only Python standard library | not applicable | Not applicable: condition absent | evals/grade_benchmark.py:10-12,26-44,60-102; evals/grade_benchmark.py:1-6 |  | No behavior claim |
| A34 | Actual file loading | adapt | Partial: exact source reads/hashes complete | SKILL.md:1-19; exact reviewed inventory |  | Installed/native loading untested |
| A35 | No concrete qualified MCP tool identifier | not applicable | Not applicable: condition absent | SKILL.md:1-19 |  | No behavior claim |
| A36 | Tools and named dependencies | adapt | Partial: required source resources inspected | SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | Actual tools, availability and host permissions untested |
| S01 | Review-only subagent ownership | adapt | Static: implementation and other changes prohibited | SKILL.md:13,19 |  | No enforced subagent containment |
| S02 | File/tool access scope | adapt | Partial: relevant resources described | SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | No actual tool access trace |
| S03 | Inputs/results may contain sensitive data | adapt | Unresolved: output redaction and sensitive-input handling not exercised | SKILL.md:9-19 |  | No real input/output disclosure test; static read is not vulnerability clearance |
| S04 | Untrusted input/dependency instructions | adapt | Unresolved: no adversarial instruction-trust evidence | SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | No prompt-injection or external instruction trace |
| R01 | Scope/name/trigger preservation | adopt | Static: protected contracts recorded | SKILL.md:2-4; protected contracts |  | Human disposition pending; no change authorized |
| R02 | Existing invocation controls | adopt | Static: disable-model-invocation and sidecar false retained | SKILL.md:4; agents/openai.yaml:4-5 | SAG-001/SAG-012 (bounded consumer facts) | Required-host enforcement untested |
| R03 | Suggestions-only autonomy | adopt | Static: no fixes or other changes allowed | SKILL.md:13,19 |  | Native write prohibition untested |
| R04 | Required dependencies/delegation | adapt | Partial: dependency consumers inspected | SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | Actual helper loading/dispatch availability untested |
| R05 | End at review suggestions | adopt | Static: suggestions-only boundary; typo stop unresolved | SKILL.md:9-19; evals/evals.json:38-47 | QH-010 | No triviality branch selected |
| R06 | Task output contracts | adopt | Static: existing result contract retained | SKILL.md:11-13 |  | Native output fidelity untested |
| R07 | This audit repository authority | adopt | Static: only owned report written; primary sources unchanged | ../../../AGENTS.md:13-18,49-62; exact reviewed inventory |  | Parent owns canonical documentation/finding pass |
| R08 | Maintained source versus generated artifacts | adopt | Static: entry/resources/eval definitions separated from runs | SKILL.md:1-19; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No generated run primary evidence |
| R09 | Later source-validation prerequisites | adapt | Partial: source JSON/YAML/AST parsed; no helper executed | SKILL.md:1-19; ../../../.agents/memory/testing/skills.md:8-14 | SAG-001 (bounded consumer fact) | Later accepted changes need exact scoped validation; retained controls stay |
| R10 | No Upgrade procedure or proposed Upgrade consumer | not applicable | Not applicable: condition absent | SKILL.md:1-19 |  | No behavior claim |
| R11 | Plan grading versus task behavior | adapt | Partial: declared review/router flags graded, not performed review | evals/grade_benchmark.py:60-85 | QH-010; DD-004 (proposed addition); SAG-008 (proposed addition) | Trace-backed read-only/routing evidence later; existing protocols pending |
| R12 | Source formatting | adopt | Static: LF; no trailing/blank whitespace in 26-file inventory | SKILL.md:1-19; ../../../.editorconfig:6-19 |  | Source em dashes were not changed; new report contains none |
| C01 | Native discovery/activation | adapt | Unresolved: source metadata is not activation evidence | SKILL.md:2-4 |  | No native Codex discovery or permitted implicit trace |
| C02 | Shipped resources | adapt | Static: non-eval files selected; evals stripped | ../../../scripts/install.sh:40-55; ../../../scripts/install.ps1:251-276 |  | No installed file access trace |
| C03 | Client-specific sidecar/control metadata | adapt | Static: parsed Codex-sidecar fields; enforcement qualified | agents/openai.yaml:1-5 |  | Sidecar is not universal client enforcement |
| C04 | Tool/activation consent | adapt | Unresolved: source invocation is not portable tool consent | SKILL.md:2-4; SKILL.md:9; skills/delegate-to-subagents/SKILL.md:17,85-110 |  | Required-host consent/isolation untested |

### code-review

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: bounded task purpose | SKILL.md:9-117 |  | Context cost unmeasured |
| A02 | Scope/confidence/routing precision | adapt | Partial: change-linked 80+ gate; required role/tier tension | SKILL.md:14-21,54-85 | QH-002; QH-003 | Required-role mapping and routing interpretation unresolved |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | SKILL.md:2-4,30-38; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No selected native cases or seven-model runs |
| A04-F | Entry and required YAML | adapt | Static: parsed string name and description | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N | Name syntax and directory match | adapt | Static: matching lowercase kebab-case; under 64 characters | SKILL.md:2 |  | Required-host discovery not exercised |
| A04-D | Description bounds | adapt | Static: nonempty; 168 characters; no XML tags | SKILL.md:3 |  | 1024-character advice is source-specific |
| A05 | Preserved meaningful identity | adopt | Static: name matches declared purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Purpose and trigger metadata | adapt | Static: declared scope in description | SKILL.md:2-4,30-38 |  | Activation requires later native traces |
| A07 | Focused entry body | adapt | Static: task-focused entry; length is review signal | SKILL.md:9-117 |  | No automatic defect from line count |
| A08 | Seven conditional bundled references | adopt | Static: each reference called from relevant branch | SKILL.md:20,37,42,48,60-63,80,90 |  | Native loading untested |
| A09 | PR/local/fixed point/large changes | adopt | Static: advanced paths conditioned on request and size | SKILL.md:30-42,62-66,87-90 |  | No conditional resource-load trace |
| A10 | Direct one-hop reference navigation | adopt | Static: all seven referenced paths exist | SKILL.md:20,37,42,48,60-63,80,90 |  | Installed relative resolution untested |
| A11 | No bundled reference over 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-117 |  | No behavior claim |
| A12 | Entry/resource versus eval paths | adapt | Defective: eval oracles use stale underscore paths | SKILL.md:20,60-63,90; evals/grade_benchmark.py:150,174,186 | QH-001 | Current source paths exist; artifact recognition requires repair validation |
| A13 | Multi-step workflow | adopt | Static: ordered task method | SKILL.md:23-100 |  | Native sequencing untested |
| A14 | False-positive feedback loop | adapt | Partial: exact hunk and 80+ filtering; tier conflict | SKILL.md:79-85,104-117; references/false-positive-rubric.md:3-26 | QH-003 | Filter correctness and routed floor untested |
| A15 | No dated or historical factual instructions | not applicable | Not applicable: condition absent | SKILL.md:1-117 |  | No behavior claim |
| A16 | Review score/reference terminology | adapt | Defective: eval wording diverges from current entry | SKILL.md:20,84; evals/evals.json:11-19,40-48 | QH-001 | No current oracle execution |
| A17 | Normal/PR/YAML outputs | adopt | Static: exact outputs/no-op templates; eval path wording stale | SKILL.md:87-100; references/output-formats.md:3-68 | QH-001 | Produced output fidelity untested |
| A18 | Report templates and scenario examples | adapt | Partial: concrete templates; stale scenario constraints | references/output-formats.md:9-68; evals/evals.json:5-69 | QH-001 | Examples do not prove workflow |
| A19 | PR eligibility/spec/large-change/lightweight branches | adopt | Static: explicit branches; unverified role/tier constraints | SKILL.md:30-66,87-100; references/pr-protocol.md:22-33 | QH-002; QH-003 | Lightweight exception retained; no all-host execution claim |
| A20 | Four-perspective default and lightweight exception | adapt | Partial: exact default; host role/parallel capacity unresolved | SKILL.md:54-66,79-85 | QH-002; QH-003 | Four concurrent jobs and Fast-tier interpretation not exercised |
| A21 | Baseline-driven improvement claims | adapt | Unresolved: source snapshot is not behavioral baseline | SKILL.md:1-117; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No current baseline/candidate comparison |
| A22 | Four paper evaluations and grader | adapt | Defective: stale cutoff/path/intake/stop predicates | evals/evals.json:9-19,38-48; evals/grade_benchmark.py:128-150,174-186 | QH-001 | No native review; preserved cases need matched artifact validation |
| A23 | Reusable task knowledge/history | adapt | Static: reusable instructions; provenance of task learning unverified | SKILL.md:9-117 |  | No real-task history corpus established |
| A24 | Fresh-session iteration evidence | adapt | Unresolved: no fresh-session runs | SKILL.md:2-4,30-38; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No matched fresh-state iterations |
| A25 | Team-use feedback evidence | adapt | Unresolved: source alone is not team feedback | SKILL.md:1-117 |  | No team-use corpus inspected |
| A26 | Observed activation/navigation | adapt | Unresolved: no native activation/load trace | SKILL.md:2-4,30-38; SKILL.md:25-28,54-66; skills/delegate-to-subagents/SKILL.md:85-110 |  | Explicit and permitted implicit activation remain later work |
| A27 | Bundled evaluator error handling | adapt | Partial: static CLI/error branches; shape/no-run gap | evals/grade_benchmark.py:19-58,78-105,114-242 | DD-004 (proposed producer addition) | Existing failure-outcome protocol pending; no grader executed |
| A28 | Review thresholds and metric defaults | adapt | Partial: 80+ and triage reasons evident; stale oracle and zero defaults | SKILL.md:20,42; references/false-positive-rubric.md:3-17; evals/grade_benchmark.py:38,48-58,149-150 | QH-001; SAG-008 (proposed addition) | Metric protocol pending; thresholds are not automatic defect signals |
| A29 | Repeated deterministic evaluation | adapt | Static: reusable grader utility exists | evals/grade_benchmark.py:19-58,78-105,114-242 |  | Utility correctness untested |
| A30 | Bundled evaluator versus task procedure | adapt | Static: evaluator separate from entry; read only in audit | evals/grade_benchmark.py:19-58,78-105,114-242; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No execution permission inferred |
| A31 | No layout/spatial input contract | not applicable | Not applicable: condition absent | SKILL.md:1-117 |  | No behavior claim |
| A32 | Review result before external commenting | adapt | Static: target/intake precedes review; recheck before post | SKILL.md:30-38,87-100; references/pr-protocol.md:29-33 |  | User comment mode/host consent remains necessary; no external mutation |
| A33 | Evaluator imports only Python standard library | not applicable | Not applicable: condition absent | evals/grade_benchmark.py:19-58,78-105,114-242; evals/grade_benchmark.py:1-6 |  | No behavior claim |
| A34 | Actual file loading | adapt | Partial: exact source reads/hashes complete | SKILL.md:1-117; exact reviewed inventory |  | Installed/native loading untested |
| A35 | No concrete qualified MCP tool identifier | not applicable | Not applicable: condition absent | SKILL.md:1-117 |  | No behavior claim |
| A36 | Required roles/Git/PR intake | adapt | Unresolved: missing repository generalist definition; tools not exercised | SKILL.md:21,37-38,54-66; references/pr-protocol.md:7; agents/ inventory | QH-002 | Host-supported mapping and parallel capacity unverified |
| S01 | Change scope and review-only authority | adapt | Static: scope fixed; no unsolicited builds/tests | SKILL.md:14-18,79-85 |  | Persona task constraints and containment untested |
| S02 | Repository read and requested PR comment | adapt | Static: requested mode and PR recheck bound external write | SKILL.md:87-100; references/pr-protocol.md:29-33 |  | No live GitHub read/post; host consent untested |
| S03 | Inputs/results may contain sensitive data | adapt | Unresolved: output redaction and sensitive-input handling not exercised | SKILL.md:9-117 |  | No real input/output disclosure test; static read is not vulnerability clearance |
| S04 | Repo/spec/issue/dependency content | adapt | Partial: explicit cited standards and change evidence required | SKILL.md:19,44-52,79-85; references/code-smells.md:3-10 |  | No embedded-instruction trust trace |
| R01 | Scope/name/trigger preservation | adopt | Static: protected contracts recorded | SKILL.md:2-4,30-38; protected contracts |  | Human disposition pending; no change authorized |
| R02 | Existing invocation controls | adopt | Static: disable-model-invocation and sidecar false retained | SKILL.md:4; agents/openai.yaml:4-5 | SAG-001/SAG-012 (bounded consumer facts) | Required-host enforcement untested |
| R03 | Review-only and requested comment mode | adopt | Static: no unsolicited validation; requested mode governs posting | SKILL.md:16,87-100; references/pr-protocol.md:29-33 |  | Role prompts must retain consumer boundary; no runtime consent evidence |
| R04 | Mandatory helpers/four roles/routing | adapt | Unresolved: role absence and Fast-floor conflict | SKILL.md:25-28,54-66,79-85; skills/subagent-model-router/reference/review-routing.md:7-9,40-49 | QH-002; QH-003 | Exact dependency/role interpretation requires decision |
| R05 | Clarification/missing resource/PR eligibility stops | adopt | Static: three defined PR states; stale additional oracle | SKILL.md:15,21,35; references/pr-protocol.md:22-26; evals/grade_benchmark.py:135-150 | QH-001 | No already-reviewed stop added |
| R06 | Task output contracts | adopt | Static: existing result contract retained | SKILL.md:87-100; references/output-formats.md:3-68 |  | Native output fidelity untested |
| R07 | This audit repository authority | adopt | Static: only owned report written; primary sources unchanged | ../../../AGENTS.md:13-18,49-62; exact reviewed inventory |  | Parent owns canonical documentation/finding pass |
| R08 | Maintained source versus generated artifacts | adopt | Static: entry/resources/eval definitions separated from runs | SKILL.md:1-117; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No generated run primary evidence |
| R09 | Later source-validation prerequisites | adapt | Partial: source JSON/YAML/AST parsed; no helper executed | SKILL.md:1-117; ../../../.agents/memory/testing/skills.md:8-14 | SAG-001 (bounded consumer fact) | Later accepted changes need exact scoped validation; retained controls stay |
| R10 | No Upgrade procedure or proposed Upgrade consumer | not applicable | Not applicable: condition absent | SKILL.md:1-117 |  | No behavior claim |
| R11 | Evaluation and actual-review evidence | adapt | Defective: stale artifact oracle; runtime traces absent | evals/grade_benchmark.py:114-214,227-242 | QH-001; DD-004 (proposed addition); SAG-008 (proposed addition) | No checklist accepted as proof of dispatch or review |
| R12 | Source formatting | adopt | Static: LF; no trailing/blank whitespace in 26-file inventory | SKILL.md:1-117; ../../../.editorconfig:6-19 |  | Source em dashes were not changed; new report contains none |
| C01 | Native discovery/activation | adapt | Unresolved: source metadata is not activation evidence | SKILL.md:2-4,30-38 |  | No native Codex discovery or permitted implicit trace |
| C02 | Shipped resources | adapt | Static: non-eval files selected; evals stripped | ../../../scripts/install.sh:40-55; ../../../scripts/install.ps1:251-276 |  | No installed file access trace |
| C03 | Client-specific sidecar/control metadata | adapt | Static: parsed Codex-sidecar fields; enforcement qualified | agents/openai.yaml:1-5 |  | Sidecar is not universal client enforcement |
| C04 | Tool/activation consent | adapt | Unresolved: source invocation is not portable tool consent | SKILL.md:2-4,30-38; SKILL.md:25-28,54-66; skills/delegate-to-subagents/SKILL.md:85-110 |  | Required-host consent/isolation untested |

### code-simplify

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: bounded task purpose | SKILL.md:6-22 |  | Context cost unmeasured |
| A02 | Incremental behavior-preserving edits | adopt | Static: caller/edge/test understanding then small tested changes | SKILL.md:8,11-22 |  | Actual behavioral equivalence untested |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | SKILL.md:2-3,8,12; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No selected native cases or seven-model runs |
| A04-F | Entry and required YAML | adapt | Static: parsed string name and description | SKILL.md:1-4 |  | Native parser/discovery untested |
| A04-N | Name syntax and directory match | adapt | Static: matching lowercase kebab-case; under 64 characters | SKILL.md:2 |  | Required-host discovery not exercised |
| A04-D | Description bounds | adapt | Static: nonempty; 91 characters; no XML tags | SKILL.md:3 |  | 1024-character advice is source-specific |
| A05 | Preserved meaningful identity | adopt | Static: name matches declared purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Purpose and trigger metadata | adapt | Static: declared scope in description | SKILL.md:2-3,8,12 |  | Activation requires later native traces |
| A07 | Focused entry body | adapt | Static: task-focused entry; length is review signal | SKILL.md:6-22 |  | No automatic defect from line count |
| A08 | Required Addy guidance, useful delegation | adapt | Static: named helper reuse avoids copied bulk guidance | SKILL.md:6,10; skills/addy-code-simplification/SKILL.md:32-59,101-105,157-185 |  | Imported helper excluded from primary review |
| A09 | Useful delegation and specified-scope alternative | adapt | Static: conditional delegation, broader scope only when specified | SKILL.md:8,10,12 |  | Named helper/condition enforcement untested |
| A10 | Dependency/reference navigation | adapt | Static: named dependency or resource present | SKILL.md:6,10; skills/addy-code-simplification/SKILL.md:101-105,157-185 |  | Installed/named resolution untested |
| A11 | No bundled reference over 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A12 | Documented paths/resources | adapt | Static: scoped path or dependency names | SKILL.md:6,10; skills/addy-code-simplification/SKILL.md:101-105,157-185 |  | Actual path access untested |
| A13 | Seven incremental steps | adopt | Static: ordering from conventions/scope to verification | SKILL.md:10-22 |  | No edit/test/build trace |
| A14 | Tests per simplification and final build | adopt | Static: incremental tests and final clean diff | SKILL.md:21-22; skills/addy-code-simplification/SKILL.md:157-185 |  | No evidence of passing tests/build |
| A15 | No dated or historical factual instructions | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A16 | Consistent task terminology | adopt | Static: source terminology follows task purpose | SKILL.md:6-22 |  | Execution artifacts not observed |
| A17 | No fixed report schema/template required | not applicable | Not applicable: condition absent | SKILL.md:6-22 |  | No behavior claim |
| A18 | Simplification technique examples | adopt | Static: nesting/function/ternary/name/duplication/dead-code examples | SKILL.md:14-20 |  | Examples are method guidance, not execution |
| A19 | Recent/specified scope and safe dead code | adopt | Static: user scope, useful dispatch and confirmation condition | SKILL.md:8,10,12,20 |  | Confirmation and scope handling untested |
| A20 | Default recent-change scope | adopt | Static: recent changes unless broader scope specified | SKILL.md:8,12 |  | No broadened scope inferred |
| A21 | Baseline-driven improvement claims | adapt | Unresolved: source snapshot is not behavioral baseline | SKILL.md:1-22; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No current baseline/candidate comparison |
| A22 | Evaluation evidence | adapt | Unresolved: no bundled eval definition | SKILL.md:1-22 |  | Safe native cases/fixtures remain later work |
| A23 | Reusable task knowledge/history | adapt | Static: reusable instructions; provenance of task learning unverified | SKILL.md:6-22 |  | No real-task history corpus established |
| A24 | Fresh-session iteration evidence | adapt | Unresolved: no fresh-session runs | SKILL.md:2-3,8,12; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No matched fresh-state iterations |
| A25 | Team-use feedback evidence | adapt | Unresolved: source alone is not team feedback | SKILL.md:1-22 |  | No team-use corpus inspected |
| A26 | Observed activation/navigation | adapt | Unresolved: no native activation/load trace | SKILL.md:2-3,8,12; SKILL.md:6,10; skills/addy-code-simplification/SKILL.md:101-105,157-185 |  | Explicit and permitted implicit activation remain later work |
| A27 | No bundled executable resource | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A28 | No configurable executable constants | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A29 | No repeated deterministic utility need established | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A30 | No bundled or named executable helper command | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A31 | No layout/spatial input contract | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A32 | Understand before source edits | adapt | Static: purpose/callers/edges/test coverage before changing | SKILL.md:11-13 |  | No inspected intermediate task artifact |
| A33 | No external runtime package required by this bundle | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A34 | Actual file loading | adapt | Partial: exact source reads/hashes complete | SKILL.md:1-22; exact reviewed inventory |  | Installed/native loading untested |
| A35 | No concrete qualified MCP tool identifier | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| A36 | Project tests/build and helpers | adapt | Partial: project conventions required; commands project-specific | SKILL.md:6,10-13,21-22 |  | Do not invent generic commands; actual tool availability untested |
| S01 | Exact behavior and changed-code scope | adapt | Static: behavior preservation and selected scope explicit | SKILL.md:8,12-13,21-22 |  | No before/after outcome comparison |
| S02 | File/tool access scope | adapt | Partial: relevant resources described | SKILL.md:6,10; skills/addy-code-simplification/SKILL.md:101-105,157-185 |  | No actual tool access trace |
| S03 | Inputs/results may contain sensitive data | adapt | Unresolved: output redaction and sensitive-input handling not exercised | SKILL.md:6-22 |  | No real input/output disclosure test; static read is not vulnerability clearance |
| S04 | Untrusted input/dependency instructions | adapt | Unresolved: no adversarial instruction-trust evidence | SKILL.md:6,10; skills/addy-code-simplification/SKILL.md:101-105,157-185 |  | No prompt-injection or external instruction trace |
| R01 | Scope/name/trigger preservation | adopt | Static: protected contracts recorded | SKILL.md:2-3,8,12; protected contracts |  | Human disposition pending; no change authorized |
| R02 | No invocation control or sidecar exists | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| R03 | Source refactoring authority | adopt | Partial: exact behavior/scope; helper approval contracts preserved | SKILL.md:6,8,12,20; skills/addy-code-simplification/SKILL.md:32-59,157-185 |  | No external or broad mutation authority inferred |
| R04 | Required Addy simplification and Delegate | adapt | Static: both helpers exist; delegation conditional on usefulness | SKILL.md:6,10; bounded dependency section |  | Actual helper loading/dispatch untested |
| R05 | Final verification and helper rollback | adopt | Static: passing tests/build/clean diff; helper reverts failed or unclear edits | SKILL.md:21-22; skills/addy-code-simplification/SKILL.md:157-185 |  | No rollback action executed |
| R06 | Verified simplification result | adopt | Static: exact behavior, tests/build and clean diff required | SKILL.md:8,21-22 |  | No final result artifact or fixed report format claimed |
| R07 | This audit repository authority | adopt | Static: only owned report written; primary sources unchanged | ../../../AGENTS.md:13-18,49-62; exact reviewed inventory |  | Parent owns canonical documentation/finding pass |
| R08 | Maintained source versus generated artifacts | adopt | Static: entry/resources/eval definitions separated from runs | SKILL.md:1-22; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No generated run primary evidence |
| R09 | Later source-validation prerequisites | adapt | Partial: source JSON/YAML/AST parsed; no helper executed | SKILL.md:1-22; ../../../.agents/memory/testing/skills.md:8-14 | SAG-001 (bounded consumer fact) | Later accepted changes need exact scoped validation; retained controls stay |
| R10 | No Upgrade procedure or proposed Upgrade consumer | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| R11 | Evidence and grading integrity | adapt | Unresolved: no native/evaluator evidence | SKILL.md:1-22 |  | Artifact plans distinct from performed actions |
| R12 | Source formatting | adopt | Static: LF; no trailing/blank whitespace in 26-file inventory | SKILL.md:1-22; ../../../.editorconfig:6-19 |  | Source em dashes were not changed; new report contains none |
| C01 | Native discovery/activation | adapt | Unresolved: source metadata is not activation evidence | SKILL.md:2-3,8,12 |  | No native Codex discovery or permitted implicit trace |
| C02 | Shipped resources | adapt | Static: non-eval files selected; evals stripped | ../../../scripts/install.sh:40-55; ../../../scripts/install.ps1:251-276 |  | No installed file access trace |
| C03 | No client-specific adapter fields bundled | not applicable | Not applicable: condition absent | SKILL.md:1-22 |  | No behavior claim |
| C04 | Tool/activation consent | adapt | Unresolved: source invocation is not portable tool consent | SKILL.md:2-3,8,12; SKILL.md:6,10; skills/addy-code-simplification/SKILL.md:101-105,157-185 |  | Required-host consent/isolation untested |

### fixing-accessibility

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Focused HTML accessibility rules | adopt | Static: categories, priorities and small examples within scope | SKILL.md:33-136 |  | Guideline utility unmeasured |
| A02 | Minimal targeted UI changes | adopt | Static: concrete rules, native-first and no unrelated refactors | SKILL.md:21,49-113,133-136 |  | Real keyboard/contrast/focus behavior untested |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | SKILL.md:2-3,12-29; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No selected native cases or seven-model runs |
| A04-F | Entry and required YAML | adapt | Static: parsed string name and description | SKILL.md:1-4 |  | Native parser/discovery untested |
| A04-N | Name syntax and directory match | adapt | Static: matching lowercase kebab-case; under 64 characters | SKILL.md:2 |  | Required-host discovery not exercised |
| A04-D | Description bounds | adapt | Static: nonempty; 218 characters; no XML tags | SKILL.md:3 |  | 1024-character advice is source-specific |
| A05 | Preserved meaningful identity | adopt | Static: name matches declared purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Purpose and trigger metadata | adapt | Static: declared scope in description | SKILL.md:2-3,12-29 |  | Activation requires later native traces |
| A07 | Focused entry body | adapt | Static: task-focused entry; length is review signal | SKILL.md:6-136 |  | No automatic defect from line count |
| A08 | Inline concise rule categories | adapt | Static: quick reference and examples; no bundled dependencies | SKILL.md:33-129 |  | No long-reference extraction need established |
| A09 | No optional advanced resource branch | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A10 | No bundled reference or named skill dependency | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A11 | No bundled reference over 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A12 | File argument and element identifiers | adapt | Static: generic file argument and small HTML IDs | SKILL.md:15-19,117-129 | SAG-012 (bounded analogy only) | Host file-argument binding untested |
| A13 | Rule-based review/application | adapt | Static: invocation mode then priority order; no complex batch workflow | SKILL.md:12-21,33-45,131-136 |  | No staged application trace |
| A14 | Accessibility quality feedback | adapt | Partial: rules and review guidance; no explicit interactive verification loop | SKILL.md:57-70,95-107,131-136 |  | Keyboard, screen reader, focus, motion and contrast checks not run |
| A15 | No dated or historical factual instructions | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A16 | Consistent task terminology | adopt | Static: source terminology follows task purpose | SKILL.md:6-136 |  | Execution artifacts not observed |
| A17 | File review output | adopt | Static: exact snippet, short impact and code-level fix | SKILL.md:15-19,135 |  | No emitted review artifact |
| A18 | Concrete before/after HTML | adopt | Static: names/native button/linked error examples | SKILL.md:117-129 |  | Examples do not certify accessible runtime UI |
| A19 | Bare invocation versus file report | adapt | Static: two declared modes; conditional dialog/media rules | SKILL.md:12-19,63,102-107 |  | Native argument binding and conditional application untested |
| A20 | Native semantics and minimal fixes default | adopt | Static: native-first, no broad rewrites/library migrations | SKILL.md:21,74,111-113,134,136 |  | No custom-widget/library choice inferred |
| A21 | Baseline-driven improvement claims | adapt | Unresolved: source snapshot is not behavioral baseline | SKILL.md:1-136; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No current baseline/candidate comparison |
| A22 | Evaluation evidence | adapt | Unresolved: no bundled eval definition | SKILL.md:1-136 |  | Safe native cases/fixtures remain later work |
| A23 | Reusable task knowledge/history | adapt | Static: reusable instructions; provenance of task learning unverified | SKILL.md:6-136 |  | No real-task history corpus established |
| A24 | Fresh-session iteration evidence | adapt | Unresolved: no fresh-session runs | SKILL.md:2-3,12-29; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No matched fresh-state iterations |
| A25 | Team-use feedback evidence | adapt | Unresolved: source alone is not team feedback | SKILL.md:1-136 |  | No team-use corpus inspected |
| A26 | Observed activation/navigation | adapt | Unresolved: no native activation/load trace | SKILL.md:2-3,12-29; SKILL.md:111-113,136 |  | Explicit and permitted implicit activation remain later work |
| A27 | No bundled executable resource | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A28 | No configurable executable constants | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A29 | No repeated deterministic utility need established | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A30 | No bundled or named executable helper command | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A31 | UI layout/states and capable host | adapt | Partial: contrast/focus/media rules support visual inspection | SKILL.md:59-70,95-107 |  | No screenshot/browser/assistive-technology inspection; visual proof alone is insufficient |
| A32 | No prescribed risky batch/destructive action | not applicable | Not applicable: condition absent | SKILL.md:21,111-113 |  | No behavior claim |
| A33 | No external runtime package required by this bundle | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A34 | Actual file loading | adapt | Partial: exact source reads/hashes complete | SKILL.md:1-136; exact reviewed inventory |  | Installed/native loading untested |
| A35 | No concrete qualified MCP tool identifier | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| A36 | Actual UI inspection capability | adapt | Unresolved: no browser/assistive-tool prerequisites prescribed | SKILL.md:57-70,95-107,131-136 |  | Host UI tooling and verification remain future task-specific evidence |
| S01 | Minimal UI task boundary | adapt | Static: unrelated refactoring and library migration excluded | SKILL.md:21,111-113 |  | No actual write boundary trace |
| S02 | Given-file review or UI constraints | adapt | Static: source mode and minimal edits stated | SKILL.md:12-21,111-113 |  | No UI or network access exercised |
| S03 | Inputs/results may contain sensitive data | adapt | Unresolved: output redaction and sensitive-input handling not exercised | SKILL.md:6-136 |  | No real input/output disclosure test; static read is not vulnerability clearance |
| S04 | Untrusted input/dependency instructions | adapt | Unresolved: no adversarial instruction-trust evidence | SKILL.md:111-113,136 |  | No prompt-injection or external instruction trace |
| R01 | Scope/name/trigger preservation | adopt | Static: protected contracts recorded | SKILL.md:2-3,12-29; protected contracts |  | Human disposition pending; no change authorized |
| R02 | No invocation control or sidecar exists | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| R03 | Mode-specific review versus fixes | adopt | Static: file mode reports; no large UI rewriting | SKILL.md:12-21,111-113 |  | No ambiguity resolved by extra global approval gate |
| R04 | No required delegated role/helper | not applicable | Not applicable: no named mandatory skill/agent | SKILL.md:1-136 |  | Established accessible primitives are advice, not a named dependency |
| R05 | Review/result boundary | adopt | Static: bounded file report and minimal-change rules; no separate handoff file | SKILL.md:15-21,111-113,131-136 |  | No native stopping trace |
| R06 | Three-part findings and concrete fixes | adopt | Static: output wording explicitly specified | SKILL.md:15-19,135 |  | Runtime output fidelity untested |
| R07 | This audit repository authority | adopt | Static: only owned report written; primary sources unchanged | ../../../AGENTS.md:13-18,49-62; exact reviewed inventory |  | Parent owns canonical documentation/finding pass |
| R08 | Maintained source versus generated artifacts | adopt | Static: entry/resources/eval definitions separated from runs | SKILL.md:1-136; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No generated run primary evidence |
| R09 | Later source-validation prerequisites | adapt | Partial: source JSON/YAML/AST parsed; no helper executed | SKILL.md:1-136; ../../../.agents/memory/testing/skills.md:8-14 | SAG-001 (bounded consumer fact) | Later accepted changes need exact scoped validation; retained controls stay |
| R10 | No Upgrade procedure or proposed Upgrade consumer | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| R11 | Evidence and grading integrity | adapt | Unresolved: no native/evaluator evidence | SKILL.md:1-136 |  | Artifact plans distinct from performed actions |
| R12 | Source formatting | adopt | Static: LF; no trailing/blank whitespace in 26-file inventory | SKILL.md:1-136; ../../../.editorconfig:6-19 |  | Source em dashes were not changed; new report contains none |
| C01 | Native discovery/activation | adapt | Unresolved: source metadata is not activation evidence | SKILL.md:2-3,12-29 |  | No native Codex discovery or permitted implicit trace |
| C02 | Shipped resources | adapt | Static: non-eval files selected; evals stripped | ../../../scripts/install.sh:40-55; ../../../scripts/install.ps1:251-276 |  | No installed file access trace |
| C03 | No client-specific adapter fields bundled | not applicable | Not applicable: condition absent | SKILL.md:1-136 |  | No behavior claim |
| C04 | Tool/activation consent | adapt | Unresolved: source invocation is not portable tool consent | SKILL.md:2-3,12-29; SKILL.md:111-113,136 |  | Required-host consent/isolation untested |

### techdebt

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: bounded task purpose | SKILL.md:9-98 |  | Context cost unmeasured |
| A02 | Behavior-preserving dedupe and approvals | adapt | Partial: strong scope/priority gates; dependency/rollback tensions | SKILL.md:17-30,49-87 | QH-004; QH-005; QH-006 | Conflicting branches require separate intent decisions |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | SKILL.md:2-4,15-26; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No selected native cases or seven-model runs |
| A04-F | Entry and required YAML | adapt | Static: parsed string name and description | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N | Name syntax and directory match | adapt | Static: matching lowercase kebab-case; under 64 characters | SKILL.md:2 |  | Required-host discovery not exercised |
| A04-D | Description bounds | adapt | Static: nonempty; 125 characters; no XML tags | SKILL.md:3 |  | 1024-character advice is source-specific |
| A05 | Preserved meaningful identity | adopt | Static: name matches declared purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Purpose and trigger metadata | adapt | Static: declared scope in description | SKILL.md:2-4,15-26 |  | Activation requires later native traces |
| A07 | Focused entry body | adapt | Static: task-focused entry; length is review signal | SKILL.md:9-98 |  | No automatic defect from line count |
| A08 | Required delegation/exploration/TDD | adapt | Partial: named reuse; caller conditions disagree with helpers | SKILL.md:13,30,69-77; skills/explore/SKILL.md:13,33; skills/tdd/SKILL.md:3 | QH-005; QH-006 | No helper scope silently waived |
| A09 | Provided candidates skip discovery | adopt | Static: supplied candidates versus status/diff default | SKILL.md:17-26 |  | No supplied-candidate branch execution |
| A10 | Dependency/reference navigation | adapt | Static: named dependency or resource present | SKILL.md:13,30,69-76; skills/explore/SKILL.md:13-15,33; skills/tdd/SKILL.md:3,18-24,38 |  | Installed/named resolution untested |
| A11 | No bundled reference over 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A12 | Documented paths/resources | adapt | Static: scoped path or dependency names | SKILL.md:13,30,69-76; skills/explore/SKILL.md:13-15,33; skills/tdd/SKILL.md:3,18-24,38 |  | Actual path access untested |
| A13 | Scope/discover/prioritize/refactor/validate/report | adapt | Partial: clear six stages, narrow/TDD conditions unresolved | SKILL.md:11-98 | QH-005; QH-006 | Native dependency sequencing untested |
| A14 | Per-candidate validation and rollback | adapt | Unresolved: competing otherwise clause readings | SKILL.md:65-79 | QH-004 | Pass/fail/repair/unresolved-failure branches need intent choice |
| A15 | No dated or historical factual instructions | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A16 | Consistent task terminology | adopt | Static: source terminology follows task purpose | SKILL.md:9-98 |  | Execution artifacts not observed |
| A17 | Dedupe report fields | adopt | Static: scope/helpers/validation/candidate states required | SKILL.md:89-98 |  | No completed dedupe report or commands observed |
| A18 | Duplication classes and paper examples | adapt | Partial: examples span backend/scripts/UI; eval context unspecified | SKILL.md:32-43; evals/evals.json:5-38 |  | No grounded changed-repo fixture evidence |
| A19 | Scope/no-op/approval/rollback branches | adapt | Unresolved: otherwise rollback and helper conditions conflict | SKILL.md:17-30,45,63,74-87 | QH-004; QH-005; QH-006 | No branch interpretation selected |
| A20 | Safest 1-3 candidates and narrow exploration | adapt | Partial: safe ordering explicit; dispatch condition conflict | SKILL.md:49-63,30; skills/explore/SKILL.md:13-15,33 | QH-005 | Broad-area count retained; narrow override unresolved |
| A21 | Baseline-driven improvement claims | adapt | Unresolved: source snapshot is not behavioral baseline | SKILL.md:1-98; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No current baseline/candidate comparison |
| A22 | Three paper prompts using current repository context | adapt | Partial: parseable report-oriented cases; no fixture files/grader | evals/evals.json:5-38 |  | Reproducible changed repo, no-op, approvals and rollback cases remain gaps |
| A23 | Reusable task knowledge/history | adapt | Static: reusable instructions; provenance of task learning unverified | SKILL.md:9-98 |  | No real-task history corpus established |
| A24 | Fresh-session iteration evidence | adapt | Unresolved: no fresh-session runs | SKILL.md:2-4,15-26; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No matched fresh-state iterations |
| A25 | Team-use feedback evidence | adapt | Unresolved: source alone is not team feedback | SKILL.md:1-98 |  | No team-use corpus inspected |
| A26 | Observed activation/navigation | adapt | Unresolved: no native activation/load trace | SKILL.md:2-4,15-26; SKILL.md:13,30,69-76; skills/explore/SKILL.md:13-15,33; skills/tdd/SKILL.md:3,18-24,38 |  | Explicit and permitted implicit activation remain later work |
| A27 | No bundled executable resource | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A28 | No configurable executable constants | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A29 | No repeated deterministic utility need established | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A30 | No bundled or named executable helper command | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A31 | No layout/spatial input contract | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A32 | Shortlist and prioritize before edits | adopt | Static: candidate shortlist/classification then safety ordering | SKILL.md:26,39-43,49-63 |  | No scoped candidate artifact or approval trace |
| A33 | No external runtime package required by this bundle | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A34 | Actual file loading | adapt | Partial: exact source reads/hashes complete | SKILL.md:1-98; exact reviewed inventory |  | Installed/native loading untested |
| A35 | No concrete qualified MCP tool identifier | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| A36 | Explorer/refactor/validator and project commands | adapt | Partial: source roles/helpers exist; exact commands task-dependent | SKILL.md:19,30,69-76; agents/code-explorer.md:1-5 |  | Actual runtime availability and validation commands untested |
| S01 | In-scope behavior-preserving edits | adapt | Static: safe candidate limit and user high-risk gate | SKILL.md:9,23-24,49-63,71-87 |  | No mutation/rollback containment exercised |
| S02 | File/tool access scope | adapt | Partial: relevant resources described | SKILL.md:13,30,69-76; skills/explore/SKILL.md:13-15,33; skills/tdd/SKILL.md:3,18-24,38 |  | No actual tool access trace |
| S03 | Inputs/results may contain sensitive data | adapt | Unresolved: output redaction and sensitive-input handling not exercised | SKILL.md:9-98 |  | No real input/output disclosure test; static read is not vulnerability clearance |
| S04 | Untrusted input/dependency instructions | adapt | Unresolved: no adversarial instruction-trust evidence | SKILL.md:13,30,69-76; skills/explore/SKILL.md:13-15,33; skills/tdd/SKILL.md:3,18-24,38 |  | No prompt-injection or external instruction trace |
| R01 | Scope/name/trigger preservation | adopt | Static: protected contracts recorded | SKILL.md:2-4,15-26; protected contracts |  | Human disposition pending; no change authorized |
| R02 | Existing invocation controls | adopt | Static: disable-model-invocation and sidecar false retained | SKILL.md:4; agents/openai.yaml:4-5 | SAG-001/SAG-012 (bounded consumer facts) | Required-host enforcement untested |
| R03 | Explicit high-risk change approvals | adopt | Static: public API/architecture/UI/naming/unrelated changes ask | SKILL.md:81-87 | QH-006 | TDD seam approval preserved if activated; no new approvals inferred |
| R04 | Required Delegate/Explore/TDD consumer contract | adapt | Unresolved: narrow dispatch and conditional TDD conflict | SKILL.md:13,30,69-76; skills/explore/SKILL.md:13,33; skills/tdd/SKILL.md:3,18-24 | QH-005; QH-006 | Human resolves caller exceptions versus helper conditions |
| R05 | No changes/duplication and unsafe/ambiguous stops | adapt | Partial: clear no-op stops; rollback otherwise ambiguous | SKILL.md:23-24,45,77-87 | QH-004 | No rollback semantics selected |
| R06 | Validated duplicates removed and candidate states | adapt | Partial: report fields clear; successful candidate retention unresolved | SKILL.md:77,89-98 | QH-004 | Native result and branch interpretation missing |
| R07 | This audit repository authority | adopt | Static: only owned report written; primary sources unchanged | ../../../AGENTS.md:13-18,49-62; exact reviewed inventory |  | Parent owns canonical documentation/finding pass |
| R08 | Maintained source versus generated artifacts | adopt | Static: entry/resources/eval definitions separated from runs | SKILL.md:1-98; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No generated run primary evidence |
| R09 | Later source-validation prerequisites | adapt | Partial: source JSON/YAML/AST parsed; no helper executed | SKILL.md:1-98; ../../../.agents/memory/testing/skills.md:8-14 | SAG-001 (bounded consumer fact) | Later accepted changes need exact scoped validation; retained controls stay |
| R10 | No Upgrade procedure or proposed Upgrade consumer | not applicable | Not applicable: condition absent | SKILL.md:1-98 |  | No behavior claim |
| R11 | Evidence and grading integrity | adapt | Partial: eval source reviewed, no passing/native claims | evals/evals.json:5-38 |  | Artifact plans distinct from performed actions |
| R12 | Source formatting | adopt | Static: LF; no trailing/blank whitespace in 26-file inventory | SKILL.md:1-98; ../../../.editorconfig:6-19 |  | Source em dashes were not changed; new report contains none |
| C01 | Native discovery/activation | adapt | Unresolved: source metadata is not activation evidence | SKILL.md:2-4,15-26 |  | No native Codex discovery or permitted implicit trace |
| C02 | Shipped resources | adapt | Static: non-eval files selected; evals stripped | ../../../scripts/install.sh:40-55; ../../../scripts/install.ps1:251-276 |  | No installed file access trace |
| C03 | Client-specific sidecar/control metadata | adapt | Static: parsed Codex-sidecar fields; enforcement qualified | agents/openai.yaml:1-5 |  | Sidecar is not universal client enforcement |
| C04 | Tool/activation consent | adapt | Unresolved: source invocation is not portable tool consent | SKILL.md:2-4,15-26; SKILL.md:13,30,69-76; skills/explore/SKILL.md:13-15,33; skills/tdd/SKILL.md:3,18-24,38 |  | Required-host consent/isolation untested |

### harness-analysis

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Task instructions | adopt | Static: bounded task purpose | SKILL.md:9-235 |  | Context cost unmeasured |
| A02 | Read-only audit of sensitive traces | adopt | Static: limits, cheap metrics, sanitized evidence and no hook execution | SKILL.md:19-26,30-62,87-94 |  | Permission and sensitive-content stopping untested |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | SKILL.md:2-4,13-17; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No selected native cases or seven-model runs |
| A04-F | Entry and required YAML | adapt | Static: parsed string name and description | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N | Name syntax and directory match | adapt | Static: matching lowercase kebab-case; under 64 characters | SKILL.md:2 |  | Required-host discovery not exercised |
| A04-D | Description bounds | adapt | Static: nonempty; 443 characters; no XML tags | SKILL.md:3 |  | 1024-character advice is source-specific |
| A05 | Preserved meaningful identity | adopt | Static: name matches declared purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Agent/session audit description and sidecar | adapt | Partial: trigger metadata specific; sidecar advertises test harness | SKILL.md:3,13-17; agents/openai.yaml:3 | SAG-011 (proposed target addition) | No expanded accepted target or native activation claim |
| A07 | Focused entry body | adapt | Static: task-focused entry; length is review signal | SKILL.md:9-235 |  | No automatic defect from line count |
| A08 | Core controls plus inline technique/template | adapt | Static: bounded workflow, evidence ledger and template | SKILL.md:19-62,66-94,130-202 |  | No unnecessary extraction inferred from length |
| A09 | Sparse data/failure/strong evidence branches | adopt | Static: fallback stops and candidate versus high-impact condition | SKILL.md:35,57,89-94,202 |  | No measured-impact branch exercised |
| A10 | Candidate paths and source navigation | adapt | Static: inventory locations and linked-doc candidates named | SKILL.md:38-41,68-79 |  | Paths are examples/candidates; actual installation shape unverified |
| A11 | No bundled reference over 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-235 |  | No behavior claim |
| A12 | Portable candidate locations and fallbacks | adapt | Partial: candidates and verify-shape rule exist; host paths untested | SKILL.md:38-41,89-93 |  | No Codex-specific directory inference or installed-log discovery claim |
| A13 | Bounded six-step audit | adopt | Static: inventory/counts before justified deep reading | SKILL.md:30-62,228-234 |  | Actual order untested |
| A14 | Evidence/uncertainty and final quality gate | adopt | Static: validation paired with recommendations and checklist | SKILL.md:108-118,224-235 |  | No measured recommendation improvement |
| A15 | No dated or historical factual instructions | not applicable | Not applicable: condition absent | SKILL.md:1-235 |  | No behavior claim |
| A16 | Agent harness versus test harness terminology | adapt | Partial: entry consistent; sidecar scope differs | SKILL.md:3,11,15-17; agents/openai.yaml:3 | SAG-011 (proposed target addition) | Parent/human target reconciliation outstanding |
| A17 | Exact report headings and read-only attestation | adapt | Unresolved: eval artifact writes versus absolute no-file rule | SKILL.md:21,130-202,235; evals/evals.json:6,24,42,56,76 | QH-008 | Capture/approved artifact boundary needs intent decision |
| A18 | Evidence ledger, recommendation and report examples | adopt | Static: good/weak evidence and concrete template | SKILL.md:75-85,120-128,134-200 |  | Example metrics illustrative, not observed work |
| A19 | Missing data/tool/path/URL/regex/sensitive stops | adopt | Static: explicit bounded branches and fallback | SKILL.md:89-94,202 |  | Native stop behavior untested; grader wording does not prove it |
| A20 | Bounded default sampling and fallback | adopt | Static: 14-day/10-session/20-hook defaults; metadata first | SKILL.md:32-35,49-51,89-94 |  | No measured adequacy or sampled run |
| A21 | Baseline-driven improvement claims | adapt | Unresolved: source snapshot is not behavioral baseline | SKILL.md:1-235; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No current baseline/candidate comparison |
| A22 | Five synthetic report/redirect evaluations | adapt | Defective: polarity and semantic-placement predicates | evals/evals.json:5-88; evals/grade_benchmark.py:60,78,96,131,142,148 | QH-007; QH-008 | Read-only output capture intent unresolved; no native task evidence |
| A23 | Reusable task knowledge/history | adapt | Static: reusable instructions; provenance of task learning unverified | SKILL.md:9-235 |  | No real-task history corpus established |
| A24 | Fresh-session iteration evidence | adapt | Unresolved: no fresh-session runs | SKILL.md:2-4,13-17; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No matched fresh-state iterations |
| A25 | Team-use feedback evidence | adapt | Unresolved: source alone is not team feedback | SKILL.md:1-235 |  | No team-use corpus inspected |
| A26 | Observed activation/navigation | adapt | Unresolved: no native activation/load trace | SKILL.md:2-4,13-17; SKILL.md:38-41,77,89-94 |  | Explicit and permitted implicit activation remain later work |
| A27 | Bundled evaluator error handling | adapt | Partial: static CLI/error branches; shape/no-run gap | evals/grade_benchmark.py:30-37,40-218 | DD-004 (proposed producer addition) | Existing failure-outcome protocol pending; no grader executed |
| A28 | Sampling and grader constants | adapt | Partial: limits serve bounded audit; unknown metrics zero-filled | SKILL.md:32-35,89-94; evals/grade_benchmark.py:166-177 | SAG-008 (proposed producer addition) | No arbitrary defect from count; unknown-metric choice pending |
| A29 | Repeated deterministic evaluation | adapt | Static: reusable grader utility exists | evals/grade_benchmark.py:30-37,40-218 |  | Utility correctness untested |
| A30 | Bundled evaluator versus task procedure | adapt | Static: evaluator separate from entry; read only in audit | evals/grade_benchmark.py:30-37,40-218; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No execution permission inferred |
| A31 | No layout/spatial input contract | not applicable | Not applicable: condition absent | SKILL.md:1-235 |  | No behavior claim |
| A32 | Read-only intermediate evidence before recommended changes | adopt | Static: ledger and validation-bearing recommendations; no implementation | SKILL.md:21-26,66-73,110-118 |  | No approval or execution inferred from a recommendation |
| A33 | Evaluator imports only Python standard library | not applicable | Not applicable: condition absent | evals/grade_benchmark.py:30-37,40-218; evals/grade_benchmark.py:1-6 |  | No behavior claim |
| A34 | Actual file loading | adapt | Partial: exact source reads/hashes complete | SKILL.md:1-235; exact reviewed inventory |  | Installed/native loading untested |
| A35 | Illustrative session_store_sql tool reference | adapt | Partial: example source tool, no callable qualified MCP identifier established | SKILL.md:77,93 |  | Actual host tool/namespace availability untested; do not invent identifier |
| A36 | Filesystem/search/log/structured-source tools | adapt | Static: unavailable tool/zero rows/missing path fallbacks | SKILL.md:34-47,89-94 |  | Runtime tools and file permissions untested |
| S01 | Read-only process audit boundaries | adopt | Static: no file mutation or hook execution | SKILL.md:21-24,52,94,106 | QH-008 | Report-artifact exception unresolved; actual containment untested |
| S02 | Local instruction/session/hook source access | adapt | Static: bounded candidates; no hook script execution | SKILL.md:22,30-52,89-94 |  | No home-directory or log access actually performed |
| S03 | Sensitive logs and personal data | adopt | Static: no pasting; stop sensitive body and recommend redaction | SKILL.md:24,52,94,113 |  | No sensitive-input native trace |
| S04 | Logs/user prompts/vendor/external content | adopt | Static: explicitly treat as untrusted evidence | SKILL.md:52 |  | Native embedded-instruction handling untested |
| R01 | Scope/name/trigger preservation | adopt | Static: protected contracts recorded | SKILL.md:2-4,13-17; protected contracts |  | Human disposition pending; no change authorized |
| R02 | Existing invocation controls | adopt | Static: disable-model-invocation and sidecar false retained | SKILL.md:4; agents/openai.yaml:4-5 | SAG-001/SAG-012 (bounded consumer facts) | Required-host enforcement untested |
| R03 | Absolute no-write and no hook execution | adopt | Unresolved: report artifact prompts clash with absolute scope | SKILL.md:21-24; evals/evals.json:6,24,42,56,76 | QH-008 | Human must distinguish harness capture from approved artifact writes |
| R04 | No required helper skill or delegated role | not applicable | Not applicable: condition absent | SKILL.md:1-235 |  | No behavior claim |
| R05 | Bounded failures/sensitive content and final attestation | adopt | Partial: explicit stops; artifact/attestation tension | SKILL.md:89-94,235 | QH-008 | No stop trace; final statement truthfulness depends on capture decision |
| R06 | Evidence/Uncertainty/candidate report | adopt | Partial: strong template; required no-files statement conflicted by eval write | SKILL.md:26,130-202,235; evals/evals.json:6 | QH-008 | Preserve read-only system boundary and truthful report output |
| R07 | This audit repository authority | adopt | Static: only owned report written; primary sources unchanged | ../../../AGENTS.md:13-18,49-62; exact reviewed inventory |  | Parent owns canonical documentation/finding pass |
| R08 | Maintained source versus generated artifacts | adopt | Static: entry/resources/eval definitions separated from runs | SKILL.md:1-235; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No generated run primary evidence |
| R09 | Later source-validation prerequisites | adapt | Partial: source JSON/YAML/AST parsed; no helper executed | SKILL.md:1-235; ../../../.agents/memory/testing/skills.md:8-14 | SAG-001 (bounded consumer fact) | Later accepted changes need exact scoped validation; retained controls stay |
| R10 | No Upgrade procedure or proposed Upgrade consumer | not applicable | Not applicable: condition absent | SKILL.md:1-235 |  | No behavior claim |
| R11 | Semantic output grading versus actual workflow | adapt | Defective: lexeme predicates can misgrade meaning | evals/grade_benchmark.py:60,78,96,131,142,148,166-218 | QH-007; QH-008; DD-004 (proposed addition); SAG-008 (proposed addition) | No native stopping/latency/authorization inference from report text |
| R12 | Source formatting | adopt | Static: LF; no trailing/blank whitespace in 26-file inventory | SKILL.md:1-235; ../../../.editorconfig:6-19 |  | Source em dashes were not changed; new report contains none |
| C01 | Native discovery/activation | adapt | Unresolved: source metadata is not activation evidence | SKILL.md:2-4,13-17 |  | No native Codex discovery or permitted implicit trace |
| C02 | Shipped resources | adapt | Static: non-eval files selected; evals stripped | ../../../scripts/install.sh:40-55; ../../../scripts/install.ps1:251-276 |  | No installed file access trace |
| C03 | Codex sidecar meaning and control | adapt | Partial: control parsed, short description misstates scope | agents/openai.yaml:2-5; SKILL.md:3 | SAG-011 (proposed target addition) | Keep control; sidecar scope addition not yet accepted |
| C04 | Tool/activation consent | adapt | Unresolved: source invocation is not portable tool consent | SKILL.md:2-4,13-17; SKILL.md:38-41,77,89-94 |  | Required-host consent/isolation untested |

### improve-repo-harness

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Brief external-source question | adapt | Partial: small entry but actual task contract underspecified | SKILL.md:3,9 | QH-009 | No concrete clarity judgment selected from length alone |
| A02 | Action scope and external methodology | adapt | Unresolved: recommendation versus implementation boundary | SKILL.md:3,9 | QH-009 | Human must choose intended behavior before workflow authoring |
| A03 | Intended model behavior | adapt | Unresolved: no native model evidence | SKILL.md:2-4; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No selected native cases or seven-model runs |
| A04-F | Entry and required YAML | adapt | Static: parsed string name and description | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N | Name syntax and directory match | adapt | Static: matching lowercase kebab-case; under 64 characters | SKILL.md:2 |  | Required-host discovery not exercised |
| A04-D | Description bounds | adapt | Static: nonempty; 88 characters; no XML tags | SKILL.md:3 |  | 1024-character advice is source-specific |
| A05 | Preserved meaningful identity | adopt | Static: name matches declared purpose | SKILL.md:2-3 |  | No rename proposed |
| A06 | Trigger/action description | adapt | Unresolved: adding/fixing description versus how-to question | SKILL.md:3,9; agents/openai.yaml:3 | QH-009 | No widened implementation trigger or test-harness scope selected |
| A07 | Focused entry | adapt | Partial: three body lines; purpose remains unresolved | SKILL.md:7-9 | QH-009 | A short body does not establish a complete contract |
| A08 | Unbundled external repository dependency | adapt | Partial: remote methodology pointer; no bundled procedure | SKILL.md:9 | QH-009 | Source version/retrieval/authority unverified |
| A09 | No advanced optional branch specified | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A10 | One remote repository pointer | adapt | Partial: direct URL named; no local supporting resource | SKILL.md:9 |  | Remote contents not read as governing instructions; no retrieval evidence |
| A11 | No bundled reference over 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A12 | Named remote dependency | adapt | Partial: GitHub URL spelled out; no artifact paths specified | SKILL.md:9 | QH-009 | Working directory/output paths depend on intended workflow decision |
| A13 | Task procedure | adapt | Unresolved: one question, no selected staged workflow | SKILL.md:9 | QH-009 | Do not invent proposal or implementation sequence |
| A14 | Result quality/verification | adapt | Unresolved: expected outcome and quality gate not stated | SKILL.md:3,9 | QH-009 | Validation depends on intended result |
| A15 | Time-sensitive unbundled upstream | adapt | Unresolved: no version or dated remote applicability evidence | SKILL.md:9 |  | No current upstream fact or historical provenance claim |
| A16 | Repository harness versus test harness | adapt | Unresolved: sidecar narrows to test harness without resolved meaning | SKILL.md:3,9; agents/openai.yaml:3 | QH-009 | Do not extend SAG-011 target before intent decision |
| A17 | Expected output | adapt | Unresolved: no report/result contract specified | SKILL.md:9 | QH-009 | Recommendations versus source changes requires choice |
| A18 | No output/style example or known output shape | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A19 | Case/permission/failure branches | adapt | Unresolved: no described behavior branch | SKILL.md:3,9 | QH-009 | Intended cases and unavailable source handling unknown |
| A20 | Recommended default and exceptions | adapt | Unresolved: default action not established | SKILL.md:3,9 | QH-009 | No inferred automatic implementation or mandatory approval gate |
| A21 | Baseline-driven improvement claims | adapt | Unresolved: source snapshot is not behavioral baseline | SKILL.md:1-9; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No current baseline/candidate comparison |
| A22 | Evaluation evidence | adapt | Unresolved: no bundled eval definition | SKILL.md:1-9 |  | Safe native cases/fixtures remain later work |
| A23 | Knowledge reuse from remote methodology | adapt | Partial: upstream pointer, no task-derived local evidence | SKILL.md:9 |  | Remote material applicability and actual task history unestablished |
| A24 | Fresh-session iteration evidence | adapt | Unresolved: no fresh-session runs | SKILL.md:2-4; ../tickets/set-audit-evidence-and-model-coverage.md#resolution |  | No matched fresh-state iterations |
| A25 | Team-use feedback evidence | adapt | Unresolved: source alone is not team feedback | SKILL.md:1-9 |  | No team-use corpus inspected |
| A26 | Observed activation/navigation | adapt | Unresolved: no native activation/load trace | SKILL.md:2-4; SKILL.md:9 |  | Explicit and permitted implicit activation remain later work |
| A27 | No bundled executable resource | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A28 | No configurable executable constants | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A29 | No repeated deterministic utility need established | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A30 | No bundled or named executable helper command | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A31 | No layout/spatial input contract | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A32 | Risky harness changes/intermediate plan | adapt | Unresolved: risky-action scope and approval boundaries unknown | SKILL.md:3,9 | QH-009 | No plan or permission inferred from brief invocation |
| A33 | No external runtime package required by this bundle | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A34 | Actual file loading | adapt | Partial: exact source reads/hashes complete | SKILL.md:1-9; exact reviewed inventory |  | Installed/native loading untested |
| A35 | No concrete qualified MCP tool identifier | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| A36 | Remote source retrieval and repository operations | adapt | Unresolved: prerequisites/fallback not specified | SKILL.md:9 | QH-009 | Available retrieval/tools and absent-source behavior untested |
| S01 | Harness improvement versus task authority | adapt | Unresolved: exact operational scope not established | SKILL.md:3,9 | QH-009 | No implementation workflow or containment evidence |
| S02 | External repository and local harness access | adapt | Partial: remote URL only explicit source target | SKILL.md:9 | QH-009 | Network method, source trust and allowed local writes unresolved |
| S03 | Inputs/results may contain sensitive data | adapt | Unresolved: output redaction and sensitive-input handling not exercised | SKILL.md:9 |  | No real input/output disclosure test; static read is not vulnerability clearance |
| S04 | External methodology trust boundary | adapt | Unresolved: quote points to remote guidance without authority boundary | SKILL.md:9 | QH-009 | No fetched content/injection trace; external source is not approval |
| R01 | Preserve name/controls; resolve purpose | adopt | Unresolved: current scope sources leave action choice open | SKILL.md:2-4,9 | QH-009 | Human intent choice precedes authoring proposal |
| R02 | Existing invocation controls | adopt | Static: disable-model-invocation and sidecar false retained | SKILL.md:4; agents/openai.yaml:4-5 | SAG-001/SAG-012 (bounded consumer facts) | Required-host enforcement untested |
| R03 | Approval and autonomy boundaries | adopt | Unresolved: implementation authority versus recommendation unstated | SKILL.md:3,9 | QH-009 | No permission or workflow default selected |
| R04 | Remote methodology dependency | adapt | Partial: required reference pointer retained; content unavailable in bundle | SKILL.md:9 | QH-009 | Retrieval and authority boundaries depend on human choice |
| R05 | Stopping/handoff boundary | adopt | Unresolved: no concrete stop or handoff contract | SKILL.md:9 | QH-009 | Do not add a new execution flow without intent decision |
| R06 | Output contract | adopt | Unresolved: question does not choose report/change result | SKILL.md:3,9 | QH-009 | Expected output remains human decision |
| R07 | This audit repository authority | adopt | Static: only owned report written; primary sources unchanged | ../../../AGENTS.md:13-18,49-62; exact reviewed inventory |  | Parent owns canonical documentation/finding pass |
| R08 | Maintained source versus generated artifacts | adopt | Static: entry/resources/eval definitions separated from runs | SKILL.md:1-9; ../tickets/choose-audit-batches-and-evidence-format.md#resolution |  | No generated run primary evidence |
| R09 | Later source-validation prerequisites | adapt | Partial: source JSON/YAML/AST parsed; no helper executed | SKILL.md:1-9; ../../../.agents/memory/testing/skills.md:8-14 | SAG-001 (bounded consumer fact) | Later accepted changes need exact scoped validation; retained controls stay |
| R10 | No Upgrade procedure or proposed Upgrade consumer | not applicable | Not applicable: condition absent | SKILL.md:1-9 |  | No behavior claim |
| R11 | Evidence and grading integrity | adapt | Unresolved: no native/evaluator evidence | SKILL.md:1-9 |  | Artifact plans distinct from performed actions |
| R12 | Source formatting | adopt | Static: LF; no trailing/blank whitespace in 26-file inventory | SKILL.md:1-9; ../../../.editorconfig:6-19 |  | Source em dashes were not changed; new report contains none |
| C01 | Native discovery/activation | adapt | Unresolved: source metadata is not activation evidence | SKILL.md:2-4 |  | No native Codex discovery or permitted implicit trace |
| C02 | Shipped resources | adapt | Static: non-eval files selected; evals stripped | ../../../scripts/install.sh:40-55; ../../../scripts/install.ps1:251-276 |  | No installed file access trace |
| C03 | Codex-only sidecar/control | adapt | Partial: control parsed; test-harness wording intent unresolved | agents/openai.yaml:2-5; SKILL.md:3,9 | QH-009 | No sidecar scope change before purpose resolution |
| C04 | Tool/activation consent | adapt | Unresolved: source invocation is not portable tool consent | SKILL.md:2-4; SKILL.md:9 |  | Required-host consent/isolation untested |

## Source metadata and bounded dependency fingerprints

Body counts exclude YAML delimiters, frontmatter and leading blank lines; physical line counts use splitlines and include an unterminated last line. Every primary source SHA256 was rechecked against current bytes and baseline.

| Skill | Physical entry lines | Body lines |
| --- | --- | --- |
| `adversarial-review` | 19 | 13 |
| `code-review` | 117 | 111 |
| `code-simplify` | 22 | 17 |
| `fixing-accessibility` | 136 | 131 |
| `techdebt` | 98 | 92 |
| `harness-analysis` | 235 | 229 |
| `improve-repo-harness` | 9 | 3 |

Dependency hashes identify inspected source bytes; the final column states actual read scope. A whole-file hash does not imply full content audit. These eighteen files are bounded dependencies, not new primary candidates. Shared root checklists were checked for existence only; remote harness-engineering content was not read.

| Dependency | Bytes | Lines | SHA256 | Baseline | Read scope |
| --- | --- | --- | --- | --- | --- |
| [agents/addy-code-reviewer.md](../../../agents/addy-code-reviewer.md) | 3987 | 107 | `7545a83f2f0585384feceffdfdeacfb26281a4f0278d0378c930c78823af74e1` | unchanged | Full role definition; bounded Code Review consumer |
| [agents/addy-security-auditor.md](../../../agents/addy-security-auditor.md) | 5012 | 112 | `6cabd436e653b2b7b601eb2a6d4133b4390f7815869d5fa72eaa2fcfb3c9c064` | unchanged | Full role definition; bounded Code Review consumer |
| [agents/addy-test-engineer.md](../../../agents/addy-test-engineer.md) | 3290 | 95 | `0855e12fe021d4999e72d01a292a4d52e7e8002f9fa07232f555ec2a96a3c163` | unchanged | Full role definition; bounded Code Review consumer |
| [agents/code-explorer.md](../../../agents/code-explorer.md) | 2334 | 61 | `e6d92f5082b25afa56bdfc4715f87bb894f42ae38285a2355b2788e7d55a0775` | unchanged | Full role definition; bounded Techdebt consumer |
| [agents/code-simplifier.md](../../../agents/code-simplifier.md) | 3670 | 69 | `210dcb5d42e3bdbfdfdf0a03ca0dbacb40aaafdccd660c2e3ac0e97324fd433f` | unchanged | Full role definition; bounded Simplify consumer |
| [agents/code-reviewer.md](../../../agents/code-reviewer.md) | 4415 | 112 | `90e00060e786c94c7e7b2babea883a4bbcc2c5cfdbd511e075105f2775ed5928` | unchanged | Full role definition; bounded alternate review-role comparison |
| [skills/delegate-to-subagents/SKILL.md](../../../skills/delegate-to-subagents/SKILL.md) | 12184 | 308 | `670318c390b55da662f617e2e1d2538da299f4f151b3c82f03bb9443ffa9ef32` | unchanged | Full procedure read for these callers; Delegation and Discovery owns primary review |
| [skills/subagent-model-router/SKILL.md](../../../skills/subagent-model-router/SKILL.md) | 8127 | 168 | `7de60f23f3152164ee4b9dd0c7caa329b9aa42f57f44677c14f54b26b61a5ac1` | unchanged | Lines 1-130; bounded routing consumer |
| [skills/subagent-model-router/reference/review-routing.md](../../../skills/subagent-model-router/reference/review-routing.md) | 2609 | 61 | `8da047069ddf7db33243a4d4c9253525e999977f30aa9135a8fec9b17135fd1f` | unchanged | Full reference; bounded Code Review tier consumer |
| [skills/explore/SKILL.md](../../../skills/explore/SKILL.md) | 1305 | 38 | `5fefe9f992e78ddac3642698d1ea824f54e1216c7b63b42441640b02b826f83b` | unchanged | Full entry; bounded Techdebt consumer |
| [skills/tdd/SKILL.md](../../../skills/tdd/SKILL.md) | 3752 | 38 | `7c09709d9a8ebea6c3286c14d7ba25ee0957de08d8d9a921752177a4640ac5c0` | unchanged | Lines 1-38; imported helper scope and seam contract only |
| [skills/addy-code-review-and-quality/SKILL.md](../../../skills/addy-code-review-and-quality/SKILL.md) | 22146 | 407 | `42e89a0cbc04200f32018b2d592b8e9e51535c50db2661216878a717d0e4100b` | unchanged | Lines 142-203,232-248,304-358 plus named dependency navigation; imported helper only |
| [skills/addy-code-simplification/SKILL.md](../../../skills/addy-code-simplification/SKILL.md) | 13550 | 331 | `85ec2815c4183f3c8d0db4fb8faac370673ddd14baae2faec13bd5df2b4882db` | unchanged | Lines 32-59,101-105,157-185 and named entry; imported helper only |
| [skills/addy-security-and-hardening/SKILL.md](../../../skills/addy-security-and-hardening/SKILL.md) | 28008 | 524 | `ba1e00e052143c33c249608d68295400fcfee219886a687c9875ecec2c643754` | unchanged | Lines 21-75 and named dependency navigation; imported helper only |
| [scripts/install.sh](../../../scripts/install.sh) | 8229 | 224 | `a7cd93792b919a2773c8a79061359dc54d023381024e5a47d6be0a6f3d5e35fa` | unchanged | Lines 40-66 plus relevant source/destination selection; no execution |
| [scripts/install.ps1](../../../scripts/install.ps1) | 22007 | 510 | `9b4b245ceae22c533f26c87f6a0bf86ab150b7174a77881dbfab658e8ee2b022` | unchanged | Lines 251-281 plus relevant source/destination selection; no execution |
| [scripts/install-codex-agents.py](../../../scripts/install-codex-agents.py) | 21357 | 514 | `f2442b0f64f93fbcb3fe909d75b697209bb7931a26c9e2092838408eedd3af01` | unchanged | Lines 174-187,280-291 and source-selection search only; no execution |
| [skills/dotnet/SKILL.md](../../../skills/dotnet/SKILL.md) | 4971 | 103 | `4160d151f90c0fc9b24b6f21d5ba80bf316d9ad1f27a2091dcf342dbe683c93c` | unchanged | Line 3 only; bounded .NET precedence consumer metadata |

Custom-agent name discovery inspected all nineteen top-level source filenames and parsed their frontmatter names. Only the six role definition bodies above were fully read. Names: `addy-code-reviewer`, `addy-security-auditor`, `addy-test-engineer`, `analyzer`, `architecture-critic`, `business-rules-extractor`, `code-architect`, `code-explorer`, `code-reviewer`, `code-simplifier`, `comparator`, `grader`, `legacy-analyst`, `scaffolder`, `security-auditor`, `test-engineer`, `ui-auditor`, `uplift-migrator`, `version-delta-analyst`. No `generalist` source file/name was found; current required-client catalog availability remains unverified.

## Static completion and ownership release

All 26 primary maintained files were read in full. Eighteen bounded dependencies have distinct read scopes and fingerprints; all 44 fingerprinted files match baseline `72a3ae956e3533aaddf33eb1e8d8ecf30b69d08f` and current bytes. The seven matrices contain exactly 58 unique catalog IDs in catalog order, 406 rows total, each with the required seven-column shape. Every numeric matrix source anchor was checked against an existing file and its current physical line count. JSON/YAML parsing, Python AST parsing, source formatting and report whitespace/no-em-dash checks passed without executing any audited helper. Code Review's seven references exist and remain selected by their intended branches; fixture inventory is empty.

These checks validate the saved static evidence record, not task behavior or grader correctness. Native Codex evidence, installed access, client enforcement, actual tool/role availability, human finding disposition and underlying behavior/protocol decisions remain open. No static pass waives them. Create Skill and Skill Creator were loaded solely as paper-review guidance; no authoring workflow, baseline or installation was activated. Domain-modeling was waived for this effort.

Report ownership is released to the parent for independent validation and reconciliation. The parent owns canonical findings, coverage, tickets, map, planning handoff and the final end-of-session agent-document pass. No commit was created.

## Parent source-review dispatch audit

The parent selected and explicitly submitted `gpt-6.1-sol` at `high`, with unused same-tier fallback `gpt-6-sol` at `high`. Premium floor followed authorization/trust and false-pass risks. Catalog guidance remained provisional; desktop billing and task-specific capability measurements were unavailable. This source investigation is not a native medium-effort baseline.

Initial parent wall-clock window: 2026-10-06 15:40:09-16:00:09 UTC. Saved inventory, five-minute and ten-minute checkpoints were inspected; status was checked while finishing fingerprints and anchors. The completion/ownership-release notification preceded the parent's 16:00:30 UTC clock check. Exact completion time is unconfirmed, so completion before the limit is not asserted. The parent clock check was 21 seconds after the declared limit while preparing reconciliation. No interruption or extension occurred; the agent was already complete when that check was made. Keep future limit checks scheduled independently of long parent writes.

Routing metadata and orchestration audit stayed outside the task prompt. Selected/submitted settings matched the printed route; executed model/effort, tool duration and usage remain unconfirmed. Independent parent checks cover all source fingerprints, matrices, consequential predicates and record dependencies. Ownership was released before parent report writes. The reviewer's long report-writing command hit Tool Guardian's command-token limit before execution and was replaced with an inspectable patch; no audited helper ran. Parent corrected a guessed commit-reference path and a stale append anchor by loading the exact existing paths/text. These are process corrections, not native failures or source defects.

```yaml
dispatches:
  - subtask_id: quality-harness-static
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
      mechanism: Parent wall-clock window, saved five-minute checkpoints, status check before stopping or extending
    completion_observed_at: 2026-10-06 16:00:30 UTC
    exact_completion_at: unconfirmed
    status: completed
    output_verified: true
    routing_compliant: true
    runtime_check_at_limit: delayed 21 seconds
```

## Parent reconciliation verification and documentation pass

Parent registered QH-001 through QH-010 once, removed draft duplication and linked seven blocked decision routes. SAG-008/DD-004/SAG-011 additions remain proposed; accepted scopes and unresolved choices stay unchanged. Claim release leaves the batch open for three prepared live questions, without Resolution.

`rtk proxy python3 /private/tmp/skill-audit-verify-four-batches.py` passed: 33-ticket acyclic graph (ten closed/twenty-three open/no claims), 1,334 rows, 102 primary hashes, twenty-five separately declared fixture hashes, eighteen bounded quality/harness dependencies, thirty-two unique findings/index, preserved existing decisions/scopes, links/anchors, formatting, fog and unchanged protected sources. These are source/record checks, not runtime or grader-correctness tests.

Formal Update Agent Docs changes only `.agents/memory/known-issues/skills.md`, type Known Issue: broaden grader-integrity pointer and add bounded caller/helper-contract pointer. Existing routing/index coverage suffices; no API, skill, installer or test strategy changed. OKF loaded profile only; `rtk proxy ./scripts/lint-okf.py` exited 0 across both bundles. Added: caller/helper-contract pointer. Changed: grader-integrity pointer. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None. Human disposition, native evidence and implementation acceptance remain outstanding.
