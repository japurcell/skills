## Self-improve handoff payload (what orchestrator must pass)

- Distilled reusable guidance summary only (not raw progress transcript), grouped by:
  - validation/safety rules
  - cache/state/replay rules
  - UX/accessibility rules
  - testing/anti-flake rules
  - environment/setup rules
- Destination context: nearby `AGENTS.md` plus linked docs when detail is too long for `AGENTS.md`.
- Scope instruction: preserve representative concrete rules; omit story tracking metadata.

## Progress sections to mine

1. `## Codebase Patterns` (top-level durable patterns).
2. Every timestamped entry’s `**Learnings for future iterations:**` block, including:
   - `Patterns discovered`
   - `Gotchas encountered`
   - `Useful context`
3. `## ... - FINALIZATION` reviewer entry learnings (explicitly includes what durable capture must cover).

## Reusable learnings to preserve

- Auth/return-url safety
  - Validate redirect prefix safety on decoded values, not raw-only checks.
  - Reuse shared return-url policy coverage across guard/login/startup paths.
- Cache/state/replay stability
  - Keep cached stream for read paths; use fresh-fetch command path for mutations.
  - Treat `shareReplay(1)` stale-first behavior as replay-regression risk in success flows.
- UX/accessibility invariants
  - Compose `aria-describedby` in stable order: helper text first, contextual errors next.
  - Extend helper association without regressing existing error/focus behavior.
- Test reliability and scope discipline
  - Avoid nested Jasmine `it` blocks.
  - Use range-based assertions for time claims to reduce flake.
  - Keep validator tests single-rule targeted to avoid unrelated false negatives.
  - Avoid placeholder defaults that trigger unrelated validation failures.
- Environment/setup execution context
  - Dev route prefix can change browser route validation behavior.
  - Startup production-route tests may require staged dist artifact: `wwwroot/dist/browser/index.html`.
- Documentation placement guidance
  - Keep auth/login durable rules in nearby scoped auth docs instead of root-level guidance sprawl.

## Exclusions (must not be forwarded as durable rules)

- Story IDs, timestamps, one-off blockers, and incidental per-run file lists.
- Raw progress entry formatting/tracking structure itself.
