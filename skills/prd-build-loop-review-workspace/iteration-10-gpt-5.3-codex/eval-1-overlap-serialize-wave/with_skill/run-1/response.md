Loading required fixture and skill instructions, then I’ll compute wave/dispatch and write `outputs/decision.md`.
I’ve identified the active ready wave; next I’ll write the dry-run decision file with serialized dispatch due to shared owner file overlap.
1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/overlap-serialize-fixture/progress.txt`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` is `2`; ready story IDs are `US-002` and `US-003`.
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.
5. Overlap conflict signal: `US-002` and `US-003` both likely touch `src/ui/BillingSettingsPage.tsx` (same owner surface), so they are not parallel-safe.
6. Safe dispatch plan: serialize by priority within wave 2 — dispatch `US-002` first, append progress/status, then dispatch `US-003`; do not start `US-004` (`parallelBatch` `3`) until wave 2 resolves.
