---
type: Agent Instruction
description: Rules and conventions for skills under `skills/`.
---

# Skills Conventions

- Use `SKILL.md` as the entry point for each skill.
- Start `SKILL.md` with YAML frontmatter.
- Keep `name` lowercase kebab-case.
- Keep `description` concrete and trigger-oriented.
- Do not remove an existing `disable-model-invocation: true` frontmatter key from a skill without explicit human approval.
- Put generated evaluation output in a sibling `*-workspace/` directory unless the repository already treats it as a checked-in fixture.
- Validate skill changes with `.agents/memory/testing/skills.md`.

## Benchmarking

Manage skill benchmark evals and iterations using this workflow.

### Snapshot and Iteration Structure

For existing-skill comparisons:

- Snapshot the pre-edit skill under `skills/<skill>-workspace/skill-snapshot/`
- Benchmark the edited skill in a fresh `iteration-N/` directory

### Canonical Eval Layout

Keep each benchmark eval in one canonical `iteration-N/eval-*/` directory with a single `eval_metadata.json` beside all config run folders. Split eval directories break local helper scripts (`grade_benchmark.py`, `aggregate_benchmark.py`).

### Live model reruns

- For live `copilot -p` benchmark runs, point the prompt at the exact local `skills/<skill>/SKILL.md` or baseline snapshot path and tell the model to ignore other installed copies of the same skill name.
- Capture canonical run artifacts with `--output-format json` plus `--share <transcript.md>` so each run can save `response.md`, `timing.json`, and `transcript.md` before `grade_benchmark.py` and `aggregate_benchmark.py` run.

### Grading

If a skill ships `evals/grade_benchmark.py`, use it to grade iteration artifacts:

```bash
python3 skills/<skill-name>/evals/grade_benchmark.py skills/<skill-name>-workspace/<iteration-dir>
```

## Refactor boundaries

- For large skill refactors, preserve any explicit exclusions or approval requirements already documented for that skill.

## Subagent router maintenance

- `skills/subagent-model-router/reference/model-catalog.md` owns tier membership and the task-default model table. Other routing references use named defaults instead of copying preferred model IDs.

- `skills/agent-brain/` bundles standard-library retrieval, lifecycle coordination, evidenced publication, finite dream coverage, optional configured source ingestion, and reviewed reversible setup. Preserve informational recall without delivery receipts or state initialization, required-read ordering and explicit affected gaps. For bridge or registered stage changes, load [the lifecycle protocol](../../skills/agent-brain/references/lifecycle.md), [learn](../../skills/agent-brain/references/learn.md) and [dream](../../skills/agent-brain/references/dream.md); for software/activation and mapping ownership, load [setup](../../skills/agent-brain/references/setup.md). Validate public subprocess behavior through [scripts testing](../memory/testing/scripts.md). Semantic evidence stays foreground-authored; deterministic checks cannot certify every claim. Keep protocol and native offline fixtures in disposable Git repositories. Exact managed activation does not certify deployed native consumption, actual-home installation or publisher pilot behavior.
- Activated supported update-agent-docs and clean-agent-docs join the canonical learn/dream obligation. Focused ingest-source proposes all semantic summary and knowledge changes through learn's checked reversible publication; preserve its inactive legacy workflow and mandatory document obligations. Source action readiness requires current checked learning and actual self-contained guidance delivery, including newly required units. Do not relabel direct canonical edits as learned through recovery or run a recursive semantic pass.
- Agent-brain's optional disposable certified calendar plans and schemas support frozen longitudinal validation only. The legacy offline fixture clock remains separate. Run the public pilot suite with the existing lifecycle/maintenance/native suites when changing this boundary; offline calculator gates and process certificates do not establish product benefit or native consumption.
