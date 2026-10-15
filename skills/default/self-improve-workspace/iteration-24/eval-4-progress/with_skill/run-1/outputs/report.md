# Learnings
- Keep auth/login detail in `docs/auth.md`, not root `AGENTS.md`.
- Stage and clean up a minimal `wwwroot/dist/browser/index.html` artifact when startup tests need the production `_Host` branch.
- Preserve existing focus and error behavior when extending login helpers.
- Use ranges for time-based claim assertions.
- Keep validation tests single-rule targeted and avoid placeholder defaults.

# Applied updates
- Copied fixture repo into `outputs/repo/`.
- Updated `outputs/repo/docs/auth.md` with the durable auth and test guidance from `progress.txt`.
- Left `outputs/repo/AGENTS.md` unchanged so root guidance stays short.

# Assumptions
- `docs/auth.md` was the correct home for these auth/login learnings because root `AGENTS.md` already delegates there.
- No other fixture files needed edits for this benchmark.
