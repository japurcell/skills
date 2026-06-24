# Authoring rules

## Skills

- Use `SKILL.md` as the entry point for each skill.
- Start `SKILL.md` with YAML frontmatter.
- Keep `name` lowercase kebab-case.
- Keep `description` concrete and trigger-oriented.
- Use imperative instructions in the body.
- For weaker models, spell out verification selection in order: infer the slice's surface and stack first, then choose matching test/build/manual checks instead of defaulting to generic frontend commands.
- Keep bundled resources next to the skill instead of scattering supporting files elsewhere.
- Put generated evaluation output in a sibling `*-workspace/` directory unless the repository already treats it as a checked-in fixture.
- For large-skill refactors, change only skills you own or have explicit approval to modify; in this harness-process-improvements program, treat `skills/gh-cli` and `skills/skill-creator` as excluded from splitting or similar structural refactors unless explicit approval is granted, and preserve top-level triggerability and workflow clarity for any later approved refactor.

## Agents

- Store each custom agent as a single Markdown file in `agents/`.
- Use YAML frontmatter with `name` and `description`.
- Keep the body focused on execution guidance, output shape, and decision criteria.

## Helper scripts

- Follow the existing shebang style: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`.
- Keep scripts directly executable and simple.
- Prefer standard-library solutions unless a dependency is already implied by the existing script.

## Refactoring and simplification

- When using `code-simplifier` or similar refactoring help, state intentional path boundaries explicitly (for example `.gemini/` vs `.copilot/`) so required non-standard paths are not "corrected" away.
