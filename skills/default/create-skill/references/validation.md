# Evaluation validation and evidence

Use when authoring evaluation fixtures or graders, running skill benchmarks, or interpreting results.

## Artifacts and baselines

Keep one `iteration-N/eval-*/` directory per evaluation, with one `eval_metadata.json` beside configuration/run directories. Use a sibling `<skill-name>-workspace/` or a disposable external workspace. Snapshot the existing skill before editing. Keep baseline snapshots and input fixtures immutable by writing each run's outputs to its own directory in a fresh iteration.

For skill-enabled runs, point live prompts at the exact local SKILL.md or snapshot and instruct the model to ignore installed copies. Preserve the absence of the skill in `without_skill` baselines. Use consistent provider versions/settings and separate roots for paired runs.

## Runner evidence and benchmark artifacts

The runner records execution evidence; it does not grade behavior or create all benchmark artifacts. Preserve its native files before deriving the formats required by the maintained grader and aggregator:

| Native evidence | Contents and use |
| --- | --- |
| `manifest.json` | Run identity, snapshot/configuration hashes, provider preflight, settings, session identity, smoke receipt, and turn records. |
| `evidence/<NN>-<phase>.json` | Captured stdout/stderr, command, cwd, prompt-file path, timestamps, `duration_seconds`, exit code, and timeout status. Keep the referenced prompt files too. |
| `evidence/<NN>-<phase>-response.txt` | Codex's requested final-response output, when produced; verify its presence before using it. Copilot responses remain in captured provider output. |
| `evidence/provider-logs/` | Copilot logs, when produced; inspect their coverage before treating them as a transcript. |

When a consumer expects `response.md`, `timing.json`, or `transcript.md`, produce those derived artifacts with an explicit mapping to the selected run and source turn files:

- **Response:** extract the actual assistant response for the scored turn, preserving raw output. Do not substitute a summary of what the agent should have done.
- **Timing:** populate `total_duration_seconds` from the selected turns' observed `duration_seconds`. Record which turns are included and whether smoke/retry costs are excluded; report excluded costs separately. These durations measure provider subprocess execution, excluding preparation, preflight, and time between turns. Record `total_tokens` only from observed provider usage; mark unavailable metrics as unmeasured rather than zero.
- **Transcript:** render retained prompts and provider events in order, with source references and explicit coverage gaps. Logs or stdout are not automatically a complete conversation transcript. Missing evidence required by an assertion fails that assertion; do not invent missing messages or tool activity.

For direct Copilot runs through an alternative harness, retain `--output-format json` output and a `--share <transcript.md>` export using that harness's supported CLI options. The bundled runner does not expose `--share` or arbitrary argument passthrough; normalize its captured evidence instead. Preserve scenario-specific authored files, fixture observations, and actual Git results alongside provider records when the grader needs them. Require the consumer's artifacts before grading or aggregation; a successful runner exit alone is insufficient.

## Assertions and graders

Before comparing runs, validate fixture-specific rubrics through positive and negative public-CLI cases. Include missing and malformed artifacts; every assertion fails when required input is unavailable. Exclude scenario-inapplicable assertions from success totals. Inspect authored output and retained evidence beyond text matches.

State intended write boundaries and each scored field's type and expected value or format in the prompt or scenario. If the rubric requires a format the scenario leaves open, preserve the raw output and score. Report the ambiguity separately from behavioral failures, clarify the scenario, then rerun. Apply the same procedure to other unstated restrictions. Preserve earlier valid failures and identify the selected run for every scenario.

When a feature is removed, retire assertions that require its old behavior. Keep coverage for behavior the skill still promises.

When changing task completion semantics, cover historical reconciliation as well as fresh outputs. Include stale all-true input, unresolved verification, commit audits, and repeat completed invocation with genuine progress evidence. Review authority, context sufficiency, dependencies, negative cases, and integrated acceptance semantically.

Run the affected skill's documented grader command. Compile changed graders and run their focused existing public CLI tests. A grader may exit zero because it wrote results despite failed assertions; inspect its documented result fields, including `expectations` and `summary.failed` where applicable. Invalid invocation and malformed input must remain distinguishable from a graded failure.

## Interpretation limits

Keep instruction coverage separate from sampled performance claims. Preserve raw artifacts, selected-run identities, and delta direction. Check the installed aggregator against each run's raw metrics. For example, `aggregate_benchmark.py` can substitute output character count for missing tokens and zero for missing duration. Label the character count as a proxy and the duration as unmeasured. One selected run per scenario does not establish repeated-run variance. Wording checks are scenario heuristics, not general natural-language verification.
