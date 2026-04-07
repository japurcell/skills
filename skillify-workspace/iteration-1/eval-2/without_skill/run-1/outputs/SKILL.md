# benchmark-triage

Use this skill when you need to triage the results of a completed skill benchmark run and turn the results into a short, actionable report. This skill is designed to run as a forked, self-contained subagent once the benchmark path is known.

## Invocation

`/benchmark-triage $benchmark_path`

Arguments:

- `$benchmark_path`: Path to a `benchmark.json` file or to an iteration directory that contains benchmark outputs and nearby eval artifacts.

## Goals

- Cluster repeated failures instead of describing evals one-by-one.
- Identify the weakest assertions and the highest-variance evals.
- Deep-dive representative failing evals to separate repeated root causes from noise.
- Call out flaky assertions explicitly.
- End with concrete next edits to try on the skill under evaluation.

## Inputs

- Benchmark summary data from `benchmark.json`.
- Nearby eval directories, transcripts, prompts, outputs, or artifacts needed to explain representative failures.

## Required Behavior

- Run as a forked, self-contained workflow. Do not interrupt the parent conversation for follow-up questions once `$benchmark_path` is available.
- Preserve a per-eval deep-dive pattern, but only for representative failures and outliers.
- Prefer parallel per-eval review when several failing cases need inspection.
- Capture the benchmark-analysis tool mix accurately when reporting what was used.
- Keep the final report short, concrete, and oriented toward the next skill edits.

## Recommended Tooling

- `Read` for benchmark summaries, transcripts, prompts, and outputs.
- `Grep` and `Glob` for locating repeated patterns and nearby eval artifacts.
- `Bash(python:*)` for lightweight local analysis when the benchmark data needs custom grouping or counting.
- Task agent for per-eval deep dives when multiple failing evals can be reviewed in parallel.
- `Edit` and `Write` only if the triage workflow is also expected to save a report artifact.

## Workflow

1. Resolve the benchmark input.
   - If `$benchmark_path` is a file, treat it as the benchmark summary.
   - If `$benchmark_path` is a directory, locate `benchmark.json` and identify the nearby eval directories that correspond to the reported failures.

2. Read the benchmark summary first.
   - Identify the weakest assertions, the largest failure clusters, and any high-variance or outlier evals.
   - Build a short candidate list of failures worth deeper inspection.

3. Group failures before drilling in.
   - Cluster failures by repeated symptom, assertion, or output pattern.
   - Separate likely systemic issues from single-eval anomalies.
   - Flag anything that already looks flaky or under-specified.

4. Deep-dive representative evals.
   - Inspect a small set of representative failures from each important cluster.
   - Include outliers when they could reveal a distinct root cause.
   - Review transcripts, outputs, and prompts closely enough to explain why the assertion failed.

5. Use parallel review when helpful.
   - If several evals need inspection, split them into parallel per-eval deep dives.
   - Keep the parent synthesis focused on comparing patterns across those deep dives.

6. Synthesize root causes.
   - Distinguish between prompt gaps, workflow gaps, missing constraints, poor decomposition, tool misuse, and flaky evaluation logic.
   - Prefer explanations that account for multiple failures at once.

7. Propose the next edits.
   - Recommend a short list of concrete skill changes to try next.
   - Tie each proposed edit to the failure clusters it is meant to address.
   - If a failure looks like evaluator flakiness rather than a skill problem, say so directly.

## Output Format

Produce a short triage report with these sections:

### Failure Clusters

- List the main repeated failure patterns.
- Note which assertions or eval groups they affect.

### Representative Deep Dives

- Summarize the few evals inspected in detail.
- Explain what each one reveals about the broader pattern.

### Flaky Or Questionable Assertions

- Call out any assertions that appear unstable, ambiguous, or mismatched to the intended behavior.

### Recommended Next Edits

- Provide concrete skill changes or evaluation changes to try next.
- Keep this list short and prioritized.

### Tool Mix Used

- Record the tools used for the analysis, including local Python helpers or task agents if they were used.

### Save And Invoke

- End by stating the recommended save path for the skill and the invocation command:
  - `.agents/skills/benchmark-triage/SKILL.md`
  - `/benchmark-triage $benchmark_path`

## Quality Bar

- Do not stop at raw benchmark counts; explain patterns.
- Do not inspect every failing eval if a representative sample is enough.
- Do not present vague advice such as "improve the prompt" without naming the concrete missing behavior.
- Keep the report concise, but specific enough that the next editor knows what to change.
- Prefer evidence-backed conclusions over speculation.
