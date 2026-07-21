---
name: hooks-design
description: Use when modifying, debugging, reviewing, or extending repository-managed GitHub Copilot CLI hooks under .github/hooks/ or Gemini CLI hooks under .gemini/hooks/. Covers hook response JSON, stdout/stderr discipline, cache behavior, file classification parity, formatter/verifier hooks, tests, and hook runtime failures.
---

# GitHub Copilot and Gemini Hook Maintenance

Maintain repository hook scripts so they are safe, schema-valid, cache-correct, and aligned across:

- GitHub Copilot hooks: `.github/hooks/`
- Gemini CLI hooks: `.gemini/hooks/`

Do not treat `~/.copilot/hooks/` as repository hook configuration.

## Start Here

When asked to change hooks:

1. Identify the repository layout:
   - Split scripts: `format-backend.sh`, `format-frontend.sh`, `verify-backend.sh`, `verify-frontend.sh`
   - Unified scripts: `format.sh`, `verify.sh`
2. Inspect both GitHub and Gemini versions before changing behavior.
3. Preserve platform-specific response schemas.
4. Preserve exact JSON-only `stdout`.
5. Keep file classification, cache keys, and cache invalidation aligned.
6. Treat caches as optimization only.
7. Add or update focused regression tests.
8. Run existing hook tests, or tell the user exactly what to run.
9. Summarize changes, risks, and verification.

## Hard Rules

### Stdout

Hook scripts must write exactly one schema-valid JSON response to `stdout`.

Never write logs, debug output, command traces, audit lines, or dependency diagnostics to `stdout`.

Send non-response output to:

- `stderr`
- `.github/hooks/audit.log`
- `.gemini/hooks/audit.log`

If `stdout` contains non-JSON text, the CLI may fail to parse the hook response.

### Fallback JSON

If `jq` is missing or broken, still emit schema-valid fallback JSON without using `jq`.

Dependency diagnostics go to `stderr`.

### Entrypoint Stability

Do not casually change:

- `.github/hooks/hooks.json`
- `.gemini/settings.json`

Only change event registration when explicitly requested.

### GitHub/Gemini Parity

When changing any of these for one platform, make the equivalent change for the other:

- file classification
- cache keys
- cache invalidation
- file fingerprints
- verification scope
- response shape, where schemas allow
- lock behavior
- failure behavior

Use the layout that already exists. Do not invent a new script layout unless asked.

## Read More When Needed

- Response schemas and exits: `references/schemas-and-exits.md`
- Cache rules: `references/cache.md`
- Formatter/verifier procedures: `references/procedures.md`
- Platform-specific gotchas: `references/platform-gotchas.md`
- Bash and dependency rules: `references/bash-and-deps.md`
- Testing and review checklist: `references/testing-checklist.md`

## Official References

Consult only when event behavior or schema details are unclear:

- GitHub Copilot hooks reference: `https://docs.github.com/en/copilot/reference/hooks-reference`
- GitHub Copilot hooks article body: `https://docs.github.com/api/article/body?pathname=/en/copilot/reference/hooks-reference`
- Gemini CLI hooks reference: `https://geminicli.com/docs/hooks/`
- Gemini CLI writing hooks guide: `https://geminicli.com/docs/hooks/writing-hooks/`
- Gemini CLI exit-code guidance: `https://geminicli.com/docs/hooks/best-practices/#check-exit-codes`
