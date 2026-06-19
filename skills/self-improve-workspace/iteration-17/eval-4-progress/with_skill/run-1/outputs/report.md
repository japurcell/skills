# Learnings

- Return-url safety checks should validate decoded prefixes, and guard/login coverage should stay aligned on shared policy behavior.
- Login replay regressions are best handled by keeping cached read streams and using fresh-fetch command paths for mutations; `shareReplay(1)` stale-first behavior is a known success-path failure source.
- Accessibility and UX updates should preserve existing error/focus behavior while composing `aria-describedby` in helper-first, error-second order.
- Auth/login tests are more stable when Jasmine `it` blocks are not nested, time-based claims use ranges, and validator coverage stays single-rule focused.
- Startup production-route tests may require staging `wwwroot/dist/browser/index.html` to exercise `_Host` instead of `/Error` + OIDC challenge fallback.

# Applied updates

- Copied fixture repository contents to `outputs/repo/`.
- Updated `outputs/repo/docs/auth.md` with durable auth/login implementation and testing guidance mined from `progress.txt`.
- Kept root `outputs/repo/AGENTS.md` unchanged so auth/login detail remains owned by `docs/auth.md`.

# Assumptions

- Since root guidance already routes auth/login detail to `docs/auth.md`, all qualified learnings from `progress.txt` were placed there rather than in root `AGENTS.md`.
- `/home/adam/.agents/skills/self-improve/SELF_IMPROVE_REFERENCE.md` was not readable in this environment, so updates were derived from the requested `SKILL.md` and fixture artifacts.
