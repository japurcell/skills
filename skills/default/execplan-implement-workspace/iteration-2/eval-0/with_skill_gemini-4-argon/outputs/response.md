Derive three distinct tasks mapped to the Progress entries, not one whole-milestone task:
1. Bounded feasibility/decision task for parser unknown (no prerequisites; in-progress frontier).
2. Implementation task for compatible parser/summary vertical slice (prerequisite: feasibility task complete with recorded decision/evidence).
3. Milestone integration/parity verification task comparing legacy and new CLI outputs on the integrated result (prerequisite: implementation task complete).

Only the feasibility task is on the frontier now. Resolve design uncertainty before dependent implementation.

Send the first worker the smallest sufficient task packet:
- Current requirements, shared default-output invariant, and negative cases (malformed-input failures).
- Relevant design context, source entry points, and allowed resources/ownership.
- Deliverable, verification commands/criteria, promotion/rework/discard criteria, and explicit stop boundary (stop after feasibility resolves; do not implement the vertical slice).
- Instruction to use task-appropriate evidence for decision/feasibility work without inventing product tests or code changes if the outcome is read-only.

Milestone acceptance is proven only after the feasibility and vertical-slice tasks complete, changes integrate on base, and the composed-behavior parity check runs on the integrated tree—exercising legacy and new paths on identical valid and malformed-input fixtures—and passes while preserving the shared default-output invariant. Update `Status: done`, `Acceptance: met`, and all `[milestone-X]` Progress entries together with recorded evidence.
