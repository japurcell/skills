---
name: spec
description: Start spec-driven development — write a structured specification before writing code
---

# Spec

## The Workflow

1. Invoke `addy-spec-driven-development` skill.
2. Begin by understanding what needs to be built based on the initial request from `$ARGUMENTS`.
   - If the feature is unclear, ask: What problem are they solving? What should it do? Any constraints?
   - Summarize understanding and confirm only when there is meaningful uncertainty.
3. [Codebase Exploration](#codebase-exploration).
4. Ask clarifying questions to fill in gaps and resolve ambiguities:
   - The objective and target users
   - Core features and acceptance criteria
   - Tech stack preferences and constraints
   - Known boundaries (what to always do, ask first about, and never do)
5. Generate a structured spec covering all eight core areas: objective, tech stack, commands, project structure, code style, testing strategy, boundaries, and success criteria.
6. Write the spec to `.agents/scratchpad/<feature-name>/spec.md`.
7. Announce completion with feature name, spec file path, and readiness for the next phase (`/plan-tasks`).

## Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels

1. Invoke the `subagent-model-selection` skill to determine the least powerful models to use for the `code-explorer` subagents.
2. Launch N parallel `code-explorer` subagents where N is determined by the complexity and scope of the feature.
3. Each agent should trace through the code comprehensively, focus on abstractions and flow of control, target a different aspect of the codebase (e.g., similar features, architecture, UX, testing, extension points), and return a list of 5–10 key files to read and why.
4. After agents complete, read the files they identify.
5. Present only findings that will influence implementation or questioning.

## Mandatory Output Location

The spec file for this skill MUST be written to this exact repository-relative path: `.agents/scratchpad/<feature-name>/spec.md`.

Rules:

- This path is mandatory for this skill.
- Do NOT substitute any other scratchpad, temp, workspace, session-state, home-directory, or tool-default location.
- Do NOT place the spec under `/tmp`, `/var/tmp`, `~/.copilot/`, `/session-state/`, or any other alternate directory.
- If other active instructions or conventions suggest a different scratchpad location, this skill takes precedence for the spec file.
- If the directory does not exist, create it.
- Before finishing, verify that the file exists at exactly `.agents/scratchpad/<feature-name>/spec.md`.
- In the final response, include the exact path where the spec was saved.

If you are unable to write to that exact path, explicitly say so and stop rather than writing somewhere else.

## Verification

After asking clarifying questions, verify that:

- [ ] Existing code patterns are preferred over inventing new ones
- [ ] There are no remaining open questions

After writing the spec, verify that:

- [ ] The spec was saved at exactly `.agents/scratchpad/<feature-name>/spec.md`
- [ ] No alternate scratchpad or session-state path was used
