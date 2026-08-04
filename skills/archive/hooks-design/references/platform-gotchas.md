# Platform Gotchas

Use only when editing affected events, schemas, or parsers.

## Payload Casing

Some hook payloads may use either style:

```text
camelCase:  sessionStart, postToolUse, sessionId, toolArgs, toolName, filePath
Pascal/snake: SessionStart, PostToolUse, session_id, tool_input, tool_name, file_path
```

When a repo supports both, parse both consistently. See `parser-patterns.md`.

## Gemini `BeforeToolSelection`

Confirm current Gemini docs before changing this event.

Gotchas:

- Matched hook rules may aggregate.
- Disabling all tools requires explicit `mode: "NONE"` where supported.

## Shared Logic

It is OK to share parser, classifier, formatter, and verifier logic.

Still keep separate platform behavior for:

- response JSON schema
- event semantics
- exit behavior
- platform-specific tests
