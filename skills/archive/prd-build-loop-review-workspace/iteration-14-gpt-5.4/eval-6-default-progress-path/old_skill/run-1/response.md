Use default sibling progress path from resolved `prd_file`:
`/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/default-progress-path-fixture/progress.txt`

Because no explicit `progress_file` was provided and no sibling `progress.txt` exists yet, orchestrator must keep that exact sibling path reserved and create/append it there on first write. Missing sibling file does not permit choosing any other location.

Forbidden fallback path families: session-state paths, scratchpad paths, home-directory paths, and `~/.copilot/...` paths. More generally, any non-sibling invented fallback path is forbidden.
