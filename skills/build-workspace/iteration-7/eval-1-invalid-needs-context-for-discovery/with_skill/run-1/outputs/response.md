**The manager should push that back to the implementer, not do the repo reading or solution design for them.** In the build workflow, ordinary repo exploration, pattern lookup, and first-pass design are explicitly implementer-owned, and “I have not explored the repo yet” is **not** a valid `NEEDS_CONTEXT`.

A correct manager response is:

> `NEEDS_CONTEXT` is not appropriate here. Per the build workflow, you own repo discovery, reading the relevant files, finding existing patterns, and forming the first-pass approach. I’m not going to pre-read the repo or hand you the solution. Use the task, success criteria, known constraints, validation commands, and any already-known file hints from the handoff, then load the minimum context yourself and proceed. Come back with `NEEDS_CONTEXT` only if you find a genuine missing requirement, missing constraint, or conflicting signal you cannot resolve from the codebase and task context.

If the manager re-dispatches, it should be the same lean handoff—not a pre-solved design.
