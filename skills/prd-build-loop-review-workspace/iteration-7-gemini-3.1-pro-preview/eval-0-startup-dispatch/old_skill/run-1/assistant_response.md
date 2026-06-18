Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
Resolved `progress_file`: dirname(prd_file) + "/progress.txt" or explicit provided path.
Selected story: highest-priority `passes: false` story.
Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
