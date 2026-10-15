# Learnings

- User wanted AGENTS cleanup by scope, not all guidance left in root.
- `web/` changes should use `pnpm --dir web test -- --runInBand`; serial execution is required because shared fixtures fail in parallel.
- `api/schema/*.json` edits should be followed by `python3 scripts/validate_schema.py`.

# Applied updates

- Kept `outputs/repo/AGENTS.md` prompt-light with only universal project notes and pointers to owning scoped files.
- Added `outputs/repo/web/AGENTS.md` for web-only test guidance.
- Added `outputs/repo/api/AGENTS.md` for API contract and schema validation guidance.

# Moved guidance

- Moved web test command and serial-fixture warning from root to `outputs/repo/web/AGENTS.md`.
- Moved API contract ownership and schema validation command from root to `outputs/repo/api/AGENTS.md`.

# Grouped files

- Root: `outputs/repo/AGENTS.md`
- Web scope: `outputs/repo/web/AGENTS.md`
- API scope: `outputs/repo/api/AGENTS.md`
