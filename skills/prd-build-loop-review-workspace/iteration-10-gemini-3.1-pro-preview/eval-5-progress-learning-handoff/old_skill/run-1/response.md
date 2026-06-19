I_CAN_SEE_SESSIONSTART_CONTEXT2026-06-18T20:13:35.060-07:00
Orchestrator must mine both `## Codebase Patterns` and detailed per-entry learnings (Patterns discovered, Gotchas encountered, Useful context) in the progress file.

It must pass concise reusable rules to self-improve, preserving precise technical tokens (framework constraints, validation/safety, fix shapes, UX, testing/anti-flake, environment/setup) and dropping story IDs, timestamps, temporary blockers, and one-off filenames.

- **Self-improve handoff summary**
  1. Destination: nearby `AGENTS.md` or linked docs.
  2. Reusable guidance only; no raw progress blocks, story-only notes, or transient blockers.
  3. Validation/safety: decoded return-url validation, shared return-url policy, single-rule targeting
  4. Cache/state/replay: cached reads vs fresh mutation fetches around shareReplay(1)
  5. UX/accessibility: stable aria-describedby order, preserve error/focus UX
  6. Testing/anti-flake: root-level Jasmine it, range-based time assertions
  7. Environment/setup: staged startup artifact wwwroot/dist/browser/index.html
