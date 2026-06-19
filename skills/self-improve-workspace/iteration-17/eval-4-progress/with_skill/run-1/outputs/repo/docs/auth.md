# Auth guidance

- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.
- Return-url prefix safety checks should validate decoded forms, not only raw strings.
- Keep guard and login paths on shared return-url policy behavior and coverage.
- For login state flows, keep cached stream reads and use a fresh-fetch command path for mutations to avoid replay regressions.
- Treat `shareReplay(1)` stale-first behavior as a likely cause when success-path UI assertions fail.
- Preserve existing failed-login behavior and coverage when fixing success-path regressions.
- Compose `aria-describedby` in stable order: helper text ID first, then contextual error IDs.
- Extend helper/error associations without changing existing error focus behavior.
- In Jasmine suites, avoid nested `it`; keep test cases directly under the surrounding `describe`.
- For time-based claim validation, assert acceptable ranges instead of exact timestamps.
- Keep validator tests single-rule focused; avoid placeholder defaults that trigger unrelated validation failures.
