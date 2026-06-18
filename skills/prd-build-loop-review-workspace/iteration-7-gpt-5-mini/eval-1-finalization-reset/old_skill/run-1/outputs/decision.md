Restore review-fix iteration count from progress_file (value recorded = 1).

1. Append fresh implementer `Progress block` from `mode: review_fix` to `progress_file` before acting on it.
2. Rerun `code-simplifier` on combined final state; append its `Progress block`.
3. Rerun `requirements-collector`; append its `Progress block`.
4. Rerun `addy-code-reviewer` on simplified combined state; append its `Progress block`.
5. If reviewer finds issues:
   a. If review-fix iteration count >= 3: append orchestrator stop-state entry to `progress_file` and ask user to decide/blocker.
   b. Else: increment review-fix iteration count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, then go to step 2.
6. If review is clean: run required final-state verification checks, append orchestrator verification entry, then set `passes: true` only if Completion Gate satisfied.
7. After setting any `passes: true`, reread `prd_file`. If every story has `passes: true`, respond exactly: <promise>COMPLETE</promise>. Otherwise append orchestrator stop-state entry and ask user to unblock specific remaining items.