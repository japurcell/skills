Orchestrator next actions:
1. Append implementer Progress block from mode: review_fix before acting on it.
2. Rerun code-simplifier on combined final state.
3. Rerun requirements-collector on prd.json, progress.txt, and any relevant sibling docs / issue refs.
4. Rerun addy-code-reviewer on combined final state after simplification.
5. If review is clean, run final checks, then set passes: true only after review is clean and final checks pass.

Do not mark completion yet. Do not set passes: true until review is clean and final checks pass.