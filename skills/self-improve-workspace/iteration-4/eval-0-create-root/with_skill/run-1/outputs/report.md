Learnings

- After editing `deploy/`, run `python3 scripts/check-config.py`.
- For sync pipeline changes, run `pytest tests/integration/test_sync.py -q`.
- Generated API clients live in `src/generated/`; extend them instead of hand-writing types.
- Agents sometimes open README before locating authoritative files. Recommendation: agents check `AGENTS.md`, `scripts/`, and `deploy/` first.

Applied updates

- Recreated `outputs/repo/` by copying fixture repo contents (excluded `session_notes.md`).
- Added `outputs/repo/AGENTS.md` containing durable guidance:
  - After editing deploy/ - `python3 scripts/check-config.py` - validate deployment config.
  - Sync pipeline changes - `pytest tests/integration/test_sync.py -q` - run sync integration tests.
  - Generated API clients in `src/generated/` - extend generated clients; do not hand-edit API types.
  - Agents: check `AGENTS.md`, `scripts/`, and `deploy/` for authoritative instructions before opening README (README may be outdated).

Summary of changed files:
- outputs/repo/AGENTS.md

Assumptions:
- README may be outdated; rule keeps agents focused on authoritative source files.
