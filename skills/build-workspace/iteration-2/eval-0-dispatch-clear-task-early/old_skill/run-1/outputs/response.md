**Before the implementer runs:** the manager should invoke **`addy-context-engineering`** and **`subagent-model-selection`**, confirm the task is the clear next pending item, then **dispatch immediately**. For this pagination task, because the task text, acceptance criteria, validation commands, and likely files are already known, the manager should **not** pre-read repo files, draft a solution, or make a patch plan first.

**What belongs in the handoff:** only the lean execution context:
1. The task text: **add pagination to `GET /api/issues`**
2. The acceptance criteria
3. Known constraints and repo rules
4. The known validation/test/build commands
5. File hints **only** if they are already named by the plan/task

Also exclude exploratory reads, speculative architecture analysis, and proposed code changes.

**What stays with the implementer:** repo discovery, reading the minimum relevant files, finding existing patterns, deciding the first-pass approach, writing the failing test first, making the code changes, running the relevant tests and build, debugging if needed, and reporting back with **DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED** plus changed files and results.

The manager keeps only coordination work: ambiguity resolution if needed, reacting to implementer status, updating plan/todo/tracking after completion, and not committing.
