Checklist Gate
- Assumed PASS for all checklists.

Implementation Context Loaded
- Plan: `.agents/scratchpad/feature-notify/plan.md`
- Active phase: Tests
- Remaining tasks: T003 parser tests, T004 ranking tests, T005 suggestions tests, T006 shared helpers, T007 parser implementation after T003
- Files in scope: `tests/notify/parser.test.ts`, `tests/notify/ranking.test.ts`, `tests/notify/suggestions.test.ts`, `tests/notify/helpers.ts`, `src/notify/parser.ts`

Phase Execution
- W1 (parallel, TDD-first): Launch W1-A (T003), W1-B (T004), and W1-C (T005) in parallel as separate implementation subagents.
- Success for each W1 member: run the new test file and confirm a `clean RED`; this is the expected result in TDD-first / RED-GREEN workflow and is not a broken test. Syntax errors in the test file, import crashes caused by the test itself, or invalid test setup do not count as `clean RED`.
- Wait for W1 results before launching W2. If any W1 member fails outside `clean RED`, allow already-launched independent work to finish; the controller does not launch another wave until the failure has been reported to the user and resolved.
- W2 (sequential): Run T006 to update `tests/notify/helpers.ts`. Keep this serialized because it changes shared test infrastructure for the notify test area.
- Wait for W2 results before launching W3.
- W3 (sequential): Run T007 in `src/notify/parser.ts` only after T003 shows `clean RED`. T003 and T007 cannot run in parallel because T007 depends on T003’s RED evidence and then must turn the parser path GREEN.
- Wait for W3 results before closing the phase.

Checkpoint Decision
- Status: PASS if T003-T007 all have verification evidence; PASS WITH DEFERRED ITEMS only if work is complete but a shared validation step is still pending and no task is marked `[X]` speculatively; FAIL if any task lacks required evidence or any checkpoint integrity error appears.
- Evidence: T003-T005 show `clean RED` outputs; T006 helper updates validate under phase-scope test execution; T007 passes parser-focused tests after implementation; changed files stay within assigned scope.
- Integrity check: Re-run the Tests phase scope. If any `[X]` task has missing outputs or failing tests, revert it to `[ ]` before proceeding.
- Next Action: Advance only if the checkpoint passes; otherwise resolve blockers before the next phase.

Code Review Findings
- Pending this phase.

Completion Validation
- Pending this phase. Before advancing, confirm `tasks.md` reflects the verification evidence and the Tests phase scope passes.
