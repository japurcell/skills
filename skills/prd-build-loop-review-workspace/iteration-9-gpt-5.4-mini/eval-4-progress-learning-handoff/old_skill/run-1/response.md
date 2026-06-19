Orchestrator must mine `progress_file` first, then call `self-improve` with a concise reusable-summary package: distilled rules only, plus nearby `AGENTS.md` and any linked docs when the rule is too long for `AGENTS.md`.

Mine these progress sections:
- `## Codebase Patterns`
- every entry's `**Learnings for future iterations:**`
  - `Patterns discovered`
  - `Gotchas encountered`
  - `Useful context`
- the FINALIZATION entry, since it often records the last durable guidance

Preserve reusable learnings of these kinds:
- validation/safety rules
- cache/replay behavior rules
- UX/accessibility preservation rules
- testing and anti-flake tactics
- environment/setup requirements

Keep stable technical tokens that are part of the rule itself, like framework names, operators, API names, helper names, and artifact paths. Drop story IDs, timestamps, temporary blockers, and one-off filenames or notes.
