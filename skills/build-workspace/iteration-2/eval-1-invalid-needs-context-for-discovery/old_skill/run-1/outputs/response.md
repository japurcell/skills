**The manager should push the work back to the implementer, not read the repo and pre-solve it.**

A good response is:

> `NEEDS_CONTEXT` is not appropriate here. In the build workflow, you own repo discovery, pattern lookup, first-pass solution design, implementation, and verification. Read the minimum relevant files, tests, types, and existing patterns yourself, then proceed. If you find a genuine gap in requirements, constraints, or conflicting signals that you cannot resolve from the codebase and task handoff, come back with `NEEDS_CONTEXT` and name the specific missing context.

That follows the local build workflow exactly: the manager stays a coordinator, does **not** pre-read source files or draft the solution, and only provides more context when something is actually missing beyond ordinary exploration.
