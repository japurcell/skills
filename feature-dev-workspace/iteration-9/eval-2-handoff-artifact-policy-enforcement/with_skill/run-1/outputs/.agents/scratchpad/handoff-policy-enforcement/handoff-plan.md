# Handoff Plan: Stricter Handoff-Policy Enforcement for feature-dev

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: skills/feature-dev — workflow enforcement rules
**Recommended Next Step**: implement directly (all decisions resolved, no blockers)

---

## Summary

The feature-dev skill has a "Handoff Artifact" section with a "When It Is Required" list and a "Quality Bar" checklist, but agents can currently stop before implementation without creating the artifact and still produce a technically compliant response. The root cause is that the enforcement is described as a set of conditions rather than a hard gate, and the `Artifact Status` section in `Default Response Shape` is marked optional ("when one is created or updated"). This handoff adds a mandatory pre-stop gate with explicit stopping rules, promotes `Artifact Status` from conditional to required when stopping before implementation, and extends the Quality Bar to include artifact verification as a pass/fail test.

The work is Standard track: it touches `SKILL.md` with surgical edits and requires a small design decision on where to insert the gate, but there are no architectural unknowns.

---

## Goal / Non-Goals

- **Goal**: Any time an agent stops before completing implementation on Standard or Deep track (or on any track when conditions 2–4 apply), the agent MUST create or update `handoff-plan.md` and include its exact path in `Artifact Status`.
- **Goal**: Insert a short pre-stop gate block that makes the enforcement rule unambiguous and hard to bypass.
- **Goal**: Promote `Artifact Status` in `Default Response Shape` from conditional to required when stopping short of implementation.
- **Non-goal**: Change the template (`references/handoff-plan-template.md`) — it is already adequate.
- **Non-goal**: Add enforcement to Light track same-turn completions — the existing "optional for Light track" policy is intentional.
- **Non-goal**: Change Phase 5 (Implementation) content — it already has the correct side-note.

---

## Relevant Findings

- `skills/feature-dev/SKILL.md` (lines 62–66): `Artifact Status` listed as conditional — "the path to the handoff artifact when one is created or updated". This makes creation feel optional.
- `skills/feature-dev/SKILL.md` (lines 145–149): Phase 5 Implementation note says "If you are not implementing yet, produce or update the handoff artifact before stopping" — correct but buried as an inline aside.
- `skills/feature-dev/SKILL.md` (lines 191–209): "When It Is Required" lists four conditions using "when any of these are true" — the language is permissive and does not say "refusing to stop without the artifact."
- `skills/feature-dev/SKILL.md` (lines 211–221): "Quality Bar" has five checks but does not include "artifact file exists at the required path" as an explicit item, nor is it framed as a hard gate.
- `skills/feature-dev/references/handoff-plan-template.md`: Well-structured. No changes needed.

---

## Technical Context and Constraints

- Language / framework: Markdown instruction file — changes are prose edits, not code changes.
- Existing conventions to preserve: RFC 2119 signal words (MUST, SHOULD) are consistent with the skill's existing style.
- Enforcement mechanism: Instructional language in a Markdown skill — the only "test" is whether an agent following the instructions creates the artifact. The Quality Bar is the closest equivalent to a runtime assertion.
- Validation surface: Manual review of agent responses in eval runs; eval assertions in `evals/evals.json`.

---

## Assumptions / Open Questions

- **Assumption**: Light track same-turn completions remain optional — this is explicitly stated and intentional.
- **Assumption**: "Stopping before implementation" means any response that does not include implementation code changes.
- **Assumption**: The pre-stop gate should be a numbered block, not a new named section, so it stays close to the enforcement descriptions without fragmenting the skill structure.
- **Open question**: None — the task is fully specified.

---

## Recommended Design

**Approach chosen**: Insert a "PRE-STOP ENFORCEMENT" block at the end of the "When It Is Required" section and change `Artifact Status` in `Default Response Shape` from conditional to required when stopping short of implementation.

