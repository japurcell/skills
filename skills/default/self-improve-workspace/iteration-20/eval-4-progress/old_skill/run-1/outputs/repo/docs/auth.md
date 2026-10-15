# Auth guidance

- Validate allowed return-url prefixes against decoded values, not only raw strings.
- Reuse shared return-url policy coverage across guard and login paths.
- Keep cached streams for auth reads; use a fresh-fetch command path for login or other auth mutations so `shareReplay(1)` stale-first behavior does not replay a false failure state.
- Preserve existing failed-login behavior when fixing success-path regressions.
- Compose `aria-describedby` in stable order: helper text first, then contextual errors, while preserving existing error and focus UX.
- In Jasmine auth specs, keep `it` blocks at describe scope; nested `it` is invalid.
- Use ranges for time-based claim assertions.
- Keep auth-validation tests focused on one rule, and avoid placeholder defaults that trigger unrelated validators.
- Browser auth checks should use the real dev route prefix; direct `/login` may miss the intended route in dev.
- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.
