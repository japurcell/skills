First write must go to the sibling progress file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/default-progress-path-fixture/progress.txt`, resolved as `dirname(prd_file) + "/progress.txt"`. If that file does not exist yet, create that same path on the first append.

Forbidden fallback path families: any session-state/scratchpad path, any home-directory path, and any `~/.copilot/...` path. Do not substitute any of them for the sibling progress file.
