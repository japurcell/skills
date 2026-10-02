# Skill Authoring Audit Handoff

## Goal and Status

The destination is a completed audit of non-imported maintained skills plus a self-contained implementation ExecPlan. The twenty-ticket map contains six closed tickets, thirteen open tickets, and one claimed ticket. [Set Audit Completion and Implementation Gates](tickets/set-audit-completion-and-implementation-gates.md) is claimed by `subagent-vmgmic`; its live human decision session is in progress. The current audit pool has 37 candidates: 32 published and five repository-local entry points, after excluding 23 configured imports.

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
- The [batch/report decision](tickets/choose-audit-batches-and-evidence-format.md#resolution) defines twelve review scopes, per-check Markdown coverage, one findings register, shared-resource ownership with consumer checks, and human review after each batch. Complete static review before reconciliation and baseline sample selection. No sample is selected yet.
- The human authorized a narrow static paper-reading exception for `dotnet-upgrade` within this audit. Preserve all invocation, migration approval, execution, installation, packaging, validator, and live-evaluation restrictions. This does not activate its upgrade procedure.
- Follow the [canonical subagent checkpoint rule](../../.agents/instructions/repo.md#subagent-checkpoints), approved after repeated premature interruptions. Missed checkpoints trigger status checks. Do not reuse the short historical limits below as defaults.

## Next Focus

Continue the claimed [Set Audit Completion and Implementation Gates](tickets/set-audit-completion-and-implementation-gates.md) through live Wayfinder and Grilling, with domain modeling still waived. Both exact blockers, `set-adoption-rules-and-protected-behavior.md` and `choose-audit-batches-and-evidence-format.md`, were verified closed before claim. The human accepted the first three gate policies and the explicit unresolved-proposal tracking clarification on 2026-10-02; the ticket's Decision Checkpoint holds their detail. Settle the remaining deferral rules, implementation acceptance, and final document requirements in the second round. Do not discard unresolved redesigns or proposals requiring new approval.

[Choose Audit Batches and Evidence Format](tickets/choose-audit-batches-and-evidence-format.md#resolution) records all seven human-confirmed policies from four rounds. Twelve static review tickets are created, each blocked by this decision and completion gates; the two resource reviews also depend on their corresponding instructions review. [Reconcile Static Findings and Select Baseline Cases](tickets/reconcile-static-findings-and-select-baseline-cases.md) is blocked by all twelve reviews. Those tickets gather source evidence, then require live human disposition decisions; they do not implement changes.

[Batch sizing evidence](batch-sizing-evidence.md) contains all 37 verified measurement rows and a bounded explicit-dependency scan. The second explorer completed without interruption under the longer limit; executed model/effort remain unconfirmed. Parent source checks corrected dependency/role distinctions, an input flag mistaken for a skill dependency, and conditional scope. Complete dependency closure, fixture readiness, and full static compliance remain unverified. Only `dotnet-upgrade/SKILL.md` and its `agents/openai.yaml` were read under the paper exception. No agent remains active and no audit baseline ran.

[Set Audit Evidence and Model Coverage](tickets/set-audit-evidence-and-model-coverage.md#resolution) records nine human-confirmed policies from four rounds. [Model and Baseline Evidence](evidence-model-baselines.md) records the native catalog, help and configuration evidence, limited eval-input checks, delegation timeouts, and unverified prerequisites. Handoff, Spec to Tasks, and OKF Authoring have promising existing inputs; they are not selected or certified fixture-ready. Explore and Create Skill illustrate additional limitations.

No complete isolated native launch recipe or grader compatibility check exists yet. The catalog does not prove account execution. Preserve these gaps when creating later baseline tickets; do not fill them by weakening controls, adding missing fixtures silently, or running a global installer. The actual sample depends on bounded content and fixture review.

[Decide Skill Ownership and Import Handling](tickets/decide-skill-ownership-and-import-handling.md#resolution) records the final scope. The human rejected the lasting provenance proposal and instead excluded imported skills; this supersedes the earlier derivative-maintenance choices in the same exchange. Keep accepted improvements in both roots with exact implementation targets and the existing documentation-maintenance restrictions. Do not resurrect ledger or import-refresh work from earlier answers.

[Current audit scope](local-inventory.md#current-audit-scope) lists all 32 published candidates. Unknown historical origin alone does not block review, but clear additional import evidence removes a candidate. [Import and Packaging Evidence](import-ownership-evidence.md) records the exclusion mappings, read-only delegation, and parent source checks. The original inventory now correctly attributes `show-me` to `humanlayer/skills` and records the four unprefixed Addy state values.

[Set Adoption Rules and Protected Behavior](tickets/set-adoption-rules-and-protected-behavior.md#resolution) holds the human-confirmed rubric, behavior contracts, exception policy, finding severities, and evidence fields. Apply it within the reduced scope.

[Set Audit Completion and Implementation Gates](tickets/set-audit-completion-and-implementation-gates.md) is claimed in the current session. Final audit and implementation-plan authoring remain in the fog until actual findings and behavioral evidence make their scopes precise.

Read the [authoring checklist](research/authoring-checklist/findings.md) and [provider comparison](research/provider-compatibility/findings.md) as needed. The latter is dated source research; the newer evidence ticket resolves the Terra identity and native IDs/efforts while retaining the runtime verification gaps.

## Verification

The previous completed session's read-only Python checks passed for the twenty-ticket graph, metadata, exact dependencies, cycles, six closed-ticket resolutions/map links, local effort links, and fog delimiters. The twelve scopes cover each of the 37 primary candidates exactly once, with two resource scopes contributing to existing skill records. Measurements and selected dependency anchors were checked against current files. This resumed session verifies twenty tickets: six closed, thirteen open, and completion gates claimed by `subagent-vmgmic`; every exact dependency target exists. Both claim blockers are closed, and the claim diff passed `rtk git diff --check`. The first three gate policies are confirmed; second-round decisions remain pending. Rerun whitespace and graph checks after resolving the ticket. No behavioral baseline, full skill audit, or implementation acceptance run has occurred.

The formal agent-document pass records the human-approved checkpoint rule in `.agents/instructions/repo.md` and updates the existing repository-workflow route in `.agents/memory/INDEX.md`. Existing `FILE_MAP.md` entries cover the effort directory and its map. The OKF representation pass uses `profile` only; the changed canonical types are Agent Instruction and Knowledge Index. `rtk proxy python3 scripts/lint-okf.py` exits 0 across both bundles after the final canonical edit. The scoped canonical diff contains exactly those two authorized paths. No skill source or tooling implementation changes.

## Resolved Execution Friction

Tool Guardian rejected an oversized multi-file patch because its input exceeded the command-segment limit. Smaller patches succeeded. The protected scratchpad parent required an approved directory creation; files were subsequently moved into the user-requested docs location. Keep future patches bounded and use the docs location directly.

The resumed session's temporary commit-message replacement used delete and add operations for the same path in one patch. `apply_patch` rejected the duplicate target; a single update operation succeeded. Use one operation per path within a patch.

`rtk --version` reports 0.50.0, and the binary resolves to `/Users/adam/homebrew/bin/rtk`. `rtk gain` cannot open its tracking database in this sandbox; ordinary RTK commands work. This does not block planning.

The provider research reached its 600-second limit before writing findings. The parent interrupted it and resumed the same configured agent for a 180-second recovery limited to saving collected evidence. Findings and a closed resolution were written before the parent stopped the recovery at its next deadline check. Parent source checks corrected the Codex metadata-budget wording: 8,000 characters is the fallback for an unknown context window, not a cap compared with 2%. Preserve source conditions and units when translating numeric rules.

Both research tasks used explicitly submitted `gpt-6-luna` with `max` effort; executed runtime values remain unconfirmed. The parent verified the final artifacts against the tickets and checked key claims against Claude, OpenAI, GitHub, and Gemini primary documentation.

The ownership explorer used explicitly submitted `gpt-6-luna` with `medium` effort and a 300-second parent-enforced limit; completion was checked at 105 seconds. Executed runtime values remain unconfirmed. Parent verification corrected its prefixed state-file wording and unsupported absence inference: all 19 mapped multi-source destinations exist. Preserve the distinction between configured origin, current file presence, and verified historical provenance.

The evidence explorer used explicitly submitted `gpt-6-luna` with `max` effort. The parent interrupted its 360-second fact-collection attempt and its one 90-second report-only recovery at their deadlines. Only partial model facts were returned; the parent verified the native catalog and independently collected the limited help/JSON observations. Fixture readiness remains unknown. Avoid making a broad source-collection report the only durable output before a deadline.

`codex exec --help` for 0.159.3 does not advertise the `--full-auto` flag shown in a dated official eval example. Use current help and configuration evidence, then verify effective permissions and discovery. `--ignore-user-config` does not establish isolated skill loading. A guessed configuration-reference URL returned 404; following the official navigation located `https://learn.chatgpt.com/docs/config-file/config-reference`. Do not infer a broken source from an unverified URL.
