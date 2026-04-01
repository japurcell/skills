# Run Notes — Eval 2 (Old Skill Baseline)

**Skill version**: old-skill-snapshot (iteration-9 baseline)
**Prompt**: "Prepare a handoff for adding stricter handoff-policy enforcement to feature-dev so another agent can implement next."

## What happened

- The old skill correctly triggered a Standard track for this scoped, multi-location SKILL.md change.
- The skill's "Stop before implementation" instruction was respected — no edit actions were taken against the target SKILL.md.
- A handoff artifact was created because the Standard track + stop-before-implementation condition explicitly satisfies "When It Is Required" condition 3.
- The `Artifact Status` section was included in the final response because the skill's Default Response Shape lists it as a section "when one is created or updated" — this was followed correctly even though the skill does not require it for Standard track stops generally.

## Observations about the old skill

- The old skill does produce a handoff when the agent correctly reads and applies the policy, but it relies on the agent noticing the condition rather than enforcing it through a hard gate.
- The `Artifact Status` inclusion was technically optional under the old skill wording; the agent chose to include it here because an artifact was created, not because the skill required it.
- This is exactly the gap that eval 2 is testing: does the old skill produce the artifact and status reliably, or only circumstantially?

## Outcome

The artifact was created and the response includes `Artifact Status`. However, the gap is observable: if the agent had stopped at "Relevant Findings" without proceeding to the Handoff Artifact section, the old skill would not have provided an explicit blocker.
