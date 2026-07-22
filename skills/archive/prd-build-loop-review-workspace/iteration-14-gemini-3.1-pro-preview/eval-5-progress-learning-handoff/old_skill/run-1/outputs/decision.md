The orchestrator must invoke `self-improve` with a distilled summary of reusable rules, directing it to update nearby `AGENTS.md` or linked auth docs rather than bloating root guidance.

It must mine both the `## Codebase Patterns` section at the top of the `progress_file` and the detailed `Learnings for future iterations` blocks from every timestamped entry.

It must preserve representative concrete rules for:
- Validation and safety (evaluating decoded forms for prefix safety, reusing shared return-url policies, single-rule targeting, avoiding placeholder defaults)
- Cache, state, and replay (using fresh-fetch command paths for mutations vs cached streams for reads to avoid `shareReplay(1)` bugs)
- UX and accessibility (stable `aria-describedby` composition ordering, preserving existing focus/error behavior)
- Testing and anti-flake (avoiding nested Jasmine `it` blocks, using ranges for time-based claims)
- Environment and setup guidance (using the staged dist artifact `wwwroot/dist/browser/index.html` for startup route tests)

It must explicitly drop story IDs, timestamps, temporary blockers, and one-off filenames before passing the summary to `self-improve`.