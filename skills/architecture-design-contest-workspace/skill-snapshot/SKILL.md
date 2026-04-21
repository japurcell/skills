---
name: architecture-design-contest
description: Generate multiple radically different designs for a feature using parallel sub-agents. Use when user wants to explore design options or mentions "design it twice".
---

# Architecture Design Contest

Based on "Design It Twice" from "A Philosophy of Software Design": your first idea is unlikely to be the best. Generate multiple radically different designs, then compare.

## Workflow

### 1. Gather Requirements

Interview me relentlessly about every aspect of my problem/feature request until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, then defer that question to codebase exploration.

### 2. Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels.

1. Launch 2+ code-explorer subagents in parallel covering different angles.
2. Each subagent should trace through the code comprehensively, focus on abstractions and flow of control, target a different aspect of the codebase (e.g., similar features, architecture, UX, testing, extension points), and return a list of 5-10 key files to read.
3. After subagents complete, read the files they identify.
4. Present only findings that will influence implementation or questioning.

When explaining why exploration cannot be skipped, connect each exploration gap to the specific downstream phase where it causes damage — don't just list generic risks. For example: missing conventions → mid-Phase 5 implementation rework; missing integration points → incorrect Phase 4 design; unknown architecture patterns → implementation gaps in Phase 5 implementation.

### 3. Generate Designs (Parallel Subagents)

- Launch 3+ parallel code-architect subagents. Each must:
  - Produce a **radically different** approach
  - Use a LLM from a different family to maximize diversity
  - Find web references to cite in your design decisions. This is important because your training data is stale. Search for up to date:
    - Tech stack official documentation
    - Best practices
    - Similar open source implementations

### 4. Present Designs

Present designs sequentially so user can absorb each approach before comparison.

### 5. Compare Designs

After showing all designs, compare them on:

- **Simplicity**: ease of understanding and use
- **General-purpose vs specialized**: Can handle future use cases without changes. But beware over-generalization.
- **Implementation efficiency**: Does this design allow for an efficient implementation, or does it force awkward workarounds?
- **Ease of correct use** vs **ease of misuse**

Discuss trade-offs in prose, not tables. Highlight where designs diverge most.

### 6. Synthesize

Often the best design combines insights from multiple options. Ask:

- "Which design best fits your primary use case?"
- "Any elements from other designs worth incorporating?"

## Anti-Patterns

- Don't let sub-agents produce similar designs - enforce radical difference
- Don't skip comparison - the value is in contrast
- Don't implement - this is purely about interface shape
- Don't evaluate based on implementation effort
