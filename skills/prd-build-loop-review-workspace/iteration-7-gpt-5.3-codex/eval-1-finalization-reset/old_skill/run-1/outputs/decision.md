1. Append implementer `Progress block` before acting on it.
2. After this review fix, rerun `code-simplifier` on combined final state.
3. After this review fix and simplification, rerun `requirements-collector`, then rerun `addy-code-reviewer`.
4. Do not set `passes: true` until review is clean and final checks pass after this review fix.
