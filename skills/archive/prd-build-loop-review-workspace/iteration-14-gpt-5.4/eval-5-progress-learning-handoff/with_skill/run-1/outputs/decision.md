1. Mine `## Codebase Patterns` and every `Learnings for future iterations` block in the detailed `US-001` entries plus the `FINALIZATION` entry, including each entry's `Patterns discovered`, `Gotchas encountered`, and `Useful context`.
2. Pass only reusable guidance into nearby `AGENTS.md` or linked docs, not story-specific notes, raw tracking data, story IDs, timestamps, temporary blockers, or one-off filenames.
3. Preserve durable rules under exact bucket labels: `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, and `Environment/setup`.
4. Preserve staged production-artifact startup-test guidance such as `wwwroot/dist/browser/index.html` when present.

`self-improve` handoff payload should include:

## Validation/safety
- Validate redirect prefix safety against decoded forms, not only raw strings.
- Reuse shared return-url policy across guard, login, validation, and startup auth paths instead of duplicating checks.
- Preserve single-rule validator targeting to avoid false negatives from unrelated validators.
- Avoid placeholder defaults that trigger unrelated validation failures.

## Cache/state/replay
- Keep cached streams for read paths; use fresh-fetch command paths for mutations to avoid replay regressions.
- Treat `shareReplay(1)` stale-first behavior as replay-risk on success flows and verify fresh mutation results do not reuse stale UI state.

## UX/accessibility
- Preserve existing focus and error behavior when extending auth helpers.
- Compose `aria-describedby` in stable order: helper text first, then contextual errors.
- Keep auth/login guidance in one scoped auth-owned location or nearby auth docs, not scattered root notes.

## Testing/anti-flake
- Keep Jasmine `it` blocks at describe root; do not nest them.
- Use filtered auth tests for fast, focused validation coverage.
- Assert time-based claims with ranges instead of exact timestamps to avoid flake.
- Preserve existing failed-login coverage while extending success-path or return-url behavior.

## Environment/setup
- Dev route prefix matters for browser checks; direct `/login` browser hits may miss intended dev route.
- Startup production-route tests may require staged dist artifact `wwwroot/dist/browser/index.html` to exercise intended branch.
- Final durable guidance should live in nearby auth docs or linked docs for that area, not in broad root-level guidance.
