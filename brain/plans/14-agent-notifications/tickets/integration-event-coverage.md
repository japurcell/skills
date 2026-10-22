# Integration event coverage

**Type:** research
**Status:** closed
**Claimed By:** subagent-hooks
**Blocked By:** none
**Research Dir:** ../research/integration-event-coverage

## Question

Which supported hooks/APIs invoke a local CLI from Codex desktop and CLI, Copilot CLI and VS Code, and Gemini CLI?

Build a primary-source matrix for success, failure, input, approval, cancellation, and externally reported stalls. Distinguish turn/session end from proven success/failure. Report absent signals honestly; app-side monitoring/stall detection is excluded. Inspect relevant repository notes/config, then verify current primary docs/source. Activate openai-docs for Codex; local evidence first, official OpenAI web fallback. Explain WSL/SSH/container local-only delivery boundaries. Recommend a minimal event envelope without finalizing syntax. No real hook changes/installations.

---

## Resolution

The coverage matrix and limitations are documented in [integration event coverage findings](../research/integration-event-coverage/findings.md). Copilot CLI provides the clearest command-hook signals for errors, permission prompts, and user elicitation. Codex app-server provides explicit turn outcomes for clients that own the session; Codex hooks and `notify` do not provide a portable turn result. Gemini has no dedicated turn-failure or cancellation hook. None reports stalls, so only externally reported stall events should be represented.
