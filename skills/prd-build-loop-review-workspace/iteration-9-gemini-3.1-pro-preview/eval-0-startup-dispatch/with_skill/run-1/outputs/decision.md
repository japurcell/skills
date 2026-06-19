1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`.
3. Selected story: highest-priority `passes: false` story.
4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.