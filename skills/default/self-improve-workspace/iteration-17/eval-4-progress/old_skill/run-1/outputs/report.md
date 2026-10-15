# Learnings

- Durable auth/login guidance belongs in `docs/auth.md`, not root `AGENTS.md`.
- Return-url safety should validate decoded prefixes and reuse a shared return-url policy across guard/login paths.
- Replay regressions are avoided by splitting cached-read streams from fresh-fetch mutation command paths (especially around `shareReplay(1)` stale-first behavior).
- Accessibility-safe helper extensions should preserve existing focus/error UX and keep `aria-describedby` ordering stable (helper before contextual errors).
- Durable test guidance: no nested Jasmine `it` blocks, time-claim assertions should use ranges, validator tests should target one rule and avoid placeholder defaults that trigger unrelated validators.
- Startup branch coverage and dev browser checks have route/artifact gotchas (`wwwroot/dist/browser/index.html` staging and correct dev route prefix usage).

# Applied updates

- Copied fixture repo from `evals/files/progress-fixture/` to `outputs/repo/`.
- Updated `outputs/repo/docs/auth.md` with mined durable auth/login patterns and gotchas from `progress.txt`.
- Kept `outputs/repo/AGENTS.md` structure unchanged so root remains short and continues routing auth detail to `docs/auth.md`.

# Assumptions

- Treated all `evals/files/...` paths as relative to `/home/adam/dev/personal/skills/skills/self-improve`.
- Considered the `progress.txt` "Learnings for future iterations" entries as the authoritative durable source for this benchmark run.
