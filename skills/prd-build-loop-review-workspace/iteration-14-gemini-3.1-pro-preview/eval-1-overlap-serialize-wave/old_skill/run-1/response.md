I_CAN_SEE_SESSIONSTART_CONTEXT2026-06-18T22:57:44.865-07:00

1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` 2 and ready story IDs US-002, US-003.
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.

US-002 and US-003 share `src/ui/BillingSettingsPage.tsx`. Serialize within the same wave by priority: dispatch US-002 (priority 2) first, wait for completion, then dispatch US-003 (priority 3).
