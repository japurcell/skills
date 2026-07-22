# Testing and Review Checklist

## Test Commands

Run existing hook tests from repo root. Use only commands that exist.

Preferred when available:

```bash
rtk bash scripts/test-hooks.sh
```

Other possible commands:

```bash
bash .github/hooks/scripts/format-hooks.test.sh
bash .github/hooks/scripts/verify-hooks.test.sh
```

## Cache Isolation

Tests should set isolated cache roots:

```bash
HOOK_CACHE_ROOT="$(mktemp -d)"
HOOK_VERIFY_CACHE_ROOT="$(mktemp -d)"
export HOOK_CACHE_ROOT HOOK_VERIFY_CACHE_ROOT
```

Do not unintentionally share `.hooks-cache/`.

## Regression Tests

When changing parser, cache, schema, response, or failure behavior, add/update focused tests for affected items:

- exactly one valid JSON response on `stdout`
- no diagnostics on `stdout`
- missing/broken `jq` fallback JSON
- payload-first path extraction
- camelCase and snake_case path payloads
- `apply_patch` object, stringified object, and raw string
- fallback behavior when payload paths are missing
- GitHub/Gemini parser and classifier parity
- no caching of formatter/verifier failures
- hash failure disables cache for the run
- signed verify cache tamper detection
- missing developer tools fail open unless repo policy says otherwise
- `set -euo pipefail` loop safety
- robust relative sourcing in copied-hook tests

Parser fixture details are in `parser-patterns.md`.

## Stdout JSON Test Helper

Use a helper like this:

```bash
test_hook_schema() {
  local script_path="$1"
  local payload="${2:-{}}"
  local stdout_output
  local json_count

  stdout_output="$(printf '%s' "$payload" | bash "$script_path" 2>/dev/null)"

  if ! printf '%s' "$stdout_output" | jq -e . >/dev/null 2>&1; then
    echo "FAIL: $script_path did not output valid JSON" >&2
    return 1
  fi

  json_count="$(printf '%s' "$stdout_output" | jq -s 'length' 2>/dev/null)"
  if [[ "$json_count" != "1" ]]; then
    echo "FAIL: $script_path emitted $json_count JSON documents; expected 1" >&2
    return 1
  fi
}
```

For hooks that intentionally write diagnostics, verify diagnostics go to `stderr`.

## Manual Cache Clearing

Repo-local format cache:

```bash
rm -r .hooks-cache/format .hooks-cache/locks
mkdir -p .hooks-cache/format .hooks-cache/locks
```

Legacy repo-local verify cache if used:

```bash
rm -r .hooks-cache/verify
mkdir -p .hooks-cache/verify
```

All repo-local hook cache state:

```bash
rm -r .hooks-cache
```

Default external verify cache, using actual repo cache directory:

```bash
rm -r "${XDG_STATE_HOME:-$HOME/.local/state}/<repo-id>-hooks-cache"
```

## Final Review

Before finishing, verify:

- [ ] Exactly one schema-valid JSON response on `stdout`.
- [ ] Logs and diagnostics go only to `stderr` or audit logs.
- [ ] Missing/broken `jq` still produces fallback JSON.
- [ ] Changed-file parsing uses `stdin` first.
- [ ] Worktree scans are fallback only unless intentionally session/worktree scoped.
- [ ] Formatting edited files has a smoke test proving paths came from `stdin`.
- [ ] GitHub and Gemini parser, classifier, cache, and failure behavior are aligned.
- [ ] Side-by-side parity diff checked path extraction and file classification.
- [ ] Entrypoint configs were not changed accidentally.
- [ ] Parser was not replaced with an input-discarding stub.
- [ ] `apply_patch` handles object, stringified object, and raw string.
- [ ] Failures are not cached.
- [ ] Cache/hash failures degrade safely.
- [ ] Post-format hashes are recalculated before cache writes.
- [ ] Verify cache entries are signed and tamper-checked.
- [ ] No top-level Bash `local`.
- [ ] Loop/filter functions are safe under `set -euo pipefail`.
- [ ] Missing developer tools fail open unless explicit repo policy requires blocking.
- [ ] `dotnet test --no-build` is preceded by `dotnet build`.
- [ ] Frontend verifier dependencies include both `npx` and `npm` when required.
- [ ] Tests use isolated cache roots.
- [ ] Relevant tests pass, or the user is told exactly what to run.
