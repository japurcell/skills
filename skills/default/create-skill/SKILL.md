---
name: create-skill
description: Create or revise portable agent skills with clear triggers, focused instructions, and self-contained resources. Use when creating, modifying, refactoring, or deduplicating a skill or its SKILL.md, or authoring skill evaluations and benchmarks.
---

# Create Skill

## Workflow

1. **Scope the request**
   - Identify the authoritative skill source and the requested write boundary. Read the target project's applicable instructions and conventions.
   - Decide whether this is a new skill or a modification. Preserve an existing directory name and frontmatter `name` unless the user requests a rename.
   - Search available skills for near-duplicate names or overlapping descriptions. Refine a matching skill instead of creating a shadow skill; explain the choice.

2. **Activate authoring guidance**
   - Activate the `skill-creator` skill for the authoring and iteration workflow.
   - Activate the `writing-for-agents` skill for context cost, progressive disclosure, pointers, and focused edits.

3. **Draft or revise the skill**
   - Before pruning or restructuring, map every behavioral obligation to its replacement. Preserve explicit exclusions, conditions, approval requirements, and actionable task verification unless removal is authorized.
   - Write invocation instructions as “activate the `<name>` skill” or “activate the `<name>` and `<name>` skills”, including worker instructions.
   - Retain an existing `disable-model-invocation: true` unless a human explicitly approves removing it, for any reason.
   - Keep the description trigger-oriented: state what the skill does and clear `Use when ...` conditions. Keep workflow steps in the body.
   - Keep the body under 500 lines. Keep references one level deep, preferably in an immediate reference directory; link directly from SKILL.md with a loading condition and read needed references completely. References longer than 100 lines MUST start with a table of contents.
   - Keep resources self-contained within the bundle. Refer to other skills through activation language, and derive target-project details from its applicable instructions instead of linking to the author's repository documents.
   - Keep a skill's own maintenance and evaluation instructions in README.md files. When writing or running evaluations and benchmarks is the skill's task, keep that procedure in its runtime instructions and bundled references.
   - Follow the [effective-skills checklist](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#checklist-for-effective-skills). Spell out exact commands and paths when required by the skill's task.

4. **Write and run evaluations**
   - Add or update `evals/evals.json` with at least three realistic scenarios covering creation, modification, and a negative or duplicate-avoidance case.
   - Use deterministic assertions and a grader when the output can be checked objectively. Preserve scenario-specific conditions and malformed/missing-input cases.
   - Benchmark new skills against `without_skill`; compare modified skills against an explicit `old_skill` snapshot. Use a fresh iteration and preserve earlier valid failures.
   - Read [evaluation validation and evidence](references/validation.md) when writing graders, running evaluations, or interpreting benchmarks.
   - Use the target project's existing validation tools and maintained skill's acceptance scope. Resolve tooling from the available skill installation rather than assuming the author's checkout layout.

5. **Review the result**
   - Check that each runtime reference resolves within the bundle and has a distinct loading trigger.
   - Confirm that another project can use the skill without this repository's documents or checkout layout.
   - Preserve unrelated content and report the changed source, verification performed, and any unresolved limits.
