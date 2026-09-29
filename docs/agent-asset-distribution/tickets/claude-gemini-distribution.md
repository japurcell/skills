# Claude Code and Gemini Distribution Support

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/claude-gemini

## Question

What officially supported mechanisms distribute skills, custom agents, hooks, and instructions for Claude Code and Gemini CLI? Establish repository versus user scope, plugin or extension packaging, discovery paths, selection, updates, version pinning, trust, prerequisites, and limits. Determine whether their native package formats can share one source or manifest with other clients without implying shared hook runtimes.

## Resolution

Both clients support portable Agent Skills, but agents, instructions, hooks, manifests, and activation are provider-specific. Claude project plugins can be enabled in committed `.claude/settings.json`, though each teammate must install the plugin. Gemini extensions are copied to each user's `~/.gemini/extensions`; workspace enable/disable state belongs in `<repo>/.gemini/settings.json`, so committed activation does not install the extension package. The Agent Plugins standard currently specifies skills and MCP, not shared agent or hook behavior. Gemini's extension-agent preview wording remains unresolved against its core-agent docs and default-enabled experimental setting. Full evidence and source links are in [findings](../research/claude-gemini/findings.md).

---
