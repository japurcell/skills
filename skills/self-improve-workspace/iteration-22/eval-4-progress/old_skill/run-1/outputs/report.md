# Self-Improve Report

## Learnings
Mined from `progress.txt`:
- Prefix safety must evaluate decoded forms, not only raw string.
- Jasmine forbids nested `it`; keep test blocks at describe root.
- Keep cached stream for reads; use fresh-fetch command path for mutations to avoid replay bugs.
- `shareReplay(1)` stale-first behavior can cause false UI failure on success flows.
- Compose `aria-describedby` in stable order: helper first, then contextual errors.
- Preserve existing error/focus UX while extending helper association.
- Time-based claim assertions should use ranges to avoid flake.
- Avoid placeholder defaults to prevent unrelated validation failures.
- Startup production-route tests may need staged dist artifact to hit intended branch: `wwwroot/dist/browser/index.html`. (Already partially documented, reinforced).

## Applied updates
- Added learnings to `outputs/repo/docs/auth.md`, since the root `AGENTS.md` explicitly states auth/login guidance belongs there.
- Kept root `AGENTS.md` unchanged to maintain its short length and specific focus.

## Assumptions
- General UI test gotchas (Jasmine `it` blocks) and state management patterns (RxJS `shareReplay`) discovered during auth implementation apply generally enough to the auth module to be documented in `auth.md`.
- Consolidated related learnings (e.g. `shareReplay` gotcha and the fresh-fetch fix) into single actionable bullet points.