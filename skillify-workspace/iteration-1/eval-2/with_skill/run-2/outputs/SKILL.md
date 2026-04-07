---
name: benchmark-triage
description: Triage a skill benchmark run by clustering failing expectations, reviewing representative evals, and recommending the next edits to try.
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
when_to_use: Use when the user wants a benchmark run triaged into reusable findings and next edits, with trigger phrases like "triage this benchmark", "analyze benchmark results", or "review this skill eval benchmark".
---

# Benchmark Triage

Review a benchmark run, inspect representative failing evals, and produce a concise triage report that explains repeated failure patterns, likely root causes, and the next skill edits to try.

## Inputs

- `$benchmark_path`: Path to a `benchmark.json` file or an iteration directory that contains benchmark results and nearby eval folders.

## Goal

Produce a short triage report that clusters the benchmark's failures, calls out flaky or weak assertions, preserves the per-eval deep-dive pattern from the source workflow, and recommends concrete edits for the next iteration of the skill.

## Steps

### 1. Load the benchmark context

Resolve `$benchmark_path` to the benchmark summary and identify the nearby eval directories, configs, and artifacts available for inspection. Read the benchmark summary first so the later deep dives stay targeted.

**Artifacts**: Candidate failure clusters, notable eval IDs, nearby artifact paths.

**Success criteria**:

- You have located the benchmark summary and any nearby eval outputs needed for inspection.
- You have a short list of the weakest assertions, worst-performing checks, or highest-variance evals to investigate further.

### 2. Prioritize the failures that matter most

Group failing expectations by repeated pattern, frequency, and impact. Separate obvious one-off noise from repeated issues that should drive changes to the skill. Highlight outliers that deserve a direct transcript or output review.

**Artifacts**: Ranked set of failure groups and representative evals.

**Rules**:

- Prefer repeated failures over isolated anomalies.
- Call out potentially flaky assertions instead of treating them as confirmed product issues.

**Success criteria**:

- Failures are grouped into clear clusters rather than a flat list.
- You have selected representative evals for each important cluster.

### 3. Run per-eval deep dives where they help

Inspect representative failing outputs, transcripts, or grading artifacts for the highest-value clusters. When there are multiple independent evals to inspect, split that work into parallel deep dives using a Task agent so the parent flow stays concise.

**Execution**: Task agent

**Artifacts**: Per-eval notes tying raw outputs back to each failure cluster.

**Rules**:

- Use parallel deep dives when eval reviews are independent.
- Keep each deep dive focused on evidence that explains why the benchmark assertion failed.

**Success criteria**:

- Each important failure cluster has at least one representative eval reviewed in detail.
- The notes capture concrete evidence from outputs or transcripts, not just restated benchmark labels.

### 4. Synthesize root causes and likely fixes

Combine the benchmark-level patterns with the per-eval evidence to identify likely root causes. Distinguish between instruction gaps, assertion weaknesses, environment/tooling issues, and output-format mismatches.

**Artifacts**: Root-cause summary and candidate edits.

**Rules**:

- Keep benchmark-tooling observations accurate, including local Python helpers when they were part of the analysis.
- Preserve the distinction between weak grading logic and genuine skill behavior failures.

**Success criteria**:

- Each major failure cluster is paired with a plausible root cause.
- The analysis separates flaky checks from changes that should actually be made to the skill.

### 5. Write the triage report

Produce a concise report that summarizes the benchmark, lists the main failure clusters, cites representative evidence, flags flaky assertions, and recommends the next edits to try. Make the output directly useful for the next skill iteration.

**Execution**: Terminate

**Success criteria**:

- The report is short, actionable, and organized by repeated pattern.
- The report includes concrete next edits to try, not just diagnosis.
- The output is sufficient for a follow-up editing pass without rerunning the entire investigation.
