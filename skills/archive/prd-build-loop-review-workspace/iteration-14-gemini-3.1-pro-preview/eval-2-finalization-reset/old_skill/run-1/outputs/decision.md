1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` on combined final state.
3. Rerun `requirements-collector`, then `addy-code-reviewer`.
4. Keep `passes: true` blocked until review is clean and final checks pass.