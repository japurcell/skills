Active wave: parallelBatch 2 (US-002 and US-003).
Conflict: Both stories are dependency-ready but share the likely-touched owner file src/ui/BillingSettingsPage.tsx. According to progress.txt learnings ("Shared owner files are conflict signals inside one wave" and "Serialize overlapping UI stories even when dependency-ready"), they must be serialized.

Safe dispatch plan:
1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Selected story: highest-priority `passes: false` story.
4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.

The orchestrator will pick US-002 (priority 2) first. Only after US-002 satisfies the Completion Gate will US-003 (priority 3) be selected.
