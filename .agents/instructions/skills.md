---
type: Agent Instruction
description: Rules and conventions for skills under `skills/`.
---

# Skills Conventions

- Use `SKILL.md` as the entry point for each skill.
- Store published skill bundles under `skills/<category>/<skill-name>/`; use `skills/default/` for the default category. Keep repository-level `skills/archive/` separate from published categories.
- Start `SKILL.md` with YAML frontmatter.
- Keep `name` lowercase kebab-case.
- Keep `description` concrete and trigger-oriented.
- Write skill invocations as “activate the `<skill-name>` skill” or the plural “activate the `<skill-name>` and `<skill-name>` skills”, substituting the actual names. Use these forms in worker instructions too.
- Do not remove an existing `disable-model-invocation: true` frontmatter key from a skill without explicit human approval.
- Put generated evaluation output in a sibling `<skill-name>-workspace/` directory unless the repository already treats it as a checked-in fixture. Published workspaces live under the skill's category, such as `skills/default/<skill-name>-workspace/`; repo-local workspaces live beside their owners under `.agents/skills/`.
- Treat `skills/archive/` as historical reference; use it as an edit target or current baseline only when the task explicitly calls for it.
- Validate skill changes with `.agents/instructions/testing/skills.md`.

## Best Practices

- [Concise is key](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#concise-is-key).
  Default assumption: you are already very smart. Only add context you do not already have. Challenge each piece of information:
  - "Do I really need this explanation?"
  - "Do I already know this?"
  - "Does this paragraph justify its token cost?"
- Keep SKILL.md body under 500 lines for optimal performance.
- Split content into separate [reference files](#reference-files) when approaching this limit.
- [Checklist for effective skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#checklist-for-effective-skills).

### Reference Files

Skills link to reference files for optimal performance by keeping SKILL.md bodies under 500 lines and by allowing conditional loading of relevant context (see [progressive disclosure patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns)).

Reference files longer than 100 lines MUST include a table of contents at the top so that agents can see the full scope of available information even when previewing for partial reads (see [Official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#structure-longer-reference-files-with-table-of-contents)).

[Avoid deeply nested references](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-deeply-nested-references). Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md to ensure you read complete files when needed.

## Benchmarking

Manage skill benchmark evals and iterations using this workflow.

### Snapshot and Iteration Structure

For existing-skill comparisons:

- Snapshot the pre-edit skill under `skills/<category>/<skill>-workspace/skill-snapshot/`, or the corresponding repo-local sibling workspace.
- Benchmark the edited skill in a fresh `iteration-N/` directory

### Canonical Eval Layout

Keep each benchmark eval in one canonical `iteration-N/eval-*/` directory with a single `eval_metadata.json` beside all config run folders. Split eval directories break local helper scripts (`grade_benchmark.py`, `aggregate_benchmark.py`).

Repo-local skill evaluations may use a disposable external workspace with the same layout. Keep generated runs and snapshots outside maintained skill bundles.

### Live model reruns

- For live `copilot -p` benchmark runs, point the prompt at the exact local `skills/default/<skill>/SKILL.md` or baseline snapshot path and tell the model to ignore other installed copies of the same skill name.
- Capture canonical run artifacts with `--output-format json` plus `--share <transcript.md>` so each run can save `response.md`, `timing.json`, and `transcript.md` before `grade_benchmark.py` and `aggregate_benchmark.py` run.

### Grading

If a skill ships `evals/grade_benchmark.py`, use it to grade iteration artifacts:

```bash
python3 skills/default/<skill-name>/evals/grade_benchmark.py skills/default/<skill-name>-workspace/<iteration-dir>
```

Review the authored documents and retained evidence as well as the scores. A fixture-specific text check can mistake valid wording for a failure or miss contradictory current guidance. Correct the rubric with positive and negative public-CLI cases before comparing runs; include missing/malformed artifacts and make each assertion fail when its required inputs are unavailable. Exclude scenario-inapplicable assertions from success totals. Preserve earlier valid failures and identify the selected run per scenario. State intended write boundaries in the scenario prompt. If an assertion adds an unstated restriction, preserve the original output and grade, clarify the prompt, and rerun instead of relabeling the failed assertion as a pass.

## Document-maintenance skills

- Keep `skills/default/handoff/` and `.agents/skills/exec-plans/` independently usable, including their evaluation bundles. Neither bundle may reference or depend on the other.
- Route their grader tests through [skills testing](testing/skills.md#document-maintenance-graders). Repository documents may link both workflows.
- Keep completed-artifact retention and cleanup in [repository documentation policy](repo.md#documentation-retention), outside both reusable workflows.

## Refactor boundaries

- For large skill refactors, preserve any explicit exclusions or approval requirements already documented for that skill.
- Before pruning a skill, map its existing behavioral obligations to the replacement. Keep actionable authoring and validation detail unless its removal is in scope; passing evals cover only the branches they exercise.

## Planning and task execution

- Keep `.agents/skills/exec-plans/` independent of `skills/default/execplan-implement/`. The implementation skill may consume the planning skill, but the planning skill must not reference its consumer.
- Keep shared task, dependency, reconciliation, and acceptance rules in `exec-plans`. Reference those rules from `execplan-implement`, which owns worker dispatch and Git integration procedures.
- Neither ExecPlan skill may reference `spec-to-tasks` or encode its schema. Their task boundaries, prerequisites, and acceptance live directly in the plan.
- `skills/default/spec-to-tasks/references/task-schema.md` owns the complete manifest contract, including completion reconciliation when tasks change. Keep `skills/default/prd-ralph/references/intake.md` aligned with it and require the same fields for every task. Preserve historical evidence; validate retained completion before shortcuts and report invalid input without rewriting it. Keep `prd-ralph-loop` blind to task selection and manifest contents during orchestration.
- Maintain semantic review alongside task grader tests: valid shape or fixture keywords do not establish context sufficiency, actual prerequisite meaning, command provenance, or integrated acceptance. Route the focused checks through [skills testing](testing/skills.md#task-workflow-graders).
- Review each dependency against the outcome or artifact it consumes, or an explicit source ordering rule. Perform coverage and manifest reviews whose inputs already exist during authoring; do not defer them behind implementation merely because they read task definitions.

## dotnet-upgrade

- Read [`skills/default/dotnet-upgrade/SKILL.md`](../../skills/default/dotnet-upgrade/SKILL.md) only for explicit upgrade requests. Preserve both invocation controls; see [known issues](../memory/known-issues/skills.md) for enforcement limits.
- Keep general procedure separate from dated route research and historical project decisions. Reconcile substantive reference changes with the bundled provenance ledger.
- Invocation alone does not approve migration edits. Require approval of the concrete plan and refreshed necessary evidence; material scope or strategy changes require renewed approval.
- Do not install the bundle, run account-wide installers, execute trial migrations or live evaluations, or change shared knowledge without separate authorization. Authoring scenarios are paper-review inputs, not evidence of runtime behavior.
- Keep local and deployment readiness distinct. Follow the [document-only review guidance](testing/skills.md#dotnet-upgrade-document-review) and use the bundled [document review](../../skills/default/dotnet-upgrade/references/document-review.md) as its acceptance record; it does not prove cross-project execution or client enforcement.

## Subagent router maintenance

- `skills/default/subagent-model-router/reference/model-catalog.md` owns tier membership and the task-default model table. Other routing references use named defaults instead of copying preferred model IDs.
