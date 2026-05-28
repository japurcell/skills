---
name: prd
description: Create a Product Requirements Document (PRD) for a feature. Use for requests like: create a PRD, write a PRD for, plan this feature, requirements for, spec out.
---

# PRD Generator

Create a clear, implementation-ready PRD. Do not implement the feature or write code.

## Rules
- Follow existing codebase patterns and conventions.
- Apply YAGNI: exclude unnecessary features.
- Resolve ambiguities before designing.
- If the user says “whatever you think is best,” give a recommendation and get explicit confirmation.

## Workflow
1. Understand `$ARGUMENTS`.
   - If needed, ask only the minimum:
     - What problem does this solve?
     - What should it do?
     - Any constraints or preferences?
   - Summarize only if there is meaningful uncertainty.
2. [Explore the codebase](#codebase-exploration) and wait for subagent results.
3. Ask clarifying questions based on the request and codebase findings.
   - Cover gaps such as edge cases, error handling, integrations, scope, backward compatibility, and performance.
   - Wait for answers before designing.
4. [Design the architecture](#architecture-design) options and wait for subagent results.
5. Present options, trade-offs, and your recommendation.
6. Ask the user to choose an approach.
7. Write the PRD.
8. Save it to `.agents/scratchpad/[feature-name]/prd.md`.
9. Final response must include:
   - feature short name
   - PRD path
   - validation status (pass/fail)
   - readiness for `/prd-to-tasks`

## Codebase Exploration

**Goal:** Understand existing patterns and relevant code.

1. Launch 1-3 parallel `code-explorer` subagents, where the number matches feature complexity.
2. Each agent should inspect a different aspect of the codebase, such as:
   - Similar features
   - Architecture and control flow
   - UI patterns
   - Tests
   - Extension points
3. Each agent should return 5–10 key files to read, with reasons.
4. Read all files identified by agents to build deep understanding.
5. Present comprehensive summary of findings and patterns discovered.

## Architecture Design

**Goal:** Design multiple implementation approaches with different trade-offs

1. Launch 2-3 parallel `code-architect` subagents, where the number matches feature complexity.
2. Each agent should propose a different approach, such as:
   - Minimal changes (smallest change, maximum reuse)
   - Clean architecture (maintainability, elegant abstractions)
   - Pragmatic balance (speed + quality)
3. Instruct each subagent to invoke the `official-sources` skill so that each proposal is grounded in current official documentation.
   - For every language, framework, library, platform, infrastructure service, or contract standard that affects the PRD, check the latest official web documentation before finalizing proposal.
   - Treat official/vendor/framework docs as the primary source; use repository context only to adapt them.
4. For each approach, include rationale, trade-offs, risks, and citations.
5. Review all approaches and form your opinion on which fits best (consider: small fix vs large feature, urgency, complexity, team context).
6. Present to user: brief summary of each approach, trade-offs comparison, **your recommendation with reasoning**, concrete implementation differences.
7. **Ask user which approach they prefer**

## PRD Structure

### 1. Introduction / Overview
Briefly describe the feature and the problem it solves.

### 2. Goals
Bullet list of specific, measurable objectives.

### 3. Tech Stack
Bullet list of key technologies/libraries and versions.

### 4. User Stories
Each story must include:
- **Title**
- **Description:** `As a [user], I want [feature] so that [benefit].`
- **Acceptance Criteria:** specific, verifiable checklist
- **Files likely touched:** best-effort guess from code exploration
- **Design Guidance:** implementation guidance, rationale, and sources from architecture/design work

Each story should be small enough for one focused implementation session.

**Format:**
```markdown
### US-001: [Title]
**Description:** As a [user], I want [feature] so that [benefit].

**Acceptance Criteria:**
- [ ] Specific verifiable criterion
- [ ] Another verifiable criterion
- [ ] Typecheck/lint passes
- [ ] **[UI stories only]** Verify in browser using playwright-cli skill

**Files likely touched:**
- `src/path/to/file.ts`
- `tests/path/to/test.ts`

**Design Guidance:**
- [Source link]
  - Guidance: [What the implementer should do and how to apply it]
  - Rationale: [Why this guidance was chosen]
```

**User Story Rules**
- Acceptance criteria must be specific and testable.
- Do not use vague criteria like “works correctly.”
- For any story with UI changes, always include: `Verify in browser using playwright-cli skill`.
- `Files likely touched` is a best-effort estimate, not a guarantee.

### 5. Functional Requirements
Numbered, explicit requirements, for example:
- `FR-1: The system must allow users to...`
- `FR-2: When a user clicks X, the system must...`

### 6. Non-Goals
State what is out of scope.

### 7. Design Considerations (Optional)
Relevant UI/UX notes, mockups, or reusable components.

### 8. Technical Considerations
Constraints, dependencies, integrations, and performance requirements.

### 9. Architectural Decisions
Key decisions, trade-offs, rationale, alternatives considered, and citations.

### 10. Success Metrics
How success will be measured.

## Writing Guidance
Assume the reader may be a junior developer or another AI agent.
- Be explicit and unambiguous.
- Avoid jargon, or explain it.
- Use numbered requirements.
- Use concrete examples when helpful.

## Output
- **Format:** Markdown
- **Path:** `.agents/scratchpad/[feature-name]/prd.md`

### Path Rules
- Use exactly `.agents/scratchpad/[feature-name]/prd.md`.
- Do not use any other directory.
- If the directory does not exist, create it.
- Before finishing, verify the file exists at that exact path.
- If you cannot write to that exact path, say so and stop.

## Checklist

### Before writing
- [ ] Clarifying questions asked and answered
- [ ] No open questions remain
- [ ] User answers incorporated
- [ ] Relevant code patterns explored
- [ ] Existing patterns preferred over new ones
- [ ] Requirements are clear enough to proceed

### Before saving
- [ ] User stories are small and specific
- [ ] Functional requirements are numbered and unambiguous
- [ ] Non-goals clearly define scope
- [ ] Architectural decisions include rationale and citations
- [ ] No code was written

### Final verification
- [ ] Saved at exactly `.agents/scratchpad/[feature-name]/prd.md`
- [ ] No alternate path was used
- [ ] No design gaps, open questions, or ambiguities remain
