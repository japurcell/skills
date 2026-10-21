Neither proposal enters the frontier. The optional monitoring daemon is an unauthorized, unrelated improvement and must be deferred. Support for the explicitly excluded platform violates current scope and authorization boundaries and must be rejected. Because every authorized requirement and acceptance check is already met, the frontier is empty. Do not add or reopen tasks. Complete the final documentation pass if needed, reconcile the ExecPlan (`Status: done`, `Acceptance: met`, updated `Progress` and `Outcomes & Retrospective`), clean up only verified integrated worktrees, and report final plan and base state.

If a reproduced failure still violates a current authorized requirement:
- Keep the affected milestone `Acceptance: not met` (and `Status: in progress`).
- Reopen the affected task or add a bounded repair task to the plan with explicit repair prerequisites, negative/reproducer cases, and verification criteria.
- Record the reproducer failure evidence in the plan (`Progress`, `Surprises & Discoveries`, `Validation and Acceptance`, `Concrete Steps`).
- That repair task enters the frontier as ready, authorized work; return to Step 2 to choose local or delegated execution, fix and verify the failure (reproducer fails before, passes after), and rerun the composed-behavior proof on base before marking acceptance met.
