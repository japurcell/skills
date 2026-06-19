Loading only required inputs, then I’ll write `outputs/decision.md` with the dry-run dispatch decision.
Now I’ll write the dry-run decision artifact in `outputs/decision.md`.
1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Selected story: highest-priority `passes: false` story.
4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.

Active wave: `parallelBatch: 2` with ready stories `US-002` and `US-003` (`US-001` already passes, `US-004` blocked by `US-002`).

Shared likely-touched owner file: `src/ui/BillingSettingsPage.tsx`.

Safe dispatch plan (dry-run):
1. Serialize wave-2 execution by shared owner file; do not dispatch `US-002` and `US-003` in parallel.
2. Dispatch `US-002` first (higher priority), keep `US-003` queued.
3. After `US-002` returns, append its `Progress block`, reread `prd_file`, then dispatch `US-003`.
4. Recompute readiness after `US-003`; dispatch `US-004` only after `US-002` is marked passing in `prd_file`.
