# Review Modernization Workflows and Assets

**Type:** grilling
**Status:** open
**Blocked By:** choose-audit-batches-and-evidence-format.md, set-audit-completion-and-implementation-gates.md, review-modernization-instructions.md
**Research Dir:** not applicable

## Question

Which authoring improvements and adaptations does this scope justify, which contracts must they preserve, and which findings should the human accept, defer, reject, or resolve as separate behavior decisions?

Review `skills/code-modernization/workflows/` and `skills/code-modernization/assets/` as supporting resources of the same primary skill. Read executable resources statically; do not execute workflows or external analysis tools. Check integration with the closed instructions review. Treat the image as an asset, not text-context bytes.

Specific review concerns: Script/instruction consistency, errors and prerequisites, intermediate artifact contracts, asset navigation, and integration gaps.

Apply the [batch/report contract](choose-audit-batches-and-evidence-format.md#resolution), [adoption policy](set-adoption-rules-and-protected-behavior.md#resolution), and [evidence contract](set-audit-evidence-and-model-coverage.md#resolution). Consult [sizing and dependency evidence](../batch-sizing-evidence.md) as a bounded inventory, not proof of dependency closure or skill quality. Account for every check and reviewed file; give shared resources an owner and check consumers across batches. Static coverage is separate from compliance and runtime evidence.

Write the scope's evidence to `docs/skill-audit/reports/review-modernization-workflows-and-assets.md`; update the shared coverage index and findings register through coordinated writes. Gather source facts, then review proposed dispositions with the human through Grilling. The ticket closes only after that live review and its recorded decision. Do not implement skill or tooling changes, run installers or imported refreshes, or launch behavioral baselines in this static review. Surface ambiguous scope and behavior as separate decisions.

---

<!-- Resolution will be appended here. -->
