Loading benchmark skill + fixture inputs, then writing dry-run decision.

Writing dry-run decision artifact.

1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` on combined final state.
3. Rerun `requirements-collector`, then `addy-code-reviewer`.
4. Keep `passes: true` blocked until review is clean and final checks pass.

Parallelization:
- `code-simplifier` and `requirements-collector` may run in parallel after step 1.
- `addy-code-reviewer` must wait for both helpers to finish and for simplifier output to define combined final state before final review.
