# Auth guidance

- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.
- Prefix safety must evaluate decoded forms, not only raw strings.
- Keep cached stream for reads; use fresh-fetch command path for mutations to avoid replay bugs (e.g. `shareReplay(1)` stale-first issues).
- Compose `aria-describedby` in stable order: helper first, then contextual errors. Preserve existing error/focus UX.
- Time-based claim assertions should use ranges to avoid flake. Avoid placeholder defaults to prevent unrelated validation failures.
- Jasmine forbids nested `it`; keep test blocks at describe root.
