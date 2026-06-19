1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt` (from `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path).
3. Active parallel wave: `parallelBatch` 2 (`US-002`, `US-003`); next dispatch target is highest-priority `passes: false` story `US-002`.
4. Before story-specific repo discovery: dispatch fresh implementer first; until then read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
