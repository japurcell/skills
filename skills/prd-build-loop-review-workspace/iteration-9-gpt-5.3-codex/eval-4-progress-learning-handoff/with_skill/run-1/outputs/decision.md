1. Destination: nearby auth-focused `AGENTS.md` or linked auth docs (prefer scoped auth guidance over root notes).
2. Reusable guidance only; no raw progress blocks, story-only notes, timestamps, or transient blockers.
3. Validation/safety: enforce decoded return-url prefix checks, reuse shared return-url policy across guard/login paths, preserve single-rule targeting, avoid placeholder defaults that trigger unrelated validators.
4. Cache/state/replay: keep cached stream for reads and fresh-fetch command path for mutations; treat `shareReplay(1)` stale-first replay as hazard and use split read/mutation path as stable fix shape.
5. UX/accessibility: keep `aria-describedby` order stable (helper text first, contextual errors second); preserve existing error and focus behavior while extending auth helpers.
6. Testing/anti-flake: keep Jasmine `it` blocks at describe root (no nested `it`); prefer filtered auth test runs for fast coverage; use range-based assertions for time-based claims.
7. Environment/setup: ensure startup production-route checks use staged artifact `wwwroot/dist/browser/index.html`; account for dev route-prefix behavior where direct `/login` may miss intended branch.

Progress-file sections to mine before self-improve handoff:
- `## Codebase Patterns` at top.
- Every detailed entry’s `**Learnings for future iterations:**` subsections:
  - `Patterns discovered`
  - `Gotchas encountered`
  - `Useful context`
- Include implementer entries and FINALIZATION reviewer entry; durable guidance appears in all of them.

Reusable learning categories that must be preserved:
- Validation/safety
- Cache/state/replay
- UX/accessibility
- Testing/anti-flake
- Environment/setup
