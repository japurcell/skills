---
name: create-skill
description: Creates or updates skills in this repository using the repo's anatomy, eval, and benchmark conventions while delegating the broader authoring loop to `skill-creator`. Use whenever the user asks to create, modify, refactor, dedupe, benchmark, improve a skill under `skills/`, or mentions `SKILL.md`, `evals/evals.json`, or `grade_benchmark.py`.
---

# Create Skill

## Overview

Create or revise a repository skill so it is ready to live under `skills/` with the right structure, concise instructions, realistic evals, and benchmark support.

Use the `skill-creator` skill for the broader authoring and iteration loop, but enforce this repository's anatomy, validation commands, and workspace layout here so the result matches local conventions instead of a generic skill draft.

## When to Use

- Create a new skill directory under `skills/`.
- Revise an existing `SKILL.md`, skill description, eval set, or benchmark grader.
- Tighten a skill that has grown repetitive, vague, or too long.
- Add weaker-model guardrails so a skill stays explicit and reliable on smaller or older models.
- Add or repair `evals/evals.json`, `evals/grade_benchmark.py`, or benchmark artifacts in a sibling `-workspace/` directory.

## Workflow

1. **Scope the request**
   - Decide whether this is a new skill or a modification.
   - If modifying, preserve the existing directory name and frontmatter `name` unless the user explicitly wants a rename.
   - Search `skills/` for near-duplicate names or overlapping descriptions before creating anything new. If a nearby skill already covers the request, refine that skill instead of creating a shadow skill.

2. **Load the required references**
   - Activate the `skill-creator` skill immediately and use it for the authoring, eval, and benchmark loop instead of recreating that workflow from memory.
   - Read `.agents/instructions/skills.md`, `.agents/instructions/repo.md`, and `.agents/instructions/testing/skills.md` so the result follows repository-specific rules.

3. **Draft or revise the skill**
   - Keep the description trigger-oriented: say what the skill does concisely, then add clear `Use when ...` conditions. Do not stuff numbered workflow steps into the description.
   - Keep the body concise. Reuse nearby skills and root references by name instead of copying long guidance blocks into the new skill.
   - When the skill needs exact commands or exact paths, spell them out.

4. **Add eval and benchmark support**
   - Add or update `evals/evals.json` with at least 3 realistic evals. Cover create, modify, and a negative or dedupe edge case.
   - When assertions can be checked objectively, add `evals/grade_benchmark.py` and prefer deterministic file/content checks over subjective grading.
   - Put generated run artifacts beside the owning skill, never inside its bundle:
     - Published owner `skills/<category>/<name>/`: `skills/<category>/<name>-workspace/iteration-N/eval-*/...`. For example, `skills/default/create-skill/` uses `skills/default/create-skill-workspace/iteration-N/eval-*/...`.
     - Repo-local owner `.agents/skills/<name>/`: `.agents/skills/<name>-workspace/iteration-N/eval-*/...`; from the owner directory, use `../<name>-workspace/iteration-N/eval-*/...`.
   - Benchmark the skill against a baseline. For a new skill use `without_skill`; for an edited skill use `old_skill` or another explicit snapshot.

5. **Validate**
   - Run `python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/<skill-name>`.
   - Run `python3 -m py_compile skills/default/<skill-name>/evals/grade_benchmark.py` when the skill ships a grader.
   - Run `python3 skills/default/<skill-name>/evals/grade_benchmark.py skills/default/<skill-name>-workspace/<iteration-dir>` when benchmark artifacts exist.
   - If the user wants a packaged archive, run `PYTHONPATH=skills/default/skill-creator python3 skills/default/skill-creator/scripts/package_skill.py skills/default/<skill-name> /tmp/skill-dist`.

## Specific Techniques

### Duplicate control

- Compare the requested skill against existing names, descriptions, and nearby workflows before creating a new directory.
- If the only meaningful change is tighter triggering, better evals, or clearer wording, update the existing skill instead of creating a sibling duplicate.
- When you decide to reuse or refine an existing skill, name the closest existing skill explicitly and explain why it is a better fit than creating a new one.

### Benchmarking guidance

- For live `copilot -p` benchmark runs, point the prompt at the exact local `skills/default/<skill>/SKILL.md` or snapshot path and tell the model to ignore other installed copies of the same skill name.
- Save response and transcript artifacts before grading so `evals/grade_benchmark.py` and `aggregate_benchmark.py` have stable inputs.
- For a brand-new skill, compare against `without_skill`. For a modified skill, compare against an explicit `old_skill` or snapshot baseline.
- For a published owner `skills/<category>/<name>/`, show its sibling `skills/<category>/<name>-workspace/iteration-N/`; for example, `skills/default/create-skill-workspace/iteration-N/` beside `skills/default/create-skill/`.
- For a repo-local owner `.agents/skills/<name>/`, use sibling `.agents/skills/<name>-workspace/iteration-N/`; from the owner directory, show the relative sibling as `../<name>-workspace/iteration-N/`.
- Prefer assertions that catch flattering but shallow drafts: missing negative cases, copied reference prose, absent baseline, or missing refresh/validation commands.

## Common Rationalizations

| Rationalization                                              | Reality                                                                                                         |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| "This is only a small skill edit, so I can skip eval work."  | Small description or structure changes often break triggering and benchmark behavior first. Keep evals current. |
| "The repo probably has a generic test command."              | It does not. Choose the narrow validation command that matches the changed files.                               |
| "A baseline is optional because the new draft looks better." | Without a baseline, you cannot show the skill actually improves outcomes instead of just adding instructions.   |

## Red Flags

- The description reads like a workflow summary instead of a trigger description.
- `SKILL.md` duplicates long passages from nearby skills.
- The skill says "run the usual tests" or invents generic frontend commands.
- Evals cover only happy paths and never test duplicate avoidance or weaker-model behavior.
- Benchmark artifacts are written inside a skill bundle instead of its sibling `-workspace/` directory.

## Verification

After completing the workflow, confirm:

- [ ] The skill request was classified as create vs modify, and duplicate checking happened before new files were added.
- [ ] `skill-creator` was invoked.
- [ ] The final `SKILL.md` is concise, trigger-oriented, and follows the anatomy section pattern.
- [ ] `evals/evals.json` covers create, modify, and at least one dedupe or negative case.
- [ ] `evals/grade_benchmark.py` exists when deterministic grading is practical, and its syntax is valid.
- [ ] The narrow repo validation commands were run.
