# AGENTS.md

- `python3 scripts/check-config.py` after editing anything under `deploy/`.
- `pytest tests/integration/test_sync.py -q` for sync pipeline changes.
- `src/generated/` holds generated API clients; extend them instead of hand-writing request/response types.
