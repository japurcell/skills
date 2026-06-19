Loading minimal context from benchmark skill and fixture inputs, then writing dry-run decision artifact.

# Decision

Orchestrator must pass `self-improve` a distilled reusable-guidance summary from `progress.txt`, plus nearby auth-focused `AGENTS.md` and linked docs as destination context. Payload should preserve representative concrete rules, but strip story IDs, timestamps, temporary status text, and one-off filenames/blockers. Because progress says auth guidance should live in scoped auth docs instead of root notes, handoff should direct `self-improve` to auth-local guidance rather than broad root guidance when detail is auth-specific.

Mine these `progress.txt` sections:
1. `## Codebase Patterns`
2. Every entry's `**Learnings for future iterations:**` subsections:
   - `Patterns discovered`
   - `Gotchas encountered`
   - `Useful context`
3. Especially the `FINALIZATION` reviewer entry, since it states which reusable rule families still need durable capture.

Preserve these reusable learnings:
- **Validation/safety:** evaluate prefix safety on decoded forms, not only raw strings; reuse shared return-url policy coverage across login/guard/startup paths; preserve single-rule targeting to avoid false negatives; avoid placeholder defaults that trigger unrelated validation failures.
- **Cache/state/replay:** keep cached stream for reads and use fresh-fetch command path for mutations; treat `shareReplay(1)` stale-first behavior as replay-regression risk on success flows.
- **UX/accessibility:** preserve existing focus and error behavior when extending auth helpers; compose `aria-describedby` in stable order with helper text first and contextual errors after.
- **Testing/anti-flake:** keep Jasmine `it` blocks at describe root; prefer filtered/targeted auth tests for focused coverage; use time-claim ranges instead of exact instants; keep existing failed-login coverage unchanged while extending success-path behavior.
- **Environment/setup:** dev route prefix matters for browser checks; direct browser `/login` may miss intended dev route; startup production-route checks may require staged dist artifact.
- **Guidance placement/ownership:** keep auth/login guidance in one scoped auth location; do not record only one obvious note when multiple reusable auth, validation, accessibility, and startup-test rules were discovered.
