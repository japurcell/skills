**The manager should push that back to the implementer, not do the exploration.** In the build workflow, ordinary repo discovery is implementer work, and `NEEDS_CONTEXT` is only valid for missing requirements, missing constraints, or conflicting signals.

A correct manager response is:

> `NEEDS_CONTEXT` is not valid for routine repo exploration. Under this workflow, you own repo discovery, pattern lookup, and first-pass design. I’m not going to pre-read files or hand you the solution before you start. Proceed from the task, success criteria, known constraints, validation commands, and any already-known file hints. Explore the relevant code yourself, implement the change, verify it, and return `DONE`, `DONE_WITH_CONCERNS`, or `BLOCKED`. If something is actually missing or conflicting, come back with the specific requirement or constraint gap.

If needed, the manager can re-dispatch with the same lean handoff, but should **not** read the repo and solve it for the implementer.
