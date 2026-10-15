# Repository Guidance

- `python3 scripts/check-config.py` - Run after editing anything under `deploy/`.
- `pytest tests/integration/test_sync.py -q` - Run for sync pipeline changes.
- `src/generated/` - Extend generated API clients here instead of hand-writing request/response types.
