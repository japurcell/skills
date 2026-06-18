# AGENTS.md — project-level durable guidance

After editing deploy/ - `python3 scripts/check-config.py` - validate deployment config.

Sync pipeline changes - `pytest tests/integration/test_sync.py -q` - run sync integration tests.

Generated API clients in `src/generated/` - extend generated clients; do not hand-edit API types.

Agents: check `AGENTS.md`, `scripts/`, and `deploy/` for authoritative instructions before opening README (README may be outdated).
