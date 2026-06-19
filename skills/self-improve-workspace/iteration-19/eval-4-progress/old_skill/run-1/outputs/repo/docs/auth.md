# Auth guidance

- Keep detailed auth/login guidance in this file (docs/auth.md); root AGENTS.md should link here and stay brief.

- Prefix safety: validate decoded URL prefixes, not only raw strings.
- Return-url policy: reuse shared return-url policy for guard/login paths.
- Cache vs mutation: use cached read streams for reads; use fresh-fetch command path for mutations to avoid replay/replaybugs. Beware `shareReplay(1)` stale-first behavior causing false UI failures.
- Accessibility: compose `aria-describedby` in stable order: helper text first, then contextual errors. Preserve existing error/focus UX when extending helper association.
- Tests and timing: Jasmine forbids nested `it` blocks — keep tests at describe root. Use time ranges for claim assertions to avoid flake. Avoid placeholder defaults that create unrelated validation failures.
- Startup tests: when exercising production `_Host` branch, stage a minimal `wwwroot/dist/browser/index.html` artifact so request path does not fall through to `/Error` + OIDC challenge behavior.
- Preserve existing failed-login behavior and its test coverage.
