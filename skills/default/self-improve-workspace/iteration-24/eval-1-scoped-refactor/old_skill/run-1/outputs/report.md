## Learnings
- `web/` tests must run serially with `pnpm --dir web test -- --runInBand`.
- Schema edits under `api/schema/*.json` should be validated with `python3 scripts/validate_schema.py`.
- Root guidance should stay minimal; scoped rules belong beside the code they govern.

## Applied updates
- Reduced root `AGENTS.md` to the single project-wide dependency note.
- Added `web/AGENTS.md` for serial web test guidance.
- Added `api/schema/AGENTS.md` for schema validation guidance.
- Added `api/AGENTS.md` for API contract location guidance.

## Moved guidance
- From root `AGENTS.md` to `web/AGENTS.md`: web test command and serial-fixture warning.
- From root `AGENTS.md` to `api/schema/AGENTS.md`: schema validation command.
- From root `AGENTS.md` to `api/AGENTS.md`: API contract location note.

## Grouped files
- `outputs/repo/AGENTS.md`
- `outputs/repo/web/AGENTS.md`
- `outputs/repo/api/AGENTS.md`
- `outputs/repo/api/schema/AGENTS.md`
