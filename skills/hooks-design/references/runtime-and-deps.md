# Runtime and Dependency Rules

Use regardless of language.

Preserve the existing runtime and invocation style unless asked to migrate.

## Runtime Safety

Rules:

- Validate startup assumptions.
- Handle missing, empty, or malformed `stdin`.
- Keep normal decisions in JSON responses, not crashes.
- Avoid partial or multiple responses.
- Cleanup temp files/locks on errors.
- Expected fail-open paths emit valid JSON and exit successfully.
- Non-zero exits are for true hard setup/runtime failures; emit JSON first when possible.

Watch for:

```text
shell: strict-mode pipelines, unbound vars, stdout logging
python: uncaught exceptions, encoding issues, stdout logging
js/ts: unhandled promises, stdout logging, serialization failures
go/rust/.net: panics/fatal exits, buffered output after JSON
```

## Repository Root Discovery

Tests may copy hooks into temp dirs. Avoid fixed-depth relative paths.

Prefer walking upward from the script path or current directory until finding a marker such as:

```text
.git
.github
.gemini
repo manifest/config
```

Document repo-specific assumptions.

## Locking

Do not require locks only for audit logging; audit logging should degrade safely.

For critical concurrent writes:

- Prefer runtime/platform file locks.
- Otherwise use atomic lock-directory/file creation.
- Always release locks in cleanup/finally/defer.
- Use bounded wait/retry.
- If lock acquisition fails, degrade safely or follow documented repo policy.
- Never let locking cause multiple JSON responses.

## Dependencies

Common infrastructure:

```text
JSON parser/serializer
git
test runner or hook harness
```

Optional helpers:

```text
jq
rtk
```

Common backend/frontend tools:

```text
dotnet
node
npm
npx
```

Missing developer tools usually:

1. write diagnostics to `stderr`
2. write audit log if available
3. emit schema-valid allow/success JSON
4. exit successfully

Block only when explicit repo policy makes the dependency mandatory for safety, security, compliance, or release gating. Document the exception.

## JSON Handling

- Prefer the language’s standard JSON library.
- Centralize response creation.
- Escape strings correctly.
- Test fallback JSON emission when optional helpers are missing.
- Do not build JSON with unsafe string concatenation unless content is static or safely escaped.

## Hashing and Integrity

For hashing, signing, or integrity fingerprints:

- Use SHA-256 or stronger.
- Do not use MD5 or SHA-1.
- If optional hashing fails, degrade safely.
- If hashing is required for a safety/security/compliance/release gate, follow explicit repo policy and document behavior.
