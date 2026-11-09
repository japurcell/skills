---
name: create-skill
description: Create or revise portable agent skills with clear triggers, focused instructions, and self-contained resources. Use when creating, modifying, refactoring, or deduplicating a skill or its SKILL.md, or authoring skill evaluations and benchmarks.
---

# Create Skill

## Core Principles

### Concise is key

The context window is a public good. A Skill shares the context window with everything else an agent needs, including:

- The system prompt
- Conversation history
- Other Skills’ metadata
- The user request

Being concise in SKILL.md matters: once an agent loads it, every token competes with conversation history and other context. So keep SKILL.md and its associated resources as concise as possible while preserving intended behavior.

**Default assumption**: The agent is already very smart

Only add context the agent doesn’t already have. Challenge each piece of information:

- “Does the agent really need this explanation?”
- “Can I assume the agent has this information?”
- “Does this paragraph justify its token cost?”

## Workflow

1. **Scope the request**
   - Identify the authoritative skill source and the requested write boundary. Read the target project's applicable instructions and conventions.
   - For a new skill, match the frontmatter `name` to the bundle directory. For a revision, preserve both names unless the user requests a rename.
   - Search available skills for near-duplicate names or overlapping descriptions. Refine a matching skill instead of creating a shadow skill; explain the choice.

2. **Activate authoring guidance**
   - Activate the `skill-creator` skill for the authoring and iteration workflow.
   - When drafting or changing agent-facing guidance, activate the `writing-for-agents` skill. Skip it when the change is confined to evaluation fixtures or graders.

3. **Draft or revise the skill**
   - Before pruning or restructuring, map every behavioral obligation to its replacement. Preserve explicit exclusions, conditions, approval requirements, and actionable task verification.
   - Write invocation instructions as “activate the `<name>` skill” or “activate the `<name>` and `<name>` skills”, including worker instructions.
   - Retain an existing `disable-model-invocation: true` unless a human explicitly approves removing it. If a validator rejects the field, check its allowlist against the target host's documented support and report the mismatch.
   - Consult the [Claude Code frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference) when choosing invocation controls and argument hints. Use documented field names and account for differences in other target hosts. Additionally, include `arguments`, `allowed-tools`, `disallowed-tools`, `compatibility` and any other helpful fields when known.
   - When adding or revising an `argument-hint`, read [argument hints](references/argument-hints.md) for invocation syntax and YAML quoting.
   - Keep the description trigger-oriented: state what the skill does and clear `Use when ...` conditions. Keep workflow steps in the body.
   - Keep the body under 200 lines. Keep references one level deep, preferably in an immediate reference directory; link directly from SKILL.md with a loading condition and read needed references completely. References longer than 100 lines MUST start with a table of contents.
   - Keep resources self-contained within the bundle. Refer to other skills through activation language, and derive target-project details from its applicable instructions instead of linking to the author's repository documents.
   - Keep a skill's own maintenance and evaluation instructions in README.md files. When writing or running evaluations and benchmarks is the skill's task, keep that procedure in its runtime instructions and bundled references.
   - Follow the [effective-skills checklist](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#checklist-for-effective-skills). Spell out exact commands and paths when required by the skill's task.
   - **Extract deterministic logic into skill-bundled scripts when it would otherwise be rewritten repeatedly or when a script materially improves reliability.** Reuse existing tools and commands directly when they already meet the task's needs. Scripts can run without loading their source into context, reducing context use and repeated inference. Follow CLI design best practices, provide actionable errors and clear usage documentation, and document required packages and verify their availability.

4. **Write and run evaluations**
   - Add or update `evals/evals.json` with at least three realistic scenarios covering creation, modification, and a negative or duplicate-avoidance case.
   - Use deterministic assertions and a grader when the output can be checked objectively. Preserve scenario-specific conditions and malformed/missing-input cases.
   - Benchmark new skills against `without_skill`; compare modified skills against an explicit `old_skill` snapshot. Use a fresh iteration and preserve earlier valid failures.
   - Read [evaluation validation and evidence](references/validation.md) when writing scenarios or graders, running evaluations, or interpreting benchmarks.
   - Use the target project's existing validation tools and maintained skill's acceptance scope. Resolve tooling from the available skill installation rather than assuming the author's checkout layout.

5. **Review the result**
   - Check that each runtime reference resolves within the bundle and has a distinct loading trigger.
   - Confirm that another project can use the skill without this repository's documents or checkout layout.
   - Preserve unrelated content and report the changed source, verification performed, and any unresolved limits.
