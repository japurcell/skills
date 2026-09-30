---
type: Agent Instruction
description: Rules and conventions for custom agent definitions under `agents/`
---

# Agents Conventions

- Store each custom agent as one top-level regular Markdown file in `agents/`; this is the canonical source for Copilot, Gemini, and Codex.
- Use UTF-8 YAML frontmatter with non-empty `name` and `description`.
- Keep body focused on execution guidance, output shape, and decision criteria.
- Copilot and Gemini receive Markdown copies. Codex receives generated personal TOML at `${CODEX_HOME:-$HOME/.codex}/agents`, owned by `.skills-repo-agents.json`; edit the source and rerun installation instead of editing managed TOML.
- Selected repository installation uses `.codex/agents/*.toml`, `.github/agents/*.agent.md`, and `.gemini/agents/*.md`. Both Codex paths reuse side-effect-free `scripts/canonical_agents.py`; preserve strict frontmatter, name/collision, and validated serialization rules.
- The Codex converter removes only manifest-owned stale outputs and preserves unmanaged personal agents.
- If installed behavior matters after an edit, refresh local copies with `./scripts/install.sh`.
