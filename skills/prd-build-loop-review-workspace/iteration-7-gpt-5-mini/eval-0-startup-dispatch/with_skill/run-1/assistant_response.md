Source of truth: /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/prd.json (prd_file is official source of truth)

Resolved progress_file: /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt (append-only resume data; already exists)

Selected story: id=story-auth-timeout, title="Auth timeout matches spec", priority=1, passes=false

Before any story-specific repo discovery (startup prerequisites):
- Reread prd_file (official) and progress_file (supplemental) to confirm state.
- Read nearby AGENTS.md only if needed to dispatch implementer.
- Do NOT inspect repo code, tests, or story-specific files before a fresh implementer is dispatched.
- Dispatch fresh implementer with full story properties, prd_file path, progress_file path, and mode.
- Require implementer to return a Progress block and append it to progress_file before any orchestrator consumption of its output.
- If progress_file missing, create it on first append with a leading "## Codebase Patterns" section (dry-run: note only).
