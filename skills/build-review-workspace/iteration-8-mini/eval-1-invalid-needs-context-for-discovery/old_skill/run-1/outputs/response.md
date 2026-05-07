Per the build workflow: ordinary repo exploration is the implementer's job (NEEDS_CONTEXT is only for missing requirements, constraints, or conflicting signals). Push this back with a lean handoff and a clear checklist.

Suggested manager reply to the implementer:
- Reminder: repo discovery/pattern lookup belongs to you; do that first.
- Handoff (short): Task: <task text>. Success criteria: <what passes>. Constraints: <known constraints or "none">.
- Do this exploration and return with:
  1) Repo surface: language, build/test commands, key files (README, docs/, tests/, package files).
  2) Commands run and their output (git --no-pager status --porcelain; run project test/build-review per README).
  3) Proposed minimal design/patch outline and files you’ll touch.
  4) Any true missing requirements or conflicts (if present, mark NEEDS_CONTEXT with specifics).
- After that, re-dispatch.
