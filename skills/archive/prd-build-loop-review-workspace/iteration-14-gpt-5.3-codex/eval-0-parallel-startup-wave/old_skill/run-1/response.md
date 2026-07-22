I’ll load the benchmark skill instructions and fixture inputs, then produce `outputs/decision.md` with the required orchestrator startup actions.

Now I’ll write the dry-run startup action block into `outputs/decision.md` using the resolved fixture state.

1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` is `2`; ready story IDs: `US-002`, `US-003`.
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.
