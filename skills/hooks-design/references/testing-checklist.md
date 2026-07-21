# Testing and Review Checklist

## Test Commands

Run the repository’s existing hook tests from the repo root.

Preferred command when available:

```bash
rtk bash scripts/test-hooks.sh
```

Other possible commands:

```bash
bash .github/hooks/scripts/format-hooks.test.sh
bash .github/hooks/scripts/verify-hooks.test.sh
```

Use only commands that exist in the repository.

## Cache Isolation in Tests

Tests should set isolated cache roots:

```bash
HOOK_CACHE_ROOT="$(mktemp -d)"
HOOK_VERIFY_CACHE_ROOT="$(mktemp -d)"
export HOOK_CACHE_ROOT HOOK_VERIFY_CACHE_ROOT
```

Do not let tests unintentionally share `.hooks-cache/`.

## Regression Tests

When changing parser, cache, schema, or response behavior, add/update focused tests for:

- missing `jq` fallback JSON
- no `stdout` pollution
- hash-failure cache invalidation
- no caching of formatter failures
- no caching of verification failures
- signed verify cache tamper detection
- `apply_patch` payload as object
- `apply_patch` payload as stringified object
- `apply_patch` payload as raw string
- `set -euo pipefail` loop behavior
- robust relative sourcing in copied hook tests

## Manual Cache Clearing

Clear repo-local format cache and locks:

```bash
rm -r .hooks-cache/format .hooks-cache/locks
mkdir -p .hooks-cache/format .hooks-cache/locks
```

Clear legacy repo-local verify cache if used:

```bash
rm -r .hooks-cache/verify
mkdir -p .hooks-cache/verify
```

Clear all repo-local hook cache state:

```bash
rm -r .hooks-cache
```

Clear default external verify cache, using the repository's actual cache directory:

```bash
rm -r "${XDG_STATE_HOME:-$HOME/.local/state}/<repo-id>-hooks-cache"
```

## Final Review

Before finishing, verify:

- [ ] Exactly one JSON response is emitted on `stdout`.
- [ ] Logs and diagnostics go only to `stderr` or audit logs.
- [ ] Missing or broken `jq` still produces valid fallback JSON.
- [ ] GitHub and Gemini file classification are aligned.
- [ ] GitHub and Gemini cache behavior are aligned.
- [ ] Entrypoint configs were not changed accidentally.
- [ ] `apply_patch` extraction handles object, stringified object, and raw string forms.
- [ ] Formatter failures are not cached.
- [ ] Verification failures are not cached.
- [ ] Cache failures degrade to uncached execution.
- [ ] Hash failures disable cache for the run.
- [ ] Post-format hashes are recalculated before cache writes.
- [ ] Verify cache entries are signed and tamper-checked.
- [ ] No top-level Bash `local` declarations exist.
- [ ] Loop/filter functions are safe under `set -euo pipefail`.
- [ ] Missing dependency paths write diagnostics to `stderr`.
- [ ] `dotnet test --no-build` is preceded by `dotnet build`.
- [ ] Frontend verifier dependencies include both `npx` and `npm` when required.
- [ ] Tests use isolated cache roots.
- [ ] Relevant hook tests pass, or the user is told exactly what to run.
