# Cache Rules

Caching is only an optimization. It must never bypass required formatting, verification, safety, or validation.

## Universal Rules

- Cache only successful formatter/verifier runs.
- Never cache formatter or verification failures.
- Cache read/write failures degrade to uncached execution.
- Hash failures disable cache read/write for that run.
- Do not cache sentinel hashes such as `error`.
- Keep GitHub and Gemini cache behavior aligned.

## Format Cache

Default repo-local paths:

```text
.hooks-cache/format/
.hooks-cache/locks/
```

Rules:

- Use post-format content hashes.
- Never write stale pre-format hashes.

Example:

```bash
if [[ -f "$absolute_file" ]]; then
  content_hash="$(file_content_hash "$absolute_file")"
fi
```

## Verify Cache

Default verify cache should live outside the workspace, under a repo-specific state directory:

```text
${XDG_STATE_HOME:-$HOME/.local/state}/<repo-id>-hooks-cache/verify/
${XDG_STATE_HOME:-$HOME/.local/state}/<repo-id>-hooks-cache/locks/
```

Reason: repo-writable processes should not be able to preseed trusted verification hits.

Rules:

- Verify cache entries must include an integrity signature tied to a host-local secret.
- Unsigned or tampered entries are misses.
- Treat `.hooks-cache/verify/` as legacy or test-only unless the repo explicitly uses it.

## Fingerprints

Use SHA-256 only.

```bash
file_content_hash() {
  local file="$1"

  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$file" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$file" | awk '{print $1}'
  else
    return 1
  fi
}
```

If fingerprinting fails, skip cache read/write for that run.

## Test Isolation

Tests should isolate caches:

```bash
HOOK_CACHE_ROOT="$(mktemp -d)"
HOOK_VERIFY_CACHE_ROOT="$(mktemp -d)"
export HOOK_CACHE_ROOT HOOK_VERIFY_CACHE_ROOT
```

Reuse a temp cache only when intentionally testing cache hits.
