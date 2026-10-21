# Create-skill repository maintenance

This README holds repository conventions and evaluation instructions for maintainers. Runtime skill instructions remain portable.

## Repository boundaries

For archive edit/baseline scope, installation ownership, and independent workflow boundaries, use [skill sources and installation](../../../brain/codebase/skills-and-installation.md). Read [repository workflow](../../../brain/codebase/repository-workflow.md) and [evaluation caveats](../../../brain/codebase/skill-evaluation.md) for work in this checkout. A maintained skill's own README owns skill-specific acceptance exceptions.

## Evaluation and validation workflow

4. **Add eval and benchmark support**
   - Add or update `evals/evals.json` with at least 3 realistic evals. Cover create, modify, and a negative or dedupe edge case.
   - When assertions can be checked objectively, add `evals/grade_benchmark.py` and prefer deterministic file/content checks over subjective grading.
   - Put generated run artifacts beside the owning skill, outside its bundle, except repository-maintained checked-in fixtures:
     - Published owner `skills/<category>/<name>/`: `skills/<category>/<name>-workspace/iteration-N/eval-*/...`. For example, `skills/default/create-skill/` uses `skills/default/create-skill-workspace/iteration-N/eval-*/...`.
     - Repo-local owner `.agents/skills/<name>/`: `.agents/skills/<name>-workspace/iteration-N/eval-*/...`; from the owner directory, use `../<name>-workspace/iteration-N/eval-*/...`.
   - Repo-local evaluations may also use a disposable external workspace with the same canonical iteration layout.
   - For grader changes, task completion-semantics changes, or benchmark interpretation, read the validation and evidence section below.
   - Benchmark the skill against a baseline. For a new skill use `without_skill`; for an edited skill use `old_skill` or another explicit snapshot.

5. **Validate**
   - After changing a skill definition, run `rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/<skill-name>`; substitute `.agents/skills/<skill-name>` for a repo-local workflow. Honor the maintained skill's own README acceptance scope.
   - Run existing focused public-CLI checks when changing grader behavior; the validation and evidence section below explains the checks and evidence limits.
   - Run `python3 -m py_compile skills/default/<skill-name>/evals/grade_benchmark.py` when the skill ships a grader.
   - Run `python3 skills/default/<skill-name>/evals/grade_benchmark.py skills/default/<skill-name>-workspace/<iteration-dir>` when benchmark artifacts exist.
   - If packaging behavior changes or the user requests a packaged archive, run `PYTHONPATH=skills/default/skill-creator python3 skills/default/skill-creator/scripts/package_skill.py skills/default/<skill-name> /tmp/skill-dist`.


### Benchmarking guidance

- For live `copilot -p` benchmark runs, point the prompt at the exact local `skills/default/<skill>/SKILL.md` or snapshot path and tell the model to ignore other installed copies of the same skill name.
- For live runs, use `--output-format json` plus `--share <transcript.md>`; save `response.md`, `timing.json`, and `transcript.md` before grading.
- Review authored outputs and retained evidence as well as scores. Preserve valid failures and the selected run identity; the validation and evidence section below defines rubric correction and honest metric reporting.
- For a brand-new skill, compare against `without_skill`. For a modified skill, compare against an explicit `old_skill` or snapshot baseline.
- For a published owner `skills/<category>/<name>/`, show its sibling `skills/<category>/<name>-workspace/iteration-N/`; for example, `skills/default/create-skill-workspace/iteration-N/` beside `skills/default/create-skill/`.
- For a repo-local owner `.agents/skills/<name>/`, use sibling `.agents/skills/<name>-workspace/iteration-N/`; from the owner directory, show the relative sibling as `../<name>-workspace/iteration-N/`.
- Prefer assertions that catch flattering but shallow drafts: missing negative cases, copied reference prose, absent baseline, or missing refresh/validation commands.


# Validation and evidence

Use when changing grader behavior, maintaining evaluation fixtures, or interpreting benchmark results. Use the matching skill's own evaluation guide for domain scenarios. Required commands, fixture constraints and evidence standards belong with that guide.

When changing task completion semantics in a producer or worker, review both the producer's historical reconciliation scenarios and the worker's sandbox scenarios. Exercise incomplete or stale all-true input, unresolved verification, commit audits, and repeat completed invocation with genuine progress evidence. Fresh-manifest grading alone is insufficient. In this repository these are `skills/default/spec-to-tasks/evals/update-scenarios.md` and `skills/default/prd-ralph/evals/evals.json`, relative to the repository root; keep each bundle's own workflow independent.

## Portable evaluation procedure

The skill's task includes writing and running evaluations. Its portable workflow lives in [SKILL.md](SKILL.md) and [evaluation validation and evidence](references/validation.md). Repository-specific commands and suite selection above remain maintainer guidance.
