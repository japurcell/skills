# Learnings

- Keep root prompt-light by moving API- and web-specific guidance into scoped `AGENTS.md` files.
- For `web/` changes, run `pnpm --dir web test -- --runInBand` because shared fixtures fail in parallel.
- After editing `api/schema/*.json`, run `python3 scripts/validate_schema.py`.

# Applied updates

## `outputs/repo/AGENTS.md`
- Reduced root guidance to project-wide runtime/tooling notes plus links to scoped files.

## `outputs/repo/api/AGENTS.md`
- Kept API ownership guidance at `api/` scope.
- Added pointer to schema-specific validation guidance.

## `outputs/repo/api/schema/AGENTS.md`
- Added schema-only validation command.

## `outputs/repo/web/AGENTS.md`
- Added web-specific serial test command and fixture warning.

# Contradictions

- None. Root guidance was compatible with scoped guidance; only scope moved.

# Deletions

- Removed API contract ownership note from root `AGENTS.md`; it now lives in `outputs/repo/api/AGENTS.md`.
- Removed web test command and shared-fixture warning from root `AGENTS.md`; they now live in `outputs/repo/web/AGENTS.md`.
- Removed schema validation command from root `AGENTS.md`; it now lives in `outputs/repo/api/schema/AGENTS.md`.

# Moved guidance

- `outputs/repo/AGENTS.md` → `outputs/repo/api/AGENTS.md`: API contract ownership guidance.
- `outputs/repo/AGENTS.md` → `outputs/repo/api/schema/AGENTS.md`: schema validation command.
- `outputs/repo/AGENTS.md` → `outputs/repo/web/AGENTS.md`: web test command.
- `outputs/repo/AGENTS.md` → `outputs/repo/web/AGENTS.md`: shared-fixture serial test warning.

# Grouped files

- `outputs/repo/AGENTS.md` - project-wide tooling plus pointers to scoped guidance.
- `outputs/repo/api/AGENTS.md` - API-only ownership guidance.
- `outputs/repo/api/schema/AGENTS.md` - schema-only validation rule.
- `outputs/repo/web/AGENTS.md` - web-only test command and serial-fixture rule.
