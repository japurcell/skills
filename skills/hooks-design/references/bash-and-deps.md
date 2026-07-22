# Bash and Dependency Rules

## Bash Safety

No top-level `local`.

Invalid:

```bash
local value="bad"
```

Valid:

```bash
value="ok"

my_function() {
  local value="ok"
}
```

Under `set -euo pipefail`, loops and filters may terminate scripts unexpectedly. Functions that process optional matches should return success when empty matches are acceptable.

```bash
filter_files() {
  while IFS= read -r file; do
    :
  done
  return 0
}
```

## Relative Sourcing in Tests

Tests may copy hooks into temp directories. Avoid brittle paths such as:

```bash
../../../common.sh
```

Prefer walking up from the script directory until finding the repo root, such as a directory containing `.git`, `.github`, or `.gemini`.

## Locking

Do not require `flock` only for audit logging. Audit logging should degrade safely without locks.

For cache or critical concurrent writes:

- prefer `flock` when available
- otherwise use a safe `mkdir` lock fallback

```bash
with_dir_lock() {
  local lock_path="$1"
  shift
  local lock_dir="${lock_path}.dirlock"
  local status

  for attempt in $(seq 1 200); do
    if mkdir "$lock_dir" 2>/dev/null; then
      "$@"; status=$?
      rmdir "$lock_dir" 2>/dev/null
      return "$status"
    fi
    sleep 0.1
  done

  echo "failed to acquire lock: $lock_path" >&2
  return 1
}
```

## Dependencies

Common infrastructure tools:

```text
jq
git
rtk
```

Common backend tools:

```text
dotnet
```

Common frontend tools:

```text
npx
npm
```

Missing dependency handling:

1. Write diagnostics to `stderr`.
2. Write to audit log if available.
3. Emit schema-valid JSON to `stdout`.
4. Exit `0` for expected fail-open control flow.

Developer-tool dependencies usually fail open:

- log warning
- emit allow/success JSON
- exit `0`

Examples:

- GitHub `postToolUse`: `{}`
- GitHub `agentStop`/`subagentStop`: `{"decision":"allow","reason":"Skipped: missing dependency ..."}`
- Gemini: `{"decision":"allow","reason":"Skipped: missing dependency ..."}`

Block only when explicit repo policy says the dependency is mandatory for safety, security, compliance, or release gating. Document the exception.

## Hashing

Never use MD5 or SHA-1 for content or identifier hashes.

Avoid:

```text
md5sum
sha1sum
shasum
```

Use SHA-256 explicitly:

```text
sha256sum
shasum -a 256
```
