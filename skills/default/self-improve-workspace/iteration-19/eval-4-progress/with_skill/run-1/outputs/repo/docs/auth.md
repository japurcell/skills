# Auth guidance

- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.

## Durable learnings (from progress artifacts)

- return-url prefix validation - Evaluate decoded form of return-url prefix, not only raw string; reuse shared return-url policy across guards/login paths.
- tests - Jasmine forbids nested `it`; keep test blocks at `describe` root to avoid test framework errors.
- streams - Use cached read stream for reads and a fresh-fetch command path for mutations to avoid replay bugs (pattern: cached-read + fresh-mutation).
- rxjs/shareReplay - `shareReplay(1)` can surface stale-first behavior; prefer explicit caching or fresh-fetch on mutations.
- aria-describedby composition - Append helper ID first, then contextual error IDs to preserve expected focus/error UX.
- dev-route checks - Dev route prefix affects browser tests; direct `/login` may not hit intended dev route.
- time-claims - Assert time-based claims with ranges to reduce flakiness.
- single-rule targeting - Keep validators single-rule targeted to avoid false negatives from unrelated validators.
- avoid placeholder defaults - Avoid placeholder defaults in validators to prevent unrelated validation failures.

Keep root AGENTS.md short and link to this doc for auth/login details.
