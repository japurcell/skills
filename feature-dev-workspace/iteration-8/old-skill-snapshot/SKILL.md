---
name: feature-dev
description: Structured feature development for medium-to-large changes in unfamiliar codebases. Use this whenever the user wants to add a feature, extend an existing subsystem, or coordinate discovery, design, implementation, and review across multiple files or moving parts. Prefer it when the task needs codebase exploration, clarifying questions, architecture trade-offs, or a reusable handoff plan for another agent. Do not use it for tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation.
argument-hint: Optional feature description
disable-model-invocation: true
---

# Feature Development

You are helping a developer deliver a feature with the right amount of process for the task. Understand the codebase, identify the decisions that actually matter, and move the work forward without turning every request into a long gated workflow.

## Core Principles

- **Calibrate the workflow**: Choose a light, standard, or deep process based on scope, ambiguity, and risk. Even within in-scope feature work, some requests are bounded and can stay lightweight, while broad or unclear features deserve a deeper process.
- **Ask only high-leverage questions**: Ask clarifying questions when the answers would materially change the design, implementation, or user-facing behavior. If something is minor and you can state a reasonable assumption, do that and keep moving.
- **Understand before acting**: Read and comprehend existing code patterns first
- **Read files identified by agents**: When launching agents, ask them to return lists of the most important files to read. After agents complete, read those files to build detailed context before proceeding.
- **Prefer forward progress when intent is clear**: If the user is plainly asking for implementation and the requirements are sufficiently specified, proceed after focused exploration instead of asking for redundant approval.
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code
- **Leave reusable artifacts**: When the work spans multiple phases or may be handed to another agent, write a concrete handoff artifact rather than leaving only prose in chat.
- **Use TodoWrite**: Track all progress throughout

---

## Process Selection

Choose one track up front and say which you chose.

### Light Track

Use for the smallest in-scope feature work: well-bounded medium-sized changes where the main risk is understanding local code context rather than resolving product ambiguity.

- Do focused exploration yourself or with one targeted agent.
- Ask questions only if something is genuinely blocking.
- Give one recommended approach rather than manufacturing multiple options.
- Implement once you have enough context.

### Standard Track

Use for medium-sized feature work that touches several files, has some ambiguity, or needs a non-trivial design choice.

- Explore the codebase in depth.
- Ask targeted clarifying questions after exploration.
- Present a recommendation and note the most important trade-offs.
- Implement after blockers are resolved.

### Deep Track

Use for large, risky, cross-cutting, or highly ambiguous work.

- Run broad exploration across architecture, similar features, and constraints.
- Gather and organize all blocking questions.
- Present multiple implementation approaches when the trade-offs are meaningful.
- Confirm direction before major implementation.

---

## Default Response Shape

Unless the user asks for a different format, structure your response using the sections that fit the current stage:

1. `Understanding` - current interpretation of the request and the chosen process track
2. `Relevant Findings` - codebase patterns, files, and constraints that matter
3. `Open Questions` - only the questions that materially affect the outcome
4. `Recommendation` - the proposed path forward and why it fits this task
5. `Implementation Map` - files, sequencing, and validation steps when useful
6. `Artifact Status` - the path to the handoff artifact when one is created or updated

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built

Initial request: $ARGUMENTS

**Actions**:

1. Create a todo list scaled to the actual work rather than blindly listing every phase
2. Identify the likely process track:
   - Light for well-bounded medium-sized feature work
   - Standard for medium feature work
   - Deep for large or ambiguous work
3. If the feature is unclear, ask the user for:
   - What problem are they solving?
   - What should the feature do?
   - Any constraints or requirements?
4. Summarize understanding and confirm only when there is meaningful uncertainty

---

## Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels

**Actions**:

1. Scale exploration depth to the chosen track:
   - Light: do direct exploration or launch 1 focused [code-explorer](agents/code-explorer.md) agent
   - Standard: launch 2 focused code-explorer agents in parallel
   - Deep: launch 2-3 code-explorer agents in parallel covering different angles
2. Each agent should:
   - Trace through the code comprehensively and focus on getting a comprehensive understanding of abstractions, architecture and flow of control
   - Target a different aspect of the codebase (eg. similar features, high level understanding, architectural understanding, user experience, etc)
   - Include a list of 5-10 key files to read

   **Example agent prompts**:
   - "Find features similar to [feature] and trace through their implementation comprehensively"
   - "Map the architecture and abstractions for [feature area], tracing through the code comprehensively"
   - "Analyze the current implementation of [existing feature/area], tracing through the code comprehensively"
   - "Identify UI patterns, testing approaches, or extension points relevant to [feature]"

