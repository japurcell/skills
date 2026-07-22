Pass to `self-improve` only distilled reusable rules, not raw progress data. Use the exact bucket labels `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, and `Environment/setup`, and keep story IDs, timestamps, temporary blockers, and one-off filenames out.

Mine `progress.txt` from `## Codebase Patterns` plus every `**Learnings for future iterations:**` block in each entry, including the FINALIZATION record. Use the `Patterns discovered`, `Gotchas encountered`, and `Useful context` lines as the source for durable guidance.

Preserve reusable learnings like: decoded-prefix validation must be checked on decoded forms; shared return-url policy coverage should be reused across login/guard/startup paths; cache/read streams and fresh command paths must stay split to avoid replay bugs; `aria-describedby` should keep helper text before contextual errors; time-based assertions should use ranges; tests should target one rule at a time; staged startup checks may need `wwwroot/dist/browser/index.html`.

Only reusable guidance belongs in nearby `AGENTS.md` or linked docs; story-specific notes stay in progress tracking only.
