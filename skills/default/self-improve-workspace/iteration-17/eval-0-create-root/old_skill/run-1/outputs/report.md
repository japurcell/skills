## Learnings

- `python3 scripts/check-config.py` is required validation after edits under `deploy/`.
- `pytest tests/integration/test_sync.py -q` is required validation for sync pipeline changes.
- API client types are generated in `src/generated/`; extend generated clients instead of hand-writing request/response types.

## Applied updates

- Copied fixture repository to `outputs/repo/`.
- Added `outputs/repo/AGENTS.md` with durable, recurring guidance from session notes.
- Excluded non-durable notes (`README` navigation detail, laptop fan noise) from standing instructions.
