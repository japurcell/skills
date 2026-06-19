1. Source of truth: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/prd.json` (`prd_file`) official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt` (`dirname(prd_file) + "/progress.txt"`); existing sibling resume path, never substitute session-state/home path.
3. Active parallel wave: `parallelBatch` 2 with ready `passes: false` stories `US-002` and `US-003`; `US-004` waits on `US-002`.
4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
