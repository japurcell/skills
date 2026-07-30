# Testing and Review Checklist

## Test Commands

Run existing hook tests from repo root. Use only commands that exist.

Preferred when available:

```text
rtk bash scripts/test-hooks.sh
```

Other possible repo-specific commands:

```text
npm test
npm run test:hooks
pnpm test
python -m pytest
pytest
go test ./...
dotnet test
cargo test
bash .github/hooks/scripts/format-hooks.test.sh
bash .github/hooks/scripts/verify-hooks.test.sh
```

Do not invent commands. If unsure, tell the user what should be run based on actual repo files.

## Regression Tests

When changing parser, schema, response, dependency, or failure behavior, test affected items:

- exactly one valid JSON response on `stdout`
- no diagnostics on `stdout`
- fallback JSON when optional JSON helper is missing/broken
- payload-first path extraction
- camelCase and snake_case payloads
- `apply_patch` object, stringified object, and raw text
- fallback behavior when payload paths are missing
- GitHub/Gemini parser and classifier parity
- missing developer tools fail open unless repo policy says otherwise
- runtime errors do not corrupt `stdout`
- robust repo-root discovery in copied-hook tests
- cleanup/lock failures do not emit multiple responses

Parser fixture details: `parser-patterns.md`.

## Stdout JSON Helper

Use a repo-appropriate test helper that verifies:

```text
run hook with payload on stdin
capture stdout/stderr separately
assert stdout parses as JSON
assert stdout contains exactly one JSON document
assert diagnostics are absent from stdout
assert expected diagnostics are on stderr or audit log
assert exit behavior matches platform/event expectations
```

## Final Review

Before finishing, verify:

- [ ] Exactly one schema-valid JSON response on `stdout`.
- [ ] Logs/diagnostics go only to `stderr` or audit logs.
- [ ] Optional JSON helper failure still produces fallback JSON.
- [ ] Changed-file parsing uses `stdin` first.
- [ ] Worktree scans are fallback only unless intentional.
- [ ] Formatting edited files has a smoke test proving paths came from `stdin`.
- [ ] GitHub and Gemini parser/classifier/failure behavior are aligned.
- [ ] Side-by-side parity check covered path extraction and file classification.
- [ ] Entrypoint configs were not changed accidentally.
- [ ] Parser was not replaced with an input-discarding stub.
- [ ] `apply_patch` handles object, stringified object, and raw text.
- [ ] Runtime failures do not corrupt `stdout`.
- [ ] Missing developer tools fail open unless repo policy requires blocking.
- [ ] `dotnet test --no-build` is preceded by `dotnet build`.
- [ ] Frontend verifier dependencies include both `npx` and `npm` when required.
- [ ] Relevant tests pass, or user is told exactly what to run.
