# Agent installation

- Edit canonical top-level Markdown in `agents/`.
- Give every agent a nonempty `name` and `description` in frontmatter. Empty quoted values do not satisfy this authoring requirement even if a converter accepts them.
- Copilot and Gemini receive copies. Codex receives generated TOML in `CODEX_HOME/agents` or `~/.codex/agents`.
- `scripts/install-codex-agents.py` owns its manifest-listed outputs. Preserve unmanaged custom agents.
- A source edit does not update the installed agent; explicit reinstall is the deployment boundary.
- Test generation and upgrade behavior with `scripts/test-codex-agents.py` and isolated installer fixtures.
- Author agent bodies as execution guidance: specify the expected output shape and decision criteria.

Evidence: [Codex agent installer](../../scripts/install-codex-agents.py), checked 2026-10-20. Recheck when schema or owned-file handling changes.
