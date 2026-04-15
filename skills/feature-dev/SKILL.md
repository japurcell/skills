---
name: feature-dev
description: Structured feature development for medium-to-large changes in unfamiliar codebases. Use this whenever the user wants to add a feature, extend an existing subsystem, or coordinate discovery, design, implementation, and review across multiple files or moving parts. Prefer it when the task needs codebase exploration, clarifying questions, architecture trade-offs, or a reusable handoff plan for another agent. Do not use it for tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation.
argument-hint: Optional feature description
disable-model-invocation: true
---

# Feature Development

Help a developer deliver a feature with the right amount of process for the task. Understand the codebase, identify the decisions that actually matter, and move work forward without gating every request on an elaborate workflow.

## Core Principles

- **Calibrate the workflow**: Choose Light, Standard, or Deep based on scope, ambiguity, and risk. Even in-scope features vary — bounded work stays lightweight; broad or unclear features deserve deeper process.
- **Ask only high-leverage questions**: Ask when answers would materially change the design or user-facing behavior. If something is minor, state a reasonable assumption and keep moving.
- **Read files identified by agents**: After agents complete, read the files they flag — your understanding should be grounded in source, not just agent summaries.
- **Prefer forward progress**: If the user plainly wants implementation and requirements are sufficiently specified, proceed after focused exploration.
- **Leave reusable artifacts**: When work spans multiple phases or may be handed to another agent, write a concrete handoff artifact.
- **Use TodoWrite**: Track all progress throughout.

---

## Process Selection

Choose one track up front and say which you chose.

### Light Track

Well-bounded, medium-sized changes where the main risk is understanding local code context.

- Focused self-exploration or 1 targeted code-explorer agent.
- Ask questions only if something is genuinely blocking.
- One recommended approach; implement once you have enough context.

### Standard Track

Medium-sized work touching several files, with some ambiguity or a non-trivial design choice.

- 2 code-explorer agents in parallel.
- Targeted clarifying questions after exploration.
- Present a recommendation with key trade-offs; implement after blockers are resolved.

### Deep Track

Large, risky, cross-cutting, or highly ambiguous work.

- 2–3 code-explorer agents in parallel covering different angles.
- Gather and organize all blocking questions.
- Present multiple approaches when trade-offs are meaningful; confirm direction before major implementation.

---

## Default Response Shape

Structure your response using the sections that fit the current stage:

1. `Understanding` — current interpretation of the request and the chosen process track
2. `Relevant Findings` — codebase patterns, files, and constraints that matter
3. `Open Questions` — only questions that materially affect the outcome
4. `Recommendation` — the proposed path forward and why
5. `Implementation Map` — files, sequencing, and validation steps when useful
6. `Artifact Status` — path to the handoff artifact when created or updated

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built.

Initial request: $ARGUMENTS

1. Create a todo list scaled to the actual work.
2. Choose the process track based on scope, ambiguity, and risk.
3. If the feature is unclear, ask: What problem are they solving? What should it do? Any constraints?
4. Summarize understanding and confirm only when there is meaningful uncertainty.

---

## Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels.

1. Scale exploration to the chosen track:
   - Light: direct exploration or 1 code-explorer agent
   - Standard: 2 code-explorer agents in parallel
   - Deep: 2–3 code-explorer agents in parallel covering different angles

2. Each agent should trace through the code comprehensively, focus on abstractions and flow of control, target a different aspect of the codebase (e.g., similar features, architecture, UX, testing, extension points), and return a list of 5–10 key files to read.

3. After agents complete, read the files they identify.
4. Present only findings that will influence implementation or questioning.

When explaining why exploration cannot be skipped, connect each exploration gap to the specific downstream phase where it causes damage — don't just list generic risks. For example: missing conventions → mid-Phase 5 implementation rework; missing integration points → incorrect Phase 4 design; unknown architecture patterns → implementation gaps in Phase 5 implementation.

