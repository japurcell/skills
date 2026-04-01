# Understanding

**Track**: Standard — this is scoped, moderately complex work touching 3 specific locations in a single SKILL.md file. There are no external systems or unknown environments; the "codebase" is the feature-dev skill itself. Stopping before implementation as requested.

---

# Relevant Findings

- `skills/feature-dev/SKILL.md` — The handoff policy lives in the **Handoff Artifact** section. Four conditions are stated for "When It Is Required", and a **Quality Bar** checklist covers artifact completeness. However:
  - The `Artifact Status` entry in the **Default Response Shape** is framed as optional ("when one is created or updated"), so an agent can silently omit it without formally violating anything.
  - Phase 5, action 7 uses soft language ("produce or update the handoff artifact before stopping") rather than explicit prohibition.
  - There is no pre-stop gate — no checklist or explicit blocker preventing a response from concluding without the artifact when conditions are met.
- `skills/feature-dev/references/handoff-plan-template.md` — Template is well-specified and complete. No changes needed here.

---

# Open Questions

None blocking. The following assumptions are stated:

- "Stricter enforcement" means adding enforcement language and a gate inside SKILL.md, not external tooling or CI scripts.
- No changes are needed in the `agents/` subfiles — the policy lives entirely in SKILL.md.

---

# Recommendation

Add a **Pre-Stop Gate** subsection to the Handoff Artifact section. This is a short, numbered checklist the agent must clear before concluding any Standard or Deep track non-implementation response. Pair this with two supporting wording changes:

1. Strengthen `Artifact Status` in the Default Response Shape to be **required** on Standard/Deep stops, not merely optional.
2. Replace the soft Phase 5, action 7 reminder with an explicit prohibition ("Mandatory… policy violation").

This targets the exact mechanism of omission — agents can currently skip the artifact without violating any named checklist item. The Pre-Stop Gate closes that gap by making the omission named and explicit.

---

# Implementation Map

All changes are in `skills/feature-dev/SKILL.md`:

| Location                                    | Change                                                      | Priority |
| ------------------------------------------- | ----------------------------------------------------------- | -------- |
| Default Response Shape, item 6              | Reword `Artifact Status` as required on Standard/Deep stops | High     |
| Phase 5, action 7                           | Replace soft language with explicit prohibition             | High     |
| Handoff Artifact section, after Quality Bar | Add `Pre-Stop Gate` numbered checklist subsection           | High     |

Sequencing: Changes 1 and 2 are independent. Change 3 should be written last so it can cross-reference them.

**No other files need modification.** The template, agent files, and supporting references are all unchanged.

---

# Artifact Status

Handoff artifact written to:

`outputs/.agents/scratchpad/feature-dev-handoff-policy-enforcement/handoff-plan.md`

The artifact is **ready for implementation** and contains goal/non-goals, relevant findings, full file-by-file implementation map with exact before/after text for all three changes, validation plan, and next-agent kickoff steps.
