# Agent Guidance

- `python3 scripts/check-config.py` - run after any change under `deploy/`.
- `pytest tests/integration/test_sync.py -q` - run for sync pipeline changes.
- `src/generated/` - extend generated API clients there; do not hand-write request/response types outside generated client surfaces.
