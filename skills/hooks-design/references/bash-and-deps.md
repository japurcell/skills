# Bash and Dependency Rules

## No Top-Level `local`

Invalid:

```bash
local value="bad"
```

Valid at top level:

```bash
value="ok"
```

Valid inside functions:

```bash
my_function() {
  local value="ok"
}
```

## `set -euo pipefail`

Under `set -euo pipefail`, loops and filters may accidentally terminate scripts.

Functions that process optional matches should end with success when appropriate:

```bash
filter_files() {
  while IFS= read -r file; do
    :
  done
  return 0
}
```

or:

```bash
true
```

## Relative Sourcing in Tests

Tests may copy hook scripts into temporary directories.

Avoid brittle paths such as:

```bash
../../../common.sh
```

Prefer walking up from the script directory until finding the repository root, such as a directory containing `.git` or `.github`.

## Audit Locking

Do not hard-require `flock` only for audit logging.

Audit helpers should degrade safely when locking is unavailable.

For cache or critical concurrent writes:

- prefer `flock` when available
- use a safe `mkdir` lock fallback when needed

Example fallback:

```bash
with_dir_lock() {
  local lock_path="$1"
  shift
  local lock_dir="${lock_path}.dirlock"
  local status

  for attempt in $(seq 1 200); do
    if mkdir "$lock_dir" 2>/dev/null; then
      if "$@"; then
        status=0
      else
        status=$?
      fi
      rmdir "$lock_dir" 2>/dev/null
      return "$status"
    fi
    sleep 0.1
  done

  echo "failed to acquire lock: $lock_path" >&2
  return 1
}
```

## Dependency Handling

Common hook infrastructure tools:

```bash
jq
git
rtk
```

Backend verifier tools may include:

```bash
dotnet
```

Frontend verifier tools may include both:

```bash
npx
npm
```

Missing dependency handling must preserve JSON discipline:

1. Write diagnostic to `stderr`.
2. Emit schema-valid JSON to `stdout`.
3. Exit `0` for expected control flow unless this is a true hard setup/runtime failure.
