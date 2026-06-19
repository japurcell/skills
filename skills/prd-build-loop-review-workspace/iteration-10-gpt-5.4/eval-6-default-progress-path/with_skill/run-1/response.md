Checking exact skill rules, then I’ll write decision artifact.
Writing decision artifact now.
Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/default-progress-path-fixture/progress.txt`.

No explicit `progress_file` given. No sibling `progress.txt` exists yet. Orchestrator must keep that sibling path reserved and create/append progress there on first write, with `## Codebase Patterns` at top. Missing sibling file is never permission to invent another location.

Forbidden fallback path families: session-state paths, scratchpads, home directories, and `~/.copilot/...` paths. More broadly, `progress_file` must never resolve anywhere except explicit path or `dirname(resolved prd_file) + "/progress.txt"`.
