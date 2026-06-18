Destination for durable guidance:
- Primary: nearby auth-scoped guidance (auth docs/notes) for detailed, domain-specific rules.
- Prompt-worthy subset: nearby `AGENTS.md` only for short, high-leverage reminders.

Progress sections orchestrator must mine before `self-improve`:
1. `## Codebase Patterns` (top-level reusable patterns).
2. Every `## ... - story-local-auth-returnurl` entry, specifically each `**Learnings for future iterations:**` block:
   - `Patterns discovered`
   - `Gotchas encountered`
   - `Useful context`
3. `## ... - FINALIZATION` reviewer entry, including its `Learnings for future iterations` (explicit recording guidance and ownership location).

What orchestrator must pass to `self-improve` (reusable rules only, no raw blocks):
1. Validation/safety rules
   - Evaluate return-url prefix safety on decoded values, not only raw strings.
   - Reuse one shared return-url policy across guard/login/startup paths and coverage.
   - Keep validator targeting narrow (single-rule targeting); avoid placeholder defaults that trigger unrelated validators.
2. Cache/state/replay rules
   - Stable fix shape for replay bugs: cached stream for reads + fresh-fetch command path for mutations.
   - Treat `shareReplay(1)` stale-first behavior as replay-risk in success flows.
3. UX/accessibility rules
   - Preserve existing focus/error UX when extending auth helpers.
   - Compose `aria-describedby` in stable order: helper text first, contextual errors second.
   - Preserve failed-login behavior unless explicitly required to change.
4. Testing/anti-flake rules
   - Use time-claim range assertions (not exact instant equality) to reduce flake.
   - Keep auth regression coverage focused/filtered for fast validation loops.
   - Jasmine structure rule: do not nest `it` blocks.
5. Environment/setup rules
   - Dev route prefix affects browser checks (`/login` may miss intended route in dev).
   - Startup production-route validation may require staged artifact path `wwwroot/dist/browser/index.html`.

Filtering constraints for handoff summary:
- Keep precise technical tokens when part of durable rules (`shareReplay(1)`, `aria-describedby`, `wwwroot/dist/browser/index.html`, Jasmine).
- Exclude story IDs, timestamps, one-off execution notes, and temporary blockers.
- Do not pass raw progress tracking structure; pass concise distilled guidance grouped by category above.