3. Once the agents return, read the files they identify so your understanding is grounded in source, not only agent summaries
4. Present the findings that will actually influence implementation or questioning. Avoid dumping low-signal details.

---

## Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing

**CRITICAL**: Ask clarifying questions when they matter. Do not force this phase when the task is already concrete enough to proceed.

**Actions**:

1. Review the codebase findings and original feature request
2. Identify underspecified aspects: edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance needs
3. Present only the questions that materially affect the approach, grouped clearly
4. If no blocking questions remain, state your assumptions and move forward
5. Wait for answers before design or implementation only when the missing information is truly blocking or likely to cause rework

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs

**Actions**:

1. Scale architecture work to the task:
   - Light: propose one concrete approach with brief rationale
   - Standard: compare 1-2 viable approaches if there is a real decision to make
   - Deep: launch 2-3 [code-architect](agents/code-architect.md) agents in parallel with different focuses such as minimal changes, clean architecture, and pragmatic balance
2. Review the approaches and decide which fits the task best based on complexity, urgency, maintainability, and existing patterns
3. Present a recommendation with concrete implementation differences and only include multiple options when the choice is meaningful
4. Ask the user to choose only when there is a real product or architectural fork. Otherwise recommend the best path and proceed.

---

## Phase 5: Implementation

**Goal**: Build the feature

**Do not create artificial approval gates.** If the user already asked for implementation and the important unknowns are resolved, proceed.

**Actions**:

1. Read all relevant files identified in previous phases
2. Implement following the chosen approach
3. Use the tdd skill when the feature warrants test-first work or when tests are the safest way to drive the change
4. Follow codebase conventions strictly
5. Write clean, maintainable code
6. Update todos as you progress
7. If you are not implementing yet, produce or update the handoff artifact before stopping

---

## Phase 6: Quality Review

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct

**Actions**:

1. Scale review depth to the risk of the change:
   - Light: do one focused review pass yourself or with one reviewer
   - Standard or Deep: launch multiple [code-reviewer](agents/code-reviewer.md) agents in parallel with different focuses such as simplicity, correctness, and conventions
2. Consolidate findings and prioritize the issues that matter most
3. Fix obvious high-severity issues directly unless the user has asked to stop after review
4. Surface remaining risks, trade-offs, and follow-up work clearly

---

## Handoff Artifact

When another agent or later turn is likely to continue the work, write a file-backed handoff artifact instead of leaving only a conversational summary.

### Required Path

Write the artifact to:

`.agents/scratchpad/<feature-name>/handoff-plan.md`

If the feature name is not explicit, choose a short slug from the request.

### Template

Read and follow [references/handoff-plan-template.md](references/handoff-plan-template.md).

Use the template structure directly unless the repository already has a stronger established artifact for the same purpose.

### When It Is Required

Create or update `handoff-plan.md` when any of these are true:

1. The work is on the Standard or Deep track and implementation may continue in another turn.
2. Another agent is likely to implement or review the change.
3. You stop after discovery, design, or review instead of completing implementation in the same turn.
4. The user asks for a plan, handoff, or reusable implementation guidance.

For Light track work that you complete in the same turn, the artifact is optional.

### Minimum Content

The artifact must capture:

1. Goal and non-goals
2. Relevant findings and source files
3. Technical context and constraints
4. Open questions or stated assumptions
5. Recommended design and why
6. Ordered implementation slices
7. File-by-file implementation map
8. Validation plan, tests, and review checkpoints
9. Next-agent kickoff steps

### Quality Bar

Before you stop, check that:

1. Every referenced file has a reason to be read.
2. The implementation map names concrete files or directories.
3. The validation plan is specific enough for another agent to run.
4. Open questions are limited to issues that materially affect the work.
5. Another agent could continue without repeating discovery.

In your user-facing response, summarize the handoff briefly and point to `handoff-plan.md` as the source of truth.

---

## When Not To Use This Skill

Do not use this skill for:

1. Tiny bug fixes or one-file edits where direct implementation is faster than process
2. Fully specified requests that only need straightforward execution
3. Pure code review requests with no feature development component
4. Open-ended brainstorming that does not need codebase-guided implementation planning

---

## Phase 7: Summary

**Goal**: Document what was accomplished

**Actions**:

1. Mark all todos complete
2. Summarize:
   - What was built
   - Key decisions made
   - Files modified
   - Suggested next steps or handoff notes

---
