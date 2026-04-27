# Stop Gates

Stop gates are explicit checkpoints between phases. The agent must not proceed past a gate until every condition listed under that gate is satisfied. In this workflow, gate state is represented by GitHub issue state, issue bodies, and issue comments rather than local artifact files.

---

## Gate A — After Phase 3 (Codebase Exploration)

**Condition**:

- The Phase 3 exploration issue is closed.
- The `files.csv` artifact subissue is closed.
- The `open-questions` artifact subissue exists.

**Failure handling**:

- If the agent could not fully explore, record a partial summary in the exploration issue body and mark the limits clearly.
- Still create the `open-questions` artifact issue so the unresolved areas can move into research.
- Do **not** proceed to Phase 5 with unexplored blocking areas — convert them to open questions first.

**Human action required**: no — gate is checked automatically.

---

## Gate B — After Phase 4 (Online Research)

**Condition**:

- The Phase 4 research issue is closed.
- The `sources.md` artifact subissue is closed.
- The `open-questions` artifact issue has no question left at `status: open`.
- Every question is marked `resolved` or `needs-human`.

**Failure handling**:

- If a research agent could not access a required resource, record that in the research issue with `confidence: low`, create or update the sources artifact entry, and escalate the relevant question to `needs-human`.

**Human action required**: no — gate is checked automatically.

---

## Gate C — After Phase 5 (Clarification)

**Condition**:

- The Phase 5 clarification issue is closed.
- The `open-questions` artifact issue is closed.
- No entry in the `open-questions` artifact issue has both `blocking: true` and `status: unanswered`.

**How to determine blocking vs non-blocking**:

- A question is `blocking: true` if proceeding without an answer would require a design assumption that materially affects implementation scope, user-facing behaviour, or security posture.
- A question is `blocking: false` if a reasonable default exists, a safe assumption can be stated, or the question affects only a non-critical detail.

**Failure handling**:

- If the human does not respond within the session, update the clarification issue and the `open-questions` issue with `status: unanswered`.
- If the unanswered question is non-blocking, record the assumption taken and proceed.
- If the unanswered question is blocking, stop and wait for the human.

**Human action required**: yes, if any `blocking: true` questions exist. Otherwise no.

---

## Gate D — After Phase 6 (Plan)

**Condition**:

- The Phase 6 plan issue is closed.
- The plan issue contains an explicit approval comment from the human.

**Approval process**:

1. Present a concise plan summary (goal, approach, key files, verification steps).
2. Ask for explicit approval: "Does this plan look correct? Should I proceed with implementation?"
3. Record the approval as a comment on the plan issue.
4. Close the plan issue immediately after approval.
5. If the human requests changes, update the plan issue body and repeat.

**Failure handling**:

- If the human does not respond, do not proceed past this gate.
- If the human rejects the plan, revise the plan issue body and keep the issue open.

**Human action required**: yes — explicit approval is always required.

---

## Gate E — After Phase 7 (TDD Task Graph)

**Condition**:

- The Phase 7 task-graph issue is closed.
- At least one implementation task issue has `stage: red`.
- Every implementation task issue has an explicit dependency list.
- No circular dependencies exist in the task graph YAML.

**Failure handling**:

- If the task graph cannot be decomposed into vertical slices, split it into at least a minimal working slice plus a follow-up slice.
- If a circular dependency is detected, revise the task graph issue body and task issue metadata before proceeding.

**Human action required**: no — gate is checked automatically.

**Mandatory session boundary after Gate E**:

1. Stop after Phase 7 once Gate E is satisfied.
2. Tell the human to resume from a fresh session with `coding-task-workflow RESUME=<slug>`.
3. Do **not** begin Phase 8 in the same conversation.
4. This is a hard stop to keep the implementation context window lean enough for Phases 8–11.

---

## Gate F — After Phase 10 (Verification)

**Condition**:

- The Phase 10 verification issue is closed.
- Every intake acceptance criterion is recorded in the verification issue with `result: pass`.
- All automated checks exit with code 0.
- No `severity: High` finding in the review issue remains open.

**Failure handling**:

- If a test fails: return to Phase 8, fix the failing behaviour, update the relevant task issue, and re-run verification.
- If a High-severity finding remains open: return to Phase 8 to fix it before closing the review issue.
- If a required check cannot run, document that explicitly in the verification issue under `## Limitations` and provide manual evidence instead.
- Do **not** open a PR with failing checks or unresolved High findings.

**Human action required**: no — gate is checked automatically.

---

## Gate Violation Protocol

If an agent discovers that it has proceeded past a gate without satisfying its conditions, it must:

1. Stop the current phase.
2. Note the violation in the active phase issue body or a comment.
3. Return to the violated gate's phase and satisfy the missing conditions.
4. Resume from the corrected phase.

---

## Summary Table

| Gate | After phase     | Conditions                                                | Human required                    |
| ---- | --------------- | --------------------------------------------------------- | --------------------------------- |
| A    | 3 Exploration   | Exploration issue closed, files artifact closed           | No                                |
| B    | 4 Research      | Research closed, `sources.md` closed, no open questions remain | No                           |
| C    | 5 Clarification | Clarification closed, `open-questions` closed, no unanswered blocking questions remain | Yes (if blocking questions exist) |
| D    | 6 Plan          | Plan issue approved and closed                            | Yes (always)                      |
| E    | 7 Task graph    | Task graph closed, at least one RED task issue exists     | No — then hard-stop and resume    |
| F    | 10 Verification | Verification closed, all criteria pass, no open High finds | No                               |
