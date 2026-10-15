# Learnings

- Prefix safety for login and return-url validation must evaluate decoded forms, not only raw values.
- Guard and login paths should share return-url policy coverage.
- Keep cached auth/login streams for reads and use fresh-fetch command paths for mutations; `shareReplay(1)` can surface stale-first success-flow failures.
- Compose `aria-describedby` helper text before contextual errors without changing existing focus/error UX.
- Auth tests need `it` blocks at describe root, time-based claim assertions as ranges, and single-rule targeting to avoid masked failures.
- Browser login checks may need dev-route-prefixed URLs, and startup production-route tests may need a staged `wwwroot/dist/browser/index.html` artifact.

# Applied updates

- Copied fixture repo to `outputs/repo/`.
- Updated `outputs/repo/docs/auth.md` with mined auth/login guidance from `progress.txt`.
- Left `outputs/repo/AGENTS.md` unchanged because it already correctly routes auth detail to `docs/auth.md` and stays minimal.

# Assumptions

- `/home/adam/.agents/skills/self-improve/SELF_IMPROVE_REFERENCE.md` was not readable in this run, so updates relied on the exact provided `SKILL.md` plus fixture instruction files.
