# Authoring rules

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
