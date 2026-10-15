# AGENTS.md

Durable, actionable guidance mined from recent session notes.

- `python3 scripts/check-config.py` - Run after editing anything under `deploy/` to validate deployment configuration.
- `pytest tests/integration/test_sync.py -q` - Run this integration test when making changes to the sync pipeline.
- `src/generated/` - Generated API clients live here; extend generated clients rather than hand-writing request/response types.
- Prefer inspecting `src/` and `deploy/` for authoritative implementation details; README may be summary or stale.
