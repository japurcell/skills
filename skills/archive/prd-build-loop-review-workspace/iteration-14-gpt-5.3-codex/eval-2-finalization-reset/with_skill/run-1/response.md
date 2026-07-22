Loading benchmark instructions and fixture context, then I’ll write only the required decision artifact.


I have enough context; now writing the required dry-run decision file.


1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` and `requirements-collector` in parallel on combined final state.
3. After both return, rerun `addy-code-reviewer`.
4. Keep `passes: true` blocked until review is clean and final checks pass.
