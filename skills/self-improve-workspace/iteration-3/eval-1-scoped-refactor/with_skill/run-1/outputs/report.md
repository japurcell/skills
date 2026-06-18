# Learnings

- `pnpm --dir web test -- --runInBand` is durable `web/` validation command because shared fixtures fail in parallel.
- `python3 scripts/validate_schema.py` is required after editing `api/schema/*.json`.
- API contract guidance belongs under `api/`, not root instructions.

# Applied updates

- Slimmed root `AGENTS.md` to repo-wide guidance only.
- Added `web/AGENTS.md` for frontend-specific test command and serial-fixture constraint.
- Added `api/AGENTS.md` for API contract scope and schema validation command.

# Moved guidance

- Moved `web/` test guidance out of root and merged it into one exact command: `pnpm --dir web test -- --runInBand`.
- Moved API contract and schema-validation guidance from root into `api/AGENTS.md`.
- Dropped README mention from session notes because it is not durable guidance.

# Grouped files

- Root: `outputs/repo/AGENTS.md`
- Web scope: `outputs/repo/web/AGENTS.md`
- API scope: `outputs/repo/api/AGENTS.md`