**Why over the alternative** (adding per-phase stop checks at phases 3 and 4): The per-phase approach would require the same wording repeated twice, increasing maintenance surface. A single gate block at the natural decision point (right after "When It Is Required") is more authoritative and easier to follow.

**Core changes** (three surgical edits):

1. **`Default Response Shape` — `Artifact Status` entry**: Change from "when one is created or updated" to "required whenever stopping before implementation; include the exact path."
2. **"When It Is Required" section** — add a `> **PRE-STOP GATE**` block immediately after the four conditions with explicit language: before any response that stops without implementation, confirm the file exists and include its path in `Artifact Status`; omitting the artifact when required is a workflow violation.
3. **"Quality Bar" section** — add a sixth check: "The artifact file exists at the required path (`.agents/scratchpad/<feature-name>/handoff-plan.md`)."

---

## Implementation Slices

### Slice 1: Strengthen `Artifact Status` in Default Response Shape

- **Outcome**: `Artifact Status` is clearly required, not optional, when stopping before implementation.
- **Files**: `skills/feature-dev/SKILL.md` (lines ~62–66)
- **Dependencies**: none

### Slice 2: Add pre-stop gate block after "When It Is Required"

- **Outcome**: Agents reading the skill see an unambiguous hard rule before reaching Phase 5.
- **Files**: `skills/feature-dev/SKILL.md` (lines ~209–210, after the four conditions)
- **Dependencies**: Slice 1

### Slice 3: Extend Quality Bar with artifact existence check

- **Outcome**: The Quality Bar, used as a final self-check, now explicitly verifies the artifact exists.
- **Files**: `skills/feature-dev/SKILL.md` (lines ~215–221)
- **Dependencies**: Slice 2

---

## File-by-File Implementation Map

### `skills/feature-dev/SKILL.md`

**Edit 1** — `Default Response Shape`, `Artifact Status` line (currently line ~65):

```
# Before
6. `Artifact Status` - the path to the handoff artifact when one is created or updated

# After
6. `Artifact Status` - **required** when stopping before implementation; include the exact path to `handoff-plan.md`
```

**Edit 2** — Add pre-stop gate block immediately after the "When It Is Required" numbered list (after item 4, before "For Light track…"):

```markdown
> **PRE-STOP GATE — HANDOFF REQUIRED**
>
> Before any response that stops without completing implementation, you MUST:
>
> 1. Create or update `handoff-plan.md` at `.agents/scratchpad/<feature-name>/handoff-plan.md`.
> 2. Include `Artifact Status` in your response with the exact file path.
>
> Stopping without the artifact when conditions 1–4 are met is a workflow violation. Do not omit it "for brevity."
```

**Edit 3** — Quality Bar, add a sixth item after the current five:

```
# After item 5, add:
6. The artifact file physically exists at `.agents/scratchpad/<feature-name>/handoff-plan.md` — not just referenced in prose.
```

---

## Validation Plan

- **Automated**: No automated linter; rely on eval assertions.
- **Manual**: Re-run eval 2 after edits. Verify:
  - The response includes an `Artifact Status` section with an exact file path.
  - The file at that path exists.
  - The response does NOT omit the artifact section.
- **Review focus**: Check that the pre-stop gate block does not conflict with or duplicate the Phase 5 side-note. They should be complementary (gate = rule; Phase 5 note = reminder).
- **Eval assertions to add** (in `evals/evals.json` for eval 2):
  - "Response includes an `Artifact Status` section with an exact file path."
  - "Artifact file exists at the path listed in Artifact Status."

---

## Next-Agent Kickoff

1. Read `skills/feature-dev/SKILL.md` (full file) to understand current structure before editing.
2. Read `skills/feature-dev/references/handoff-plan-template.md` for context (no edits needed).
3. Apply the three edits from the File-by-File Implementation Map in order (Slices 1 → 2 → 3).
4. Use `multi_replace_string_in_file` to apply all edits in one call.
5. Re-read the edited sections to verify correctness and that no surrounding context was disturbed.
6. Run the validation plan: confirm eval 2 now passes the `Artifact Status` assertion.
7. Stop and ask if any edit creates a contradiction with an existing rule (e.g., Light track optional exception).
