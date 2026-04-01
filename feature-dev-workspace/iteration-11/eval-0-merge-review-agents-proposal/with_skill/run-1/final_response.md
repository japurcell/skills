# Eval 0 — Merge Review Agents Proposal

## Task Prompt

> A developer on your team proposes streamlining the feature-dev quality review by running a single combined 'review-and-simplify' agent instead of separate subagents for simplification and code review — they say it'll save time and reduce agent overhead. Using the feature-dev workflow as your framework, evaluate this proposal and explain whether it's acceptable.

---

## Understanding

This is an evaluation question about the structure of Phase 6 (Quality Review) in the feature-dev workflow. The proposal is to collapse two distinct subagents — the `code-simplifier` and `code-reviewer` — into one combined agent to reduce overhead.

Track chosen for this evaluation: **Light** — the question is bounded and the relevant source of truth (the SKILL.md) is clear.

---

## Relevant Findings

The feature-dev skill is explicit about Phase 6 Quality Review:

> 1. Always launch an **independent** `code-simplifier` subagent to identify refactoring opportunities after implementation.
> 2. Always run **independent** `code-reviewer` agents for quality review on every track.

Three design signals stand out:

1. **The word "independent" is used deliberately.** Both the simplifier and reviewer are called out as _independent_ subagents — not just separate steps in a checklist. Independence means each agent approaches the code without being pre-shaped by the other's framing.

2. **Parallelism is an explicit feature for standard and deep tracks.** The skill says to "launch multiple independent code-reviewer agents in parallel with different focuses such as simplicity, correctness, and conventions." A merged agent cannot parallelize against itself.

3. **The two agents target distinct quality dimensions.** The `code-simplifier` is focused on DRY-ness, elegance, and readability — structural concerns. The `code-reviewer` is focused on correctness, conventions, and edge cases — functional and safety concerns. These are different lenses, and a single agent asked to do both will compress depth in favor of breadth.

---

## Recommendation

**The proposal is not acceptable.**

The "saves time" framing misdiagnoses where the cost is. The overhead of two subagents is real but small. The value those agents protect — catching defects at the cheapest possible moment, before handoff — is high. The feature-dev skill's design deliberately separates these concerns to preserve independent perspective and allow parallel execution. Merging them removes both properties.

There is also a cognitive contamination risk: an agent that first simplifies code is anchored to the state it created. It is less likely to critically evaluate correctness or conventions because it has already implicitly validated the structure. The independence requirement exists precisely to avoid this bias.

The right way to reduce overhead in Phase 6 is to calibrate agent _count_ to the chosen process track (e.g., Light track only requires one reviewer), not to eliminate the role boundary between simplification and review.

### Summary table

| Concern                     | Separate agents (current) | Merged agent (proposed) |
| --------------------------- | ------------------------- | ----------------------- |
| Independence of review      | Preserved                 | Lost                    |
| Parallel execution          | Supported                 | Not possible            |
| Depth per quality dimension | Full                      | Compressed              |
| Risk of anchoring bias      | Low                       | High                    |
| Alignment with SKILL.md     | Yes                       | No                      |

---

## Artifact Status

No handoff artifact required — this is an evaluation response, not a feature implementation.
