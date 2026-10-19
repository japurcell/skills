Derive three sequential tasks mapped to the milestone's Progress entries, not a single whole-milestone task:
1. **T1 (Feasibility/Decision):** Bounded task to resolve parser feasibility. Prerequisites: none.
2. **T2 (Implementation):** Compatible parser/summary vertical slice. Prerequisite: T1 complete with recorded decision and evidence.
3. **T3 (Parity Verification / Milestone Integration Check):** Verify legacy versus new CLI outputs, including malformed-input failures, on the integrated result. Prerequisite: T2.

Only T1 enters the current frontier because T2 and T3 depend on unfinished feasibility.

Give the T1 worker the smallest sufficient task packet: current requirements, the shared default-output invariant, relevant design context, negative cases (malformed-input failure handling), verification criteria, promotion/rework/discard criteria, stop condition (stop after feasibility and decision evidence; do not implement the vertical slice), and source entry points. For a read-only/decision outcome, require task-appropriate evidence without inventing product code or empty commits. After T1, reconcile the `Decision Log`, `Surprises & Discoveries`, `Progress`, and `Plan of Work` before dispatching T2.

The milestone is proved complete only after T1 and T2 finish and the composed-behavior parity check (T3) runs on the integrated base branch, proving identical legacy and new CLI outputs, the shared default-output invariant, and malformed-input error cases with retained evidence.
