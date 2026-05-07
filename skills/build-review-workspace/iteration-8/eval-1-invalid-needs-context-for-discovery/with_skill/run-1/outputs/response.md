**The manager should push it back to the implementer, not do the exploration.** In the build workflow, “I have not explored the repo yet” is **not** a valid `NEEDS_CONTEXT`. Ordinary repo discovery, pattern lookup, and first-pass design belong to the implementer, and the manager must **not** pre-read files or tell them the solution.

A correct manager reply is roughly:

> `NEEDS_CONTEXT` rejected. Repo exploration and first-pass design are part of your role. I’m not going to read the repo or hand you the solution. Use the lean handoff: task text, success criteria, known constraints, validation commands, and any already-known file hints. Read the relevant files yourself, find the existing patterns, form the approach, implement, validate, and report back. Only return `NEEDS_CONTEXT` if you hit genuinely missing requirements, missing constraints, or conflicting signals that cannot be resolved from the task, plan, repo rules, or codebase.

If the manager truly has missing product decisions, constraints, or conflict-resolution context, they should provide **only that** and re-dispatch; otherwise they should send the implementer back to execute.
