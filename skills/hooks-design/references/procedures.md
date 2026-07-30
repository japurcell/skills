# Formatter and Verifier Procedures

Use the repo’s existing hook layout, runtime, filenames, wrappers, and launch style unless asked to change them.

Common layouts:

```text
.github/hooks/scripts/format[-backend|-frontend].<ext>
.github/hooks/scripts/verify[-backend|-frontend].<ext>
.gemini/hooks/scripts/format[-backend|-frontend].<ext>
.gemini/hooks/scripts/verify[-backend|-frontend].<ext>
```

`<ext>` may be `.sh`, `.py`, `.js`, `.ts`, `.mjs`, `.ps1`, none, or repo-specific.

## Formatter Hooks

For `format*` hooks:

1. Read hook JSON from `stdin`.
2. Extract paths from `stdin` first.
3. Support the repo’s expected field styles:
   - camelCase: `toolArgs`, `toolName`, `filePath`
   - snake_case: `tool_input`, `tool_name`, `file_path`
4. Support `apply_patch` as object, stringified object, or raw patch text.
5. Fallback to `git`/worktree detection only when payload paths are unavailable.
6. Normalize, dedupe, and scope-filter paths.
7. Check tools; missing developer tools usually fail open.
8. Format relevant files.
9. Emit one success JSON response.

Acceptance gate: if the hook formats edited files, include a smoke test proving selected paths came from `stdin`.

## Verifier Hooks

For `verify*` hooks:

1. Read hook JSON from `stdin`.
2. Extract paths from `stdin` first when the event provides paths.
3. Support the repo’s expected field styles and `apply_patch` forms.
4. For intentional session/worktree verifiers, use worktree changed-file detection.
5. Normalize, dedupe, and scope-filter paths.
6. If no relevant files changed, log skip and emit allow/success JSON.
7. Check tools; missing developer tools usually fail open.
8. Run repo-defined verification.
9. Emit allow/success JSON for pass, or deny/block JSON for validation failure.

## Changed-File Fallback

Use only after payload extraction fails, or for intentional session/worktree events.

```text
if git is available and inside a worktree:
  changed_files = changed + untracked files
  relevant = any file matches repo classifier
else:
  relevant = true

if relevant is false:
  log skip to stderr/audit log
  emit allow/success JSON
  exit successfully
```

Keep classifiers aligned between GitHub and Gemini.

Examples only; use the repo’s actual classifiers:

```text
backend: .cs, .csproj, .sln, .slnf, Directory.Build.props
frontend: .ts, .tsx, .js, .jsx, .mjs, .cjs, .json,
          package.json, lockfiles, tsconfig, eslint/prettier configs
```

## Verification Command Notes

Run only commands that exist in the repo.

Backend examples:

```text
dotnet build
dotnet test
```

If using:

```text
dotnet test --no-build
```

run `dotnet build` first.

Frontend examples:

```text
npx tsc
npm run test:cli
```
