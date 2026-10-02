# Choose Audit Batches and Evidence Format

**Type:** grilling
**Status:** closed
**Blocked By:** set-audit-evidence-and-model-coverage.md, set-adoption-rules-and-protected-behavior.md, decide-skill-ownership-and-import-handling.md
**Research Dir:** not applicable

## Question

How should the non-imported audit candidates and their supporting resources be partitioned into bounded audit sessions, and what report makes coverage and findings reviewable?

Choose batches from actual content size, risk, dependencies, and the ownership decision. The 60-entry inventory is historical; current importer mappings exclude 23 entries and leave 37 candidates. Specify a per-skill record and coverage index that account for every applicable authoring check, preserve source anchors, distinguish static and behavioral evidence, record exclusions and justified exceptions, and link findings to proposed changes and validation. Define cross-skill reconciliation, treatment of newly discovered primary skills or import evidence, nested exceptions, and human review points. Do not add imported-derivative maintenance or a lasting provenance ledger.

After closing this ticket, create bounded audit decision tickets with exact dependencies. Keep final audit and ExecPlan work in the fog until evidence makes their precise scope clear.

---

## Batch Allocation

The human accepted this allocation on 2026-10-01. Each primary entry point has one owning batch. Resource batches finish the same skill's coverage; they do not create additional primary skills. The bounded dependency inventory supports these groups but does not establish complete dependency closure.

| Batch | Primary entry points or supporting scope |
| --- | --- |
| [Review Skill Authoring and Repository Guidance](review-skill-authoring-and-repository-guidance.md) | `skills/{create-skill,improve-skill,agents-md-improver,create-agentsmd,guidance-review,self-improve}/` |
| [Review Repository-local Workflows](review-repository-local-workflows.md) | `.agents/skills/{clean-agent-docs,exec-plans,ingest-source,okf-authoring,update-agent-docs}/` |
| [Review Delegation and Discovery](review-delegation-and-discovery.md) | `skills/{delegate-to-subagents,subagent-model-router,explore,official-sources,explain-your-thinking}/` |
| [Review Quality and Harness Skills](review-quality-and-harness-skills.md) | `skills/{adversarial-review,code-review,code-simplify,fixing-accessibility,techdebt,harness-analysis,improve-repo-harness}/` |
| [Review Requirements and Task Planning](review-requirements-and-task-planning.md) | `skills/{prd,spec-to-tasks,to-issues,architecture-design-contest}/` |
| [Review Execution and Handoff](review-execution-and-handoff.md) | `skills/{prd-ralph,prd-ralph-loop,execplan-implement,commit,handoff}/` |
| [Review GitHub CLI Guidance](review-github-cli-guidance.md) | `skills/gh-cli/` |
| [Review .NET and UI Guidance](review-dotnet-and-ui-guidance.md) | `skills/{dotnet,dotnet-ui-app}/` |
| [Review Modernization Instructions](review-modernization-instructions.md) | `skills/code-modernization/SKILL.md`, `agents/` and `commands/` within that bundle |
| [Review Modernization Workflows and Assets](review-modernization-workflows-and-assets.md) | `skills/code-modernization/{workflows,assets}/`; verify integration with the instructions batch |
| [Review Upgrade Instructions and Templates](review-upgrade-instructions-and-templates.md) | `skills/dotnet-upgrade/SKILL.md`, bundle `agents/`, `assets/`, `evals/`, top-level `references/*.md` and `references/case-studies/` |
| [Review Upgrade Route and Source Records](review-upgrade-route-and-source-records.md) | `skills/dotnet-upgrade/references/{routes,provenance}/`; inspect existing records only, with no new provenance-ledger work |

For the first eight batches, include each assigned skill's maintained bundled resources and evaluation definitions as static evidence. Exclude generated outputs and historical snapshots. Review external/shared resources only as dependencies under the approved ownership policy. The [sizing evidence](../batch-sizing-evidence.md) motivates dedicated GitHub CLI review and the two resource splits; byte counts include non-text assets and are not token budgets or quality findings.

Set completion gates next. All static batch tickets depend on those gates and this batch decision. The two resource batches also depend on their corresponding instructions batch. Cross-batch reconciliation and baseline-case selection follow all twelve batch reviews. Inspect consumers across batches without treating a skill-dependency cycle as a review-ticket dependency cycle.

## Resolution

