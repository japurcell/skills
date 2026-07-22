Got it — I’ll load the exact benchmark skill file and the two fixture inputs, then produce `outputs/decision.md` only.

1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` on combined final state.
3. Rerun `requirements-collector`, then `addy-code-reviewer`.
4. Keep `passes: true` blocked until review is clean and final checks pass.
5. Parallel helpers in this stage: none; do not run `code-simplifier` and `requirements-collector` concurrently.
6. Required wait point: `addy-code-reviewer` must wait until both reruns finish and their `Progress block`s are appended.
