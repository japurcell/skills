# Portable Distribution Methods and Additional Clients

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/portable-methods

## Question

Which portable distribution approaches best cover selected repository-level skills, agents, hooks, and instructions? Investigate Agent Skills and Agent Plugins standards, the Vercel skills CLI, Cursor and OpenCode native mechanisms, and relevant secondary clients. Compare a selective installer, native plugin or extension adapters, npm or release-archive delivery, vendored copies, Git submodules or subtrees, templates, symlinks, and MCP. Distinguish standard-backed interoperability from client-specific or speculative support. Assess team commits versus local installs, reproducibility, updates, removal, dependencies, Windows portability, and executable trust.

## Resolution

Keep committed project copies generated from canonical repository sources as the team default. Use Agent Skills format for skill payloads and Agent Plugins `plugin.json` for the shared skills/MCP subset where clients support it, with client adapters for agents, hooks, rules, and instructions. A selective installer with a committed lock best fits reproducible whole-bundle selection; Vercel's CLI is useful for skills but does not cover the full bundle and its current restore path has experimental reproducibility gaps. See the [research findings](../research/portable-methods/findings.md) for primary-source citations, client boundaries, and the alternatives comparison.

---
