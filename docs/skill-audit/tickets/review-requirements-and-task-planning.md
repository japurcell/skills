# Review Requirements and Task Planning

**Type:** grilling
**Status:** closed
**Blocked By:** choose-audit-batches-and-evidence-format.md, set-audit-completion-and-implementation-gates.md
**Research Dir:** not applicable

## Question

Which authoring improvements and adaptations does this scope justify, which contracts must they preserve, and which findings should the human accept, defer, reject, or resolve as separate behavior decisions?

Review each maintained entry point and bundled resources under `skills/prd/`, `skills/spec-to-tasks/`, `skills/to-issues/`, `skills/architecture-design-contest/`. Include evaluation definitions as static evidence; exclude generated outputs, snapshots, and fixture entry points from the primary inventory.

Specific review concerns: Intended discovery triggers, live human decisions, delegation, task/output structure, issue-tracker prerequisites, and planning boundaries.

Apply the [batch/report contract](choose-audit-batches-and-evidence-format.md#resolution), [adoption policy](set-adoption-rules-and-protected-behavior.md#resolution), and [evidence contract](set-audit-evidence-and-model-coverage.md#resolution). Consult [sizing and dependency evidence](../batch-sizing-evidence.md) as a bounded inventory, not proof of dependency closure or skill quality. Account for every check and reviewed file; give shared resources an owner and check consumers across batches. Static coverage is separate from compliance and runtime evidence.

Write the scope's evidence to `docs/skill-audit/reports/review-requirements-and-task-planning.md`; update the shared coverage index and findings register through coordinated writes. Gather source facts, then review proposed dispositions with the human through Grilling. The ticket closes only after that live review and its recorded decision. Do not implement skill or tooling changes, run installers or imported refreshes, or launch behavioral baselines in this static review. Surface ambiguous scope and behavior as separate decisions.

---

## Resolution

The human accepted all three planning recommendations with "accept all" on 2026-10-06. Static investigation and live proposal review are complete. This records later plan scope and retained decisions; it authorizes no implementation, installation, publication, audited grader execution or native evaluation.

### Accepted evaluation repairs

Accept [RPT-001](../findings.md#rpt-001-spec-evaluations-require-obsolete-schema-and-horizontal-tasks) and [RPT-004](../findings.md#rpt-004-architecture-evaluations-bind-local-absolute-fixture-paths). Align Spec to Tasks prompts and grader with the maintained `tasks.json`, `tasks`, `T001` IDs, output precedence and vertical-slice contracts. Replace Architecture evals' absolute source paths with explicitly provisioned portable isolated fixtures. Exact fixture/oracle and provisioning choices remain prerequisites before executable readiness; acceptance does not invent their design.

Exact later evaluation targets are `skills/spec-to-tasks/evals/evals.json`, `skills/spec-to-tasks/evals/grade_benchmark.py` and `skills/architecture-design-contest/evals/evals.json`, with fixture provision defined before implementation. Preserve both existing Spec fixture behavior requirements, useful checks, task schema and false/empty defaults, known-command and UI/backend distinctions, final response, names, output precedence, controls, approvals, required helpers and agent roles, independent designs and design-only scope. No production dependency/batch fields or horizontal-only task policy are approved. Necessary protocol dependencies remain pending until resolved; independent valid-artifact repairs need their exact oracles before executable scope.

### Retained behavior decisions

Keep these three underlying questions open alongside the thirteen earlier routes:

- RPT-002: [Resolve To Issues Tracker Setup](resolve-to-issues-tracker-setup.md).
- RPT-003: [Resolve Architecture Contest Narrow Exploration](resolve-architecture-contest-narrow-exploration.md).
- RPT-005: [Resolve Planning Browser Verification Prerequisite](resolve-planning-browser-verification-prerequisite.md).

The closed batch unblocks these routes without selecting tracker setup, a narrow-exploration exception or browser-helper supply/mapping. Preserve prerequisites, counts, approvals and prescribed output strings pending their separate choices. Source absence does not establish universal host unavailability; browser wording prescribes downstream verification, not browser execution while planning. Both final audit and ExecPlan must expose all sixteen pending routes and owning IDs. Genuinely dependent work stays pending. Deferral requires rationale, affected work, remaining risk and revisit trigger. Retention is neither an evidence waiver nor residual-risk acceptance.

### Accepted shared grader scope

Add exactly `skills/spec-to-tasks/evals/grade_benchmark.py` to [Choose Unknown Benchmark Metric Representation](choose-unknown-benchmark-metric-representation.md) (SAG-008) and [Define Benchmark Grader Failure Outcomes](define-benchmark-grader-failure-outcomes.md) (DD-004). Retain all eight earlier metric producers and five protocol graders, making nine producers and six graders. Their exact lists live in those owning tickets. Preserve actually measured output/transcript character counts and useful predicates. Representation, statuses, exits, schemas, eligible-run/output identity and consumer compatibility remain unresolved; this scope approval chooses no protocol and authorizes no execution or producer/consumer edit.

### Evidence, limits and next boundary

The [report](../reports/review-requirements-and-task-planning.md) owns twelve unchanged primary files, two fixtures, fourteen bounded source dependencies and four complete 58-check matrices (232 rows), at source baseline `b4d0b428aaccdc1d4f7661129c7e4c78ef85425f`. Sixteen supporting audit-record hashes identify their read checkpoint only. JSON/YAML/AST parsing and source reading do not prove automatic activation, required delegation, tool consent, installed access or successful task output. No native baseline or audited workflow ran.

All five findings now have human dispositions; no proposal was rejected or deferred. Earlier accepted scopes remain unchanged apart from the one explicit grader addition above. Finish remaining static scopes and reconciliation before baseline selection. No second ticket is claimed or started during this closure.
