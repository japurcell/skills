---
name: prd
description: Create a Product Requirements Document (PRD) for a feature. Use for requests like create a PRD, write a PRD, plan this feature, requirements for, spec out.
---

# PRD Generator

Create a clear, implementation-ready PRD. Do not implement the feature or include implementation code.

## Rules

- Follow existing codebase patterns and conventions.
- Use YAGNI; exclude unnecessary features.
- Resolve ambiguities before designing; ask only the minimum clarifying questions needed.
- If the user says “whatever you think is best,” provide a recommendation and get explicit confirmation.
- Never overwrite, rename, or delete an existing PRD.

## Workflow

1. Understand `$ARGUMENTS`.
   - If needed, ask:
     - What problem does this solve?
     - What should it do?
     - Any constraints or preferences?
2. Resolve `[feature-name]`.
   - Create a short kebab-case name from the request.
   - Target path: `.agents/scratchpad/[feature-name]/prd.md`
   - If the path exists, try `[feature-name]-2`, then `-3`, and so on until unused.
3. Discovery
   - Gather relevant codebase context: similar features, architecture, APIs/contracts, data models, UI patterns, tests, config/flags, permissions, observability, and extension points.
   - Use parallel subagents:
     - `code-explorer`: 1-3 agents, one per independent area
     - research via `official-sources` in parallel: latest official docs and best practices for all materially relevant technologies/standards
   - Read the most relevant references and summarize patterns, constraints, risks, and open questions.
4. Clarify
   - Ask focused questions based on the request and discovery.
   - Cover relevant gaps such as scope boundaries, edge cases, failure modes, integrations, backward compatibility, migration/rollout, security/privacy, and performance.
   - If answers materially change scope or assumptions, repeat **Discovery**.
   - Wait for answers before designing.
5. Architecture design
   - Launch parallel `code-architect` subagents to produce 1-3 meaningfully different approaches, such as:
     - Minimal changes
     - Clean architecture
     - Pragmatic balance
   - For each approach, include: high-level design, impacted components, data/control flow, testing strategy, rollout/migration considerations, risks, trade-offs, and citations.
6. Recommend
   - Present concise summaries of the approaches, key trade-offs, and your recommendation with reasoning.
   - Ask the user to choose an approach before writing the PRD.
7. Write the PRD.
8. Save it to `.agents/scratchpad/[feature-name]/prd.md`.
9. Final response must include:
   - feature short name
   - PRD path
   - validation status: pass/fail
   - readiness for `/prd-to-tasks`

## PRD Structure

### 1. Introduction / Overview

Describe the feature, the problem it solves, who it is for, and why it matters.

### 2. Goals

Bullet list of specific, measurable objectives.

### 3. Tech Stack

Bullet list of relevant technologies, libraries, services, and versions.

### 4. User Stories

Each story must include:

- **Title**
- **Description:** `As a [user], I want [feature] so that [benefit].`
- **Acceptance Criteria:** specific, verifiable checklist
- **Files likely touched:** best-effort guess from code exploration
- **Design Guidance:** implementation guidance, rationale, and references from discovery/architecture work

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

- [Reference link]
  - Guidance: [What the implementer should do and how to apply it]
  - Rationale: [Why this guidance was chosen]
```

**User Story Rules**

- Acceptance criteria must be specific and testable.
- Do not use vague criteria like “works correctly.”
- Include edge cases and failure cases where relevant.
- For UI changes, always include: `Verify in browser using playwright-cli skill`.

### 5. Functional Requirements

List numbered, explicit requirements, for example:

- `FR-1: The system must allow users to...`
- `FR-2: When a user clicks X, the system must...`

### 6. Non-Goals

State what is explicitly out of scope.

### 7. Design Considerations (Optional)

Relevant UI/UX notes, mockups, reusable components, copy considerations, or accessibility notes.

### 8. Technical Considerations

Document constraints, dependencies, integrations, contracts, backward compatibility, migration/rollout, security/privacy, observability, and performance requirements.

### 9. Architectural Decisions

Record key decisions, rationale, trade-offs, alternatives considered, and citations.

### 10. Success Metrics

Explain how success will be measured.

## Writing Guidance

- Write for a junior developer or another AI agent.
- Be explicit, unambiguous, and concise.
- Avoid jargon, or explain it.
- Use numbered requirements and concrete examples where helpful.
- Prefer existing patterns over new abstractions unless there is a clear reason not to.
- Tie recommendations to discovered codebase patterns and official references.

## Path Rules

- Use exactly `.agents/scratchpad/[feature-name]/prd.md`.
- Create the directory if needed.
- If the path exists, choose `[feature-name]-2`, `-3`, and so on until unused.
- Verify the file exists at that exact path before finishing.
- If you cannot write to that exact path, say so and stop.

## Checklist

### Before writing

- [ ] Clarifying questions asked and answered where needed
- [ ] No open questions, ambiguities, or large assumptions remain
- [ ] Relevant code patterns explored
- [ ] Relevant official documentation reviewed
- [ ] Selected approach is reflected consistently throughout the PRD

### Before saving

- [ ] User stories are small and independently actionable
- [ ] Acceptance criteria are concrete and testable
- [ ] Functional requirements are numbered and unambiguous
- [ ] Non-goals clearly define scope
- [ ] Technical and architectural sections include rationale and citations
- [ ] No implementation code was written
- [ ] Target path does not already exist

### Final verification

- [ ] Saved at exactly `.agents/scratchpad/[feature-name]/prd.md`
- [ ] No existing PRD was overwritten
- [ ] No design gaps, open questions, or ambiguities remain
- [ ] Final response includes feature short name, PRD path, validation status, and readiness for `/prd-to-tasks`
