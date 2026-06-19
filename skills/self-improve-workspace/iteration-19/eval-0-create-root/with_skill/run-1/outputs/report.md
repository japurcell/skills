Learnings

- After editing anything under deploy/: run `python3 scripts/check-config.py` to validate deployment config.
- For sync pipeline changes: run `pytest tests/integration/test_sync.py -q`.
- Generated API clients live in `src/generated/`; extend generated code rather than hand-writing request/response types.

Applied updates

- Created `./AGENTS.md` at repository root with the three durable learnings above. File: outputs/repo/AGENTS.md

Source: mined from evals/files/create-root-fixture/session_notes.md
