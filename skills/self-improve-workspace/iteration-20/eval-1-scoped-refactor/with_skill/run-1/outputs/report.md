## Learnings

- `web/` changes need `pnpm --dir web test -- --runInBand`; shared fixtures fail in parallel.
- `api/schema/*.json` edits need `python3 scripts/validate_schema.py`.
- Root guidance should stay prompt-light and route scoped rules to owning directories.
- README mention in session notes did not qualify.

## Applied updates

- Copied fixture repo to `outputs/repo/`.
- Slimmed `outputs/repo/AGENTS.md` to project-wide guidance plus pointers to scoped files.
- Added scoped `AGENTS.md` files under `outputs/repo/web/` and `outputs/repo/api/`.

## Moved guidance

- Moved `web/` test command and serial-fixture rule from root to `outputs/repo/web/AGENTS.md`.
- Moved API contract ownership and schema validation rule from root to `outputs/repo/api/AGENTS.md`.
- Tightened root wording to preserve short-root rule instead of repeating scoped details.

## Grouped files

- `outputs/repo/AGENTS.md` - project-wide runtime + scoping rules.
- `outputs/repo/web/AGENTS.md` - `web/` test workflow.
- `outputs/repo/api/AGENTS.md` - API contract + schema validation workflow.
