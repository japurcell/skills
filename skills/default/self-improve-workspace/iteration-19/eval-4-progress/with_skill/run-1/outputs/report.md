Learnings

- return-url prefix validation: evaluate decoded forms; reuse shared return-url policy.
- Jasmine: no nested `it`; keep tests at describe root.
- Streams: cached-read + fresh-fetch for mutations prevents replay bugs; `shareReplay(1)` can be stale-first.
- aria-describedby: helper ID then errors.
- Time-based claims: use ranges; avoid placeholder defaults; prefer single-rule targeting.

Applied updates

- Updated outputs/repo/docs/auth.md with durable learnings from progress.txt. Kept original startup-route artifact guidance.

Assumptions

- Root AGENTS.md intentionally routes auth/login to docs/auth.md; that routing remains unchanged.
- No other AGENTS.md required changes.
- Progress artifacts are authoritative source for durable learnings in this benchmark.
