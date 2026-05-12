---
name: benchmark-triage
description: Triage skill-evaluation benchmark results and turn them into concrete next edits. Use this whenever the user has a benchmark.json file, an iteration directory with benchmark artifacts, failing assertions, flaky evals, regressions, or wants a fast diagnosis of what to change next in a skill benchmark. Treat the benchmark path as the main input and drive the analysis with minimal back-and-forth.
---

# Benchmark Triage

Use this skill as a self-contained, fork-friendly workflow for analyzing benchmark results after a skill evaluation run. Keep the analysis focused on repeated failure patterns, representative evidence, and the next edits most likely to improve the benchmark.

## Inputs

- Required: a benchmark path supplied as `$benchmark_path`
- Accepted forms:
  - a `benchmark.json` file
  - an iteration directory that contains `benchmark.json`
- Expected nearby artifacts: eval directories, grading files, output files, and any run metadata that help explain failures or outliers

If the path is missing, ask once for it. Otherwise proceed without follow-up questions.

## Working Mode

- Prefer running this as a forked, self-contained subagent so the parent conversation stays concise.
- Use task agents for representative per-eval deep dives when multiple failing or high-variance evals need inspection.
- Keep the final report short, specific, and evidence-driven.

## Tooling

Use the benchmark-analysis tool mix from the original workflow:

- `Read` for benchmark summaries, grading files, transcripts, and output artifacts
- `Grep` for locating repeated failures, assertion names, and error strings
- `Glob` for finding eval directories and related run files quickly
- `Bash(python:*)` for lightweight local analysis when a small Python helper is faster than manual inspection
- Task agents for parallel per-eval deep dives
- `Edit` and `Write` only if the user asks you to save the triage report or follow-up notes

## Workflow

1. Resolve the input path.
   - If `$benchmark_path` is a directory, locate `benchmark.json` inside it.
   - If `$benchmark_path` is a file, infer the surrounding iteration directory from its parent path.
   - Identify the nearby eval directories and run artifacts you may need for follow-up inspection.

2. Read the benchmark summary first.
   - Identify the weakest assertions by pass rate.
   - Note the largest deltas between compared configurations.
   - Call out high-variance evals and clear time or token outliers.

3. Group failures before diving deep.
   - Cluster failing expectations by repeated pattern, not by eval order.
   - Separate likely skill logic problems from likely eval-quality problems.
   - Mark assertions that look flaky, non-discriminating, or too broad.

4. Select representative evals for deeper inspection.
   - Pick a small set of representative failures or outliers from each major cluster.
   - When helpful, fork task agents to inspect these evals in parallel.
   - In each deep dive, inspect the relevant grading files, outputs, transcripts, and metadata rather than skimming every eval.

5. Use local Python helpers when they materially speed up the analysis.
   - Summarize failure frequency.
   - Rank assertions by instability.
   - Compare outlier timing or token usage.
   - Prefer short, purpose-built scripts over manual counting.

6. Synthesize the root causes.
   - Explain the repeated patterns behind failures.
   - Distinguish signal from noise.
   - State clearly when evidence is tentative or when more instrumentation would be needed.

7. Recommend the next edits.
   - Propose the smallest set of concrete skill changes most likely to improve the next run.
   - Include eval or assertion changes when the benchmark itself is the limiting factor.
   - Tie every recommendation to evidence from the benchmark or deep dives.

## Report Structure

Use this structure unless the user asked for a different format:

# Benchmark Triage

## Snapshot

- Benchmark path
- Compared configurations
- Largest regressions or improvements

## Failure Clusters

- Repeated failure pattern
- Affected evals or assertions
- Likely root cause

## Flaky Or Low-Signal Checks

- Assertions that appear unstable, non-discriminating, or poorly targeted

## Suggested Next Edits

- Concrete changes to the skill
- Concrete changes to evals or assertions if needed

## Evidence

- Representative files, outputs, or benchmark facts that support the diagnosis

## Heuristics

- Prefer repeated patterns over one-off anomalies.
- Do not overfit to a single noisy eval.
- Call out assertions that pass regardless of configuration or fail for reasons unrelated to the skill.
- Treat benchmark triage as decision support, not just a dump of statistics.
- End with actionable edits, not only observations.