---

## Phase 3: Clarifying Questions

**Goal**: Fill gaps and resolve ambiguities before designing.

Ask only questions that materially affect the approach — edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance. Present a small, bounded list (3 or fewer where possible), with each question phrased concretely and tied to a specific uncertainty that would change the design or scope. Avoid listing categories of concerns — pose the actual questions. If no blocking questions remain, state your assumptions and move forward. Wait for answers only when missing information is truly blocking or likely to cause rework.

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design implementation approaches with different trade-offs.

1. Scale to the chosen track:
   - Light: one concrete approach with brief rationale
   - Standard: compare 1–2 viable approaches if there is a real decision to make
   - Deep: 2–3 code-architect agents in parallel (e.g., minimal changes, clean architecture, pragmatic balance)
2. Present a recommendation; include multiple options only when the choice is meaningful.
3. Ask the user to choose only when there is a real product or architectural fork; otherwise recommend the best path and proceed.

---

## Phase 5: Implementation

**Goal**: Build the feature.

**Do not create artificial approval gates.** If the user already asked for implementation and the important unknowns are resolved, proceed.

1. Read all relevant files identified in previous phases.
2. **Always use the tdd skill** with an explicit red-green-refactor loop. This is required on every track; do not bypass it.
3. Follow codebase conventions strictly and write clean, maintainable code.
4. Update todos as you progress.
5. If not implementing yet, produce or update the handoff artifact before stopping. When providing a pre-implementation recommendation or go/no-go checklist, always state that downstream execution still requires all three mandatory gates: TDD implementation (Phase 5), a separate code-simplifier refactor pass, and independent code-reviewer review (Phase 6).

---

## Phase 6: Quality Review

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct.

1. Launch independent [code-simplifier](../code-simplifier/SKILL.md) subagents to identify refactoring opportunities. Scale based on the number of changed files:
   - **≤5 files**: launch 1 agent covering all changed files
   - **>5 files**: partition files into non-overlapping groups (by module, directory, or logical area) and launch one agent per group in parallel. Each file must appear in exactly one agent's scope — overlapping scopes cause conflicting writes.

2. **Always** run independent code-reviewer agents for quality review on every track:
   - Light: at least one code-reviewer agent
   - Standard or Deep: multiple code-reviewer agents in parallel with different focuses (e.g., simplicity, correctness, conventions)

3. Consolidate findings, prioritize the issues that matter most, fix obvious high-severity issues directly, and surface remaining risks and follow-up work.

---

## Handoff Artifact

When another agent or later turn is likely to continue the work, write a file-backed handoff artifact.

**Path**: `.agents/scratchpad/<feature-name>/handoff-plan.md`

Read and follow [references/handoff-plan-template.md](references/handoff-plan-template.md).

Create or update `handoff-plan.md` when any of these are true:

1. Work is on the Standard or Deep track and implementation may continue in another turn.
2. Another agent is likely to implement or review the change.
3. You stop after discovery, design, or review instead of completing implementation.
4. The user asks for a plan, handoff, or reusable implementation guidance.

For Light track work completed in the same turn, the artifact is optional.

**Required content**:

1. Goal and non-goals
2. Relevant findings and source files (each with a reason to be read)
3. Technical context and constraints
4. Open questions or stated assumptions
5. Recommended design and why
6. Ordered implementation slices
7. File-by-file implementation map
8. Validation plan — **the Validation Plan section must explicitly list TDD red-green-refactor completion, code-simplifier refactor pass, and independent code-reviewer review as named discrete steps, not buried in Implementation Slices**
9. Next-agent kickoff steps

In your user-facing response, summarize the handoff briefly and point to `handoff-plan.md` as the source of truth.

---

## Phase 7: Summary

**Goal**: Document what was accomplished.

1. Mark all todos complete.
2. Summarize: what was built, key decisions made, files modified, suggested next steps or handoff notes.

---
