# Evaluation: Combined "Review-and-Simplify" Agent Proposal

## Understanding

**Process Track: Light** — This is a bounded review of a workflow design proposal. No codebase exploration is needed; the evaluation framework is the feature-dev skill itself.

The proposal is to replace the separate simplification and code-review subagents in Phase 6 (Quality Review) with a single combined "review-and-simplify" agent, on the grounds of saving time and reducing agent overhead.

---

## Relevant Findings

The feature-dev skill's Phase 6 states:

> **Always run independent [code-reviewer] agents** for quality review on every track.
>
> - Standard or Deep: launch **multiple independent code-reviewer agents in parallel** with different focuses such as **simplicity, correctness, and conventions**.

Two design principles underpin Phase 6:

1. **Independence** — each agent is kept structurally separate so it reviews with a fresh, unbiased lens. An agent that just finished simplifying code is no longer independent when it then reviews that same code for correctness.
2. **Focus** — different agents carry different mandates (simplicity, correctness, conventions). Combining mandates into one agent blurs focus and tends to produce shallower coverage of each concern.

Additionally, the Core Principles declare:

> **Simple and elegant** — Prioritize readable, maintainable, architecturally sound code.

This principle governs _output code quality_, not the workflow itself. The developer's proposal misapplies it: streamlining agent count is not the same as producing simpler, more maintainable code.

---

## Open Questions

None. The feature-dev skill is explicit enough to render a clear verdict without additional information.

---

## Recommendation

**The proposal is not acceptable under the feature-dev workflow.**

The skill's Phase 6 structure is intentional:

- **Separate agents preserve independence.** A single agent that simplifies and then reviews will unconsciously defend its own simplification choices rather than challenge them. Separation breaks that feedback loop.
- **Parallel independent agents are the explicit standard for Standard/Deep tracks.** Merging them into one sequential agent removes the parallelism benefit, so the claimed time saving is largely illusory in practice — the combined agent must still do both jobs, just in the same context window.
- **Different focuses require different prompts.** Correctness review and simplicity review ask fundamentally different questions of the code. A combined prompt risks producing a superficial pass on both rather than a thorough pass on each.

The developer's concern about "agent overhead" is a legitimate operational concern, but the right response is to ensure agents are well-scoped and their prompts are tight — not to merge concerns that the workflow deliberately keeps separate.

**If a lighter process is desired**, the correct lever is track selection: use the **Light track**, which calls for at least one code-reviewer agent rather than multiple. That is the sanctioned way to reduce review overhead without compromising independence.

---

## Summary

| Claim                         | Assessment                                                                   |
| ----------------------------- | ---------------------------------------------------------------------------- |
| Saves time                    | Marginal / not guaranteed — combined agent still does both jobs              |
| Reduces agent overhead        | True, but at the cost of independence and focus                              |
| Acceptable per feature-dev    | **No** — violates the "always run independent agents" requirement of Phase 6 |
| Acceptable alternative exists | **Yes** — use the Light track (single reviewer) for bounded work             |
