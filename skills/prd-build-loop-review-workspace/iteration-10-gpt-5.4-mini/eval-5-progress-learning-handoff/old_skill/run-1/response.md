Pass `self-improve` a distilled handoff, not raw progress data: concise reusable rules only, with nearby `AGENTS.md` or linked docs as the destination. Include stable validation/safety rules, cache/state/replay rules, UX/accessibility rules, testing/anti-flake rules, and environment/setup rules.

Mine `progress.txt` from `## Codebase Patterns` first, then every entry's `**Learnings for future iterations:**` block, especially the `Patterns discovered`, `Gotchas encountered`, and `Useful context` lines.

Preserve reusable learnings like decoded return-url validation, shared return-url policy reuse, cached reads vs fresh mutation fetches around `shareReplay(1)`, stable `aria-describedby` ordering, root-level Jasmine `it` with range-based time assertions, staged startup artifact `wwwroot/dist/browser/index.html`, and the rule to keep existing auth focus/error UX intact.
