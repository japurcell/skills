Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
Selected story: `story-billing-retry`.

Next orchestrator actions:
1. Append the fresh implementer `Progress block` from `mode: review_fix` before acting on it.
2. Rerun `code-simplifier` on the combined final state.
3. Rerun `requirements-collector`, then `addy-code-reviewer`.
4. Keep `passes: true` blocked until review is clean and final checks pass.
