# Authoring rules

## Skills

- Use `SKILL.md` as the entry point for each skill.
- Start `SKILL.md` with YAML frontmatter.
- Keep `name` lowercase kebab-case.
- Keep `description` concrete and trigger-oriented.
- Use imperative instructions in the body.
- Keep bundled resources next to the skill instead of scattering supporting files elsewhere.
- Put generated evaluation output in a sibling `*-workspace/` directory unless the repository already treats it as a checked-in fixture.

## Agents

- Store each custom agent as a single Markdown file in `agents/`.
- Use YAML frontmatter with `name` and `description`.
- Keep the body focused on execution guidance, output shape, and decision criteria.

## Helper scripts

- Follow the existing shebang style: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`.
- Keep scripts directly executable and simple.
- Prefer standard-library solutions unless a dependency is already implied by the existing script.
