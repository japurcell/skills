---
name: create-skill
description: Creates or updates skills in this repository using the repo's anatomy, eval, and benchmark conventions while delegating the broader authoring loop to `skill-creator`. Use whenever the user asks to create, modify, refactor, dedupe, benchmark, or improve a skill under `skills/`, mentions `SKILL.md`, `evals/evals.json`, `grade_benchmark.py`, or wants a skill to work better on weaker models.
---

# Create Skill

## Overview

Create or revise a repository skill so it is ready to live under `skills/` with the right structure, concise instructions, realistic evals, and benchmark support.

Use `skill-creator` for the broader authoring and iteration loop, but enforce this repository's anatomy, validation commands, and workspace layout here so the result matches local conventions instead of a generic skill draft.

## When to Use

- Create a new skill directory under `skills/`.
- Revise an existing `SKILL.md`, skill description, eval set, or benchmark grader.
- Tighten a skill that has grown repetitive, vague, or too long.
- Add weaker-model guardrails so a skill stays explicit and reliable on smaller or older models.
- Add or repair `evals/evals.json`, `evals/grade_benchmark.py`, or `skills/<skill>-workspace/` benchmark artifacts.
- Not for merely extracting the just-finished session into a one-off personal skill when `skillify` is the more direct fit.

## Workflow

1. **Scope the request**
   - Decide whether this is a new skill or a modification.
   - If modifying, preserve the existing directory name and frontmatter `name` unless the user explicitly wants a rename.
   - Search `skills/` for near-duplicate names or overlapping descriptions before creating anything new. If a nearby skill already covers the request, refine that skill instead of creating a shadow skill.

2. **Load the required references**
   - Invoke `skill-creator` immediately and use it for the authoring, eval, and benchmark loop instead of recreating that workflow from memory.
   - Read [./templates/skill-anatomy.md](./templates/skill-anatomy.md) before drafting or editing the body. Use its section pattern as the default template.
   - Read `docs/agent-guides/authoring.md` and `docs/agent-guides/validation.md` so the result follows repository-specific rules.

3. **Draft or revise the skill**
   - Use this section order unless the request has a strong reason to differ: `Overview`, `When to Use`, `Workflow`, `Specific Techniques`, `Common Rationalizations`, `Red Flags`, `Verification`.
   - Keep the description trigger-oriented: say what the skill does, then add clear `Use when ...` conditions. Do not stuff numbered workflow steps into the description.
   - Keep the body concise. Reuse nearby skills and root references by name instead of copying long guidance blocks into the new skill.
   - When the skill needs exact commands or exact paths, spell them out. Weaker models follow concrete instructions more reliably than implied conventions.

4. **Add eval and benchmark support**
   - Add or update `evals/evals.json` with at least 3 realistic evals. Cover create, modify, and a negative or dedupe edge case. Add a weaker-model or benchmark-focused case when that behavior matters.
   - When assertions can be checked objectively, add `evals/grade_benchmark.py` and prefer deterministic file/content checks over subjective grading.
   - Put generated run artifacts in `skills/<skill>-workspace/iteration-N/eval-*/...`, never inside the skill directory itself.
   - Benchmark the skill against a baseline. For a new skill use `without_skill`; for an edited skill use `old_skill` or another explicit snapshot.

5. **Validate and refresh**
   - Run `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`.
   - Run `python3 -m py_compile skills/<skill-name>/evals/grade_benchmark.py` when the skill ships a grader.
   - Run `python3 skills/<skill-name>/evals/grade_benchmark.py skills/<skill-name>-workspace/<iteration-dir>` when benchmark artifacts exist.
   - If the user wants a packaged archive, run `PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name> /tmp/skill-dist`.
   - Run `./scripts/copilot-install.sh` after source edits so installed skills, references, hooks, and instructions stay in sync.

## Specific Techniques

### Duplicate control

- Compare the requested skill against existing names, descriptions, and nearby workflows before creating a new directory.
- If the only meaningful change is tighter triggering, better evals, or clearer wording, update the existing skill instead of creating a sibling duplicate.
- When you decide to reuse or refine an existing skill, name the closest existing skill explicitly and explain why it is a better fit than creating a new one.
- Reuse [./templates/skill-anatomy.md](./templates/skill-anatomy.md) as structure, not as copy source. Keep the reference deduped by avoiding verbatim prose unless a short quote is truly necessary.

### Weaker-model guardrails

- Prefer short numbered steps over prose paragraphs.
- Name the exact files to create or edit.
- Explain validation selection in order: infer the edited surface first, then choose the matching validation command. Do not fall back to generic `npm test` or other repo-wide commands that do not exist here.
- Keep the core workflow in `SKILL.md`. Move bulky examples or long supporting material into bundled files only when they materially improve reliability.

### Benchmarking guidance

- For live `copilot -p` benchmark runs, point the prompt at the exact local `skills/<skill>/SKILL.md` or snapshot path and tell the model to ignore other installed copies of the same skill name.
- Save response and transcript artifacts before grading so `evals/grade_benchmark.py` and `aggregate_benchmark.py` have stable inputs.
- For a brand-new skill, compare against `without_skill`. For a modified skill, compare against an explicit `old_skill` or snapshot baseline.
- When you document workspace layout, show the abstract pattern `skills/<skill>-workspace/iteration-N/` and, when helpful, a concrete example for the skill you are editing.
- Prefer assertions that catch flattering but shallow drafts: missing negative cases, copied reference prose, absent baseline, or missing refresh/validation commands.

## Common Rationalizations

| Rationalization                                              | Reality                                                                                                                |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| "This is only a small skill edit, so I can skip eval work."  | Small description or structure changes often break triggering and benchmark behavior first. Keep evals current.        |
| "I can just paste the anatomy reference into the skill."     | That bloats context and duplicates repo references. Reuse the section structure and only inline what changes behavior. |
| "The repo probably has a generic test command."              | It does not. Choose the narrow validation command that matches the changed files.                                      |
| "A baseline is optional because the new draft looks better." | Without a baseline, you cannot show the skill actually improves outcomes instead of just adding instructions.          |

## Red Flags

- The description reads like a workflow summary instead of a trigger description.
- `SKILL.md` duplicates long passages from [./templates/skill-anatomy.md](./templates/skill-anatomy.md) or nearby skills.
- The skill says "run the usual tests" or invents generic frontend commands.
- Evals cover only happy paths and never test duplicate avoidance or weaker-model behavior.
- Benchmark artifacts are written inside `skills/<skill>/` instead of the sibling workspace.

## Verification

After completing the workflow, confirm:

- [ ] The skill request was classified as create vs modify, and duplicate checking happened before new files were added.
- [ ] `skill-creator` was invoked and [./templates/skill-anatomy.md](./templates/skill-anatomy.md) was used as the drafting template.
- [ ] The final `SKILL.md` is concise, trigger-oriented, and follows the anatomy section pattern.
- [ ] `evals/evals.json` covers create, modify, and at least one dedupe or negative case.
- [ ] `evals/grade_benchmark.py` exists when deterministic grading is practical, and its syntax is valid.
- [ ] The narrow repo validation commands were run, and `./scripts/copilot-install.sh` refreshed installed copies after edits.
