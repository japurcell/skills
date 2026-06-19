Mine both `## Codebase Patterns` and detailed per-entry learnings in `progress_file`.

1. Destination: nearby `AGENTS.md` or linked docs.
2. Reusable guidance only; no raw progress blocks, story-only notes, or transient blockers.
3. Validation/safety: decoded return-url checks, shared return-url policy, single-rule targeting
4. Cache/state/replay: cached reads vs fresh mutations, `shareReplay(1)` replay hazards
5. UX/accessibility: stable `aria-describedby` order, preserve error/focus UX
6. Testing/anti-flake: root-level Jasmine `it`, range-based time assertions
7. Environment/setup: staged startup artifact `wwwroot/dist/browser/index.html`
