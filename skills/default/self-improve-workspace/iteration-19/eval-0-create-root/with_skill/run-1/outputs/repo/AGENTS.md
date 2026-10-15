# AGENTS.md

Repo durable guidance (mined from session notes)

Keep root AGENTS.md minimal. Include non-default commands and validation steps.

python3 scripts/check-config.py - Run after editing anything under deploy/ to validate deployment configuration.

pytest tests/integration/test_sync.py -q - Run for sync pipeline changes (integration tests for sync behavior).

src/generated/ - Generated API clients live here; extend generated code instead of hand-writing request/response types.

Source: evals/files/create-root-fixture/session_notes.md
