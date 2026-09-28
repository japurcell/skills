# Repository OKF Hook Capabilities

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/repository-okf-hook-capabilities

## Question

Which supported repository-local hook mechanisms in current Copilot CLI and VS Code, Gemini CLI, and Codex CLI can run repository OKF lint after an agent turn or at session end? Verify event timing, project versus user scope, trust and installation rules, output and enforcement contracts, and supported platforms from official sources. State any provider gap without assuming a user-global hook is repository-local.

---

## Resolution

Research recorded in [repository OKF hook findings](../research/repository-okf-hook-capabilities/findings.md). All four local surfaces have a repository-local turn-end hook suitable for running OKF lint and asking the agent to continue: Copilot CLI `agentStop`, VS Code Local `Stop`, Gemini CLI `AfterAgent`, and Codex CLI `Stop`. Their configuration, trust, and output contracts differ. Session-end events are absent in VS Code Local or advisory/best-effort in the other providers, so they cannot serve as a reliable repair gate. Minimum installed versions and worktree/headless behavior remain unverified and require live probes before deployment.
