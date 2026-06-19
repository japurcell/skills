1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/overlap-serialize-fixture/progress.txt`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` 2 — `US-002` "Show billing threshold warning" and `US-003` "Show billing retry banner".
4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; these stories overlap on `src/ui/BillingSettingsPage.tsx`, so serialize instead of dispatching them in parallel, run `US-002` first then `US-003`, and do not start higher-batch work until wave resolves.
