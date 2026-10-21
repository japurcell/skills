# VS Code hook compatibility

- Copilot CLI and VS Code are separate delivery surfaces. A CLI fixture does not prove VS Code event or output behavior.
- Before changing a VS Code hook, inspect current official event schemas, configuration locations, OS overrides, and any custom-agent opt-in settings.
- Select the Session Target harness first. The current shared Copilot harness uses the GitHub Copilot reference; Claude and Codex targets use their own formats. Shared configuration locations alone do not establish compatibility.
- Older Local hooks are a migration source: their parser accepts event aliases and nested Claude groups, ignores matcher values, and sends Local payloads. Local `chat.useHooks` and `chat.useClaudeHooks` settings do not configure the shared Copilot harness. Verify the selected harness before reusing any historical event mapping, OS override, or custom-agent opt-in rule.
- Capture VS Code logs and visible context. Where `SubagentStart` is unavailable, verify whether `SessionStart` can cover the required context without claiming equivalent lifecycle behavior.
- Legacy snapshot details are version-sensitive; do not treat removed snapshots as authority.

Source: [VS Code hooks documentation](https://code.visualstudio.com/docs/agent-customization/hooks), harness distinction checked 2026-10-21. This is documentation verification only; recheck the deployed extension and visible delivery before claiming behavior.
