# AGENTS.md

Project uses `pnpm` and `python3`.

- Run `pnpm --dir web test` after changing anything in `web/`.
- `web/` uses shared fixtures, so test runs must stay serial.
- Run `python3 scripts/validate_schema.py` after editing `api/schema/*.json`.
- API contract details live under `api/`.
- Keep the root file short.
