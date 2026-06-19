## Learnings

- After editing anything under `deploy/`, run `python3 scripts/check-config.py`.
- For sync pipeline changes, run `pytest tests/integration/test_sync.py -q`.
- `src/generated/` is generated-client surface; extend generated clients instead of hand-writing request/response types.

## Applied updates

- Copied fixture repo into `outputs/repo/`.
- No existing `AGENTS.md` files found in copied repo, so created `outputs/repo/AGENTS.md` with 3 durable, repo-specific rules from session notes.
- Excluded non-durable notes (`README` navigation misstep, laptop fan noise).
