# Evaluation: Combined 'Review-and-Simplify' Agent Proposal

## Understanding

The proposal is to replace the Quality Review phase's two distinct subagent steps — an independent `code-simplifier` pass and one or more independent `code-reviewer` agents — with a single combined `review-and-simplify` agent. The motivation is efficiency: fewer agents, less overhead, faster cycle time.

This is a workflow design question, not a feature request, so no codebase exploration or implementation is needed. The evaluation can be resolved directly by consulting Phase 6 of the feature-dev skill.

---

## Relevant Findings

Phase 6 of the feature-dev skill is explicit and unambiguous on this point:

> **Action 1**: Always launch an **independent** `code-simplifier` subagent to identify refactoring opportunities after implementation.
>
> **Action 2**: Always run **independent** `code-reviewer` agents for quality review on every track.

Two design constraints underpin this structure:

1. **Independence is required, not optional.** The skill uses the word "independent" deliberately in both steps. This ensures each agent applies a single focused lens without the priorities of one role diluting the other.

2. **Separation of concerns is load-bearing.** The `code-simplifier` role is about elegance, DRY, and readability — structural improvements to the code. The `code-reviewer` role covers correctness, conventions, security, and edge cases — functional and standards compliance. These are different cognitive modes. A combined agent must trade off depth in one area to cover the other; a focused agent can go all-in on its mandate.

3. **Parallelism is a feature on Standard/Deep tracks.** The skill explicitly instructs launching *multiple* independent code-reviewer agents in parallel on Standard and Deep tracks, each with a different focus (simplicity, correctness, conventions). A single combined agent eliminates this parallelism, reducing coverage without a compensating gain.

4. **The skill treats this phase as non-negotiable.** Phase 6 opens with "Always launch" and "Always run" — there are no conditional paths that allow skipping or merging these steps.

---

## Open Questions

None that are blocking. The skill's instructions are clear enough to render a verdict without additional information.

---

## Recommendation

**The proposal is not acceptable under the feature-dev workflow.**

The time savings are real but misapplied. The overhead the developer wants to eliminate — two separate agents — is the mechanism the workflow uses to guarantee quality coverage across two distinct dimensions. Merging them saves one agent invocation at the cost of:

- Weakened focus (one agent serving two masters)
- Lost parallelism on Standard/Deep tracks
- A direct violation of the skill's "always independent" mandate

If the team genuinely wants to reduce agent overhead, the right lever is **process track selection**: Light track work already uses fewer agents by design. A combined agent is not sanctioned by the skill at any track level.

**Verdict: Reject the proposal as written.** Continue running `code-simplifier` and `code-reviewer` as separate, independent steps per Phase 6 of the feature-dev skill.
