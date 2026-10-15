# Learnings

- Qualified: after edits under `deploy/`, run `python3 scripts/check-config.py`.
- Qualified: for sync pipeline changes, run `pytest tests/integration/test_sync.py -q`.
- Qualified: API client work should extend code in `src/generated/` instead of hand-writing request/response types.
- Excluded: README-navigation note and laptop fan note did not qualify as durable guidance.

# Applied updates

- Copied fixture repo to `outputs/repo/`.
- Created `outputs/repo/AGENTS.md` because fixture had no existing `AGENTS.md`.
- Added 3 durable, repo-specific instructions to root `AGENTS.md`.
