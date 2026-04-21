---
name: architecture-design-contest
description: Generate multiple competing architecture designs for a feature, compare their trade-offs, and recommend or synthesize the best direction before implementation. Use this whenever the user wants architecture options, says "design it twice", asks for alternatives before coding, wants an RFC-level design review, or is unsure which approach to choose. Prefer this skill over jumping straight into implementation when the real need is exploring and comparing viable designs.
---

# Architecture Design Contest

Use this skill when the user needs decision-quality design work, not code yet. The goal is to widen the search space enough to avoid locking into the first plausible design, then narrow it with an opinionated comparison.

## Success criteria

A strong run:

- resolves only the questions that materially change the design
- grounds the options in the current codebase and current stack docs
- produces designs that differ in structure, not just naming
- explicitly revisits the user's main trade-off in the comparison
- ends with a recommendation or hybrid instead of stopping at a menu

## Workflow

### 1. Frame the design problem

Start with a compact framing:

- the goal
- non-goals
- hard constraints
- unknowns
- decision criteria

Ask only the smallest set of high-leverage questions needed to avoid designing the wrong thing. Prefer one short batch or a few sequential questions; do not interview endlessly. If a question can be answered by reading the codebase or docs, defer it to exploration instead of asking the user.

If the user has already given enough direction, state your assumptions and move on.

### 2. Explore before proposing architecture

If the design has to fit an existing codebase:

1. Launch 2+ `code-explorer` subagents in parallel with different lenses:
   - similar features and neighboring modules
   - integration points, data flow, or extension points
   - testing, operational, or UX constraints
2. Ask each explorer to return:
   - findings that materially affect the design
   - conventions and constraints worth preserving
   - 5-10 files that are worth reading next
3. Read the most important cited files yourself before finalizing the designs.
4. Surface only the findings that change the architecture, comparison, or recommendation.

When explaining why exploration matters, connect each missing fact to the design risk it creates. For example: unknown conventions lead to rework later, hidden integration points produce invalid proposals, and missing constraints create migration gaps.

If the task is greenfield, replace codebase exploration with targeted research into the likely stack, comparable implementations, and current official documentation.

### 3. Run the design contest

Launch 3+ `code-architect` subagents in parallel. Use different model families when available to increase diversity.

Each design must be meaningfully different along at least one of these axes:

- module boundaries and ownership
- control flow or orchestration
- state and data-model placement
- extensibility vs simplicity
- operational model
- migration strategy

Do not accept cosmetic variants. If two designs would produce nearly the same file map or integration pattern, re-scope one before proceeding.

Give each architect a distinct brief containing:

- the problem statement and constraints
- relevant files and exploration findings
- an explicit design bias such as minimal surface area, extension-friendly, optimize for the default path, boundary-first, or migration-first
- a requirement to cite current official docs or live references when stack-specific decisions matter

Ask each architect to produce:

1. a one-sentence thesis
2. an architecture overview
3. component or module boundaries
4. data flow and integration points
5. key risks and failure modes
6. testing and migration implications
7. why this approach is materially different from common alternatives

### 4. Present the designs clearly

Present the designs one at a time so the user can absorb them. For each design, include:

- what it optimizes for
- where it fits best
- where it creates friction
- the irreversible commitments it introduces

Use prose and focused structure. Avoid giant tables unless the user explicitly asks for them.

### 5. Compare like an architect

After all designs are on the table, compare them in prose across:

- simplicity and cognitive load
- extensibility without over-generalizing
- implementation efficiency and migration cost
- ease of correct use vs ease of misuse
- operational and testing complexity
- alignment with existing codebase patterns

Highlight where the designs diverge most. Do not reduce the comparison to raw implementation effort alone.

Explicitly name the user's primary tension in their own terms, then revisit it in the comparison. Examples: reusability vs workflow weight, resumability vs simplicity, flexibility vs guardrails. Do not make the reader infer which trade-off actually decided the recommendation.

### 6. Recommend and synthesize

Give an opinionated recommendation. Do not stop at a neutral menu.

If the best answer is a hybrid, say exactly which pieces to combine and why. If the choice depends on one unresolved constraint, name it explicitly and explain how the recommendation changes.

In the final portion of the response, always do all of the following:

1. State the winning design in one sentence.
2. Name the strongest rejected alternative and why it lost.
3. If recommending a hybrid, say **what stays separate** and **what gets combined**.
4. Tie the recommendation back to the user's main trade-off.

Prefer direct language such as:

- `Recommended design: Design B`
- `Keep separate: orchestration shell and execution engine`
- `Combine: explicit phase model from Design C with the workflow surface from Design A`
- `Why this wins: it resolves reusability vs workflow weight in favor of reuse without introducing a heavy framework`

End by asking the user to choose one of these paths:

- the recommended design as-is
- a specific alternative
- a hybrid with named elements

## Output shape

Use this structure unless the user asks for something else:

1. `Problem framing`
2. `Codebase / research findings`
3. `Design A`, `Design B`, `Design C` (and `Design D` if needed)
4. `Comparison`
5. `Recommendation`
6. `Keep separate / Combine` (or make this explicit inside `Recommendation`)
7. `Next design decision`

The `Recommendation` section should appear near the end and should be easy to skim. Make the final choice, rejected alternative, and hybrid split obvious without requiring the user to read the full comparison again.

## Anti-patterns

- Do not ask a long serial interview when exploration can answer the question faster.
- Do not let subagents return near-duplicate designs.
- Do not skip reading the key files surfaced by exploration.
- Do not implement code, patches, or file edits unless the user explicitly switches from design to execution.
- Do not hide behind "it depends" without making a recommendation.
- Do not compare only by estimated effort; correctness, change safety, and long-term system shape matter more.
