---
name: prd
description: Use to create an implementation-ready Product Requirements Document (PRD) for a feature. Trigger on requests such as "create/write a PRD," "product requirements," "plan this feature," "requirements for," "spec out," "define user stories," or "prepare for /prd-to-tasks." Do not use to implement the feature or write implementation code.
disable-model-invocation: true
---

# PRD Generator

Create a concise, unambiguous, implementation-ready PRD for a feature.

## Core rules

- Invoke `subagent-model-router` first.
- Do not implement the feature or include implementation code.
- Follow existing codebase patterns and conventions.
- Prefer YAGNI: exclude unnecessary features and abstractions.
- Resolve ambiguities before design; ask only the minimum necessary clarifying questions.
- If the user says “whatever you think is best,” recommend an approach and get explicit confirmation.
- Never overwrite, rename, or delete an existing PRD.
- `Files likely touched` must be a best-effort estimate from code exploration and must exclude files matched by repository `.gitignore`.

## Output path

1. Derive `[feature-name]` as a short kebab-case name from the request.
2. Target: `.agents/scratchpad/[feature-name]/prd.md`
3. If the path exists, use `[feature-name]-2`, then `-3`, etc. until unused.
4. Create the directory if needed.
5. Save only to the final unused path.
6. Verify the file exists at that exact path before finishing.
7. If you cannot write to that exact path, say so and stop.

## Workflow

1. **Understand request**
   - Parse `$ARGUMENTS`.
   - If needed, ask:
     - What problem does this solve?
     - What should it do?
     - Any constraints or preferences?

2. **Discovery**
   - Explore relevant codebase context: similar features, architecture, APIs/contracts, data models, UI patterns, tests, config/flags, permissions, observability, and extension points.
   - Use parallel subagents:
     - `code-explorer`: 1–3 agents, one per independent area.
     - `research`: invoke `official-sources` for current official docs and best practices for materially relevant technologies/standards.
   - Read the most relevant references and summarize patterns, constraints, risks, and open questions.

3. **Clarify**
   - Ask focused questions based on request and discovery.
   - Cover scope boundaries, edge cases, failure modes, integrations, backward compatibility, migration/rollout, security/privacy, and performance.
   - If answers materially change scope or assumptions, repeat Discovery.
   - Wait for answers before designing.

4. **Architecture options**
   - Launch parallel `code-architect` subagents to produce 1–3 meaningfully different approaches, such as:
     - minimal change
     - clean architecture
     - pragmatic balance
   - Each approach must include: high-level design, impacted components, data/control flow, testing strategy, rollout/migration, risks, trade-offs, and citations.

5. **Recommend**
   - Present concise approach summaries, key trade-offs, and a recommendation with rationale.
   - Ask the user to choose or confirm an approach before writing the PRD.

6. **Write and save PRD**
   - Write the PRD using the selected approach.
   - Save to the verified unused path.

7. **Final response**
   - Include:
     - feature short name
     - PRD path
     - validation status: `pass` or `fail`
     - readiness for `/prd-to-tasks`

## PRD structure

### 1. Introduction / Overview

Describe the feature, problem solved, target users, and why it matters.

### 2. Goals

List specific, measurable objectives.

### 3. Tech Stack

List relevant technologies, libraries, services, and versions.

### 4. User Stories

Each story must be small enough for one focused implementation session and include:

- **Title**
- **Description:** `As a [user], I want [feature] so that [benefit].`
- **Acceptance Criteria:** specific, verifiable checklist
- **Files likely touched:** best-effort estimate from code exploration; exclude files matched by repository `.gitignore`
- **Design Guidance:** implementation guidance, rationale, and references from discovery/architecture work

Format:

```md
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

User story rules:

- Acceptance criteria must be concrete and testable.
- Do not use vague criteria such as “works correctly.”
- Include edge cases and failure cases where relevant.
- For UI changes, always include: `Verify in browser using playwright-cli skill`.
- Never list files matched by repository `.gitignore`.

### 5. Functional Requirements

Number explicit requirements:

- `FR-1: The system must allow users to...`
- `FR-2: When a user clicks X, the system must...`

### 6. Non-Goals

State what is explicitly out of scope.

### 7. Design Considerations Optional

Include relevant UI/UX notes, mockups, reusable components, copy considerations, and accessibility notes.

### 8. Technical Considerations

Document constraints, dependencies, integrations, contracts, backward compatibility, migration/rollout, security/privacy, observability, and performance requirements.

### 9. Architectural Decisions

Record key decisions, rationale, trade-offs, alternatives considered, and citations.

### 10. Success Metrics

Explain how success will be measured.

## Writing guidance

- Write for a junior developer or another AI agent.
- Be explicit, concise, and unambiguous.
- Avoid jargon or explain it.
- Use numbered requirements and concrete examples where helpful.
- Prefer existing patterns over new abstractions unless clearly justified.
- Tie recommendations to discovered codebase patterns and official references.

## Validation checklist

Before writing:

- [ ] Clarifying questions asked and answered where needed
- [ ] No material ambiguities, open questions, or large assumptions remain
- [ ] Relevant code patterns explored
- [ ] Relevant official documentation reviewed
- [ ] User confirmed selected approach

Before saving:

- [ ] User stories are small and independently actionable
- [ ] Acceptance criteria are concrete and testable
- [ ] `Files likely touched` excludes files matched by repository `.gitignore`
- [ ] Functional requirements are numbered and unambiguous
- [ ] Non-goals clearly define scope
- [ ] Technical and architectural sections include rationale and citations
- [ ] No implementation code was written
- [ ] Target path does not already exist

Final verification:

- [ ] PRD saved at exactly `.agents/scratchpad/[feature-name]/prd.md`
- [ ] No existing PRD was overwritten
- [ ] No design gaps, open questions, or ambiguities remain
- [ ] Final response includes feature short name, PRD path, validation status, and readiness for `/prd-to-tasks`
