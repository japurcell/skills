1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` is `2`; ready story IDs are `US-002` and `US-003`.
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.

`US-002` and `US-003` share likely-touched owner file `src/ui/BillingSettingsPage.tsx`, so they are not parallel-safe inside wave `2`. Safe dispatch plan: serialize by priority within current wave, dispatch `US-002` first, append and record its result, then dispatch fresh implementer for `US-003`. Keep `US-004` blocked until wave `2` fully resolves.
