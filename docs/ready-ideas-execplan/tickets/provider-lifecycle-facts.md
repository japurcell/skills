# Provider Lifecycle Facts

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/provider-lifecycle-facts

## Question

Using current official Copilot CLI, Gemini CLI, and Codex CLI hook documentation, identify all available lifecycle events, which events can fire once per tool or more often, and which documented response fields produce user-visible system or progress messages. Record timeout, output, and provider-surface limits relevant to sparse notification and latency decisions. Treat the installed `load-required-skills` messages reported by the user as live evidence, not a blanket guarantee for other events.

---

## Resolution

[Research findings](../research/provider-lifecycle-facts/provider-lifecycle-facts.md) map current first-party event coverage, high-rate event paths, user-visible fields, timeouts, output limits, and CLI versus cloud surface differences. Use provider-specific message contracts: Copilot CLI progress JSON lines, Gemini `systemMessage` on supported events, and Codex `statusMessage` during execution or `systemMessage` as a warning. The user's visible `load-required-skills` output is observed evidence for that hook only. Gemini's hook stdout size limit and cross-event renderer behavior remain unverified; prove sparse notifications and latency in live CLIs before implementation promises.
