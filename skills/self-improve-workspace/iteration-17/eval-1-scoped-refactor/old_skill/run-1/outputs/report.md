# Learnings

- Durable: `web/` test runs must be serial because shared fixtures fail in parallel.
- Durable: use `pnpm --dir web test -- --runInBand` for `web/` changes.
- Durable: after `api/schema/*.json` edits, run `python3 scripts/validate_schema.py`.
- Excluded as non-durable: "repo has a README."

# Applied updates

- Refactored `outputs/repo/AGENTS.md` to stay prompt-light and route scoped rules to owning directories.
- Added scoped instruction files in `outputs/repo/web/AGENTS.md` and `outputs/repo/api/AGENTS.md`.

# Moved guidance

- From root to `web/AGENTS.md`:
  - Web test command moved and corrected to `pnpm --dir web test -- --runInBand`.
  - Serial test constraint for shared fixtures.
- From root to `api/AGENTS.md`:
  - API contract ownership under `api/`.
  - Schema validation command for `api/schema/*.json`.

# Grouped files

- Root (universal): `outputs/repo/AGENTS.md`
- Web scope: `outputs/repo/web/AGENTS.md`
- API scope: `outputs/repo/api/AGENTS.md`
