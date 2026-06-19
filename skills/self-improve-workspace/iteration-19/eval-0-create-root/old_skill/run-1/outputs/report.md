Learnings

- Non-default validation command: run `python3 scripts/check-config.py` after edits under `deploy/`.
- Integration test to run for sync pipeline changes: `pytest tests/integration/test_sync.py -q`.
- Generated API clients live in `src/generated/`; extend these rather than hand-writing types.

Applied updates

- Copied fixture repo to `outputs/repo/`.
- Created `outputs/repo/AGENTS.md` containing the three durable learnings above and a note to prefer inspecting `src/` and `deploy/` over README when unsure.

Assumptions

- Session note items 1-3 classified as durable; items about laptop fan and README open were omitted or summarized.
