# Enforce pending ingest before normal work

Status: superseded by the brain migration on 2026-10-20. The text below records the historical system; current behavior is documented in [brain hooks](../../brain/codebase/brain-hooks.md).

When `.agents/memory/sources/source-ingest-manifest.json` contains `needs_summary` or `stale` entries, Copilot and Gemini must block normal agent flow until `/ingest-source` clears all blocking entries and the affected summaries are no longer scaffolds. Pending state is derived from the manifest on every applicable turn, with prompt-time steering plus a final-response backstop so both runtimes enforce the same contract. If `/ingest-source` is unavailable, the gate stays active and surfaces an inline recovery checklist; only test and debug configuration may bypass the gate.
