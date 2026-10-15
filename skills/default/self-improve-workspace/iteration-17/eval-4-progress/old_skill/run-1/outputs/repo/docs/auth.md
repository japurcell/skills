# Auth guidance

- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.
- Validate return-url prefixes against decoded forms (not only raw strings) to avoid prefix-bypass bugs.
- Reuse one shared return-url policy across guard and login helpers; preserve existing failed-login behavior while extending success-path logic.
- For replay-prone login flows, keep cached streams for reads and use fresh-fetch command paths for mutations; avoid `shareReplay(1)` stale-first regressions on success paths.
- When extending helper associations, compose `aria-describedby` in stable order: helper text first, then contextual error ids, without regressing focus/error UX.
- In auth tests, avoid nested `it` blocks (Jasmine), assert time-based claims with ranges to reduce flakes, keep validator targeting focused to a single rule, and avoid placeholder defaults that trigger unrelated validators.
- For browser checks in dev, use the correct dev route prefix because direct `/login` may bypass the intended route.
