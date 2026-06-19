Resolved default `progress_file` from provided `prd_file`:
`/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/default-progress-path-fixture/progress.txt`.

On first write, orchestrator must create (if missing) and append at that exact sibling path only; do not substitute any other location. If creating new file, start it with `## Codebase Patterns` at top.

Forbidden fallback path families when no explicit `progress_file` is provided:
- Session-state paths
- Scratchpad paths
- Temp/session artifact paths
- Home-directory artifact paths (including `~/.copilot/...`)
- Any path outside `dirname(prd_file)`
