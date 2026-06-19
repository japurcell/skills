# Auth guidance

- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.
- Preserve existing focus and error behavior when extending login helpers.
- Time-based claim assertions should use ranges to avoid flake.
- Keep validation tests single-rule targeted to avoid false negatives from unrelated validators.
- Avoid placeholder defaults that trigger unrelated validation failures.
