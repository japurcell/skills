# Handoff Plan: feature-dev Stricter Handoff-Policy Enforcement

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: feature-dev skill — handoff artifact policy
**Recommended Next Step**: implement directly

---

## Summary

The request is to strengthen the handoff-policy enforcement in the feature-dev skill so that agents reliably create and report a handoff artifact whenever they stop before completing implementation. The current skill defines clear conditions for when an artifact is required but lacks an explicit pre-stop gate that prevents silent omission. This handoff targets the SKILL.md file and one supporting section, scoped to three localized additions plus one wording change.

---

## Goal / Non-Goals

- **Goal**: Add an explicit pre-stop enforcement gate that blocks a response from concluding without a handoff artifact when conditions are met.
- **Goal**: Make `Artifact Status` a required response section on Standard and Deep track stops, not an optional one.
- **Goal**: Strengthen the Phase 5 reminder so that stopping without the artifact is framed as a violation, not just a suggestion.
- **Non-goal**: Change which conditions trigger the artifact — the existing four conditions are correct.
- **Non-goal**: Modify `references/handoff-plan-template.md` — the template structure is already adequate.
- **Non-goal**: Add enforcement to the Light track for optional cases.

---

## Relevant Findings

- `skills/feature-dev/SKILL.md` — Primary file to modify. Handoff policy lives in the "Handoff Artifact" section (subsections: Required Path, Template, When It Is Required, Minimum Content, Quality Bar). The `Default Response Shape` section lists `Artifact Status` as present only "when one is created or updated", making it silently omittable.
- `skills/feature-dev/SKILL.md` (Phase 5) — Action 7 reads: "If you are not implementing yet, produce or update the handoff artifact before stopping." This is the right hook but uses soft language.
- `skills/feature-dev/references/handoff-plan-template.md` — Template is complete and well-structured; no changes needed here.

---

## Technical Context and Constraints

- Language / framework: Markdown with YAML frontmatter — no code execution.
- Existing conventions: The skill uses imperative action lists. New enforcement language should match the existing tone (direct, concise, not bureaucratic).
- Constraint: Changes must not add process to Light track work completed in a single turn — the existing carve-out for that case must be preserved.
- Constraint: The `Artifact Status` section must remain optional for Light track single-turn completions and for non-stopping responses.
- Validation surface: Re-run this same eval prompt after changes and confirm the response includes a populated `Artifact Status` line without any special instruction to do so.

---

## Assumptions / Open Questions

- **Assumption**: "Stricter enforcement" means adding enforcement language and a checklist gate inside the skill, not building external tooling or CI validation.
- **Assumption**: No companion changes are needed in agent files (`agents/code-explorer.md`, etc.) — the policy lives entirely in SKILL.md.
- **Risk if wrong**: If the intent was to add programmatic validation (e.g., a lint script checking responses), the implementation slices below do not cover that and would need a separate track.

---

## Recommended Design

**Add a `Pre-Stop Gate` subsection** immediately after the existing `Quality Bar` in the Handoff Artifact section. This is a short, numbered checklist an agent must confirm before ending any Standard or Deep track response that stops before completing implementation. This is more effective than adding more "when required" conditions because it makes omission a visible, named gap rather than a silent default.

Pair this with two supporting changes:

1. Strengthen the `Artifact Status` description in the Default Response Shape to make it required for Standard/Deep stops (not just "when one is created").
2. Replace the soft "produce or update the handoff artifact" phrasing in Phase 5, action 7 with an explicit prohibition.

**Why this over alternatives**: An alternative would be to add a checklist before every section. That would add noise to every response. A targeted pre-stop gate keeps the overhead minimal while closing the specific gap.

---

## Implementation Slices

### Slice 1: Strengthen Phase 5 action 7

- **Outcome**: The Phase 5 reminder explicitly states that stopping without the artifact is a violation when conditions are met.
- **Files**: `skills/feature-dev/SKILL.md` (Phase 5, action 7)
- **Dependencies**: None

### Slice 2: Make `Artifact Status` required for Standard/Deep stops

- **Outcome**: The `Artifact Status` entry in the Default Response Shape clarifies it is required on Standard and Deep track when stopping before implementation (not merely "when one is created").
- **Files**: `skills/feature-dev/SKILL.md` (Default Response Shape section)
- **Dependencies**: None (can be done in parallel with Slice 1)

### Slice 3: Add `Pre-Stop Gate` subsection

- **Outcome**: A new subsection after `Quality Bar` in the Handoff Artifact section provides a short numbered checklist the agent must clear before concluding any non-implementation Standard or Deep response.
- **Files**: `skills/feature-dev/SKILL.md` (Handoff Artifact section, after Quality Bar)
- **Dependencies**: Slices 1 and 2 should be done first so the gate cross-references them consistently, but there is no hard technical dependency.

---

## File-by-File Implementation Map

### `skills/feature-dev/SKILL.md`

**Change 1 — Default Response Shape, `Artifact Status` entry**

Current text (approximate):

```
6. `Artifact Status` - the path to the handoff artifact when one is created or updated
```

Replace with:

```
6. `Artifact Status` - **Required on Standard and Deep track when stopping before implementation.** Report the exact path to the handoff artifact, or explicitly state why no artifact is needed (Light track single-turn completion only).
```

**Change 2 — Phase 5, action 7**

Current text:

```
7. If you are not implementing yet, produce or update the handoff artifact before stopping
```

Replace with:

```
7. **Mandatory**: If you are not implementing and Standard or Deep track conditions are met, you MUST produce or update the handoff artifact before stopping. Ending the response without it is a policy violation.
```

**Change 3 — Handoff Artifact section, add `Pre-Stop Gate` after `Quality Bar`**

Add new subsection:

```markdown
### Pre-Stop Gate

Before ending any Standard or Deep track response that stops before implementation, confirm all of the following:

1. One of the "When It Is Required" conditions is explicitly met or explicitly does not apply.
2. The artifact has been written to the required path (`.agents/scratchpad/<feature-name>/handoff-plan.md`).
3. All Minimum Content sections are present in the artifact.
4. `Artifact Status` in your response includes the exact file path.

If any item is unconfirmed, do not end the response — create or complete the artifact first.
```

---

## Validation Plan

- **Automated**: None (Markdown skill file; no test runner).
- **Manual — primary**: Run this eval prompt again against the updated skill and confirm the response includes a populated `Artifact Status` section without any external prompt to do so.
- **Manual — regression**: Run a Light track prompt that completes in one turn and confirm no new `Artifact Status` requirement is forced.
- **Review focus**: Verify the `Pre-Stop Gate` language does not introduce friction for Light track or fully-completing responses.

---

## Next-Agent Kickoff

1. Read `skills/feature-dev/SKILL.md` — specifically the Default Response Shape, Phase 5, and Handoff Artifact sections.
2. Apply the three changes in the File-by-File Implementation Map above.
3. For Change 3, insert the `Pre-Stop Gate` subsection immediately after the closing paragraph of `Quality Bar`.
4. Confirm you have not accidentally changed the Light track carve-out ("For Light track work that you complete in the same turn, the artifact is optional").
5. Re-run the Validation Plan before handing back.
