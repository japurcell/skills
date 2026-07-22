# Schemas, Exits, and Timeouts

All handled paths should emit exactly one JSON response on `stdout`.

Use non-zero exits only for true hard setup/runtime failures. If possible, emit valid JSON first.

If `jq` is unavailable, emit hand-written fallback JSON and send diagnostics to `stderr`.

## Gemini CLI

Runtime/setup stop:

```json
{"continue":false,"stopReason":"..."}
```

Validation failure:

```json
{"decision":"deny","reason":"..."}
```

Allow:

```json
{"decision":"allow","reason":"..."}
```

Rules:

- Expected control flow exits `0`.
- Let JSON decide normal allow/deny behavior.
- Reserve exit code `2` for true system-block cases where `stderr` contains the reason.

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

```json
{"additionalContext":"..."}
```

Rules:

- Expected `agentStop`, `subagentStop`, and `postToolUse` paths exit `0`.
- Do not rely on exit code `2` for normal GitHub hook decisions; for many events it is warning-only or does not apply decision schemas.

## Timeout Guidance

Suggested maximums:

- Formatter/style hooks: under 30 seconds
- Lightweight verifier hooks: under 60 seconds
- Heavy build/test suites: 180–300 seconds
- Over 300 seconds only with explicit repo justification

Timeout-safe design:

- Write cache entries only after successful completion.
- Prefer temp files plus atomic rename.
- Treat incomplete cache writes as misses.
- Log to `stderr` or audit logs, not `stdout`.
- Do not rely on timeout as enforcement when the platform fails open on timeout.
