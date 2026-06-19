1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` 2 and ready story IDs US-002, US-003.
4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; if stories overlap, serialize instead of dispatching them in parallel, cite the shared owner surface or exact file `src/ui/BillingSettingsPage.tsx`, give dispatch order US-002 then US-003, and do not start higher-batch work.
