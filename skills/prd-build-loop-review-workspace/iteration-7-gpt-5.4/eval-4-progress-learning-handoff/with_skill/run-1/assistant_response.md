Self-improve handoff must pass a distilled reusable-summary, not raw progress blocks. Target destination should be nearby auth-focused `AGENTS.md` or linked auth docs, not root notes. Keep precise technical tokens when they are part of standing guidance, but exclude story IDs, timestamps, temporary blockers, and one-off file-tracking details.

Mine these `progress.txt` sections before invoking `self-improve`:
- `## Codebase Patterns`
- `## 2026-06-12T10:00:00Z - story-local-auth-returnurl`
- `## 2026-06-12T10:40:00Z - story-local-auth-returnurl`
- `## 2026-06-12T11:10:00Z - story-local-auth-returnurl`
- `## 2026-06-12T11:45:00Z - story-local-auth-returnurl`
- `## 2026-06-12T12:00:00Z - FINALIZATION`

Preserve reusable learnings across these categories:
- **Validation/safety:** validate return-url prefix safety on decoded forms, not only raw strings; reuse shared return-url policy across guard/login/startup paths; preserve single-rule targeting and avoid placeholder defaults that trigger unrelated validators.
- **Cache/state/replay:** keep cached stream for reads, but use fresh-fetch command path for mutations; replay bugs around `shareReplay(1)` need split read-vs-mutation flow to avoid stale-first success regressions.
- **UX/accessibility:** preserve existing failed-login behavior, focus handling, and error behavior; compose `aria-describedby` in stable order with helper text first and contextual errors after it.
- **Testing/anti-flake:** keep targeted auth tests filtered and focused; keep Jasmine `it` blocks at describe root; use time-claim assertion ranges instead of exact timestamps; preserve existing UX coverage while extending auth helpers.
- **Environment/setup:** browser `/login` checks may miss dev-route behavior; startup production-route tests may require staged dist artifact at `wwwroot/dist/browser/index.html`.

Also preserve two placement rules: auth/login guidance should stay in one scoped auth location instead of scattered root guidance, and final recording must capture all durable auth/validation/accessibility/startup-test rules rather than only one obvious note.
