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

- `skills/agent-brain/` is a staged, source-checkout skill with a standard-library CLI at `skills/agent-brain/scripts/agent-brain.py`. Retrieval uses namespaced JSON comments for defaults and stable unit metadata, selects conservatively by known scope, and returns required-reference closure with explicit gaps. Validate it with `python3 scripts/test-agent-brain-retrieval.py`, `python3 scripts/test-agent-brain-cli.py`, and the skill quick validator; do not imply lifecycle or provider support from this CLI surface.
