# Auth guidance

- Prefix safety must evaluate decoded forms, not only raw strings.
- Keep auth/login test blocks at `describe` root; Jasmine forbids nested `it`.
- Reuse shared return-url policy coverage for guard/login paths.
- Keep cached streams for reads and use fresh-fetch command paths for mutations to avoid replay bugs.
- Preserve existing error/focus UX when extending helper-text or `aria-describedby` associations.
- Time-based claim assertions should use ranges to avoid flake.
- Preserve single-rule targeting so unrelated validators do not cause false negatives.
- When a startup test must exercise the production `_Host` branch, stage and clean up a minimal `wwwroot/dist/browser/index.html` test artifact so the request path does not fall through to `/Error` + OIDC challenge behavior.
