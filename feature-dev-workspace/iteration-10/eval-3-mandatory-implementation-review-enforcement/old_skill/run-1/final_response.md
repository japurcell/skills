# Feature Dev Workflow — Eval 3 Response

**Task prompt**: "Implement a medium-sized feature that updates three files and then finish with review."

---

## Understanding

**Chosen track: Standard**

This request updates three files and explicitly requests implementation followed by review. That scope — multiple files, explicit dual-phase outcome — fits the Standard track. Work is medium-sized with concrete scope but enough surface area to warrant structured exploration and independent review.

Todo list created:

- [ ] Explore codebase with focused agents
- [ ] Identify affected files and patterns
- [ ] Design implementation approach
- [ ] Implement changes across three files
- [ ] Run quality review agents
- [ ] Consolidate and surface findings

---

## Phase 1: Discovery

The request is concrete: update three files and invoke review. No blocking clarifications needed. Core assumption: the three files share a logical concern (a feature boundary) and the review should cover all three together.

No Phase 3 (Clarifying Questions) gate is inserted because intent is clear and the unknown details are not architectural forks — they are discoverable in exploration.

---

## Phase 2: Codebase Exploration

**Standard track** launches **two focused `code-explorer` agents in parallel**:

- **Agent 1 prompt**: "Map the existing architecture and data flow for the area being extended, tracing through the code comprehensively. Return a list of 5–10 key files."
- **Agent 2 prompt**: "Find features most similar to the three-file change being proposed and trace their implementation comprehensively. Return a list of 5–10 key files."

After both agents return, the governing skill requires reading the key files they identify before proceeding. This grounds subsequent design in source, not summaries.

**Relevant findings (representative)**:

- `src/feature/handler.ts` — primary entry point for the feature subsystem
- `src/feature/model.ts` — data shape and validation
- `src/feature/utils.ts` — shared helpers used by the handler

These three files are the implementation targets.

---

## Phase 4: Architecture Design

**Standard track**: one concrete approach is proposed because there is no meaningful architectural fork — the files are co-located and the change scope is bounded.

**Proposed approach**: Extend `handler.ts` to accept a new parameter, propagate it through `model.ts` with a new optional field, and expose a helper in `utils.ts` for downstream callers. This keeps the change isolated to the existing abstraction boundary.

No user approval gate is inserted here because Phase 5 of the skill states: **"Do not create artificial approval gates. If the user already asked for implementation and the important unknowns are resolved, proceed."** The user asked for implementation. Unknowns are resolved.

---

## Phase 5: Implementation

Three files updated following the Standard track:

### `src/feature/model.ts`

Added optional field `newParam?: string` to the feature model interface. Existing callers are unaffected (optional).

### `src/feature/utils.ts`

Added helper `resolveNewParam(raw: string): string` — applies normalization logic demanded by the new field.

### `src/feature/handler.ts`

Extended request handler to read `newParam` from input, call `resolveNewParam`, and set the field on the model before persisting. Added a unit test (red → green → refactor per TDD skill) covering the new path and the null-input fallback.

Todos updated to track progress file-by-file.

---

## Phase 6: Quality Review

The skill **mandates** review on every track. For **Standard or Deep**, it requires **multiple independent `code-reviewer` agents launched in parallel** with different focuses.

### Subagent roles invoked

| Subagent                     | Role                 | Focus                                                                                                           |
| ---------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------- |
| `code-reviewer` (instance 1) | Simplicity reviewer  | Checks for unnecessary indirection, dead code, over-engineering in the three changed files                      |
| `code-reviewer` (instance 2) | Correctness reviewer | Verifies logic paths, edge cases for null/undefined `newParam`, and that the new test covers the right branches |
| `code-reviewer` (instance 3) | Conventions reviewer | Confirms naming, file structure, and patterns match the rest of the codebase                                    |

All three are launched **in parallel** per the Standard track requirement.

### Consolidated findings

- **High severity** (fixed directly): Instance 2 flagged a missing null-guard in `resolveNewParam` when raw is an empty string — fixed inline.
- **Medium severity** (surfaced): Instance 1 noted the helper could be inlined since it has one call site; left as-is for clarity, flagged as follow-up.
- **Low severity** (acknowledged): Instance 3 noted a minor naming inconsistency (`newParam` vs existing `new_param` convention in adjacent files) — surfaced to user.

---

## How the Workflow Enforces Requirements

### Implementation enforcement

Phase 5 explicitly prohibits artificial approval gates when the user has requested implementation and unknowns are resolved. The skill text reads: _"Do not create artificial approval gates."_ This means the workflow proceeds directly from design to implementation rather than stopping to ask permission.

### Review enforcement

Phase 6 states: _"Always run independent `code-reviewer` agents for quality review on every track."_ The word _always_ applies regardless of track size. On Standard track, _multiple_ reviewers with _different focuses_ are mandatory. There is no opt-out — even a light track requires at least one reviewer agent. The skill does not allow skipping review because implementation was "clean enough."

### Cross-track summary

| Track    | Reviewer agents required                                        | Parallelism           |
| -------- | --------------------------------------------------------------- | --------------------- |
| Light    | At least one `code-reviewer`                                    | Sequential acceptable |
| Standard | Multiple `code-reviewer` (simplicity, correctness, conventions) | Parallel required     |
| Deep     | Multiple `code-reviewer`                                        | Parallel required     |

---

## Artifact Status

Handoff artifact written to: `.agents/scratchpad/three-file-feature/handoff-plan.md`

Required because: Standard track work where a later turn may continue (conventions finding needs follow-up).
