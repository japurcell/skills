Learnings

- Prefix safety must evaluate decoded forms, not only raw strings.
- Reuse shared return-url policy across guard/login paths.
- Use cached read streams for reads and fresh-fetch for mutations to avoid replay bugs; `shareReplay(1)` can be stale-first and cause false failures.
- Compose `aria-describedby` helper first, then contextual errors; preserve focus/error UX.
- Jasmine forbids nested `it`; keep tests at describe root.
- Time-based claim assertions should use ranges to avoid flake.
- Avoid placeholder defaults that cause unrelated validation failures.
- Startup production-route tests may need staged `wwwroot/dist/browser/index.html` to hit `_Host` branch and avoid `/Error` + OIDC challenge.

Applied updates

- Updated outputs/repo/docs/auth.md with durable learnings mined from evals/files/progress-fixture/progress.txt. Added guidance on prefix validation, return-url policy reuse, cache vs mutation patterns, accessibility ordering, test gotchas, timing, and startup test artifact.
- Did not modify root AGENTS.md; root guidance remains short and links to docs/auth.md per project rules.

Assumptions

- Source of learnings: evals/files/progress-fixture/progress.txt (copied into outputs/repo/progress.txt during fixture copy).
- Work limited to current working directory; outputs/repo contains fixture copy.
- Root AGENTS.md guidance preserved; detailed auth guidance belongs in docs/auth.md per repo conventions.
- No other files modified.
