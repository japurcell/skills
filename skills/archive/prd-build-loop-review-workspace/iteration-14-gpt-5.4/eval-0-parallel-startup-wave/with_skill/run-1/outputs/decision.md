1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` is `2` and ready story IDs are `US-002`, `US-003`.
4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; `US-002` and `US-003` have distinct `filesLikelyTouched`, so they are parallel-safe for same-wave dispatch, and no higher-batch work may start before wave `2` resolves.
