Next orchestrator actions:

1. Treat latest review-fix implementer change as new final-state baseline.
2. Rerun fresh code-simplifier on combined final state.
3. Run fresh requirements-collector and fresh reviewer after simplification.
4. If review is clean, run required verification checks.
5. If checks pass, record final-state entry and set `passes: true` in `prd.json`.

Do not mark complete yet; finalization must rerun after review-fix.
