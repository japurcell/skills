# Platform Gotchas

Use this only when editing affected events or parsers.

## GitHub Copilot Payload Casing

Some Copilot hook payloads may appear in either style:

- camelCase event/field names, such as `sessionStart`, `preToolUse`, `sessionId`, `toolArgs`, `toolName`
- PascalCase event names with snake_case fields, such as `SessionStart`, `PreToolUse`, `session_id`, `tool_input`, `tool_name`

When a repository supports both, parse both forms consistently.

## Gemini `BeforeToolSelection`

When configuring Gemini `BeforeToolSelection` hooks, confirm current Gemini docs.

Important gotcha:

- matched hook rules may aggregate
- disabling all tools requires the explicit `mode: "NONE"` response/rule where supported
