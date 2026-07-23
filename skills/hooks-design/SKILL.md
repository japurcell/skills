---
name: hooks-design
description: Use when modifying, debugging, reviewing, or extending repository-managed GitHub Copilot CLI hooks in .github/hooks/ or Gemini CLI hooks in .gemini/hooks/. Covers hook JSON responses, stdout/stderr discipline, payload path extraction, GitHub/Gemini parity, caches, formatter/verifier hooks, tests, and runtime failures.
---

# Hook Maintenance: GitHub Copilot and Gemini

Maintain repository hook scripts so they are schema-valid, safe, cache-correct, and behaviorally aligned across:

- GitHub Copilot hooks: `.github/hooks/`
- Gemini CLI hooks: `.gemini/hooks/`

Do not treat `~/.copilot/hooks/` as repository hook configuration.

## Start Here

When changing hooks:

1. Identify the existing layout:
   - split: `format-backend.sh`, `format-frontend.sh`, `verify-backend.sh`, `verify-frontend.sh`
   - unified: `format.sh`, `verify.sh`
2. Inspect both GitHub and Gemini versions before changing behavior.
3. Preserve each platform’s response schema.
4. Emit exactly one JSON response on `stdout`; send logs to `stderr` or audit logs.
5. For changed-file hooks, parse paths from hook `stdin` first. Use `git diff`, `git status`, or worktree scans only as fallback.
6. Keep path extraction, file classification, cache keys, invalidation, and failure behavior aligned across platforms.
7. If parser or classifier behavior changes, update both platforms in the same change unless documenting an explicit exception.
8. Treat caches as optimization only.
9. Add or update focused regression tests for changed parser, cache, schema, or failure behavior.
10. Run existing hook tests, or tell the user exactly what to run.
11. Before finishing, compare GitHub and Gemini path-extraction and file-classification logic side by side.
12. Summarize changes, tests, risks, and any parity exceptions.

## Hard Rules

- `stdout` must contain only one schema-valid JSON response.
- Never write logs, traces, diagnostics, or audit lines to `stdout`.
- If `jq` is missing or broken, still emit fallback JSON without `jq`.
- Do not replace a parser with `cat >/dev/null` or any input-discarding stub unless the hook intentionally ignores input and documents that fact.
- Formatter/verifier hooks must not silently ignore payload paths.
- Do not casually change `.github/hooks/hooks.json` or `.gemini/settings.json`; only change event registration when requested.
- Missing local developer tools should usually fail open: log the problem, emit allow/success JSON, and exit `0`. Block only when explicit repo policy requires it.
- Caches must never bypass required formatting, verification, safety, or validation.

## Read References Only When Needed

- Formatter/verifier workflow: `references/procedures.md`
- Response schemas, exits, and timeouts: `references/schemas-and-exits.md`
- Payload/path parser patterns: `references/parser-patterns.md`
- Cache rules: `references/cache.md`
- Bash/dependency rules: `references/bash-and-deps.md`
- Platform-specific gotchas: `references/platform-gotchas.md`
- Testing/review checklist: `references/testing-checklist.md`

## Official Docs

Consult only when event behavior or schemas are unclear:

- GitHub Copilot hooks: `https://docs.github.com/en/copilot/reference/hooks-reference`
- GitHub article body API: `https://docs.github.com/api/article/body?pathname=/en/copilot/reference/hooks-reference`
- Gemini hooks: `https://geminicli.com/docs/hooks/`
- Gemini writing hooks: `https://geminicli.com/docs/hooks/writing-hooks/`
- Gemini exit codes: `https://geminicli.com/docs/hooks/best-practices/#check-exit-codes`
- Gemini tools: `https://geminicli.com/docs/reference/tools/`
