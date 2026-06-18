# Learnings

- Keep root prompt-light by moving API- and web-specific guidance into scoped `AGENTS.md` files.
- For `web/` changes, run `pnpm --dir web test -- --runInBand` because shared fixtures fail in parallel.
- After editing `api/schema/*.json`, run `python3 scripts/validate_schema.py`.

# Applied updates

## `outputs/repo/AGENTS.md`
- Removed web/API/schema operational rules from root.
- Kept root minimal and added pointers to `web/AGENTS.md` and `api/AGENTS.md`.

## `outputs/repo/api/schema/AGENTS.md`
- Tightened schema rule to explicit path: `api/schema/*.json`.

# Moved guidance

- `outputs/repo/AGENTS.md` → `outputs/repo/web/AGENTS.md`: web test command and serial-fixture rule.
- `outputs/repo/AGENTS.md` → `outputs/repo/api/AGENTS.md` and `outputs/repo/api/schema/AGENTS.md`: API ownership + schema validation scope.

# Grouped files

- `outputs/repo/AGENTS.md` - project-wide runtime/tooling and links only.
- `outputs/repo/web/AGENTS.md` - web test command + serial execution constraint.
- `outputs/repo/api/AGENTS.md` - API contract ownership and schema guidance pointer.
- `outputs/repo/api/schema/AGENTS.md` - schema JSON validation command.
