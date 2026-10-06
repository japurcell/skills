# Review Quality and Harness Skills

**Type:** grilling
**Status:** closed
**Blocked By:** choose-audit-batches-and-evidence-format.md, set-audit-completion-and-implementation-gates.md
**Research Dir:** not applicable

## Question

Which authoring improvements and adaptations does this scope justify, which contracts must they preserve, and which findings should the human accept, defer, reject, or resolve as separate behavior decisions?

Review each maintained entry point and bundled resources under `skills/adversarial-review/`, `skills/code-review/`, `skills/code-simplify/`, `skills/fixing-accessibility/`, `skills/techdebt/`, `skills/harness-analysis/`, `skills/improve-repo-harness/`. Include evaluation definitions as static evidence; exclude generated outputs, snapshots, and fixture entry points from the primary inventory.

Specific review concerns: Review intake, consequence and confidence, mandatory roles and helper skills, quality loops, and imported dependencies. Distinguish subagent roles from skill entry points.

Apply the [batch/report contract](choose-audit-batches-and-evidence-format.md#resolution), [adoption policy](set-adoption-rules-and-protected-behavior.md#resolution), and [evidence contract](set-audit-evidence-and-model-coverage.md#resolution). Consult [sizing and dependency evidence](../batch-sizing-evidence.md) as a bounded inventory, not proof of dependency closure or skill quality. Account for every check and reviewed file; give shared resources an owner and check consumers across batches. Static coverage is separate from compliance and runtime evidence.

Write the scope's evidence to `docs/skill-audit/reports/review-quality-and-harness-skills.md`; update the shared coverage index and findings register through coordinated writes. Gather source facts, then review proposed dispositions with the human through Grilling. The ticket closes only after that live review and its recorded decision. Do not implement skill or tooling changes, run installers or imported refreshes, or launch behavioral baselines in this static review. Surface ambiguous scope and behavior as separate decisions.

---

## Source Investigation Checkpoint

Claimed as `subagent-Q7c2N9` on 2026-10-06 after both exact blockers were verified closed. Source baseline is `72a3ae956e3533aaddf33eb1e8d8ecf30b69d08f`. The source reviewer owns only `docs/skill-audit/reports/review-quality-and-harness-skills.md`; parent owns shared records and the final canonical documentation pass. Human dispositions were pending at this source checkpoint; the live answers are recorded below.

The initial parent-enforced runtime window is 2026-10-06 15:40:09-16:00:09 UTC. Inspect saved five-minute checkpoints and request status if one is missed. Check status at the declared limit before stopping safely or recording a justified extension; elapsed time alone does not trigger interruption. This is static source investigation, not a native audit baseline.

At the source checkpoint, investigation and parent reconciliation were complete and the claim was released for the then-pending live review. The [report](../reports/review-quality-and-harness-skills.md) owns seven exact 58-check matrices, twenty-six unchanged primary files and eighteen bounded dependency fingerprints. The [single register](../findings.md) owns QH-001 through QH-010 and SAG-008/DD-004/SAG-011 scope additions. The Resolution below records subsequent human disposition and closure. No native baseline or source implementation occurred.

## Prepared Live Review

1. Accept QH-001/QH-007 evaluation repairs and only the Harness Analysis sidecar addition to SAG-011 for later planning? Align Code Review's oracles with current intake, references, 80+ and PR stops; correct Harness claim polarity, bounded-stop recommendations and section placement. Preserve useful checks, four review responsibilities, controls, approvals, read-only intent and output contracts. Set exact fixture/oracle choices and genuine protocol prerequisites before executable readiness. The accepted original SAG-011 target remains included.
2. Retain QH-002/QH-003/QH-004/QH-005/QH-006/QH-008/QH-009/QH-010 in their seven linked decision tickets? These cover required generalist portability, verification routing floor, Techdebt rollback, two helper conflicts, Harness report capture, Improve Repo Harness intent and adversarial trivial-case intent. Keep all six earlier routes as well: thirteen underlying routes stay visible in both final documents. Retention selects no behavior or waiver.
3. Add exactly `skills/adversarial-review/evals/grade_benchmark.py`, `skills/code-review/evals/grade_benchmark.py` and `skills/harness-analysis/evals/grade_benchmark.py` to SAG-008's metric-producer and DD-004's grader-protocol scope? Preserve the five original metric targets and two original protocol targets, actually computed character counts and useful predicates. Unknown representation, failure statuses, exits, schemas and compatibility remain unresolved. If accepted, update the two existing decision tickets; do not create duplicate findings or expand excluded helpers.

All three questions concerned planning dispositions. None grants implementation, installer/refresh/validator/grader execution, native baseline execution, evidence waiver or residual-risk acceptance. The Resolution records the human's accepted dispositions.

## Resolution

On 2026-10-06 the human answered "Accept all 3" to the three prepared live questions. This closes only Review Quality and Harness Skills after source investigation, parent reconciliation and live proposal review. Both exact blockers remained closed. Closure claim `subagent-C8d4K2` ends here; no other non-research ticket closes in this logical session.

1. Accept QH-001/QH-007 evaluation repairs for later planning, and add only `skills/harness-analysis/agents/openai.yaml` to SAG-011's accepted authoring scope. Align Code Review oracles with current intake, actual reference paths, 80+ and existing PR stops. Fix Harness claim polarity, stopping recommendations and section placement. Preserve useful checks, all four review responsibilities, controls, approvals, read-only intent, names and outputs. Preserve the original `skills/create-agentsmd/agents/openai.yaml` target. Exact fixture/oracle choices and genuine protocol prerequisites remain executable-readiness gates.
2. Retain QH-002/QH-003/QH-004/QH-005/QH-006/QH-008/QH-009/QH-010 in their seven linked decision routes. The closed batch unblocks those routes without selecting the underlying contracts. Keep all six earlier routes too; all thirteen underlying decisions stay pending and visible by ID/route in both final documents. Genuinely dependent work remains pending.
3. Add exactly `skills/adversarial-review/evals/grade_benchmark.py`, `skills/code-review/evals/grade_benchmark.py` and `skills/harness-analysis/evals/grade_benchmark.py` to SAG-008's metric-producer and DD-004's grader-protocol scope. Retain the five original metric targets and two original protocol targets, for eight producers and five graders. Preserve computed character counts and useful predicates. Representation, statuses, exits, schemas and compatibility remain unresolved in their existing decisions; excluded helper changes are not included.

No proposal was rejected or deferred. These are planning dispositions only, not implementation, installation, refresh, validator/grader execution or native-baseline authorization. No evidence waiver or residual-risk acceptance was given. Source defects and unresolved runtime evidence remain unchanged by approval.

The [report](../reports/review-quality-and-harness-skills.md) owns seven complete 58-check matrices and source fingerprints; [findings](../findings.md) owns exact proposals, dispositions and validation needs. Closure synchronizes coverage, map, pending target scope and handoff. The next static review remains unstarted.
