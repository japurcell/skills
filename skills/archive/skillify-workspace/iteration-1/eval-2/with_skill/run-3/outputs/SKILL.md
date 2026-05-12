---
name: benchmark-triage
description: Review a skill benchmark run, inspect representative failing evals, and produce a concise triage report with concrete next edits.
allowed-tools: Read, Grep, Glob, Write, Bash(python:*), Task
argument-hint: [benchmark-path]
arguments:
  - benchmark_path
context: fork
when_to_use: Use when the user wants a quick triage of benchmark or eval results, asks to review a benchmark.json or iteration directory, or says things like "triage this benchmark", "review these eval failures", or "summarize what the benchmark says to fix next".
---

# Benchmark Triage

Review a benchmark run, inspect representative failing evals, and produce a short report that clusters failures, flags likely flaky assertions, and recommends the next skill edits to try.

## Inputs

- `$benchmark_path`: Path to a `benchmark.json` file or an iteration directory that contains benchmark outputs and nearby eval artifacts.

## Goal

Produce a triage report that explains the main failure clusters, calls out the most informative outliers, and recommends concrete next edits. The workflow is complete when the report is grounded in the benchmark data and representative eval evidence, not just aggregate counts.

## Steps

### 1. Locate benchmark inputs and map the failure surface

Resolve `$benchmark_path` to the benchmark file and identify any nearby eval directories, transcripts, or review artifacts that can support deeper inspection. Read the benchmark summary to find the weakest expectations, highest-variance cases, and the evals most worth inspecting.

**Success criteria**:

- The benchmark source is resolved correctly.
- The most important failing expectations or unstable evals are listed.
- Candidate eval artifacts for deeper review are identified.

**Artifacts**: Resolved benchmark path, shortlist of failing expectations, shortlist of representative evals.

**Rules**:

- Prefer the existing benchmark structure instead of guessing file locations.
- Focus first on failures that combine frequency with signal, not just raw count.

### 2. Deep-dive representative evals

Inspect the most representative failing evals and any notable outliers. When several evals can be reviewed independently, use Task agents to analyze them in parallel. For each deep dive, extract the failure mode, what the model did instead, and whether the issue looks like a missing instruction, poor trigger guidance, formatting drift, or a potentially flaky expectation.

**Success criteria**:

- At least a few representative failing evals or outliers have been inspected directly.
- Each inspected eval has a short explanation of the failure mode.
- Parallel deep dives are used when that improves coverage without losing clarity.

**Execution**: Task agent

**Artifacts**: Per-eval notes on failure modes, candidate root causes, flaky-or-not assessment.

**Rules**:

- Preserve the per-eval deep-dive pattern rather than relying only on aggregate benchmark numbers.
- Use local Python helpers only when they materially speed up inspection or summarization.

### 3. Synthesize recurring patterns and likely causes

Group the observed failures into repeated patterns. Distinguish between issues caused by unclear instructions, missing constraints, poor skill structure, brittle wording, or benchmark assertions that may be too strict. Note which patterns appear to explain multiple eval failures.

**Success criteria**:

- Repeated failure clusters are clearly named.
- Likely root causes are tied to direct evidence from benchmark data or inspected evals.
- Potentially flaky assertions are separated from real workflow gaps.

**Artifacts**: Failure clusters, likely root causes, flaky assertion candidates.

### 4. Write the triage report

Produce a concise report that includes: the main failure clusters, a few representative examples, any flaky assertion concerns, and the next edits to try on the skill or benchmark. Keep the recommendations concrete and ordered by expected impact.

**Success criteria**:

- The report is short, actionable, and evidence-based.
- Recommended edits are concrete enough to implement next.
- The report makes clear which findings are high-confidence versus tentative.

**Execution**: Direct

**Artifacts**: Final triage report.

**Rules**:

- Do not stop at describing failures; propose the next edits to try.
- Keep the final output concise enough to use as an iteration handoff.
