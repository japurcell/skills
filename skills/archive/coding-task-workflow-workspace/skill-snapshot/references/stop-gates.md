# Stop Gates

Stop gates are explicit checkpoints between phases. The agent must not proceed past a gate until every condition listed under that gate is satisfied. Gates exist to prevent wasted work and to ensure human oversight at the right moments.

---

## Gate A — After Phase 3 (Codebase Exploration)

**Condition**:

- `02-exploration/summary.md` exists.
- `02-exploration/summary.md` frontmatter has `status: complete`.
- `02-exploration/open-questions.md` exists (may be empty if no open questions).

**Failure handling**:

- If the agent could not fully explore (e.g., repository is very large), write a partial summary with `status: partial` and note which areas were not covered.
- Proceed to Phase 4 with the partial summary; exploration gaps become research questions.
- Do **not** proceed to Phase 5 (Clarification) with unexplored blocking areas — convert them to research questions first.

**Human action required**: no — gate is checked automatically.

---

## Gate B — After Phase 4 (Online Research)

**Condition**:

- `03-research/findings.md` exists.
- `03-research/findings.md` frontmatter has `status: complete`.
- All questions from `open-questions.md` are marked `resolved` or `needs-human` (not `open`).

**Failure handling**:

- If a research agent could not access a required resource (network unreachable, docs behind auth), mark the finding `confidence: low` with a note, escalate to `needs-human`, and continue.
- Record unavailable sources in `03-research/sources.md` with `status: unavailable`.

**Human action required**: no — gate is checked automatically.

---

## Gate C — After Phase 5 (Clarification)

**Condition**:

- `04-clarifications.md` exists.
- No entry in `04-clarifications.md` has both `blocking: true` and `status: unanswered`.

**How to determine blocking vs non-blocking**:

- A question is `blocking: true` if proceeding without an answer would require a design assumption that materially affects the implementation scope, user-facing behaviour, or security posture.
- A question is `blocking: false` if a reasonable default exists, a safe assumption can be stated, or the question only affects a non-critical detail.

**Failure handling**:

- If the human does not respond to a clarification prompt within a session, record the question as `status: unanswered`, document the default assumption taken, and proceed if `blocking: false`.
- If `blocking: true` and no answer: do not proceed. Persist the artifact and record the reason in `04-clarifications.md`. Resume when the human provides an answer.

**Human action required**: yes, if any `blocking: true` questions exist. Otherwise no.

---

## Gate D — After Phase 6 (Plan)

**Condition**:

- `05-plan.md` exists.
- `00-intake.md` frontmatter has `plan_approved: true`.

**Approval process**:

1. Present a concise plan summary (goal, approach, key files, verification steps).
2. Ask for explicit approval: "Does this plan look correct? Should I proceed with implementation?"
3. Record the approval in `00-intake.md` frontmatter: `plan_approved: true`, `plan_approved_at: <ISO timestamp>`.
4. If the human requests changes: update `05-plan.md`, present the updated summary, and repeat.

**Failure handling**:

- If the human does not respond, do not proceed past this gate. Persist all artifacts.
- If the human rejects the plan, document their feedback in `05-plan.md` under `## Revision History` and revise.

**Human action required**: yes — explicit approval is always required.

---

## Gate E — After Phase 7 (TDD Task Graph)

**Condition**:

- `06-task-graph.yaml` exists.
- At least one task with `stage: red` is present.
- All tasks have explicit `depends_on` lists (empty list `[]` is valid for root tasks).
- No circular dependencies exist in the graph.

**Failure handling**:

- If the task graph cannot be decomposed into vertical slices (e.g., the plan describes a single monolithic change), split the plan into at least two slices: a minimal working version and an enhancements slice.
- If a circular dependency is detected, resolve it by adding an intermediate task or re-ordering slices.

**Human action required**: no — gate is checked automatically.

**Mandatory session boundary after Gate E**:

1. Stop after Phase 7 once Gate E is satisfied.
2. Tell the human to resume from a fresh session with `coding-task-workflow RESUME=<slug>`.
3. Do **not** begin Phase 8 in the same conversation. Refuse direct user requests to continue immediately; the correct response is always the resume handoff.
4. This is a hard stop to keep the implementation context window lean enough for Phases 8–11.

---

## Gate F — After Phase 10 (Verification)

**Condition**:

- `09-verification.md` exists.
- Every acceptance criterion in `00-intake.md` is listed in `09-verification.md` with `result: pass`.
- All automated check commands exit with code 0.
- No `severity: High` finding in any `08-review/*.md` is marked `status: open`.

**Failure handling**:

- If a test fails: return to Phase 8, fix the failing behaviour, re-run verification. Repeat until all pass.
- If a High-severity security or code finding is still open: return to Phase 8 to fix it.
- If a test command is unavailable (no test suite): document this explicitly in `09-verification.md` under `## Limitations`, provide manual verification evidence instead, and proceed.
- Do **not** open a PR with failing tests or unresolved High-severity findings under any circumstances.

**Human action required**: no — gate is checked automatically. The agent returns to Phase 8 as many times as needed.

---

## Gate Violation Protocol

If an agent discovers that it has proceeded past a gate without satisfying its conditions (e.g., resuming from a partial artifact), it must:

1. Stop the current phase.
2. Note the violation in a `## Gate Violation` section at the top of the current phase's artifact.
3. Return to the violated gate's phase and re-satisfy the conditions.
4. Resume from the corrected phase.

This prevents artifact drift where later phases are based on incomplete earlier work.

---

## Summary Table

| Gate | After phase     | Conditions                                | Human required                    |
| ---- | --------------- | ----------------------------------------- | --------------------------------- |
| A    | 3 Exploration   | `summary.md` complete                     | No                                |
| B    | 4 Research      | `findings.md` complete, no open questions | No                                |
| C    | 5 Clarification | No unanswered blocking questions          | Yes (if blocking questions exist) |
| D    | 6 Plan          | Plan approved                             | Yes (always)                      |
| E    | 7 Task graph    | Graph exists, at least one RED task       | No — then hard-stop and resume    |
| F    | 10 Verification | All criteria pass, no open High findings  | No                                |
