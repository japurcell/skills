1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/default-progress-path-fixture/progress.txt; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` 1 and ready story IDs US-001.
4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.

Forbidden fallback paths: session state, scratchpads, home directories, or ~/.copilot/...
