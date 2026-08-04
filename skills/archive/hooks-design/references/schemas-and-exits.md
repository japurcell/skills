# Schemas, Exits, and Timeouts

Every handled path should emit exactly one JSON response on `stdout`.

Use non-zero exits only for true hard setup/runtime failures. Emit valid JSON first when possible.

Diagnostics go to `stderr` or audit logs, never `stdout`.

## Gemini CLI

Runtime/setup stop:

```json
{"continue":false,"stopReason":"..."}
```

Validation failure:

```json
{"decision":"deny","reason":"..."}
```

Allow/skip/pass:

```json
{"decision":"allow","reason":"..."}
```

Rules:

- Expected control flow exits successfully.
- Use JSON for normal allow/deny decisions.
- Reserve exit code `2` for true system-block cases where `stderr` contains the reason.
- Do not use process failure for ordinary validation when a response schema applies.

## GitHub Copilot CLI

For `agentStop` and `subagentStop`:

```json
{"decision":"allow","reason":"..."}
```

```json
{"decision":"block","reason":"..."}
```

For `postToolUse` formatting hooks:

```json
{}
```

or:

```json
{"additionalContext":"..."}
```

Rules:

- Expected `agentStop`, `subagentStop`, and `postToolUse` paths exit successfully.
- Do not rely on exit code `2` for normal GitHub decisions.
- Preserve the exact response shape expected for the configured event.

## Missing Dependency Responses

Missing developer tools usually fail open.

Examples:

```json
{}
```

```json
{"decision":"allow","reason":"Skipped: missing dependency ..."}
```

Use the platform/event-appropriate schema.

## Timeouts

Suggested maximums:

```text
format/style:       < 30s
light verification: < 60s
heavy build/test:   180-300s
>300s:              requires repo justification
```

Timeout-safe design:

- Do not leave partial hook-owned temp files.
- Do not rely on timeout as enforcement if the platform fails open.
- Cleanup handlers must not emit a second JSON response.
