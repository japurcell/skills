The orchestrator must append or create progress on first write at the explicit sibling path:
/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/default-progress-path-fixture/progress.txt

Forbidden fallback path families include:
- session-state paths
- scratchpads
- temp/session artifacts
- home artifacts
- ~/.copilot/... paths
- any other path not inside dirname(prd_file)