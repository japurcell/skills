# Learnings

- Durable: `web/` test runs must be serial; use `pnpm --dir web test -- --runInBand`.
- Durable: after editing `api/schema/*.json`, run `python3 scripts/validate_schema.py`.
- Durable: keep root `AGENTS.md` prompt-light and move scoped workflow details closer to owning folders.
- Excluded as non-durable: "repo has a README".

# Applied updates

- Copied fixture repo to `outputs/repo/`.
- Refactored `outputs/repo/AGENTS.md` to keep only project-wide routing guidance.
- Added scoped guidance files:
  - `outputs/repo/web/AGENTS.md`
  - `outputs/repo/api/AGENTS.md`
- Updated web test command to the corrected durable form with `-- --runInBand`.

# Moved guidance

| From | To | Guidance |
| --- | --- | --- |
| `outputs/repo/AGENTS.md` | `outputs/repo/web/AGENTS.md` | web test command + serial fixture constraint |
| `outputs/repo/AGENTS.md` | `outputs/repo/api/AGENTS.md` | schema validation command + API contract location note |

# Grouped files

- Root (project-wide only): `outputs/repo/AGENTS.md`
- Web scoped guidance: `outputs/repo/web/AGENTS.md`
- API scoped guidance: `outputs/repo/api/AGENTS.md`
