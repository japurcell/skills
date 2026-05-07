**Before the implementer runs, the manager should do only the setup work:** invoke `addy-context-engineering` and `subagent-model-selection`, confirm this is the next ready task, and dispatch a single-task wave. If the pagination slice were ambiguous or conflicted with the plan, the manager would resolve that first; otherwise, no repo exploration or patch drafting.

**The handoff should stay lean:** task text + acceptance criteria, known constraints, known validation commands, and only the already-known file hints from the plan. Don’t include a proposed design, guessed patch, or extra context hunting.

**Must stay with the implementer:** repo discovery, pattern lookup, first-pass design, reading the relevant code/tests/types, writing the failing test, implementing the fix, choosing and running the narrowest validations, and reporting back.
