Pass `self-improve` a concise reusable-rules summary, not raw progress blocks. Target nearby auth docs first because progress says auth/login guidance should stay scoped there; use nearby `AGENTS.md` only for short prompt-worthy rules and linked docs for longer auth/testing details. Exclude story IDs, timestamps, one-off file lists, and transient blockers.

Mine these `progress.txt` sections before handoff:
- `## Codebase Patterns`
- Every entry's `**Learnings for future iterations:**` block under `Patterns discovered`, `Gotchas encountered`, and `Useful context`
- The `## 2026-06-12T12:00:00Z - FINALIZATION` reviewer entry, especially its reminder to capture auth, validation, accessibility, and startup-test rules

Preserve reusable learnings in these categories:
- **Validation/safety:** validate unsafe prefixes on decoded values, not only raw strings; reuse one shared return-url policy across login, guard, validation, and startup paths; preserve single-rule targeting; avoid placeholder defaults that trigger unrelated validators
- **Cache/state/replay:** keep cached stream for reads and use fresh-fetch command path for mutations; treat `shareReplay(1)` stale-first behavior as replay-bug risk
- **UX/accessibility:** preserve existing focus and error behavior; keep failed-login UX unchanged; compose `aria-describedby` in stable order with helper text first and contextual errors second
- **Testing/anti-flake:** keep filtered auth tests for fast focused coverage; avoid nested Jasmine `it`; use ranged assertions for time-based claims to reduce flake
- **Environment/setup:** browser checks must use correct dev route prefix; direct `/login` may miss intended dev route; startup production-route tests may require staged artifact `wwwroot/dist/browser/index.html`
