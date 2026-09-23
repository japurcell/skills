# Provider Hook Capabilities

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/provider-hook-capabilities

## Question

What do current official Copilot CLI and VS Code, Gemini CLI, and Codex hook contracts permit at user scope for intercepting file and shell actions, reporting denials or warnings visibly, and running on Windows? Record event names, output fields, timeouts, and limitations that affect Ready items 2, 3, and 4. Cite primary sources and distinguish documented support from inference.

---

## Resolution

Findings: [provider hook capabilities](../research/provider-hook-capabilities/findings.md).
Official contracts establish user-scope interception for file and shell actions
in Copilot CLI (`preToolUse`), VS Code (`PreToolUse`), Gemini CLI
(`BeforeTool`), and Codex (`PreToolUse`). They also document provider-specific
visible denial or warning channels and Windows command overrides. The plan must
preserve the material differences: Copilot timeouts are explicitly fail-open;
Gemini timeouts are millisecond-valued (60,000 default); Codex has a
600-second general default and incomplete local-tool coverage; VS Code ignores
invalid rewritten tool input. Primary links: [Copilot](https://docs.github.com/en/copilot/reference/hooks-reference), [VS Code](https://code.visualstudio.com/docs/agents/reference/hooks-reference), [Gemini](https://geminicli.com/docs/hooks/reference/), [Codex](https://developers.openai.com/codex/hooks).
