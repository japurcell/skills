# Review Skill Authoring and Repository Guidance

**Type:** grilling
**Status:** closed
**Blocked By:** choose-audit-batches-and-evidence-format.md, set-audit-completion-and-implementation-gates.md
**Research Dir:** not applicable

## Question

Which authoring improvements and adaptations does this scope justify, which contracts must they preserve, and which findings should the human accept, defer, reject, or resolve as separate behavior decisions?

Review each maintained entry point and bundled resources under `skills/create-skill/`, `skills/improve-skill/`, `skills/agents-md-improver/`, `skills/create-agentsmd/`, `skills/guidance-review/`, `skills/self-improve/`. Include evaluation definitions as static evidence; exclude generated outputs, snapshots, and fixture entry points from the primary inventory.

Specific review concerns: Description scope, authoring loops, repository-doc ownership, imported helper dependencies, installer instructions, and stopping rules.

Apply the [batch/report contract](choose-audit-batches-and-evidence-format.md#resolution), [adoption policy](set-adoption-rules-and-protected-behavior.md#resolution), and [evidence contract](set-audit-evidence-and-model-coverage.md#resolution). Consult [sizing and dependency evidence](../batch-sizing-evidence.md) as a bounded inventory, not proof of dependency closure or skill quality. Account for every check and reviewed file; give shared resources an owner and check consumers across batches. Static coverage is separate from compliance and runtime evidence.

Write the scope's evidence to `docs/skill-audit/reports/review-skill-authoring-and-repository-guidance.md`; update the shared coverage index and findings register through coordinated writes. Gather source facts, then review proposed dispositions with the human through Grilling. The ticket closes only after that live review and its recorded decision. Do not implement skill or tooling changes, run installers or imported refreshes, or launch behavioral baselines in this static review. Surface ambiguous scope and behavior as separate decisions.

---

<!-- Resolution will be appended here. -->

## Review checkpoint

2026-10-05: static investigation is complete in the [batch report](../reports/review-skill-authoring-and-repository-guidance.md), with 45 unchanged-source bundle hashes, scoped supporting-source records, and six 58-check matrices. [Coverage](../coverage.md) tracks the full 37-candidate pool; [findings](../findings.md) owns all fourteen proposals. No native run, installer, grader execution, skill implementation, or fixture repair occurred.

The live Grilling round presented authoring-repair dispositions, evaluation-repair dispositions, and retention of four separate pending questions. The human answered all three on 2026-10-05; the Resolution below records those answers. Approval of plan scope does not authorize implementation.

## Resolution

2026-10-05: the human accepted the authoring repairs, accepted the evaluation repairs, and chose to keep all four separate decisions pending and visible. The [finding register](../findings.md) owns each finding's human disposition, evidence, affected work, and validation requirements.

- Accept SAG-001, SAG-009, SAG-010, SAG-011, SAG-012, SAG-014, and only SAG-013's documentation cleanup for later authoring plan scope. Preserve approvals, invocation controls, names, required dependencies, stopping rules, and output contracts. SAG-012's actual client enforcement remains unverified.
- Accept SAG-004, SAG-005, SAG-006, and SAG-007 for later evaluation repair scope. Ground the duplicate-avoidance fixture/oracle in documented current planning overlap; settle exact fixture/oracle choices before executable plan readiness. Preserve response-only Improve Skill and loaded-target prerequisites, restore bounded notes fixtures, and use source/diff, file-existence, adversarial checks, and semantic review for preservation.
- Keep SAG-002, SAG-003, SAG-008, and SAG-013's execution-authority question pending in their four linked decision tickets. Their dependent implementation stays pending. Both final documents must retain every unresolved ID and route. Routing is not a behavior choice, unknown-metric representation, waiver, risk acceptance, or execution approval.

Static investigation and human proposal review are complete for this batch: six skills, 45 unchanged-source bundle files, and 348 coverage rows. Native evidence and implementation acceptance remain outstanding. The accepted proposals are later plan scope only; no skill source was changed and no installer, grader, validator, or native audit baseline ran.

This closes the only non-research ticket resolved in this logical session. The four separate decisions are now unblocked by this review; their other status remains open. The next allocated static scope is [Review Repository-local Workflows](review-repository-local-workflows.md), unless the human prioritizes a separate decision.
