# Evaluation validation and evidence

Use when authoring evaluation fixtures or graders, running skill benchmarks, or interpreting results.

## Artifacts and baselines

Keep one `iteration-N/eval-*/` directory per evaluation, with one `eval_metadata.json` beside configuration/run directories. Use a sibling `<skill-name>-workspace/` or a disposable external workspace. Snapshot the existing skill before editing. Keep baseline snapshots and input fixtures immutable by writing each run's outputs to its own directory in a fresh iteration.

Point live prompts at the exact local SKILL.md or snapshot and instruct the model to ignore installed copies. For live `copilot -p` runs, use `--output-format json` and `--share <transcript.md>`. Retain `response.md`, `timing.json`, and `transcript.md` before grading or aggregation.

## Assertions and graders

Before comparing runs, validate fixture-specific rubrics through positive and negative public-CLI cases. Include missing and malformed artifacts; every assertion fails when required input is unavailable. Exclude scenario-inapplicable assertions from success totals. Inspect authored output and retained evidence beyond text matches.

State intended write boundaries and each scored field's type and expected value or format in the prompt or scenario. If the rubric requires a format the scenario leaves open, preserve the raw output and score. Report the ambiguity separately from behavioral failures, clarify the scenario, then rerun. Apply the same procedure to other unstated restrictions. Preserve earlier valid failures and identify the selected run for every scenario.

When a feature is removed, retire assertions that require its old behavior. Keep coverage for behavior the skill still promises.

When changing task completion semantics, cover historical reconciliation as well as fresh outputs. Include stale all-true input, unresolved verification, commit audits, and repeat completed invocation with genuine progress evidence. Review authority, context sufficiency, dependencies, negative cases, and integrated acceptance semantically.

Run the affected skill's documented grader command. Compile changed graders and run their focused existing public CLI tests. A grader may exit zero because it wrote results despite failed assertions; inspect its documented result fields, including `expectations` and `summary.failed` where applicable. Invalid invocation and malformed input must remain distinguishable from a graded failure.

## Interpretation limits

Keep instruction coverage separate from sampled performance claims. Preserve raw artifacts, selected-run identities, and delta direction. Check the installed aggregator against each run's raw metrics. For example, `aggregate_benchmark.py` can substitute output character count for missing tokens and zero for missing duration. Label the character count as a proxy and the duration as unmeasured. One selected run per scenario does not establish repeated-run variance. Wording checks are scenario heuristics, not general natural-language verification.
