---
name: spec
description: Start spec-driven development — write a structured specification before writing code
---

# Spec

## The Workflow

- Invoke the `addy-spec-driven-development` skill.
- Begin by understanding what the user wants to build. Ask clarifying questions about:
  1. The objective and target users
  2. Core features and acceptance criteria
  3. Tech stack preferences and constraints
  4. Known boundaries (what to always do, ask first about, and never do)
- Generate a structured spec covering all six core areas: objective, commands, project structure, code style, testing strategy, and boundaries.
- Write the spec to `.agents/scratchpad/<feature-name>/spec.md`.

## Codebase Exploration

If a question can be answered by exploring the codebase, explore the codebase instead.

## Parallelization Opportunities

When subagents are available:

- **Delegate Exploration**: Launch N code-explorer subagents in parallel where N is determined by the complexity and scope of the feature. Each agent should:
  - Cover a different angle to avoid redundancy and maximize coverage.
  - Return a list of 5–10 key files with reasons.
- **Select the right subagent model**: Invoke the `subagent-model-selection` skill.

## Verification

After asking clarifying questions, verify that:

- [ ] There are no remaining open questions
