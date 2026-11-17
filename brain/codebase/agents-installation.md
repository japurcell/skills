# Agent installation

- Edit canonical top-level Markdown in `agents/`.
- Give every agent a nonempty `name` and `description` in frontmatter. Empty quoted values do not satisfy this authoring requirement even if a converter accepts them.
- `scripts/install-codex-agents.py` owns its manifest-listed outputs. Preserve unmanaged custom agents.
- A source edit does not update the installed agent; explicit reinstall is the deployment boundary.
- Author agent bodies as execution guidance: specify the expected output shape and decision criteria.

Evidence: [Codex agent installer](../../scripts/install-codex-agents.py), checked 2026-10-20. Recheck when schema or owned-file handling changes.
