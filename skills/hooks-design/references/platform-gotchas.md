# Platform Gotchas

Use only when editing affected events, schemas, or parsers.

## GitHub Copilot Payload Casing

Copilot payloads may appear as either:

- camelCase event/field names: `sessionStart`, `postToolUse`, `sessionId`, `toolArgs`, `toolName`
- PascalCase events with snake_case fields: `SessionStart`, `PostToolUse`, `session_id`, `tool_input`, `tool_name`

When a repo supports both, parse both consistently. See `parser-patterns.md`.

## Gemini `BeforeToolSelection`

When configuring Gemini `BeforeToolSelection`, confirm current Gemini docs.

Important gotcha:

- matched hook rules may aggregate
- disabling all tools requires explicit `mode: "NONE"` where supported
