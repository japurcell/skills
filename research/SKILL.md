---
name: research
description: Conduct research on relevant technologies, libraries, or existing code that could inform the design of a specification.
disable-model-invocation: true
---

# Research

Conduct research on relevant technologies, libraries, or existing code that could inform the design.

## Inputs

You receive these parameters in your prompt:

- **spec_file** (required): The path to the spec file to base the research on.

## Steps

1. Read spec_file into context if it isn't already.
2. Launch 3 specialized subagents in parallel for external research. Each agent should:
   - Prefer official docs first, then high-signal references.
   - Find relevant version-specific guidance and migration concerns.
   - Capture common pitfalls, performance considerations, and security implications.
3. Launch 2-3 code-explorer agents in parallel. Each agent should:
   - Read `agents/code-explorer.agent.md`.
   - Trace abstractions and flow of control end-to-end.
   - Focus on different angles (similar features, architecture boundaries, data flow, testing patterns, UX behavior, etc.).
   - Return a list of 5-10 key files and symbols.

   **Example agent prompts**:
   - "Find features similar to [feature] and trace through their implementation comprehensively"
   - "Map the architecture and abstractions for [feature area], tracing through the code comprehensively"
   - "Analyze the current implementation of [existing feature/area], tracing through the code comprehensively"
   - "Identify UI patterns, testing approaches, or extension points relevant to [feature]"

4. Summarize key findings that will inform the design
5. Save research findings to <same directory as spec file>/research.md
6. Fold research findings into the spec file, ensuring they are clearly linked to the requirements and design decisions they inform.
7. Ask questions if research uncovers new questions or considerations
8. Update research.md and spec_file with any clarifications or decisions made during step 7.

DO NOT BEGIN IMPLEMENTATION
