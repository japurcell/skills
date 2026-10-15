# Learnings

- After editing anything under `deploy/`, run `python3 scripts/check-config.py`.
- For sync pipeline changes, run `pytest tests/integration/test_sync.py -q`.
- Generated API clients live in `src/generated/`; extend them instead of hand-writing request/response types.

# Applied updates

- Copied fixture repo to `outputs/repo/`.
- Added `outputs/repo/AGENTS.md` with the three durable repo guidance items above.
