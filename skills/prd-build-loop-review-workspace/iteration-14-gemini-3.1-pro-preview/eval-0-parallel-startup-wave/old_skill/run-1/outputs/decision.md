1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: evals/files/startup-fixture/progress.txt
3. Active wave: lowest ready `parallelBatch` (2) and ready story IDs (US-002, US-003).
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.
