1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/overlap-serialize-fixture/progress.txt`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` is `2`; ready story IDs: `US-002`, `US-003`.
4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; stories overlap on shared owner surface/exact file `src/ui/BillingSettingsPage.tsx`, so serialize instead of dispatching them in parallel in priority order `US-002` then `US-003`, and do not start higher-batch work (`US-004`) until current wave resolves.
