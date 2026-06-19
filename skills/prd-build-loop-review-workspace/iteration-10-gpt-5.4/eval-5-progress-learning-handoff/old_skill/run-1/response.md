Need exact skill, fixture inputs, nothing extra. Reading minimal context, then writing decision artifact.
# Self-improve handoff decision

Orchestrator must pass `self-improve` a concise distilled summary from `progress.txt`, plus nearby `AGENTS.md` and linked auth-area docs as destination context. Pass reusable rules only. Do not pass raw progress blocks, story IDs, timestamps, or transient blocker/tracking notes.

Mine these progress-file sections before handoff:
- `## Codebase Patterns`
- `## 2026-06-12T10:00:00Z - US-001`
- `## 2026-06-12T10:40:00Z - US-001`
- `## 2026-06-12T11:10:00Z - US-001`
- `## 2026-06-12T11:45:00Z - US-001`
- `## 2026-06-12T12:00:00Z - FINALIZATION`

Preserve reusable learnings in these categories:
- **Validation/safety:** validate decoded return-url prefixes, not only raw strings; reuse one shared return-url policy across login, guard, validation, and startup paths; preserve single-rule targeting; avoid placeholder defaults that trigger unrelated validators.
- **Cache/state/replay:** keep cached stream for reads; use fresh-fetch command path for mutations; treat `shareReplay(1)` stale-first replay as known login success-flow hazard; cached-read plus fresh-mutation split is stable fix shape.
- **UX/accessibility:** preserve existing focus and error UX when extending auth helpers; compose `aria-describedby` in stable order with helper text before contextual errors.
- **Testing/anti-flake:** keep Jasmine `it` blocks at describe root; use filtered auth tests for focused coverage; use range-based assertions for time claims to avoid flake.
- **Environment/setup/routing:** browser `/login` checks may need correct dev route prefix; startup production-route coverage may require staged artifact `wwwroot/dist/browser/index.html`.
- **Guidance placement:** keep auth/login guidance in one scoped nearby location; nearby auth docs should own these rules instead of root guidance.

Representative distilled handoff for `self-improve`:
1. Destination: nearby `AGENTS.md` or linked auth docs, not root guidance.
2. Reusable guidance only; no raw progress structure or story-only notes.
3. Validation/safety: decoded return-url validation, shared return-url policy reuse, single-rule targeting, no placeholder defaults that trigger unrelated validators.
4. Cache/state/replay: cached reads vs fresh mutation fetches, `shareReplay(1)` stale replay hazard, stable split fix shape.
5. UX/accessibility: stable `aria-describedby` order, preserve existing error/focus behavior.
6. Testing/anti-flake: root-level Jasmine `it`, filtered auth coverage, range-based time assertions.
7. Environment/setup: correct dev route prefix for browser login checks; staged startup artifact `wwwroot/dist/browser/index.html` for production-route coverage.
