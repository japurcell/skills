1. Append implementer `Progress block` before acting on it.
2. Run `code-simplifier` and `requirements-collector` in parallel on combined final state.
3. Wait for both helpers, then rerun `addy-code-reviewer`; keep `passes: true` blocked until review is clean and final checks pass.
