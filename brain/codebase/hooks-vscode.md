# VS Code hook compatibility

- Copilot CLI and VS Code are separate delivery surfaces. A CLI fixture does not prove VS Code event or output behavior.
- Before changing a VS Code hook, inspect current official event schemas, configuration locations, OS overrides, and any custom-agent opt-in settings.
- Capture VS Code logs and visible context. Where `SubagentStart` is unavailable, verify whether `SessionStart` can cover the required context without claiming equivalent lifecycle behavior.
- Legacy snapshot details are version-sensitive; do not treat removed snapshots as authority.

Source: [VS Code hooks documentation](https://code.visualstudio.com/docs/agent-customization/hooks). Migration reviewed 2026-10-20; exact current VS Code semantics are not independently verified in this migration. Recheck against the deployed extension before use.
