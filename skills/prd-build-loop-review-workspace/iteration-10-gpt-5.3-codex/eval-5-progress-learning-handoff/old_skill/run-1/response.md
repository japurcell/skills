Reading benchmark skill + fixture inputs, then I’ll write `outputs/decision.md` exactly per dry-run requirements.
Now switching to writing the dry-run decision artifact in `outputs/decision.md`.
Self-improve handoff summary (dry-run):
1. Destination: nearby auth-focused `AGENTS.md`; if details exceed scope, linked auth docs.
2. Reusable guidance only; no raw progress blocks, story-only notes, timestamps, or transient blockers.
3. Validation/safety: validate decoded return-url prefixes (not raw-only); enforce shared return-url policy across guard/login/startup paths; preserve single-rule targeting to avoid unrelated validator failures.
4. Cache/state/replay: keep cached stream for reads and fresh-fetch command path for mutations; guard against `shareReplay(1)` stale-first replay regressions.
5. UX/accessibility: keep `aria-describedby` order stable (helper text first, then contextual errors); preserve existing error and focus UX while extending helper associations.
6. Testing/anti-flake: keep Jasmine `it` blocks at describe root (no nested `it`); use range-based time assertions to reduce flake; keep auth tests filtered/targeted for fast validation.
7. Environment/setup: for startup production-route coverage, stage `wwwroot/dist/browser/index.html`; ensure dev route prefix is correct for browser `/login` checks.

Progress-file mining scope orchestrator must use before invoking `self-improve`:
- `## Codebase Patterns` (top-level durable patterns).
- Every entry's `**Learnings for future iterations:**` subsections:
  - `Patterns discovered`
  - `Gotchas encountered`
  - `Useful context`
- Include entries from all implementer blocks and FINALIZATION reviewer block so durable capture is complete, not single-note.

What orchestrator must pass to `self-improve`:
- Distilled, deduplicated durable rules from the mined sections above, grouped by: validation/safety, cache/state/replay, UX/accessibility, testing/anti-flake, environment/setup.
- Destination intent: update nearby auth guidance (`AGENTS.md` and linked auth docs) instead of root-level broad notes.
- Context inputs: `prd_file`, `progress_file`, nearby `AGENTS.md`, and linked docs needed for precise placement.
