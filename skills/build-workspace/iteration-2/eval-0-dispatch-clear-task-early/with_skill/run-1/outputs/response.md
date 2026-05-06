**Before the implementer runs, the manager should only do setup and dispatch.** In this workflow, that means:

1. Invoke `addy-context-engineering` and `subagent-model-selection`.
2. Confirm this is the next pending plan task and that it is clear enough to execute.
3. Resolve only real ambiguity, conflicting plan signals, or missing requirements first.
4. Dispatch immediately once clear.

The manager should **not** pre-read a broad file set, explore the repo, draft the solution, sketch patches, or do first-pass design. It also should **not** update tracking yet.

**The handoff should stay lean.** Include:
- the task text
- the acceptance/success criteria
- known constraints
- the known validation commands
- only the already-known file hints from the plan/task/repo rules

Do **not** include a pre-solved design, repo research, guessed implementation details, or exploratory findings the manager gathered.

**Work that must stay with the implementer**:
- repo discovery
- reading the minimum relevant code, tests, patterns, types, and commands
- forming the first-pass approach
- writing the failing test first
- making the minimum code change to pass it
- choosing and running the narrowest relevant validations
- debugging if a step fails
- reporting status, files changed, commands run, and concerns

If the implementer asks the manager to explore the repo or hand over a solution, the build workflow says to push that work back to the implementer. `NEEDS_CONTEXT` is only for genuinely missing requirements, constraints, or conflicting signals—not routine discovery.
