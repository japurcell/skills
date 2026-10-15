# Learnings

- `web/` test runs must stay serial, so use `pnpm --dir web test -- --runInBand`.

# Applied updates

- Kept `outputs/repo/AGENTS.md` prompt-light with only the repo-wide toolchain note.
- Added `outputs/repo/web/AGENTS.md` for web-only test guidance.
- Added `outputs/repo/api/AGENTS.md` for API schema validation and contract scoping.

# Moved guidance

- `web/` test command and serial-fixture warning moved from root into `web/AGENTS.md`.
- `api/schema/*.json` validation and API contract scoping moved from root into `api/AGENTS.md`.

# Grouped files

- `outputs/repo/AGENTS.md`
- `outputs/repo/web/AGENTS.md`
- `outputs/repo/api/AGENTS.md`
