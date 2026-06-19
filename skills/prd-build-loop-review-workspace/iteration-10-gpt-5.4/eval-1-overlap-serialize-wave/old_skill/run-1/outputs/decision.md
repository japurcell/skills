Active wave: `parallelBatch: 2`, serialized because `US-002` and `US-003` are both ready and both likely touch shared owner file `src/ui/BillingSettingsPage.tsx`.

1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Selected story: highest-priority `passes: false` story.
4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.

Safe dispatch plan:
1. Treat batch 2 as conflict-serialized wave, not parallel wave, because `US-002` and `US-003` share likely-touched owner file `src/ui/BillingSettingsPage.tsx`.
2. First dry-run dispatch target: `US-002` (`Show billing threshold warning`) because it is highest-priority ready story.
3. Hold `US-003` until `US-002` implementer output is recorded in `progress_file` and loop reselects next ready story from updated official state.
4. Keep `US-004` out of this wave until `US-002` eventually satisfies completion gate in `prd_file`; its dependency remains open while `US-002` is still `passes: false`.
5. After `US-002`, rerun selection; if `US-003` remains ready, dispatch it next as separate serialized unit against updated billing settings page state.
