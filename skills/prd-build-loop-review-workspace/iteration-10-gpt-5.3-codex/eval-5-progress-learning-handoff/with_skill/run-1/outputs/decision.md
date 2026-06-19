Self-improve handoff must include a distilled, reusable guidance summary (not raw progress log) sourced from `progress.txt`, with destination guidance: update nearby auth-focused guidance (`AGENTS.md` and linked auth docs), not root/global notes.

Mine these progress-file sections:
1. `## Codebase Patterns` (top-level durable patterns).
2. Every entry’s `**Learnings for future iterations:**` block, including `Patterns discovered`, `Gotchas encountered`, and `Useful context`.
3. Finalization reviewer entry (`## ... - FINALIZATION`) for explicit recording expectations and scope.

Preserve reusable learnings in these durable categories:
- **Validation/Safety:** validate decoded return-url prefixes (not raw-only checks); reuse one shared return-url policy across guard/login/startup paths.
- **Cache/State/Replay:** keep cached stream for reads, use fresh-fetch command path for mutations; avoid `shareReplay(1)` stale-first regressions in success flows.
- **UX/Accessibility:** compose `aria-describedby` in stable order (helper text before contextual errors); preserve existing focus/error behavior when extending helpers.
- **Testing/Anti-flake:** avoid nested Jasmine `it`; use range-based assertions for time claims; keep validator tests single-rule targeted to prevent unrelated false negatives.
- **Environment/Setup:** dev route prefix must match browser path checks; startup production-route coverage may require staged dist artifact at `wwwroot/dist/browser/index.html`.

Filter before passing to `self-improve`: remove story IDs, timestamps, temporary blockers, and one-off execution details; keep representative concrete rules that future agents can apply broadly.
