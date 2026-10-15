## Learnings

From `session_notes.md`, the following durable learnings were qualified:
- **Keep**: `python3 scripts/check-config.py` - Must run after editing anything under `deploy/`.
- **Keep**: `pytest tests/integration/test_sync.py -q` - Must run for sync pipeline changes.
- **Keep**: `src/generated/` - Extend generated API clients instead of hand-writing request/response types.
- **Skip**: The agent opened the README before finding the real files (transient noise).
- **Skip**: The user's laptop fan got loud during one test run (transient noise).

## Applied updates

No `AGENTS.md` files existed. 

Created `outputs/repo/AGENTS.md` with the top 3 durable learnings using the `<command or pattern> - <brief description>` format as instructed by the skill.
