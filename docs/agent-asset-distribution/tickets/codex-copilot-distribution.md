# Codex and Copilot Distribution Support

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/codex-copilot

## Question

What officially supported mechanisms distribute skills, custom agents, hooks, and instructions for Codex and GitHub Copilot, including CLI, desktop, VS Code, and hosted surfaces where behavior differs? Establish repository versus user scope, native plugin compatibility, discovery paths, selection, updates, version pinning, trust, and limits. Separate package location from activation scope and do not infer capabilities across product surfaces.

## Resolution

Official documentation supports a shared skills layer through repository `.agents/skills` and portable Agent Plugins packaging for skills and MCP. Custom agents and hooks remain client-specific: Codex project agents are TOML under `.codex/agents`, Copilot repository profiles use `.github/agents` with `.agent.md` serialization, and hook paths, schemas, runtime, and trust differ. Codex repo plugins use `.agents/plugins/marketplace.json` plus `.codex/config.toml`; Copilot repo activation uses `.github/copilot/settings.json`, with personal overrides in `.github/copilot/settings.local.json`. Copilot cloud only receives committed repository inputs and has distinct hook constraints. Codex hosted-cloud custom asset discovery and cross-client pin/rollback guarantees remain unverified. See [research/codex-copilot/findings.md](../research/codex-copilot/findings.md) for the evidence, surface-by-surface paths, and sources.

---
