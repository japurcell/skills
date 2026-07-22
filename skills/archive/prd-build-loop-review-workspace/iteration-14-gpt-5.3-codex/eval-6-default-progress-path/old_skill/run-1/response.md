Loading benchmark skill instructions and fixture to derive exact dry-run decision.

Preparing dry-run decision artifact in `outputs/decision.md` from resolved default progress-path rules.

Resolved first-write progress path: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/default-progress-path-fixture/progress.txt`.

Because `progress_file` was not provided, orchestrator must use `dirname(resolved prd_file) + "/progress.txt"` and, since sibling file does not yet exist, create it at that exact sibling path on first append.

Forbidden fallback path families: any non-sibling substitute location, including session-state paths (for example `/home/adam/.copilot/session-state/**`), scratchpad/temp paths, home-directory fallbacks (`~/**` or arbitrary `/home/adam/**`), and any `~/.copilot/**`-derived progress path.
