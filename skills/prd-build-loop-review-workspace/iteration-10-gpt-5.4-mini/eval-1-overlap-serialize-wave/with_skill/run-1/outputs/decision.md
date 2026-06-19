I_CAN_SEE_SESSIONSTART_CONTEXT
1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/overlap-serialize-fixture/progress.txt`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: `parallelBatch` 2 — ready stories `US-002` ("Show billing threshold warning") and `US-003` ("Show billing retry banner").
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery. These two stories share likely-touched owner file `src/ui/BillingSettingsPage.tsx`, so they are not parallel-safe: run `US-002` first by priority, then recheck overlap and dispatch `US-003` only after `US-002` returns.