The human confirmed seven policies in four Grilling rounds on 2026-10-01: batch reports, human review cadence, explicit per-check coverage, shared-resource ownership, a narrow protected-reading exception, static-first sequencing, and the twelve scopes above. These decisions authorize audit evidence gathering and reviewable planning records, not skill implementation.

### Report contract

Keep working audit records under `docs/skill-audit/`:

- `coverage.md` holds the shared check catalog, candidate and exclusion index, source revision, shared-resource ownership, and separate static and behavioral coverage states.
- `reports/<batch-slug>.md` holds that batch's scope and per-skill sections. Each section records the exact files reviewed, source revision and hashes, intended purpose, protected contracts, dependency/consumer checks, and evidence limits.
- `findings.md` holds each finding once with a stable identifier. Batch reports and coverage rows link to the same finding rather than copying its details. Use batch-prefixed identifiers and coordinate shared-record writes when sessions run concurrently.

Create these records when review begins; do not prefill them with passing claims. The final audit remains `audit.md`, and the later self-contained implementation plan remains `ExecPlan.md`.

Assign stable IDs and descriptive labels to every check in the approved authoring checklist, including its related security clarification, and to applicable repository/client requirements. Define the source anchors, strength, and applicability conditions once in the catalog. Each per-skill matrix has a row for every check, with applicability, adoption disposition, current compliance, evidence/source anchors, finding links, and unresolved gaps. Split a compound check when its outcomes differ. Give adaptations and exclusions specific reasons. Missing evidence stays unresolved; it is not incompatibility or passing compliance.

Keep static review completion separate from whether the skill satisfies a criterion and from behavioral evidence completion. Source reading can complete a static investigation while exposing a defect or an untested runtime claim. Existing eval files and grades are not evidence of native discovery or current passing behavior. Use the established evidence contract for required cases, models, repetitions, traces, failures, and explicit waivers.

Findings retain all fields from the adoption decision: source/check, affected file and line, evidence and failure mechanism, provider/client surface, observed configuration when tested, proposed change, contract boundary, consequence-based severity, confidence, and validation still needed. Also record the human's proposal status: accepted authoring improvement, deferred, rejected, or separate behavior decision required. Acceptance of an authoring proposal does not authorize implementation. An unresolved redesign never enters the plan as an accepted change.

### Shared resources, scope, and exceptions

Assign each included shared resource one review owner in the coverage index. Review its content once, then check every consumer's paths, applicability, and preserved contracts. Cross-batch skill calls still receive consumer checks even when the called skill has a different owner. Imported skills remain excluded; inspect only dependencies needed by included skills, without auditing or revising the excluded bundles.

Record nested exceptions at the exact skill, file, check, and client scope that supports them. Preserve their source and rationale; do not turn a local waiver into a global rule. Conflicting or unclear contracts remain unresolved for a separate human decision.

Maintain visible candidate/exclusion history in the coverage index. Clear additional import evidence removes a candidate with source and updated counts. A newly discovered maintained primary entry point under either approved root is recorded and assigned a bounded review scope when its inclusion is clear; ambiguous scope requires a human decision. Fixtures, snapshots, and generated outputs remain excluded. Historical provenance recovery and new provenance-ledger work remain out of scope.

The human explicitly authorized static paper reading of `dotnet-upgrade` instructions and resources for this audit, overriding the repository's explicit-upgrade-only reading restriction within this effort. Preserve invocation controls and every execution, migration approval, installation, packaging, validator, and live-evaluation restriction. The existing document-only acceptance remains the relevant boundary. Reading the skill does not activate its migration procedure or authorize any of those operations.

### Review sequence and human decisions

Set audit completion and implementation gates next. Then gather static evidence and review findings with the human after each batch. Record accepted authoring proposals, deferred proposals, and behavior questions separately. For split bundles, a batch can finish its assigned scope while the primary skill remains partially reviewed until all parts and integration checks are complete.

After all twelve static reviews, reconcile duplicate/cross-skill findings, shared resources, conflicts, exclusions, and coverage gaps once. Choose up to three risk-selected fixture-ready skills and their exact baseline cases using the full static review. No sample is selected by this decision. Baseline setup and execution tickets follow when eligibility and exact cases make their scopes precise. Required unresolved baseline gaps still block the completed-audit label unless the human explicitly waives them under the evidence contract.

The final audit and ExecPlan remain in the fog until actual findings and baseline evidence make their precise content and validation obligations clear. Repartition or expand review only for concrete content, risk, dependency, or coverage evidence, with revised ownership and exact ticket dependencies. Do not treat line/byte thresholds as automatic failures.
