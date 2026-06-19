# Self-improve handoff

Pass `self-improve` a distilled summary of reusable auth guidance plus nearby auth/login `AGENTS.md` and linked docs as context. Tell it to record scoped guidance near auth surfaces, not in root notes. Pass rules only; drop story IDs, timestamps, temporary blockers, and one-off filenames.

## Progress sections to mine

- `## Codebase Patterns`
- `## 2026-06-12T10:00:00Z - US-001`
- `## 2026-06-12T10:40:00Z - US-001`
- `## 2026-06-12T11:10:00Z - US-001`
- `## 2026-06-12T11:45:00Z - US-001`
- `## 2026-06-12T12:00:00Z - FINALIZATION`

## Reusable learnings to preserve

1. **Validation/safety:** Decode return-url prefixes before safety checks, and reuse one shared return-url policy across login, guard, validation, and startup paths.
2. **Cache/state/replay:** Keep cached streams for reads and use fresh-fetch command paths for mutations; stale-first replay behavior such as `shareReplay(1)` can break success flows.
3. **UX/accessibility:** Preserve existing focus and error behavior when extending auth helpers; compose `aria-describedby` in stable order with helper text before contextual errors.
4. **Testing/anti-flake:** Keep Jasmine `it` blocks at describe root, use time-claim ranges instead of exact timestamps, preserve single-rule validator targeting, avoid placeholder defaults that trigger unrelated failures, and keep existing failed-login coverage while adding new success-path coverage.
5. **Environment/setup:** Capture stable setup rules for auth browser checks and startup-route coverage, including dev-route prefix sensitivity and any required staged production artifact setup when that requirement is durable enough for nearby docs.
6. **Documentation placement:** Keep auth/login guidance in one scoped nearby location so future agents do not scatter rules across root-level notes.
