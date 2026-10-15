# Self Improve Report

## Learnings

- Captured the correct web test command (`pnpm --dir web test -- --runInBand`) from session notes to ensure tests run in serial.
- Excluded the obvious fact that the repo has a README.

## Applied updates

- Updated root `AGENTS.md` to remove directory-specific details, keeping it prompt-light.
- Created `web/AGENTS.md` with the updated web test command and shared fixtures context.
- Created `api/AGENTS.md` with schema validation commands and API contract notes.

## Moved guidance

- Moved "Run `pnpm --dir web test` after changing anything in `web/`" to `web/AGENTS.md`.
- Moved "`web/` uses shared fixtures, so test runs must stay serial" to `web/AGENTS.md`.
- Moved "Run `python3 scripts/validate_schema.py` after editing `api/schema/*.json`" to `api/AGENTS.md`.
- Moved "API contract details live under `api/`" to `api/AGENTS.md`.

## Grouped files

- `./AGENTS.md` (root, near-universal rules)
- `./web/AGENTS.md` (web-scoped rules)
- `./api/AGENTS.md` (api-scoped rules)