# Runtime-local auto-ingest hooks share one repo manifest

Source auto-ingest now runs through dedicated startup hook entrypoints in `.copilot/hooks/scripts/` and `.gemini/hooks/scripts/`, not through the existing required-skill injectors. Each runtime keeps its executable logic local to its own hook tree, while both write the same committed manifest at `.agents/memory/sources/source-ingest-manifest.json` so source changes, stale summaries, and orphan cleanup stay consistent across tools without introducing cross-runtime shared hook code.
