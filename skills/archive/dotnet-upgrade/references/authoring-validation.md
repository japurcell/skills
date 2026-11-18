# Authoring validation and evaluation scope

Use when authoring or evaluating this bundle's documentation, provenance, or paper scenarios. Work from the authoritative skill source when evaluation assets are needed; an installed runtime copy may omit them.

## Document-only acceptance

Keep general procedure distinct from dated route research and historical project decisions. Reconcile substantive reference changes with `references/provenance/source-map.json`. Review ledger destinations, bundled navigation, evidence scope, exact invocation controls, and all six paper scenarios.

From the authoritative skill directory, run applicable non-mutating checks:

    rtk proxy python3 -m json.tool references/provenance/source-map.json
    rtk proxy python3 -m json.tool evals/evals.json

Use the containing repository's scoped whitespace check when available. Report absent evaluation assets as unavailable; do not infer a passing evaluation from runtime-copy completeness.

Document-only acceptance does not require archive packaging, live models, benchmarks, trial upgrades, application commands, or installers. Preserve invocation controls when validators disagree with metadata; do not remove controls to obtain a passing result. JSON parsing, navigation, and whitespace checks establish structure, not successful migrations, refreshed vendor evidence, live client enforcement, or sampled agent performance.

## Execution boundaries

Document authoring does not authorize installation, live evaluations, benchmarks, trial migrations, or changes to shared knowledge. Honor existing authorization; otherwise obtain it before those actions. For authorized evaluations, retain exact inputs, baseline/source revisions, commands, raw outputs, observed results, and failures. Separate paper instruction coverage from measured behavior and performance. Never report invented or unexecuted results.

Concrete-plan approval and refreshed necessary evidence remain required before migration edits, with renewed approval for material scope or strategy changes. Evaluation success does not waive those gates.
