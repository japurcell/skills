Loading required benchmark inputs, then I’ll write `outputs/decision.md` exactly from the skill’s dry-run rules.

Writing the dry-run decision file now with the exact startup action shape and resolved wave details.

1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` is `2` with ready story IDs `US-002` and `US-003`.
4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; for this wave, dispatch `US-002` and `US-003` in parallel, and do not start higher-batch work.
