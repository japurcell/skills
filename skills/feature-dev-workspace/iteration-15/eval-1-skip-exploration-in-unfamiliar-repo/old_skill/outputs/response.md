# Feature Dev Response: Go/No-Go on Skipping Exploration

## Understanding

**Process Track Selected: Standard**

You're new to the repo, the feature is medium-sized, and the request has meaningful ambiguity—you don't yet know the codebase's conventions, architecture, or existing patterns. Standard track applies: medium-sized feature with several unknowns and non-trivial design choices ahead.

Your lead's suggestion to skip exploration and figure out conventions as you go is the exact scenario this skill is designed to protect against.

---

## Relevant Findings

Without codebase access I can't surface specific file patterns, but the risk profile is clear from what you've described:

- **Unfamiliar codebase**: conventions, abstractions, and architectural decisions are unknown
- **Medium-sized feature**: likely touches multiple files or subsystems
- **Time pressure**: increases temptation to cut process, but increases the cost of rework if conventions are violated

Skipping exploration in this situation has a well-documented failure mode: you implement something technically functional that doesn't fit the codebase, violates conventions, and requires significant rework in review—costing more time than the exploration would have.

---

## Recommendation

**NO-GO on skipping exploration.**

The feature-dev skill is explicit: *"Understand before acting: Read and comprehend existing code patterns first."* This is not optional ceremony—it's the minimum due diligence that prevents convention mismatch, architectural drift, and rework.

For a **new developer in an unfamiliar repo**, exploration is even more critical, not less. The risk of building something that doesn't fit the codebase is highest precisely when you don't know the codebase.

"Figure out conventions as you go" during implementation is a pattern that leads to inconsistent code, failed reviews, and late-stage rewrites.

**What the skill recommends instead:** Focused, time-boxed exploration (Standard track: 2 parallel code-explorer agents) before any implementation. This takes hours, not days, and directly funds faster, cleaner implementation.

---

## Minimum Pre-Implementation Checklist

Complete these before writing any feature code:

### Phase 1: Discovery (do this now)
- [ ] Define the feature clearly: what problem it solves, what it must do, what it must not do
- [ ] Identify the process track (you're on **Standard** given your situation)
- [ ] Create a todo list capturing all phases: exploration → questions → design → implement → review

### Phase 2: Codebase Exploration (required — do not skip)
- [ ] Launch 2 parallel code-explorer agents targeting different angles:
  - Agent 1: *"Find features similar to [your feature] and trace through their implementation comprehensively, listing 5–10 key files"*
  - Agent 2: *"Map the architecture and abstractions for [relevant area], tracing through the code comprehensively, listing 5–10 key files"*
- [ ] After agents return, **read the key files they identify** — ground your understanding in source, not just summaries
- [ ] Note the conventions you see: naming, file structure, error handling, testing patterns, abstractions

### Phase 3: Clarifying Questions (resolve blockers before design)
- [ ] Identify the 2–4 questions that would materially change the implementation if answered differently
- [ ] Resolve those questions (with your lead, the codebase, or existing tests)
- [ ] State any remaining assumptions explicitly

### Phase 4: Architecture Design (before implementation)
- [ ] Propose a concrete implementation approach aligned with existing patterns
- [ ] Identify 1–2 real trade-offs if the choice is meaningful
- [ ] Confirm direction (only gate if there's a genuine architectural fork)

### Phase 5: Ready to Implement — Green Light Conditions
You can proceed to implementation when:
- [ ] You understand how similar features are structured in this codebase
- [ ] You know the naming, testing, and error-handling conventions
- [ ] All blocking questions are resolved or explicitly assumed
- [ ] You have a concrete, file-level implementation plan

---

## Open Questions

One question that materially affects how you proceed:

1. **What is the feature?** Without knowing what it does, I can't help you scope the exploration or flag specific risks. Name the feature and I'll tailor the agent prompts and checklist to your actual work.

---

## A Note on "Moving Quickly"

The fastest path through a medium-sized feature in an unfamiliar codebase is:
1. Short, focused exploration (hours)
2. Clear design aligned with existing patterns
3. Confident implementation with TDD (red-green-refactor)
4. Targeted review

Skipping step 1 typically adds days of rework after review, not hours of savings before it. The checklist above is the minimum — not a bureaucratic gate, but the actual fastest route to a mergeable feature.
