# Auth guidance

- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.
- Prefix safety must evaluate decoded forms, not only raw string.
- Jasmine forbids nested `it`; keep test blocks at describe root.
- Existing guard/login paths should reuse shared return-url policy coverage.
- Keep cached stream for reads; use fresh-fetch command path for mutations to avoid replay bugs. Fresh-fetch command path plus cached read stream split is stable fix shape for replay bugs.
- `shareReplay(1)` stale-first behavior can cause false UI failure on success flows.
- Compose `aria-describedby` in stable order: helper first, then contextual errors. Preserve existing error/focus UX while extending helper association through composed `aria-describedby`.
- Dev route prefix matters for browser checks. Browser direct `/login` may not hit the right dev route.
- Time-based claim assertions should use ranges to avoid flake.
- Preserve single-rule targeting to avoid false negatives from unrelated validators.
- Avoid placeholder defaults to prevent unrelated validation failures.
