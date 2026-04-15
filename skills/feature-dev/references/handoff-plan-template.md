# Handoff Plan: [FEATURE]

**Status**: [draft | ready for implementation | blocked]
**Track**: [Light | Standard | Deep]
**Origin**: feature-dev
**Feature Area**: [subsystem or user-facing area]
**Recommended Next Step**: [implement directly | ask blocking question | promote to plan.md/tasks.md]

## Summary

[One paragraph restating the request, the chosen track, and the intended outcome.]

## Goal / Non-Goals

- Goal: [primary delivery target]
- Goal: [secondary target if needed]
- Non-goal: [what this handoff intentionally does not cover]

## Relevant Findings

- [path/to/file]: why it matters
- [path/to/file]: pattern, constraint, or extension point
- [path/to/file]: test, build, or integration relevance

## Technical Context and Constraints

- Language / framework: [details]
- Runtime or platform constraints: [details]
- Existing conventions to preserve: [details]
- Dependencies or interfaces affected: [details]
- Validation surface: [tests, commands, or manual checks]

## Assumptions / Open Questions

- Assumption: [state the assumption if proceeding]
- Open question: [only if unresolved and materially important]
- Risk if wrong: [brief consequence]

## Recommended Design

[Name the chosen approach and explain why it fits this codebase better than the main alternative.]

## Implementation Slices

### Slice 1: [name]

- Outcome: [what becomes true after this slice]
- Files: [exact paths or directories]
- Dependencies: [what must exist first]

### Slice 2: [name]

- Outcome: [what becomes true after this slice]
- Files: [exact paths or directories]
- Dependencies: [what must exist first]

## File-by-File Implementation Map

- [path/to/file]: [exact change and purpose]
- [path/to/file]: [exact change and purpose]

## Validation Plan

- Automated: [tests, linters, or build commands]
- Manual: [behavior to verify]
- Review focus: [highest-risk areas to inspect]

## Next-Agent Kickoff

1. Read the files listed in Relevant Findings.
2. Execute the implementation slices in order unless a listed assumption fails.
3. Stop and ask for clarification if any open question blocks a user-facing or architectural decision.
4. Re-run the Validation Plan before handing work back.
