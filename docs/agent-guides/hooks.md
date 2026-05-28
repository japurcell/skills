# Hooks Implementation Guidance

When creating or modifying hooks:

- [ ] Always read official documentation first
- [ ] Cite official documentation references when planning and implementing

## GitHub Copilot

Applies to `.copilot/hooks/**`.

There are differences between Copilot CLI and VS Code hook definitions that must be preserved. In `.copilot/hooks/hooks.json`, keep both `subagentStart` (CLI) and `SubagentStart` (VS Code). For response payloads, CLI returns top-level `additionalContext`, while VS Code returns `hookSpecificOutput` plus `additionalContext`.

### Copilot CLI

[Official GitHub Copilot Hooks Reference](https://docs.github.com/en/copilot/reference/hooks-reference)

### VS Code GitHub Copilot

[Official Agent hooks in Visual Studio Code](https://code.visualstudio.com/docs/copilot/customization/hooks)

## Gemini CLI

Applies to `.gemini/hooks/**`.

[Gemini CLI Hooks](https://geminicli.com/docs/hooks/)
[Hooks Best Practices](https://geminicli.com/docs/hooks/best-practices/)
[Writing Hooks for Gemini CLI](https://geminicli.com/docs/hooks/writing-hooks/)
