1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt`; sibling path already exists, and if it did not exist yet, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` 2 with `US-002` and `US-003`.
4. Before any story-specific repo discovery: read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work; then dispatch one fresh implementer per parallel-safe story, and do not read story-specific files, tests, code, or behavior before that first implementer.
