1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` and ready story IDs.
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.

- Lowest ready `parallelBatch`: `2`
- Ready story IDs: `US-002`, `US-003`
- Conflict signal: both ready stories likely touch shared owner file `src/ui/BillingSettingsPage.tsx`, so current wave is not parallel-safe.
- Safe dispatch order: `US-002` first, then `US-003`, because same-wave overlap must be serialized by priority.
- Higher batch stays blocked: `US-004` cannot start until current wave resolves and `US-002` passes.
