Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt` (from `dirname(prd_file) + "/progress.txt"`; it exists, so read `## Codebase Patterns` and latest entries first).
Selected story: `story-auth-timeout` (highest-priority story with `passes: false`).
Before story-specific discovery: invoke `subagent-model-router` in principle (dry-run: do not spawn), then read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch a fresh `implementer` with `./implementer-prompt.md`.
