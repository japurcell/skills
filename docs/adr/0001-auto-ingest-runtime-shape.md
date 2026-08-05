# Runtime-local auto-ingest hooks share one repo manifest

Source auto-ingest now runs through dedicated startup hook entrypoints in `.github/hooks/scripts/` for Copilot and `.gemini/hooks/scripts/` for Gemini, not through the existing required-skill injectors. Each runtime keeps its executable logic local to its active hook surface, while both write the same committed manifest at `.agents/memory/sources/source-ingest-manifest.json` so source changes, stale summaries, and orphan cleanup stay consistent across tools without introducing cross-runtime shared hook code.
