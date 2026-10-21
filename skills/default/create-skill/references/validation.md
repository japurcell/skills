# Evaluation validation and evidence

Use when authoring evaluation fixtures or graders, running skill benchmarks, or interpreting results.

## Artifacts and baselines

Keep one `iteration-N/eval-*/` directory per evaluation, with one `eval_metadata.json` beside configuration/run directories. Use a sibling `<skill-name>-workspace/` or a disposable external workspace; keep generated runs outside the maintained bundle. Snapshot the existing skill before editing and use a fresh iteration for comparisons.

Point live prompts at the exact local SKILL.md or snapshot and instruct the model to ignore installed copies. For live `copilot -p` runs, use `--output-format json` and `--share <transcript.md>`. Retain `response.md`, `timing.json`, and `transcript.md` before grading or aggregation.

## Assertions and graders

Before comparing runs, validate fixture-specific rubrics through positive and negative public-CLI cases. Include missing and malformed artifacts; every assertion fails when required input is unavailable. Exclude scenario-inapplicable assertions from success totals. Inspect authored output and retained evidence beyond text matches.

State intended write boundaries in the prompt. If an assertion imposes an unstated restriction, preserve the original output and grade, clarify the prompt, then rerun. Preserve earlier valid failures and identify the selected run for every scenario.

When changing task completion semantics, cover historical reconciliation as well as fresh outputs. Include stale all-true input, unresolved verification, commit audits, and repeat completed invocation with genuine progress evidence. Review authority, context sufficiency, dependencies, negative cases, and integrated acceptance semantically.

Compile changed graders and run their focused existing public CLI tests. A grader may exit zero because it wrote results despite failed assertions; inspect its documented result fields, including `expectations` and `summary.failed` where applicable. Invalid invocation and malformed input must remain distinguishable from a graded failure.

## Interpretation limits

Keep instruction coverage separate from sampled performance claims. Preserve raw artifacts, selected-run identities, and delta direction. Label missing data and proxies: substituted character counts are not measured tokens, and defaulted zero duration is not measured time. One selected run per scenario does not establish repeated-run variance. Wording checks are scenario heuristics, not general natural-language verification.
