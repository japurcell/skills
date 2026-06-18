# Learnings

- `deploy/` changes require `python3 scripts/check-config.py`.
- Sync pipeline changes require `pytest tests/integration/test_sync.py -q`.
- API request and response types should come from `src/generated/`; extend generated clients instead of hand-writing them.

# Applied updates

- Created `outputs/repo/AGENTS.md` because fixture repo had no existing `AGENTS.md`.
- Added repo-wide deploy validation, sync-test validation, and generated-client guidance to root instructions.
- Excluded one-off session noise such as opening `README` first and laptop fan noise during test run.
