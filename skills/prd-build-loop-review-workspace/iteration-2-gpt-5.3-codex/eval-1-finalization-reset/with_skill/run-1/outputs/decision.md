1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` on combined final state.
3. Rerun `requirements-collector`, then rerun `addy-code-reviewer` after simplification.
4. Do not set `passes: true` until review is clean and final checks pass.
