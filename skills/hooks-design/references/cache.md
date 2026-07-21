# Cache Rules

Caching is only an optimization. It must never bypass formatting, verification, safety, or validation.

## Universal Rules

- Cache only successful formatter runs.
- Cache only successful verifier runs.
- Never cache formatter failures.
- Never cache verification failures.
- Cache read/write failures must degrade to normal uncached execution.
- Hash failures disable cache read/write for that run.
- Do not cache sentinel hashes such as `error`.
- GitHub and Gemini cache behavior must remain aligned.

## Format Cache

Default repo-local paths:

```text
.hooks-cache/format/
.hooks-cache/locks/
```

Formatter cache entries must use post-format content hashes.

Do not write stale pre-format hashes.

## Verify Cache

Default verify cache should live outside the workspace, under a repo-specific state directory, for example:

```text
${XDG_STATE_HOME:-$HOME/.local/state}/<repo-id>-hooks-cache/verify/
${XDG_STATE_HOME:-$HOME/.local/state}/<repo-id>-hooks-cache/locks/
```

Reason: repo-writable processes should not be able to preseed trusted verification hits.

Verify cache entries must include an integrity signature tied to a host-local secret.

Unsigned or tampered verify cache entries are misses.

Treat `.hooks-cache/verify/` as legacy or test-only unless the repository explicitly uses it.

## Test Overrides

Tests should isolate caches:

```bash
HOOK_CACHE_ROOT="$(mktemp -d)"
HOOK_VERIFY_CACHE_ROOT="$(mktemp -d)"
export HOOK_CACHE_ROOT HOOK_VERIFY_CACHE_ROOT
```

Reuse one temp cache only in tests that intentionally verify cache-hit behavior.
