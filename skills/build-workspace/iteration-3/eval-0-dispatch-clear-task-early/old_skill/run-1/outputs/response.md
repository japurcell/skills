Manager before dispatch: run addy-context-engineering and subagent-model-selection; mark the task in the tracker as in_progress; prepare a lean handoff; then dispatch an implementer subagent using implementer-prompt.md. Do not pre-read files or draft the solution.

Handoff (must include): task + acceptance criteria; known constraints (param names, defaults, limits, compatibility); validation commands (test/build/API smoke); explicit file hints named by the plan; repo rules and "do not commit; leave changes uncommitted."

Left to implementer: repo discovery and pattern lookup; write failing tests (RED→GREEN), implement code, run tests/build, verify end‑to‑end, and report status/files/concerns.
