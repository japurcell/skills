Before invoking `self-improve`, orchestrator must pass a distilled summary mined from `progress.txt` that includes only reusable guidance destined for nearby `AGENTS.md` or linked docs (not raw tracking data).

Mine these `progress.txt` sections:
1. `## Codebase Patterns`.
2. Every entry’s `**Learnings for future iterations:**` block.
3. Within each learnings block, mine all three subsections: `Patterns discovered`, `Gotchas encountered`, and `Useful context`.

Pass reusable rules under these exact buckets:

`Validation/safety`
- Validate auth return-url prefix safety on decoded forms, not raw-only strings.
- Reuse one shared return-url policy across guard/login paths.
- Preserve single-rule validator targeting to avoid unrelated false negatives.
- Avoid placeholder defaults that trigger unrelated validation failures.

`Cache/state/replay`
- Use cached stream for reads and fresh-fetch command path for mutations.
- Treat `shareReplay(1)` stale-first behavior as replay-regression risk on success flows.

`UX/accessibility`
- Preserve existing focus/error UX when extending auth helpers.
- Compose `aria-describedby` in stable order: helper text first, contextual errors second.
- Keep auth/login guidance in scoped auth docs location instead of root-note sprawl.

`Testing/anti-flake`
- Keep auth validation checks focused via filtered targeted tests.
- Use range-based assertions for time claims to reduce flake.
- In Jasmine, do not nest `it` blocks; keep them at describe root.

`Environment/setup`
- Respect dev route prefix requirements for browser checks.
- Preserve staged startup artifact guidance when needed for startup-route branch coverage: `wwwroot/dist/browser/index.html`.

Exclude from `self-improve` handoff: story IDs, timestamps, temporary blockers, per-run status text, and other non-durable tracking details.
