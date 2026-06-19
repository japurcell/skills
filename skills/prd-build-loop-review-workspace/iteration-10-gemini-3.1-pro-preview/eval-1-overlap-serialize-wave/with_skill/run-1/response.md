I_CAN_SEE_SESSIONSTART_CONTEXT

I_CAN_SEE_SESSIONSTART_CONTEXT<current_datetime>2026-06-18T20:12:02.379-07:00</current_datetime>

1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` (2) and ready story IDs (US-002, US-003).
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.

Safe dispatch plan:
- Both US-002 and US-003 share the same likely-touched owner file (`src/ui/BillingSettingsPage.tsx`).
- Because of this exact file overlap, they are not parallel-safe.
- They must be serialized by priority within the same wave. 
- US-002 (priority: 2) will be dispatched first.
- US-003 (priority: 3) will only be dispatched after US-002 resolves to avoid conflicts.
