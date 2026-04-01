## Minimum Non-Negotiable Phase 6 Steps

Reading the feature-dev workflow's Phase 6 directly:

> "Always run independent code-reviewer agents for quality review on every track."

That is the single non-negotiable mandate Phase 6 states. The workflow enforces it unconditionally: "on every track" means Light, Standard, and Deep alike.

---

### The mandatory minimum (per workflow)

| Step                       | Subagent role   | Scale by track                                                        |
| -------------------------- | --------------- | --------------------------------------------------------------------- |
| Independent quality review | `code-reviewer` | Light: at least one agent; Standard/Deep: multiple agents in parallel |

Nothing in Phase 6 can be dropped below this floor.

---

### Why it cannot be removed

The workflow's goal for Phase 6 is:

> "Ensure code is simple, DRY, elegant, easy to read, and functionally correct."

An independent code-reviewer is the mechanism the workflow provides to achieve this. Skipping it removes the only structured quality gate before delivery.

---

### What you can do to reduce cost without violating the mandate

- **Use the Light track** when the feature is genuinely small and bounded. This scales Phase 6 down to one code-reviewer agent (not multiple), which is the smallest valid review footprint the workflow allows.
- **Scope the review tightly**: give the code-reviewer a specific focus (e.g., correctness only for a low-risk change) so the review run is shorter.
- **Do not eliminate the step entirely**: there is no "Phase 6 optional" path in the workflow.

The two-step path (multiple code-reviewers for Standard/Deep) has cost because coverage has cost. The minimum isn't about eliminating agents — it's about using the track that legitimately scales them down.
