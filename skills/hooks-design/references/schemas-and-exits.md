# Hook Schemas and Exit Behavior

All handled hook paths should emit exactly one JSON response on `stdout`.

Use non-zero exits only for true hard setup/runtime failures. If possible, still emit valid JSON before exiting.

## Gemini CLI

Runtime/setup error:

```json
{ "continue": false, "stopReason": "..." }
```

Validation failure:

```json
{ "decision": "deny", "reason": "..." }
```

Allow:

```json
{ "decision": "allow", "reason": "..." }
```

Rules:

- Expected hook control flow exits `0`.
- Let JSON decide normal allow/deny behavior.
- Reserve exit code `2` for true system-block cases where `stderr` contains the reason.

## GitHub Copilot CLI

For `agentStop` and `subagentStop`:

```json
{ "decision": "allow", "reason": "..." }
```

```json
{ "decision": "block", "reason": "..." }
```

For `postToolUse` formatting hooks:

```json
{}
```

```json
{ "additionalContext": "..." }
```

Rules:

- Expected `agentStop`, `subagentStop`, and `postToolUse` paths exit `0`.
- Do not rely on exit code `2` for normal GitHub hook decisions; it is warning-only for many events and may not apply decision schemas.
