---
name: hooks-design
description: Use when modifying, debugging, reviewing, or extending repository-managed GitHub Copilot CLI hooks in .github/hooks/ or Gemini CLI hooks in .gemini/hooks/. Covers hook JSON responses, stdout/stderr discipline, payload path extraction, GitHub/Gemini parity, formatter/verifier hooks, tests, dependencies, and runtime failures. Language agnostic.
---

# Hook Maintenance: GitHub Copilot and Gemini

Use for repo hooks in:

- `.github/hooks/`
- `.gemini/hooks/`

Do **not** treat `~/.copilot/hooks/` as repo hook config.

Hooks may be shell, Python, JavaScript/TypeScript, Go, Rust, .NET, binaries, or wrappers. Preserve the repo’s existing language, filenames, config, and invocation style unless asked to change them.

## Workflow

1. Identify the existing layout:
   - split: `format-backend`, `format-frontend`, `verify-backend`, `verify-frontend`
   - unified: `format`, `verify`
2. Inspect both GitHub and Gemini versions before changing behavior.
3. Preserve each platform’s response schema.
4. Emit exactly one JSON response on `stdout`.
5. Send logs, traces, diagnostics, progress, and audit lines to `stderr` or an audit log.
6. For changed-file hooks, parse paths from hook `stdin` first.
7. Use `git diff`, `git status`, or scans only as fallback, unless the hook is intentionally session/worktree scoped.
8. Keep path extraction, file classification, skip logic, dependency handling, and failures aligned across platforms.
9. Update both platforms for parser/classifier changes unless documenting an explicit exception.
10. Add/update focused regression tests.
11. Run existing hook tests, or tell the user exactly what to run.
12. Before finishing, compare GitHub and Gemini path/classifier logic side by side.
13. Summarize changes, tests, risks, and parity exceptions.

## Hard Rules

- `stdout` contains only one schema-valid JSON response.
- Never write diagnostics to `stdout`.
- Preserve platform-specific response schemas, even with shared logic.
- Do not replace a parser with an input-discarding stub unless intentional and documented.
- Formatter/verifier hooks must not silently ignore payload paths.
- Do not casually change `.github/hooks/hooks.json` or `.gemini/settings.json`.
- Missing local developer tools usually fail open: log, emit allow/success JSON, exit successfully.
- Block only when explicit repo policy requires it.
- Do not depend exclusively on optional JSON tools such as `jq`; emit fallback valid JSON when possible.
- Use SHA-256 or stronger for hashing/signing/integrity. Do not use MD5 or SHA-1.

## References

Read only what you need:

- Formatter/verifier flow: `references/procedures.md`
- Schemas, exits, timeouts: `references/schemas-and-exits.md`
- Payload/path parsing: `references/parser-patterns.md`
- Runtime/dependencies: `references/runtime-and-deps.md`
- Platform gotchas: `references/platform-gotchas.md`
- Testing/review: `references/testing-checklist.md`

## Official Docs

Use when event behavior or schemas are unclear:

- GitHub Copilot hooks: <https://docs.github.com/en/copilot/reference/hooks-reference>
- Gemini hooks: <https://geminicli.com/docs/hooks/>
- Gemini writing hooks: <https://geminicli.com/docs/hooks/writing-hooks/>
- Gemini exit codes: <https://geminicli.com/docs/hooks/best-practices/#check-exit-codes>
- Gemini tools: <https://geminicli.com/docs/reference/tools/>
