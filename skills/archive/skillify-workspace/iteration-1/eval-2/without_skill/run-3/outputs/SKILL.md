---
name: benchmark-triage
description: Triage skill benchmark results and turn them into concrete next edits. Use this whenever the user wants help reviewing benchmark.json, an iteration directory, failing evals, flaky assertions, or high-variance benchmark outcomes. If a benchmark path is provided, proceed without follow-up questions and produce a short triage report with failure clusters, representative deep dives, and recommended skill changes.
compatibility:
  tools:
    - Read
    - Grep
    - Glob
    - Edit
    - Write
    - Bash
  agents:
    - Task
---

# Benchmark Triage

Use this skill as a self-contained fork. Once the benchmark path is known, do not stop to ask the user clarifying questions unless the path is missing or unreadable.

## Inputs

Accept one argument:

- `$benchmark_path`: path to `benchmark.json` or to an iteration directory that contains it

Treat nearby eval directories, grading files, and saved outputs as the source of truth.

## Outcome

Produce a short triage report that:

- clusters the main failure modes
- calls out flaky or high-variance assertions and evals
- cites representative deep dives with concrete evidence
- proposes the next skill edits to try

## Workflow

1. Resolve the benchmark target.
   - If `$benchmark_path` is a directory, look for `benchmark.json` inside it.
   - Derive the iteration root from the benchmark location.
   - Confirm which run pairs are present, such as `with_skill`, `without_skill`, or `old_skill`.

2. Read the benchmark summary before opening individual evals.
   - Inspect aggregate pass rates, token usage, duration, and deltas.
   - Identify the weakest expectations and the evals with the largest variance or most surprising regressions.
   - Do not deep-dive every eval by default. Start with the patterns that can change the next iteration.

3. Select representative evals for deeper inspection.
   - Pick examples that cover repeated failures, not just a single noisy outlier.
   - Include at least one suspicious high-variance case when the benchmark suggests flakiness.
   - Prefer evals whose outputs or transcripts make the root cause legible.

4. Fork per-eval deep dives when that will speed up review.
   - Use Task agents for independent eval investigations instead of handling each one serially in the parent agent.
   - Give each task agent a narrow brief: inspect one eval pair, summarize what failed, quote the evidence, and suggest the most likely root cause.
   - Keep the parent agent focused on synthesis across evals.

5. Inspect the local artifacts for each chosen eval.
   - Read `eval_metadata.json`, `grading.json`, outputs, and any nearby transcripts or notes.
   - Use `Read`, `Grep`, and `Glob` first.
   - Use small local Python helpers through `Bash(python:*)` when parsing JSON or grouping failures is faster than manual inspection.
   - Use `Edit` or `Write` only if the user asks for a saved report or follow-on artifact.

6. Synthesize patterns, not just symptoms.
   - Group repeated failures by likely cause such as missing instruction coverage, over-specific wording, bad decomposition, formatting drift, or flaky assertions.
   - Separate true skill problems from weak benchmarks.
   - Call out assertions that always pass, always fail, or depend on noisy evidence.

7. Recommend the next edits.
   - Suggest the smallest set of skill changes most likely to improve the next iteration.
   - Distinguish between skill-body changes, eval changes, and grader or assertion changes.
   - If the benchmark is too weak to support a confident edit, say so and recommend how to strengthen it.

## Deep-Dive Checklist

For each representative eval, answer these questions:

1. What exact expectation failed or varied?
2. What evidence in the saved output or transcript explains the result?
3. Is this failure likely caused by the skill, by the eval design, or by the grader?
4. Does the same pattern appear in other evals?
5. What concrete change would most likely fix it?

## Report Structure

Use this exact structure:

```markdown
# Benchmark Triage Report

## Overall signal

## Failure clusters

## Flaky or high-variance findings

## Representative deep dives

## Recommended next edits

## Save and invoke
```

Keep the report short and decision-oriented. Favor grouped patterns and concrete edits over exhaustive narration.

## Save And Invoke

Always end the report with these two lines, adjusted only if the user explicitly asks for a different location or command:

- Recommended save path: `.agents/skills/benchmark-triage/SKILL.md`
- Invocation command: `/benchmark-triage $benchmark_path`

## Assumptions

- The workflow runs as a forked, self-contained subagent.
- The benchmark artifacts already exist; this skill triages them rather than generating them.
- Nearby eval directories contain enough evidence to inspect representative failures.
