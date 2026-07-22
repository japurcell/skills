1. Resolved `progress_file` must be `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/default-progress-path-fixture/progress.txt` (sibling of resolved `prd_file`).
2. If that sibling `progress.txt` does not exist yet, orchestrator must create that exact sibling path on first append.
3. Forbidden fallback path families: any session-state path, scratchpad path, home-directory path, or `~/.copilot/...` path; no alternate location may be invented.
