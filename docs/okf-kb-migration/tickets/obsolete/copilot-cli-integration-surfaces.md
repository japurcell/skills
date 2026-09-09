# Copilot CLI Integration Surfaces

**Type:** research
**Status:** obsolete
**Blocked By:** none
**Research Dir:** ../research/copilot-cli-integration-surfaces

## Question

Which currently supported GitHub Copilot CLI surfaces can perform deterministic per-prompt OKF context selection for the standard CLI experience, and what documented guarantees and limitations does each surface have for prompt identity, context injection, pre-model denial, workspace identity, failure handling, privacy, offline operation, and dependency requirements?

---

<!-- Resolution will be appended here -->

## Resolution

Current official GitHub sources establish that a repository-scoped Copilot CLI extension is the strongest integration boundary that preserves the normal interactive CLI experience. It can register `onUserPromptSubmitted`, receive one submitted prompt plus the working directory, and add hidden context using the SDK bundled with the CLI. It avoids both the discarded output of config-file `userPromptSubmitted` hooks and the batched-message ambiguity of `userPromptTransformed`.

The extension cannot reject a submitted prompt before model inference. It can atomically fall back to legacy context and deny subsequent tool calls, but any stronger prompt-admission guarantee requires a separate SDK-hosted application or a future native capability. Extensions are currently experimental, so enrollment must be capability-tested against the actual target build. The main agent performed this research because no subagent-spawn capability was available in the session. See [the research report](../../research/copilot-cli-integration-surfaces.md).
