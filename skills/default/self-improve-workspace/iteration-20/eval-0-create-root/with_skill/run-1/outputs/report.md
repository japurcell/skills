## Learnings

- `python3 scripts/check-config.py` after editing anything under `deploy/`.
- `pytest tests/integration/test_sync.py -q` for sync pipeline changes.
- Generated API clients live in `src/generated/`; extend them instead of hand-writing request/response types.

## Applied updates

- No `AGENTS.md` existed in fixture repo, so created `outputs/repo/AGENTS.md`.
- Kept root guidance minimal with only three durable repo-specific rules.
- Excluded one-off notes about opening `README` first and laptop fan noise because they did not qualify as durable guidance.
