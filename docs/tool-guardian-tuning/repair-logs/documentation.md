# Final canonical documentation pass

Completed once after all delegated source, original-reviewer and performance work finished. Applied update-agent-docs and the OKF shared profile; no source-summary branch applies. Canonical changes are limited to four existing documents, with unchanged metadata types and stable paths:

- `.agents/instructions/hooks.md`: Agent Instruction; body-only proof, strict remaining arguments, normalized budgets and retained nested executable context.
- `.agents/instructions/repo.md`: Agent Instruction; retained plan, current handoff and repair-log routes.
- `.agents/memory/testing/hooks.md`: Testing Guidance; regression controls, disposable observability override and temporary-log lifetime outside measured elapsed time.
- `.agents/memory/FILE_MAP.md`: Agent Memory; route added retained repair logs/evidence and current handoff.

No API, diagnostic ID, limit, test registration, source file or protected AGENTS section changed in this pass. Existing API and known-issue guidance remains accurate. No new memory concept needs an INDEX entry; file-map and area routes cover the added feature artifacts. Semantic content and nearby related guidance were checked for duplication and stale claims.

Verification:

- `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 scripts/lint-okf.py`: exit 0, no diagnostics, both canonical bundles.
- `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy python3 scripts/generate-hooks.py --check`: exit 0, 29 files current.
- Scoped canonical diff: exactly the four paths above, five line replacements; frontmatter/body outside those rules preserved.
- All 39 frozen runtime and 43 integrated evidence hashes match after these checks. Runtime suites were not repeated for doc-only changes or conflict-free rebases.

Added: None
Changed: Four canonical documents listed above.
Split or moved: None
Deduplicated: None
Index updates: Existing file-map and repo instruction routes; no INDEX.md change needed.
Remaining doc quality TODOs: None

Suggested skill improvement, not implemented: performance guidance could require checking fixture lifetime before post-return logging verification, with deferred cleanup in finally. No skill files were edited.
