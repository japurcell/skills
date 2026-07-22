# Formatter and Verifier Procedures

Use the script layout already present in the repo. Do not invent a new layout unless asked.

Common split layout:

```text
.github/hooks/scripts/format-backend.sh
.github/hooks/scripts/format-frontend.sh
.github/hooks/scripts/verify-backend.sh
.github/hooks/scripts/verify-frontend.sh
.gemini/hooks/scripts/format-backend.sh
.gemini/hooks/scripts/format-frontend.sh
.gemini/hooks/scripts/verify-backend.sh
.gemini/hooks/scripts/verify-frontend.sh
```

Common unified layout:

```text
.github/hooks/scripts/format.sh
.github/hooks/scripts/verify.sh
.gemini/hooks/scripts/format.sh
.gemini/hooks/scripts/verify.sh
```

## Formatter Hooks

Applies to `format*.sh`.

Procedure:

1. Read hook JSON from `stdin`.
2. Extract file paths from `stdin` first.
3. Support both common field styles:
   - camelCase: `toolArgs`, `filePath`, `toolName`
   - snake_case: `tool_input`, `file_path`, `tool_name`
4. Support `apply_patch` as object, stringified object, or raw patch text.
5. Use `git diff`, `git status`, or worktree scans only when payload paths are unavailable.
6. Normalize, deduplicate, and scope-filter paths.
7. Check required tools; missing developer tools usually fail open.
8. Check format cache.
9. On valid cache hit, skip formatting.
10. Run formatter.
11. Recalculate hashes after formatting.
12. Cache only successful post-format hashes.
13. Emit one success JSON response.

Acceptance gate: if the hook formats edited files, at least one smoke test must prove selected include paths came from `stdin`.

## Verifier Hooks

Applies to `verify*.sh`.

Procedure:

1. Read hook JSON from `stdin`.
2. Extract file paths from `stdin` first when the event provides paths.
3. Support both common field styles and all common `apply_patch` forms.
4. For intentional session/worktree verifiers, use a worktree changed-files filter.
5. Normalize, deduplicate, and scope-filter paths.
6. If no relevant files changed, log skip and emit allow/success JSON.
7. Check required tools; missing developer tools usually fail open.
8. Build a fingerprint from current relevant file contents.
9. Check signed verify cache.
10. On valid cache hit, skip verification.
11. Run full verification.
12. Cache only successful verification.
13. Emit allow/success JSON for pass or deny/block JSON for validation failure.

## Changed-Files Fallback

Use fallback detection only after payload-first extraction fails, or for intentional session/worktree events.

Example backend filter:

```bash
backend_changed=false

if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git status --porcelain --untracked-files=all \
    | grep -E '\.(cs|csproj|sln|slnf)$|Directory\.Build\.props$' >/dev/null 2>&1; then
    backend_changed=true
  fi
else
  backend_changed=true
fi

if [[ "$backend_changed" = false ]]; then
  log_stderr "Skipping verification: no backend files changed."
  emit_allow "Skipped: no backend files changed."
  exit 0
fi
```

Keep extension lists and sentinel files aligned between GitHub and Gemini.

## Verification Command Notes

Backend examples:

```bash
dotnet build
dotnet test
```

If using:

```bash
dotnet test --no-build
```

run an explicit `dotnet build` first.

Frontend examples:

```bash
npx tsc
npm run test:cli
```
