Do not update tracking yet. Next: dispatch the code-simplifier (then run the code-reviewer; only update tracking after the final reviewer returns DONE).

Send the code-simplifier this context:
- The four touched file paths
- The implementer’s verification context (what checks ran and their passing results)
- All uncommitted files from git status --porcelain (exclude deleted files and .gitignore)
Also follow manager guardrails: pass only already-known plan/task/repo info and read any implementer concerns before proceeding.
