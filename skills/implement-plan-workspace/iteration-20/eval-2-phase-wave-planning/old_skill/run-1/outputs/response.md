Checklist Gate
- PASS — all checklists assumed complete.

Implementation Context Loaded
- Active phase: Tests.
- Remaining tasks: T003 parser tests, T004 ranking tests, T005 suggestions tests, T006 shared helpers, T007 parser implementation.
- TDD constraint: T007 waits for T003 to reach clean RED.

Phase Execution
- W1 (parallel): Launch W1-A (T003), W1-B (T004), and W1-C (T005) in parallel as separate implementation subagents.
  - W1-A: tests/notify/parser.test.ts
  - W1-B: tests/notify/ranking.test.ts
  - W1-C: tests/notify/suggestions.test.ts
  - Verification target: each new test file reaches clean RED. Missing implementation/module-not-found is acceptable clean RED here; syntax errors in the test file, import crashes caused by the test itself, or invalid test setup are not.
- Wait for W1 results before launching W2.
- If any W1 task fails, let already-launched independent work finish; the controller does not launch another wave until the failure has been reported to the user and resolved.
- W2 (sequential): Run T006 in tests/notify/helpers.ts.
  - Reason: shared helper changes affect the phase-wide test surface, so keep them serialized after W1 findings are known.
  - Verification target: helpers load cleanly and W1 tests still fail only for the intended clean RED reasons.
- Wait for W2 results before launching W3.
- W3 (sequential): Run T007 in src/notify/parser.ts.
  - Reason: T007 depends on T003 and must not start before parser tests exist.
  - Verification target: parser compiles and parser-focused tests pass.
- Wait for W3 results before leaving the Tests phase.

Checkpoint Decision
- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- PASS: T003-T007 verified, no missing outputs, and phase-scope tests behave as expected.
- PASS WITH DEFERRED ITEMS: any deferred or unverified work remains explicitly unmarked [ ] and is called out with owner/next step.
- FAIL: any clean-RED check is actually a broken test, any task verification fails, any expected file/output is missing, or any [X] task fails the integrity check.
- Evidence: tasks attempted/completed, files changed, RED/GREEN state, commands run, blockers, and deferments.
- Integrity check: confirm no [X] task points to a missing file; confirm T003 produced clean RED before T007; confirm related notify tests pass after T007.
- Next Action: advance only on PASS or approved PASS WITH DEFERRED ITEMS; otherwise resolve blockers first.

Code Review Findings
- Not started in this phase handoff.

Completion Validation
- Pending later review and final cross-phase validation.
