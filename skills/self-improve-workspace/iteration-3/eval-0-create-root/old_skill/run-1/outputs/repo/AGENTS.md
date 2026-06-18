# Project guidance

- After editing files under `deploy/`, run `python3 scripts/check-config.py`.
- For sync pipeline changes, run `pytest tests/integration/test_sync.py -q`.
- API client request/response types belong in `src/generated/`; extend generated clients instead of hand-writing parallel types.
- Start investigations from feature directories (`deploy/`, `src/`, `tests/`) instead of reading `README` first.
