# Auth guidance

- Prefix safety for login and return-url validation must evaluate decoded forms, not only raw string values.
- Reuse shared return-url policy coverage across guard and login paths so auth redirect behavior stays aligned.
- Keep cached auth/login streams for reads; use fresh-fetch command paths for mutations to avoid replay bugs.
- `shareReplay(1)` stale-first behavior can cause false UI failures on login success flows; keep success-path mutations off cached replayed reads.
- Compose `aria-describedby` in stable order: helper text first, then contextual errors, while preserving existing error and focus behavior.
- Keep auth test `it` blocks at describe root; Jasmine forbids nested `it`.
- Time-based auth claim assertions should use ranges to avoid flake.
- Preserve single-rule targeting in auth validation tests so unrelated validators do not hide failures.
- Browser checks for login may need dev-route-prefixed URLs; direct `/login` can miss intended dev routing.
- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.
