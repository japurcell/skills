---
name: benchmark-triage
description: Triage a completed benchmark run into clustered failure patterns and concrete next edits.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit
  - Write
  - "Bash(python:*)"
argument-hint: "$benchmark_path"
arguments:
  - benchmark_path
context: fork
when_to_use: Use when you have a completed benchmark run to inspect, want a triage report from a benchmark.json or iteration directory, or ask to "triage benchmark results", "analyze this benchmark run", or "review eval failures".
---

# Benchmark Triage

Analyze a completed benchmark run, inspect representative failing evals, and produce a short triage report with concrete next edits to try.

## Inputs

- `$benchmark_path`: Path to a `benchmark.json` file or an iteration directory that contains benchmark results and nearby eval artifacts.

## Goal

Produce a self-contained triage report that clusters repeated failures, identifies flaky or noisy assertions, highlights representative deep dives, and recommends the next edits to the evaluated skill or workflow.

## Steps

### 1. Resolve benchmark scope

Locate the benchmark summary from `$benchmark_path`. If the input is a directory, find the relevant `benchmark.json` and the nearby eval folders or transcripts that support deeper inspection.

**Artifacts**: Resolved benchmark file path, related eval directories, and any supporting transcripts or outputs to inspect later.

**Rules**: Accept either a direct `benchmark.json` path or an iteration directory. Stay within local benchmark artifacts and do not assume missing files exist.

**Success criteria**: The benchmark summary is located, the inspectable eval artifacts are identified, and the available evidence set is clear enough to continue.

### 2. Cluster failures and choose deep dives

Read the benchmark summary to identify the weakest assertions, the most frequent failure groups, and the highest-variance or otherwise representative evals. Use local Python helpers only if they materially speed up grouping or counting.

**Artifacts**: Failure clusters, a shortlist of representative evals to inspect, and any benchmark-level counts worth citing.

**Rules**: Preserve the benchmark-analysis tool mix narrowly. Prefer direct reading and grep/glob first; use `Bash(python:*)` only when structured analysis is genuinely useful.

**Success criteria**: The main failure buckets are identified and a justified shortlist of representative evals is ready for detailed inspection.

### 3. Inspect representative evals

Review the selected failing evals and their outputs or transcripts. When multiple deep dives are independent, run them in parallel using task agents rather than handling every eval serially in the parent agent.

**Execution**: Task agent

**Artifacts**: Per-eval notes covering what failed, what evidence supports the failure classification, and any signs of flakiness or prompt mismatch.

**Rules**: Preserve the per-eval deep-dive pattern from the source workflow. Favor representative outliers and recurring failures over exhaustive inspection of every eval.

**Success criteria**: Representative evals have been inspected closely enough to explain the failure modes with concrete evidence.

### 4. Synthesize root causes

Combine the benchmark-level patterns with the deep-dive findings to separate repeated root causes from one-off noise. Call out flaky assertions, brittle wording, missing instructions, or tool-usage mismatches where supported by the evidence.

**Artifacts**: A root-cause summary mapped to the main failure clusters.

**Rules**: Distinguish confidence levels clearly. Do not overstate conclusions when the evidence is thin or contradictory.

**Success criteria**: The repeated failure patterns are explained, likely root causes are stated, and flaky or noisy assertions are explicitly identified when present.

### 5. Write the triage report

Produce a short report that summarizes the failure clusters, cites representative eval observations, flags flaky assertions, and recommends the next edits to try on the skill or workflow under evaluation.

**Rules**: Keep the report concise and action-oriented. Recommendations should be concrete enough that a follow-up editor can implement them without redoing the full analysis.

**Success criteria**: The final report clusters failures, highlights representative evidence, identifies likely flaky checks, and proposes concrete next edits.
