The orchestrator must pass to `self-improve` a distilled summary of durable learnings, along with nearby `AGENTS.md` and linked docs. It must name the destination in the handoff: nearby `AGENTS.md` when prompt-worthy, and linked docs when the detail is too long for `AGENTS.md` (e.g., routing auth guidance to nearby auth docs instead of bloating root guidance).

It must mine both:
1. The `## Codebase Patterns` section.
2. The detailed per-entry learnings from the `progress_file` (`**Learnings for future iterations:**`).

It must preserve concise, representative concrete rules while dropping raw tracking structure, story IDs, timestamps, temporary blockers, and one-off filenames. The kinds of reusable learnings it must preserve include:
- Validation/safety: Prefix safety must evaluate decoded forms, not just raw strings. Reuse shared return-url policy. Preserve single-rule targeting.
- Cache/state/replay: Keep cached streams for reads and use fresh-fetch command paths for mutations to avoid replay bugs. Note `shareReplay(1)` stale-first behavior.
- UX/accessibility: Compose `aria-describedby` in a stable order (helper first, then contextual errors). Preserve existing error/focus UX.
- Testing/anti-flake: Jasmine forbids nested `it` blocks; time-based claim assertions should use ranges.
- Environment/setup guidance: Startup production-route tests may need staged dist artifacts (`wwwroot/dist/browser/index.html`); dev route prefix matters for browser checks.
