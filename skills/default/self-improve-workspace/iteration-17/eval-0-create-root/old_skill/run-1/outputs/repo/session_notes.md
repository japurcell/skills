# Session notes

- After editing anything under `deploy/`, run `python3 scripts/check-config.py`.
- For sync pipeline changes, run `pytest tests/integration/test_sync.py -q`.
- Generated API clients live in `src/generated/`; extend them instead of hand-writing request/response types.
- The agent opened the README before finding the real files.
- The user's laptop fan got loud during one test run.
