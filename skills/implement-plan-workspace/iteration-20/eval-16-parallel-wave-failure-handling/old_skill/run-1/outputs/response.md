Checklist Gate
- Status: PASS. All checklists pass, so the controller proceeds into the Integration phase.

Implementation Context Loaded
- Loaded `.agents/scratchpad/feature-webhooks/plan.md` and `tasks.md` for the webhook feature.
- Active phase: Integration.
- Ready parallel work: T020, T021, and T022.

Phase Execution
- **W1**
  - **W1-A:** T020 — add webhook contract tests in `tests/webhooks/contract.test.ts`.
  - **W1-B:** T021 — implement webhook retry policy in `src/webhooks/retry.ts`.
  - **W1-C:** T022 — implement webhook signature verifier in `src/webhooks/signature.ts`.
- Launch W1-A (T020), W1-B (T021), and W1-C (T022) in parallel as separate implementation subagents.
- Wait for W1 results before launching W2.
- W1-A returns first with failed verification: `tests/webhooks/contract.test.ts` has a syntax error. This is **not** a clean RED; it is a broken test.
- Controller action for T020: report the failure with the file and error context, leave T020 as `[ ]` in `tasks.md`, and do not mark it complete.
- W1-B returns with passing task-local verification for `src/webhooks/retry.ts`.
- Controller action for T021: mark T021 as `[X]` because its own verification passed.
- W1-C is already running when T020 fails, so the controller lets that already-launched independent work finish and collects its result before any checkpoint decision.
- The controller does not launch another wave until the failure has been reported to the user and resolved.

`tasks.md` immediately after T020 fails and before T022 finishes:
```md
- [ ] T020 [P] add webhook contract tests in tests/webhooks/contract.test.ts
- [X] T021 [P] implement webhook retry policy in src/webhooks/retry.ts
- [ ] T022 [P] implement webhook signature verifier in src/webhooks/signature.ts
```

- After T022 finishes, the controller records its outcome separately:
  - if T022 passes its own verification, mark only T022 as `[X]`;
  - if T022 fails, leave T022 as `[ ]`.
- Either way, no W2 is launched yet because the wave has a reported failure on T020.

Checkpoint Decision
- Status: FAIL
- Evidence: T020 failed verification due to a syntax error in the new test file; T021 passed verification and is marked `[X]`; T022 was allowed to finish because it was already in flight.
- Integrity check: T020 remains `[ ]` because broken-test verification does not satisfy the RED-step rule. T021 is `[X]` only because its own verification passed. T022 is not marked complete until its own result is collected and verified.
- Next Action: fix the syntax error in `tests/webhooks/contract.test.ts`, rerun T020 verification, then decide whether the controller can resume scheduling.

Code Review Findings
- Not started for this checkpoint; the Integration phase is blocked on the failed wave result.

Completion Validation
- Not complete. Integration cannot advance past this failed wave yet.
- The controller has reported the failure, preserved correct `tasks.md` state, and paused further wave launches until T020 is resolved.
