# Agent guidance

- After editing anything under `deploy/`, run `python3 scripts/check-config.py`.
- For sync pipeline changes, run `pytest tests/integration/test_sync.py -q`.
- `src/generated/` contains generated API clients; extend generated clients instead of hand-writing request/response types.
