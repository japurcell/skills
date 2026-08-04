---
coverage: Rules and conventions for custom agent definitions under `agents/`
---

# Agents Conventions

- Store each custom agent as one Markdown file in `agents/`.
- Use YAML frontmatter with `name` and `description`.
- Keep body focused on execution guidance, output shape, and decision criteria.
- If installed behavior matters after an edit, refresh local copies with `./scripts/install.sh`.
