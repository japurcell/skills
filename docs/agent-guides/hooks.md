# Hooks Implementation Guidance

When creating or modifying hooks:

- [ ] Always read official documentation first
- [ ] Cite official documentation references when planning and implementing
- [ ] If a security hook scans raw tool payloads, expect self-edits of that hook to trip the guard; prefer small transforms from existing files or a temporary allowlist instead of pasting large threat-pattern blocks directly into `apply_patch` or shell heredocs

## GitHub Copilot

Applies to `.copilot/hooks/**`.

There are differences between Copilot CLI and VS Code hook definitions that must be preserved. In `.copilot/hooks/hooks.json`, keep both `subagentStart` (CLI) and `SubagentStart` (VS Code). For response payloads, CLI returns top-level `additionalContext`, while VS Code returns `hookSpecificOutput` plus `additionalContext`.
- For final-response quality validators, prefer `agentStop` over `subagentStop`; `subagentStop` has no matcher support in the Copilot hook reference, and the built-in `general-purpose` agent does not emit `subagentStart` or `subagentStop`.

### Repo-specific hook gotchas

- Keep `.copilot/hooks/scripts/format.sh` in sync with `scripts/test-hooks-format.sh`; that test expects audit-backed logging, formatter command/failure logging, session-event file recovery, rollover, and lock waiting.
- When editing Tool Guard rules or tests that mention dangerous commands, avoid pasting raw threat strings into tool payloads; construct the exact strings dynamically so the active guard hook does not block the edit itself.

### Copilot CLI

[Official GitHub Copilot Hooks Reference](https://docs.github.com/en/copilot/reference/hooks-reference)

### VS Code GitHub Copilot

[Official Agent hooks in Visual Studio Code](https://code.visualstudio.com/docs/copilot/customization/hooks)

## Gemini CLI

Applies to `.gemini/hooks/**`.

- For final-response quality validators, prefer `AfterAgent` over `AfterModel`; use `prompt_response` as the text under review and `stop_hook_active` to avoid retry loops.

[Gemini CLI Hooks](https://geminicli.com/docs/hooks/)
[Gemini CLI Hooks Reference](https://geminicli.com/docs/hooks/reference/)
[Hooks Best Practices](https://geminicli.com/docs/hooks/best-practices/)
[Writing Hooks for Gemini CLI](https://geminicli.com/docs/hooks/writing-hooks/)
