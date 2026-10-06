# Skill Audit Findings

Single owning register, started 2026-10-05. First-batch source revision: `91ba7ab941450327c8d178c27966d1150bd0b74b`; repository-local review source revision: `bd7b1a68a081ea847b2e6c1712363000ef01751f`; delegation/discovery source revision: `991b14b86440dab452ac28312c5f05a2b4a42266`. Static observations and predicted consequences remain separate from observed runtime behavior. No native audit baseline has run.

Applicability, adoption disposition, compliance, proposal status, and implementation acceptance are distinct. The human reviewed SAG-001 through SAG-014 and RLW-001 through RLW-003 on 2026-10-05, then DD-001 through DD-005 on 2026-10-06. All twenty-two findings have recorded dispositions. Accepted repairs remain later plan scope; six underlying decisions remain pending, including DD-004. RLW-001/RLW-003 are accepted clarifications, while RLW-002 retains its separate intended-output decision. None authorizes implementation, installation, or publication. Model/client run configuration: none for these static findings. Source-review delegation settings belong in the batch report, not behavioral evidence.

## Proposal index

| ID | Finding | Human status | Route / affected work |
| --- | --- | --- | --- |
| [SAG-001](#sag-001-validation-prerequisites-and-retained-control-exceptions) | Validation prerequisites and retained-control exceptions | Accepted for later planning | Later authoring plan scope |
| [SAG-002](#sag-002-installer-ownership-conflict) | Installer ownership conflict | Pending separate decision | [Separate decision](tickets/resolve-installer-authority-for-skill-authoring.md) |
| [SAG-003](#sag-003-undefined-anatomy-expectation) | Undefined anatomy expectation | Pending separate decision | [Separate decision](tickets/define-create-skill-body-contract.md) |
| [SAG-004](#sag-004-stale-duplicate-avoidance-oracle) | Stale duplicate-avoidance oracle | Accepted for later planning | Later evaluation plan scope; fixture/oracle prerequisite |
| [SAG-005](#sag-005-improve-skill-evals-reward-prohibited-writes) | Improve-skill evals reward prohibited writes | Accepted for later planning | Later evaluation plan scope |
| [SAG-006](#sag-006-missing-improve-skill-fixture-inputs) | Missing improve-skill fixture inputs | Accepted for later planning | Later evaluation plan scope |
| [SAG-007](#sag-007-grader-predicates-do-not-prove-preservation) | Grader predicates do not prove preservation | Accepted for later planning | Later evaluation plan scope; preserve intended contracts |
| [SAG-008](#sag-008-unmeasured-metrics-become-zero) | Unmeasured metrics become zero | Pending separate decision | [Separate decision](tickets/choose-unknown-benchmark-metric-representation.md) |
| [SAG-009](#sag-009-cappedunscoped-agents-discovery) | Capped/unscoped AGENTS discovery | Accepted for later planning | Later authoring plan scope |
| [SAG-010](#sag-010-broken-template-fences-and-unreachable-update-guide) | Broken template fences and unreachable update guide | Accepted for later planning | Later authoring plan scope |
| [SAG-011](#sag-011-misleading-codex-sidecar-scope) | Misleading Codex sidecar scope | Accepted for later planning | Later authoring plan scope |
| [SAG-012](#sag-012-argument-binding-and-control-adapter-evidence-gaps) | Argument binding and control adapter evidence gaps | Accepted for later planning | Later authoring plan scope; runtime enforcement unverified |
| [SAG-013](#sag-013-public-claims-and-command-validation-ambiguity) | Public claims and command validation ambiguity | Documentation accepted; execution decision pending | [Separate decision](tickets/set-safe-command-validation-scope-for-agents-authoring.md) |
| [SAG-014](#sag-014-trailing-whitespace-in-improve-skill-grader) | Trailing whitespace in Improve Skill grader | Accepted for later planning | Later authoring cleanup scope |
| [RLW-001](#rlw-001-maintenance-type-table-disagrees-with-the-root-only-okf-contract) | Maintenance type table disagrees with the root-only OKF contract | Accepted for later planning | Later authoring clarification scope |
| [RLW-002](#rlw-002-prior-plan-reference-exception-has-unclear-relationship-to-single-file-self-containment) | Prior-plan reference exception has unclear relationship to single-file self-containment | Pending separate decision | [Separate decision](tickets/resolve-execplan-self-containment-and-prior-plan-references.md) |
| [RLW-003](#rlw-003-clarify-reported-okf-reference-and-orchestration-evidence) | Clarify reported OKF reference and orchestration evidence | Accepted for later planning | Later authoring clarification scope; native trace evidence outstanding |
| [DD-001](#dd-001-explore-spawn-grading-omits-independent-area-assertions) | Explore spawn grading omits independent-area assertions | Accepted for later planning | Later evaluation plan scope; protocol prerequisites |
| [DD-002](#dd-002-evaluation-setup-does-not-establish-required-prior-context-or-cache-hit) | Evaluation setup does not establish required prior context or cache hit | Accepted for later planning | Later evaluation plan scope; fixture/oracle prerequisites |
| [DD-003](#dd-003-official-source-graders-equate-text-mentions-with-citation-and-cache-evidence) | Official-source graders equate text mentions with citation and cache evidence | Accepted for later planning | Later evaluation plan scope; trace evidence outstanding |
| [DD-004](#dd-004-graders-can-announce-success-without-grading-runs-and-do-not-validate-json-shape) | Graders can announce success without grading runs and do not validate JSON shape | Pending separate decision | [Separate decision](tickets/define-benchmark-grader-failure-outcomes.md); exact protocol pending |
| [DD-005](#dd-005-explore-grader-contains-prohibited-blank-line-whitespace) | Explore grader contains prohibited blank-line whitespace | Accepted for later planning | Later authoring cleanup scope |

## Pending decisions and approval

The 2026-10-05 live review accepted SAG-001, SAG-009, SAG-010, SAG-011, SAG-012, SAG-014 and only SAG-013's documentation cleanup as authoring repairs; SAG-004 through SAG-007 are accepted evaluation repairs. Four precise questions remain pending in separate Wayfinder routes: installer authority (SAG-002), body output structure (SAG-003), compatible unknown metrics (SAG-008), and command-validation authority (SAG-013). The human explicitly chose to keep all four pending and visible. The closed [batch Resolution](tickets/review-skill-authoring-and-repository-guidance.md#resolution) unblocks their tickets without choosing their behavior or design. No proposal was rejected or deferred.

The repository-local live review accepted RLW-001/RLW-003 for later authoring planning on 2026-10-05. RLW-001 aligns the table with existing root-only typing. RLW-003 distinguishes reported reference/ownership values from independently reconstructed output checks; required native trace grading remains later evidence work, and SAG-007's targets are not expanded. The human retained RLW-002's unclear predecessor-plan semantics in its separate decision without selecting an interpretation. The closed [repository-local Resolution](tickets/review-repository-local-workflows.md#resolution) unblocks that ticket. All five separate decisions remain open; no proposal was rejected or deferred.

Accepted authoring work may enter the later plan only when its design prerequisites are resolved. SAG-004 needs a grounded fixture/oracle mapping rather than an invented successor. SAG-007's evaluator repair must preserve intended contracts; disputed body structure follows SAG-003. SAG-013 wording cleanup can be independent only when it does not choose execution authority. SAG-012 keeps client enforcement unverified until actual evidence exists.

Both final `audit.md` and `ExecPlan.md` must expose every unresolved proposal by stable ID and link its owner and route. Reconciliation accounts for accepted, rejected, deferred, and unresolved items. A deferral requires rationale, affected work, remaining risk, and revisit trigger. Evidence waiver and residual-risk acceptance are separate.

The human accepted DD-001/DD-002/DD-003/DD-005 for later planning on 2026-10-06: independent area checks, reproducible inputs and cache branches, honest citation/trace grading, and five whitespace-line cleanups. DD-004's exact invalid/incomplete grading outcomes remain in [Define Benchmark Grader Failure Outcomes](tickets/define-benchmark-grader-failure-outcomes.md). The closed [delegation/discovery Resolution](tickets/review-delegation-and-discovery.md#resolution) unblocks that route; all six underlying decisions are now open and unblocked. The human also accepted Explore and Official Sources as additional SAG-008 producer targets, retaining the original three and the unresolved representation. DD-004's type/error protocol is not selected by the accepted repairs. Preserve valid predicates, allowed exploration scope, direct narrow reads, optional cache, dependencies, names, controls and approvals; exact fixture/oracle choices and genuine protocol dependencies precede affected executable work. No proposal was rejected or deferred.

## Findings

### SAG-001: Validation prerequisites and retained-control exceptions

- Checks/applicability/disposition: A30/A33/A36/R02/R09/R10; create-skill repo validation; adapt.
- Evidence: `skills/create-skill/SKILL.md:45,48,99`; grader `56-66,150,190,256`; helper validator `9,42-50`; package `17,70-76`; `.agents/memory/known-issues/skills.md:13-25`. Plain commands omit the known vendored PyYAML path. The validator allowlist rejects preserved `disable-model-invocation` and `argument-hint` fields.
- Mechanism and impact: missing environment package can fail import; retained controls fail the allowlist and inherited grader subprocess check. Predicted pressure to remove controls or inability to complete validation. Static imports/allowlist are certain; environment failure is untested.
- Severity/confidence/client: Major/high; all repo authoring clients and shared Python tooling.
- Proposal/contract: document vendored runtime and scoped retained-control failures in the owned consumer, preserving fields and dotnet-upgrade document-only exception. Equivalent prerequisite/honest reporting repair; no excluded helper edits.
- Exact decision/validation: approve consumer clarification; broader helper maintenance or validation-policy redesign is separate. Later isolated metadata/missing-package cases and preserved-key checks; dotnet-upgrade remains document-only.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted authoring repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-002: Installer ownership conflict

- Checks/applicability/disposition: A02/A32/S02/R03/R07/C04; create-skill refresh; unresolved pending authority choice.
- Evidence: `create-skill/SKILL.md:49,99` requires installer after edits; `.agents/instructions/repo.md:15` requires refresh before live checks; `.agents/instructions/scripts.md:24` strictly permits agents only targeted verification/test scripts. `install.sh:26-38,183-207` writes multiple home destinations/settings.
- Mechanism/impact: contradictory instructions can produce broad account installation or inconsistent stops. This audit's explicit no-install boundary was honored; general future behavior remains unresolved.
- Severity/confidence/client: Major/high textual contradiction; all repo agents and installed Codex/Copilot/Gemini configuration.
- Proposal/contract: separate authority/autonomy decision; do not silently make required refresh optional.
- Exact decision/validation: may agents run account install after authorized skill edits, or must the human refresh, and what stop/authorization applies? Later approved/denied/static-only paper cases; real install remains separately authorized.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: the human confirmed a separate pending decision on 2026-10-05. The authority or design choice remains unresolved. No implementation approval, evidence waiver, or residual-risk acceptance.
- Owning decision: [Question](tickets/resolve-installer-authority-for-skill-authoring.md). Affected implementation stays pending until that choice is resolved or explicitly deferred with independent scope.

### SAG-003: Undefined anatomy expectation

- Checks/applicability/disposition: A12/A17/R06; create-skill body structure; unresolved intended contract, separate decision required.
- Evidence: `create-skill/SKILL.md:10,96` promises anatomy; grader `10-18,156-160` and evals `10-14` require seven named headings. Entry/linked repo guidance does not define those headings. Imported helper `SKILL.md:73-84` describes directory anatomy. `references/skill-anatomy.md` is absent.
- Mechanism/impact: a draft can follow loaded anatomy yet fail grader-only expectations; predicted hidden-oracle failure.
- Severity/confidence/client: Minor/high; all authoring clients.
- Proposal/contract: separate output-contract decision before defining/linking any required body template. The seven grader headings are evidence of an expectation, not automatically binding intent; do not force them on unrelated skills.
- Exact decision/validation: human chooses whether those seven headings are required, a flexible default, or a historical grader preference. Then align the owned procedure and oracle with that approved choice. Later novice walkthrough and matched draft cases.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: the human confirmed a separate pending decision on 2026-10-05. The authority or design choice remains unresolved. No implementation approval, evidence waiver, or residual-risk acceptance.
- Owning decision: [Question](tickets/define-create-skill-body-contract.md). Affected implementation stays pending until that choice is resolved or explicitly deferred with independent scope.

### SAG-004: Stale duplicate-avoidance oracle

- Checks/applicability/disposition: A15/A22/R11; create-skill dedupe eval; adapt.
- Evidence: `evals/evals.json:34-40`; grader `226,233-245` accepts only `create-plan`/`create-tasks`. Both source entries are absent. Current planning entries include prd/spec-to-tasks/to-issues/wayfinder; `plan-maker-request.md:7-15` asks to reuse an actual existing skill.
- Mechanism/impact: correct current-scope answers can fail; any single accepted revised name also masks extra renamed outputs. Predicted grading distortion.
- Severity/confidence/client: Major/high; local grading across providers.
- Proposal/contract: refresh fixture/oracle against verified current planning responsibilities, preserving duplicate avoidance and identity. Bounded metadata/workflow inspection establishes that local `exec-plans` creates self-contained execution plans and embeds research/validation (`SKILL.md:8-20,26-34,52-58`); `prd` prepares implementation-ready requirements for task breakdown (`SKILL.md:3,9,17-21,23-36`). `spec-to-tasks`/`to-issues` are downstream breakdown, not the requested prior planning step (`SKILL.md:3,8,12-29` and `to-issues/SKILL.md:3,9`). None establishes a 1:1 replacement with this fixture's `plan.md` layout. This bounded check is dependency/fixture evidence, not additional primary skill audit or activation.
- Exact decision/validation: approve an authoring/eval repair that explicitly grounds the scenario in current planning overlap and judges justified reuse without the two removed names or an invented successor. Human need not choose an environmental successor fact. Any desired new output layout remains a separate scope change. Later current justified reuse/duplicate/multiple-revision cases.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted evaluation repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-005: Improve-skill evals reward prohibited writes

- Checks/applicability/disposition: A17/A22/R03/R06/R11; improve-skill eval contract; adapt.
- Evidence: `SKILL.md:8,49-69,73,82` forbids edits and defines response/no-op output. Evals `6,13-22,27-43,48-60` demand applying/saving files; grader `99-126` rewards them. Prompts do not establish loaded-target context required at `SKILL.md:12-14`.
- Mechanism/impact: obeying response-only/loaded-target rules can be penalized, violating them rewarded. Static contradiction, not an observed run.
- Severity/confidence/client: Major/high; all clients using these evals.
- Proposal/contract: align prompts/oracles to response proposals, explicit loaded targets, no writes and exact no-op. Equivalent eval repair; changing the skill to edit is separate behavior.
- Exact decision/validation: restore evals to existing response-only contract or separately approve redesign? Later write-monitor, loaded/unloaded target, scoped suggestion and no-op cases.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted evaluation repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-006: Missing improve-skill fixture inputs

- Checks/applicability/disposition: A12/A22/A34/R11; improve-skill fixture setup; adopt.
- Evidence: `evals/evals.json:8-10,29-31,50-52` names `evals/files/{commit-session,review-session,noop-session}/session_notes.md`; none exists. Other named target skills exist as external source inputs.
- Mechanism/impact: harness cannot copy declared notes; missing fixture is an unusable setup, not a skill failure.
- Severity/confidence/client: Major/high; all consuming harnesses/clients.
- Proposal/contract: restore bounded self-contained fixture inputs aligned with SAG-005; preserve target-loaded prerequisites and separate fixture data from active instructions.
- Exact decision/validation: approve fixture restoration with eval contract repair; no implementation authorization yet. Later manifest/existence closure before native runs.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted evaluation repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-007: Grader predicates do not prove preservation

- Checks/applicability/disposition: A22/A27/A28/R11; all three graders; adapt.
- Evidence: improve-skill grader `105-126` uses `status`/`lint` and 100-10,000-character size instead of diff/order/rule preservation asserted at evals `14-16,35-37`. Create-skill grader `224-246` accepts any one revised name. Self-improve grader `9-10,92-93,135-164` treats missing root as zero lines and checks only two moved commands.
- Mechanism/impact: unrelated rewrites, mention-only commands, wrong order, renamed extras or lost root rules can satisfy predicates. Predicted false-positive grading; no adversarial execution here.
- Severity/confidence/client: Major/high; provider-neutral local grading.
- Proposal/contract: contract-based negative/source-diff/file-existence/preserved-rule assertions and human semantic review. Equivalent measurement repair.
- Exact decision/validation: approve grader correction while confirming disputed intended contracts separately. Later valid minimal edit, unrelated rewrite, mention-only, deleted root, extra renamed output and unique-control preservation cases.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted evaluation repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-008: Unmeasured metrics become zero

- Checks/applicability/disposition: A22/R11; all five included grader outputs; adapt.
- Additional static evidence and accepted target scope: `skills/explore/evals/grade_benchmark.py:49,59-70` and `skills/official-sources/evals/grade_benchmark.py:38,47-58` use the same zero-filling pattern. The human accepted both additions on 2026-10-06, retaining Create Skill, Improve Skill and Self-improve. The delegation/discovery report records these unchanged producers. Representation and producer/consumer edits remain pending in the existing decision; no duplicate finding is created.
- Evidence: create-skill grader `331-342`, improve-skill `59-70`, self-improve `51-62` hardcode tool calls/steps/errors/grader time to zero; missing timing also defaults zero. Exact imported consumer anchors inspected as dependency only: `skill-creator/scripts/aggregate_benchmark.py:137-154` defaults omitted time/tool/error fields to zero, uses them in aggregation/output (`186-218,248-250,311-323`); `references/schemas.md:110-125,155,169-191` describes numeric measurements and executor metrics source. No nullable/availability-aware representation is established by this source inspection.
- Mechanism/impact: output does not distinguish unknown from measured zero; consumers may infer no errors/steps without trace analysis. Downstream behavior untested.
- Severity/confidence/client: Minor/high; local benchmark/viewer consumers.
- Proposal/contract: trusted trace-derived metrics or explicit unavailable reporting with downstream measurement claims withheld. Honest reporting purpose is supported, but a compatible unknown/availability representation remains an unverified implementation design prerequisite. Do not silently select `null`, omitted keys, or zero, and do not redesign the excluded helper.
- Exact decision/validation: implementation design must establish how unavailable measurements are represented and consumed without false zero averages under retained schema/consumer contracts. No accepted executable change is asserted. Later missing/malformed timing, nonzero trace and schema compatibility cases.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: the human confirmed a separate pending decision on 2026-10-05. The authority or design choice remains unresolved. No implementation approval, evidence waiver, or residual-risk acceptance.
- Owning decision: [Question](tickets/choose-unknown-benchmark-metric-representation.md). Affected implementation stays pending until that choice is resolved or explicitly deferred with independent scope.

### SAG-009: Capped/unscoped AGENTS discovery

- Checks/applicability/disposition: A12/A13/R07/R08; agents-md-improver and self-improve discovery in this checkout; adapt.
- Evidence: agents-md-improver `SKILL.md:17-20` says all but uses `head -50`, hides errors and excludes no fixtures/workspaces. Self-improve `SKILL.md:15-16` prunes only `.git`. Repo exclusions are `.agents/instructions/repo.md:16-17` and architecture boundary list.
- Mechanism/impact: silent cap omits guidance; fixture/workspace AGENTS may become active guidance/edit targets. Runtime effects inferred.
- Severity/confidence/client: Major/high cap/exclusion mismatch; all clients, especially this repository.
- Proposal/contract: uncapped scoped discovery with explicit error accounting and applicable host exclusions. Equivalent completeness plus local adaptation, not a universal fixture ban.
- Exact decision/validation: approve scoped discovery clarification. Later >50 real AGENTS, nested scope, git/workspace/fixture exclusions and explicit fixture-target override.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted authoring repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-010: Broken template fences and unreachable update guide

- Checks/applicability/disposition: A08/A10/A17/A31; agents-md-improver references; adapt.
- Evidence: `references/templates.md:36-46,126-147,153-191,199-223` mix outer three/four backtick fences and prematurely close Markdown examples. Maintained `references/update-guidelines.md` is never linked from the entry or other resources; entry `33,144` links only rubric/templates.
- Mechanism/impact: copied templates can have broken presentation; unique update validation guide may be missed. No render/navigation run occurred.
- Severity/confidence/client: Minor/high; all resource readers.
- Proposal/contract: balance nested fences and select update guide at update phase. Equivalent presentation/navigation repair. Existing headings help scanning; length alone does not justify splitting.
- Exact decision/validation: approve authoring repair, preserving additions-only and approval rules. Later Markdown parse/render, copied templates and native navigation.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted authoring repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-011: Misleading Codex sidecar scope

- Checks/applicability/disposition: A06/A16/C03/R01; create-agentsmd Codex UI; adapt.
- Evidence: `agents/openai.yaml:2-3` advertises creating/managing intelligent agents; `SKILL.md:3,9,29` creates repository AGENTS.md.
- Mechanism/impact: metadata describes a different capability, potentially misdirecting manual selection. UI behavior untested.
- Severity/confidence/client: Minor/high; Codex UI only.
- Proposal/contract: describe AGENTS.md guidance creation, preserving both implicit-invocation controls. Equivalent discovery wording.
- Exact decision/validation: approve metadata wording; agent-creation functionality would be separate scope. Later parse/UI inspection and retained `allow_implicit_invocation: false`.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted authoring repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-012: Argument binding and control adapter evidence gaps

- Checks/applicability/disposition: A12/A36/C01/C03/C04/R02; guidance-review input and agents-md-improver invocation; adapt where equivalent support exists, otherwise unresolved.
- Evidence: guidance-review `SKILL.md:4,10-11` relies on `$ARGUMENTS`; its Codex sidecar only disallows implicit activation. Provider research establishes no portable placeholder binding. Agents-md-improver retains `disable-model-invocation: true` (`4`) and has no Codex sidecar; other two controlled entries have sidecars.
- Mechanism/impact: placeholder may lack injection or implicit-only control may not apply on a host. Possible provider gap, not proven failure/incompatibility.
- Severity/confidence/client: Observation/medium; Codex/Gemini input/control behavior and Copilot VS Code field enforcement remain unknown.
- Proposal/contract: define equivalent supplied user text/path and inspect supported adapter for existing explicit-only intent. Preserve all controls; no implicit expansion.
- Exact decision/validation: approve adapter scope and later explicit/implicit/path/text native cases; do not assert universal enforcement.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: accepted authoring repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. No implementation authorization.

### SAG-013: Public claims and command validation ambiguity

- Checks/applicability/disposition: A15/A36/S02/S04/R03/C04; create-agentsmd public examples and command testing; adapt, authority unresolved.
- Evidence: `SKILL.md:9,23,166-194,218,228,242` references agents.md, claims 20+ tools without date-bound evidence, quotes mutation commands and says test all commands. Output subjects include database/deployment/setup (`41-46,71-76`). Existing example/customization labels (`110,198-220`) partially constrain transfer.
- Mechanism/impact: sample stack commands may be transferred or test-all may imply setup/deploy permission. Predicted ambiguity, not unsafe behavior observed. No external refresh was attempted.
- Severity/confidence/client: Observation/medium; all authoring clients, compatibility count unverified.
- Proposal/contract: repo-evidence-based examples, qualified public facts and explicit inspected-versus-authorized-executed validation. Equivalent documentation repair; execution authority needs separate choice.
- Exact decision/validation: what setup/deploy validation scope is allowed, and should compatibility count be omitted or dated/sourced? Later destructive-command/sample-stack paper cases and honest execution-status report.
- Observed configuration: no behavioral run; model/client runtime values not applicable.
- Human status: the human accepted documentation cleanup for later plan scope on 2026-10-05 and explicitly kept execution authority pending. Cleanup must not choose that authority. No implementation approval, evidence waiver, or residual-risk acceptance.
- Owning decision: [Question](tickets/set-safe-command-validation-scope-for-agents-authoring.md). Execution-related implementation stays pending until that choice is resolved or explicitly deferred with independent scope; accepted documentation cleanup may proceed in later plan scope only when independent of that choice.

### SAG-014: Trailing whitespace in Improve Skill grader

- Checks/applicability/disposition: R12; maintained Python source formatting; adopt.
- Evidence: `skills/improve-skill/evals/grade_benchmark.py:133,139,142` contains whitespace on blank lines. A byte-level scan of all 45 files in the six bundles confirms these three violations and no CR or tab bytes. `.agents/memory/CONVENTIONS.md#code-style` prohibits trailing/blank-line whitespace.
- Mechanism and impact: source violates the repository formatting requirement. No lint suite or grader was executed; no functional behavior failure is asserted.
- Severity/confidence/client: Minor/high; repository source formatting independent of model/provider.
- Proposal/contract: remove only the three whitespace runs during later implementation. Preserve logic, outputs, names and controls.
- Validation: scoped diff/whitespace check after the eventual edit; no behavioral rerun needed for whitespace-only repair.
- Observed configuration: deterministic source byte inspection; no behavioral model/client run.
- Human status: accepted authoring repair for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Exact decision/affected work/route: include this accepted behavior-equivalent cleanup in the later plan. No independent work depends on it.

### RLW-001: Maintenance type table disagrees with the root-only OKF contract

- Severity and confidence: Minor, high confidence from exact static text. When authoring a nested `INDEX.md` or `LOG.md`, the updater's table selects the root-special type while OKF and lint select the matching area/default type. The required later OKF pass can catch it, so this establishes local contradictory guidance, not an unusable whole workflow or observed failure.
- Source/check and applicability: A02/A16/A19/R04/R06/R09; adopt consistent terminology and adapt path precedence to the actual repository profile. Applies when an updater touches a nested uppercase index/log concept.
- Evidence and file/line: `.agents/skills/update-agent-docs/refs/indexes-frontmatter.md:19-20` says `.agents/memory/**/INDEX.md` and `**/LOG.md`; `.agents/skills/okf-authoring/references/profile.md:8-9`, `scripts/lint-okf.py:121-124`, and OKF grader :83-86 select only exact root `INDEX.md`/`LOG.md`. No current nested index/log example or executed failure was found in this bounded scope.
- Affected clients: Provider-neutral repository documentation workflow in Codex, Copilot and Gemini; no model/version/configuration was observed.
- Exact proposed change: Replace the two wildcard table paths with `.agents/memory/INDEX.md` and `.agents/memory/LOG.md`, retaining order and all other rows. State that nested files follow their area/default type rather than introducing new special types.
- Protected contract: Preserve path-derived typing, all existing names/paths, metadata-only body preservation, updater semantic ownership and mandatory one-way OKF verification. This is an equivalent authoring repair to the canonical profile, not new behavior.
- Validation needed: Compare the two tables plus lint/grader derivation statically; later scoped ordinary root and nested index/log examples should derive the same types. No grader/lint execution occurred in this review.
- Human status: accepted authoring clarification for later plan scope by the human on 2026-10-05. Preserve the stated contracts and resolve design prerequisites before executable plan readiness. No implementation approval, evidence waiver, or residual-risk acceptance.
- Source configuration: static source review at `bd7b1a68a081ea847b2e6c1712363000ef01751f`; no behavioral model/client run. Source-review delegation is not native baseline evidence.
- Route: accepted later authoring plan scope, subject to stated prerequisites and final reconciliation; native workflow gaps remain separate. The [batch Resolution](tickets/review-repository-local-workflows.md#resolution) records the human answer.

### RLW-002: Prior-plan reference exception has unclear relationship to single-file self-containment

- Severity and confidence: Minor, high confidence in the textual tension; moderate confidence in predicted effect. A restarting reader may require a second plan for essential knowledge, but no concrete broken implementation or recovery run was observed.
- Source/check and applicability: A17/A32/R05/R06; adapt output guidance only after intended contract is resolved. Applies to a plan building on a checked-in predecessor.
- Evidence and file/line: `.agents/skills/exec-plans/SKILL.md:8,18,26` requires the current single plan to contain all knowledge and enable restart alone. :34 permits incorporating a checked-in prior plan by reference, while skeleton :129 says not to refer to prior plans. The text does not define whether incorporation means optional evidence or a required external instruction dependency.
- Affected clients: Any stateless agent or human novice consuming an ExecPlan; Codex/Copilot/Gemini authoring paths. No runtime configuration tested.
- Exact proposed change and decision: Ask the human whether the prior-plan clause allows required predecessor knowledge outside the current file or only optional historical/evidence links with all executable knowledge embedded. Then align :34 and :129 with that decision and state the allowed link purpose explicitly. Do not silently delete the exception or choose one interpretation in an authoring pass.
- Protected contract: Self-contained novice output, prior-plan exception, living sections, atomic progress/milestone updates, standalone Markdown envelope and required sync remain protected until the decision resolves their relationship. Autonomous authorized implementation language is not evidence of an approval bypass; no new approval flow is proposed.
- Validation needed: Paper review a plan with a checked-in predecessor and one with an unavailable predecessor, checking knowledge availability against the chosen rule. Later restart-only baseline if selected. No plan execution occurred.
- Human status: separate intended-output decision remains pending; the human accepted its retention and routing on 2026-10-05. No contract interpretation, implementation approval, evidence waiver, or residual-risk acceptance.
- Source configuration: static source review at `bd7b1a68a081ea847b2e6c1712363000ef01751f`; no behavioral model/client run. Source-review delegation is not native baseline evidence.
- Owning decision: [Resolve ExecPlan Self-containment and Prior-plan References](tickets/resolve-execplan-self-containment-and-prior-plan-references.md), unblocked by the closed repository-local review. The human approved routing without selecting the underlying contract. Dependent implementation stays pending; both final documents must retain this ID and route.

### RLW-003: Clarify reported OKF reference and orchestration evidence

- Severity and confidence: Observation, high confidence in the predicate boundary and moderate confidence that assertion wording could be misunderstood. No false native-workflow certification or failed behavior was observed. [SAG-007](#sag-007-grader-predicates-do-not-prove-preservation) provides related evidence-integrity context; this is a separate clarification of what this grader already measures, not an automatic extension of its accepted repairs.
- Source/check and applicability: A22/A26/R04/R11; adapt evaluation guidance to separately measure output, coordinator verification, and model workflow. Applies when reporting the grader's reference/composition expectations as evidence of performed workflow.
- Evidence and file/line: `.agents/skills/okf-authoring/evals/grade_benchmark.py:219-232` checks `references_loaded` only in model-written outcome JSON. :268-272 checks claimed orchestration plus phrases in current skill sources; it does not inspect the run transcript. `validate_run_artifacts:325-345` requires a nonempty transcript but never validates read/delegation events. Eval assertions at `evals.json:18,32,46` request profile/reference and one-way ownership evidence. Tests at `test_grade_benchmark.py:58-72` use a synthetic transcript and claimed reference/owner values.
- Affected clients: Provider-neutral local grading used for Codex/Copilot/Gemini output artifacts; no native runtime or model was tested.
- Exact proposed clarification: Label the `evals.json:18,32,46` profile/reference and ownership assertions as reported references/ownership, consistent with `grade_benchmark.py:219-232,268-272`. Preserve artifact/metadata/body predicates and valid independent coordinator lint/diff evidence. Native required-read and composition ordering evidence belongs to the already-required later baseline trace grading; absent trace evidence remains unverified. Do not add these targets to earlier accepted grader repair scope automatically.
- Protected contract: Mandatory profile and conditional summary reads, semantic-versus-representation ownership, no reverse updater call, exact authorized output/diff and unknown evidence states. Do not make required dependencies optional or claim trace absence establishes failure.
- Validation needed: Static review that assertion names describe reported output and coordinator evidence precisely. Later native baseline design can contrast claimed reads with usable reference/order events, including absent events. Distinguish coordinator reconstructed validation-sandbox changes (:191-205) from live model workspace mutations; no baseline containment failure is claimed.
- Human status: accepted authoring clarification for later plan scope by the human on 2026-10-05. Preserve the stated contracts and valid independent checks; do not expand SAG-007's targets. No implementation approval, evidence waiver, or residual-risk acceptance.
- Source configuration: static source review at `bd7b1a68a081ea847b2e6c1712363000ef01751f`; no behavioral model/client run. Source-review delegation is not native baseline evidence.
- Route: accepted later authoring plan scope, subject to stated prerequisites and final reconciliation; required native trace evidence remains outstanding. The [batch Resolution](tickets/review-repository-local-workflows.md#resolution) records the human answer.


### DD-001: Explore spawn grading omits independent-area assertions

- Checks/applicability/disposition: A22/A27/R11; inspectable exploration evaluations and deterministic grading; adapt to artifact grading rather than native dispatch claims.
- Evidence: `skills/explore/SKILL.md:15,21-31` requires independent focused areas. `skills/explore/evals/evals.json:9-21` asserts valid JSON and distinct areas. `skills/explore/evals/grade_benchmark.py:117-135` checks count/agent/parallel flags, then concatenates every prompt and accepts `has_backend or has_frontend or has_db` (:129). It emits no pairwise distinction check. JSON/schema validation is a separate DD-004 mechanism.
- Mechanism/consequence: lexical relevance in one prompt can satisfy the area predicate while other spawns repeat the same area or are irrelevant. Predicted false-positive grading, not observed execution. Major severity; high confidence from exact predicates and asserted contract. Affected surface is provider-neutral local output grading, not demonstrated host dispatch behavior.
- Behavior-preserving proposal: grade each spawn's bounded relevant area and pairwise independence, retain valid agent/count/parallel checks, and consume structurally validated data under DD-004. Preserve the allowed 1-3 areas; the three listed directories are examples, not an all-three requirement. Output-only spawns remain declared plans; actual routing/dispatch must be established later from coordinator traces.
- Later validation: duplicate/irrelevant spawn artifacts and valid one-, two-, three-area plans; DD-004 owns malformed schema inputs. Independent native trace checks belong only in later authorized evidence work.
- Human status: accepted evaluation repair for later planning on 2026-10-06. Preserve stated contracts and resolve genuine protocol prerequisites before affected executable work. No implementation authorization, evidence waiver or residual-risk acceptance.
- Source configuration: static source review at `991b14b86440dab452ac28312c5f05a2b4a42266`; no behavioral model/client run.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. The [batch Resolution](tickets/review-delegation-and-discovery.md#resolution) records the human answer. No skill change has been implemented.

### DD-002: Evaluation setup does not establish required prior context or cache hit

- Checks/applicability/disposition: A12/A21/A22/R08/R11; declared evaluation inputs; adapt with explicit fixture/setup evidence.
- Evidence: `skills/explore/evals/evals.json:26-30,44-47` references `.agents/scratchpad/exploration_results.md` and `backend/auth/constants.py`; neither is bundled in Explore's maintained set and no `evals/files/` exists there. `skills/official-sources/evals/evals.json:106` permits hit or miss, but :107 requires hit, and :108-110 supplies only React files. Seven official fixtures were read; none seeds `official-sources-cache.json`. Historical external-runner provisioning was not inspected and remains unknown.
- Mechanism/consequence: the checked-in definitions alone cannot recreate the prior-context/cache-hit precondition. A correct cache miss/fetch branch may be penalized by an unconditional hit oracle. Major severity for reproducibility and branch scoring; high confidence in missing declared setup, unobserved runtime impact. Provider-neutral fixture setup affects all future native evaluations.
- Behavior-preserving proposal: bundle or declare deterministic prior-context and exact-match cache setup; distinguish cache-hit/miss inputs and expectations, preserve optional cache and narrow direct-read exploration. Clarify `should_explore: false` as skipping redundant/broad exploration or delegation where applicable; it does not assert that relevant direct reads were forbidden or absent.
- Later validation: fresh isolated fixture construction, provided/missing context, exact hit/miss/mismatched version/topic cases, and coordinator file-read/network evidence. No new skill output or autonomy contract is selected.
- Human status: accepted evaluation repair for later planning on 2026-10-06. Preserve stated contracts and settle exact fixture/oracle choices before executable plan readiness. No implementation authorization, evidence waiver or residual-risk acceptance.
- Source configuration: static source review at `991b14b86440dab452ac28312c5f05a2b4a42266`; no behavioral model/client run.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. The [batch Resolution](tickets/review-delegation-and-discovery.md#resolution) records the human answer. No skill change has been implemented.

### DD-003: Official-source graders equate text mentions with citation and cache evidence

- Checks/applicability/disposition: A14/A22/R11; citations, bounded-fetch and cache assertions; adapt to separate report-shape/content checks from trace checks.
- Evidence: `skills/official-sources/evals/grade_benchmark.py:105-106` tests only a domain substring for an official citation. :170-180 and :283-290 inspect self-written phrases for failed-fetch/fallback assertions. :299-315 accepts any cache-path/scratchpad mention; cache reuse :314 passes `has_cache_note or "usenavigate" in normalized`. Eval :107 requests no new fetching, but no corresponding trace predicate exists. :36 reads transcript solely to count its characters. The grader retains independently useful section/version/API/conflict/UNVERIFIED checks.
- Mechanism/consequence: a plain `reactrouter.com` mention or a lookalike URL can meet the domain check; `useNavigate` alone can meet cache reuse, and reported stopping/caching does not establish actual fetch/read order. Major severity; high confidence from exact predicate insufficiency. Predicted false-positive compliance claims remain untested. Affected surface: provider-neutral artifact grader; required later audit traces apply only to selected native Codex cases. Copilot/Gemini compatibility remains static within this audit.
- Behavior-preserving proposal: parse actual citation URLs and official host identity for report-level citation claims; label stopping/cache statements as reported behavior; keep useful independent content predicates. Grade file reads, failed fetch counts, fallback, cache load and absence of extra fetches separately from usable coordinator traces. Do not require fake cache-hit phrases on a valid miss path.
- Later validation: domain-only/lookalike/proper URLs; cache mention without loaded data; correct hit/miss outputs; reported stops versus independent traces. This does not claim a source was visited, official, correct for the version, or fetched by the current audit.
- Human status: accepted evaluation repair for later planning on 2026-10-06. Preserve useful independent content predicates; required trace evidence remains outstanding. No implementation authorization, evidence waiver or residual-risk acceptance.
- Source configuration: static source review at `991b14b86440dab452ac28312c5f05a2b4a42266`; no behavioral model/client run.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. The [batch Resolution](tickets/review-delegation-and-discovery.md#resolution) records the human answer. No skill change has been implemented.

### DD-004: Graders can announce success without grading runs and do not validate JSON shape

- Checks/applicability/disposition: A27/R11; executable evaluation helpers; adapt to explicit artifact validation and no-run outcome.
- Evidence: Explore `skills/explore/evals/grade_benchmark.py:13-19` catches JSON syntax only; :85-91,107-109,141-155 assume dict-like metadata/decision values, and :100-101,119-120 assume spawn containers and records. :177-188 returns zero and prints "Wrote grading.json files" even when no matching runs exist. Official-source :17-24 similarly accepts any JSON timing value used with `.get` at :38; :332-344 has an empty-loop success path. This finding owns structure/error/no-run outcomes; DD-001 owns relevance/independence of valid spawn records.
- Mechanism/consequence: valid JSON with the wrong root/value shape can raise errors instead of a structured invalid-artifact result. An empty or mislaid iteration can report a successful write operation despite writing no grades. Major severity for claimed grading completeness; high confidence in control flow, untested observed failure. All local grading providers affected.
- Behavior-preserving proposal: validate metadata/decision/timing mappings and spawn list/record shapes, preserve all useful predicates, and explicitly report no eligible runs or invalid artifacts without claiming completed grading. Do not silently skip invalid expected runs. Existing source does not establish a clear consumer contract for failure outcomes, so exact statuses, exit codes and error/result schemas remain a design prerequisite. No new representation or incompatible exit behavior is selected by this proposal.
- Exact unresolved design question: what honest incomplete/invalid outcomes can existing aggregate/report consumers distinguish, and which status/exit/result schema preserves their compatibility? Parent reconciliation must keep that question explicit and route a separate decision if source investigation cannot establish an equivalent contract.
- Later validation: empty/mislaid iterations, wrong-root metadata/decision/spawns/timing JSON, unsupported eval IDs, valid canonical directories, and downstream outcome compatibility. No grader was run for this review.
- Human status: separate pending decision retained by the human on 2026-10-06. Failure statuses, exit codes, schemas and compatibility remain unresolved. No implementation authorization, evidence waiver or residual-risk acceptance.
- Source configuration: static source review at `991b14b86440dab452ac28312c5f05a2b4a42266`; no behavioral model/client run.
- Owning decision: [Define Benchmark Grader Failure Outcomes](tickets/define-benchmark-grader-failure-outcomes.md). Exact failure-status, exit-code and result-schema changes remain pending; retain this ID and route in both final documents.

### DD-005: Explore grader contains prohibited blank-line whitespace

- Checks/applicability/disposition: R12; repository source formatting; adopt.
- Evidence: `skills/explore/evals/grade_benchmark.py:116,121,143,145,156` contain whitespace-only lines. Non-mutating source inspection detected five; no CR bytes were found.
- Consequence/severity/confidence: Minor/high; repository formatting violation without observed runtime impact, provider-neutral source.
- Behavior-preserving proposal: remove whitespace from those blank lines only, preserving predicates and control flow.
- Later validation: scoped diff/whitespace check; no broad rewrite or evaluation weakening.
- Human status: accepted authoring cleanup for later planning on 2026-10-06. Preserve predicates and control flow. No implementation authorization, evidence waiver or residual-risk acceptance.
- Source configuration: static source review at `991b14b86440dab452ac28312c5f05a2b4a42266`; no behavioral model/client run.
- Route: accepted later plan scope, subject to stated design prerequisites and final reconciliation. The [batch Resolution](tickets/review-delegation-and-discovery.md#resolution) records the human answer. No skill change has been implemented.
