# Evaluation: Combined "review-and-simplify" Agent Proposal

## Understanding

The proposal is to replace Phase 6's two-subagent quality review with a single combined agent. Evaluating against the feature-dev workflow's Phase 6 specification.

**Track chosen**: Light — this is a question about the workflow itself, not a feature task.

---

## Assessment: Not Acceptable

The feature-dev workflow's Phase 6 explicitly requires **two separate, independent subagents** in a specific order. Merging them into a single pass violates the workflow's mandated structure.

### What Phase 6 Actually Requires

Phase 6 specifies the following **required** actions:

1. **Always launch an independent `code-simplifier` subagent** — to identify refactoring opportunities after implementation. This runs first.
2. **Always run independent `code-reviewer` agents** — for quality review on every track:
   - Light: at least one independent `code-reviewer` agent
   - Standard or Deep: multiple independent `code-reviewer` agents in parallel with different focuses (e.g., simplicity, correctness, conventions)

These are not optional steps. The word "always" appears for both requirements.

### Why Merging Them Undermines the Workflow

**Independence is the point.** The `code-simplifier` and `code-reviewer` serve distinct, non-overlapping purposes:

- `code-simplifier` focuses narrowly on identifying refactoring opportunities — making the code simpler, DRY, and more elegant. It is optimized for structural clarity, not correctness.
- `code-reviewer` agents examine quality dimensions: simplicity, correctness, and conventions — as _separate reviewer lenses_, not as a refactoring pass.

Running a single combined agent collapses these lenses. A combined agent will tend to anchor on whatever review dimension surfaces first and give the other dimension shallow treatment. The workflow separates them precisely so each task gets full attention without cross-contamination.

**Order matters too.** The `code-simplifier` runs **before** the `code-reviewer` pass. The sequence is:

```
Implementation → code-simplifier (refactor pass) → code-reviewer(s) (quality review)
```

Merging the agents also destroys this ordering guarantee. If simplification findings are not addressed before review, the reviewer is assessing code that may still have structural noise — producing lower-quality feedback.

**"Overhead" is the wrong framing.** The two-step structure is not accidental process budget: it is the mechanism by which the workflow guarantees that code is both well-structured _and_ independently reviewed. Removing one step removes one guarantee.

### Recommendation

Reject the proposal. The feature-dev workflow mandates `code-simplifier` and `code-reviewer` as separate, sequenced subagents, and this cannot be streamlined away without dropping a required safeguard. If review duration is a concern, acceptable optimizations include:

- Scoping the `code-reviewer` focus more tightly
- Running multiple `code-reviewer` agents in parallel (Standard/Deep track) instead of sequentially
- Using the Light track (one `code-reviewer`) for bounded changes

But collapsing the `code-simplifier` and `code-reviewer` into a single agent is not among the acceptable reductions.
