---
name: prd
description: Create a Product Requirements Document (PRD) for a feature. Use for requests like - create a PRD, write a PRD for, plan this feature, requirements for, spec out.
---

# PRD Generator

Create a clear, implementation-ready PRD. Do not implement the feature.

## Capability Rules

- Use subagents, named skills, codebase access, browser tools, and file operations only if they are available in the current environment.
- Do not claim to have used tools, read files, generated citations, run browser checks, or saved files unless you actually did.
- If a required capability is unavailable, use the best available fallback and clearly state any limitations.

## Workflow

1. Understand the request from `$ARGUMENTS`.
   - If unclear, ask only the minimum needed:
     - What problem does this solve?
     - What should it do?
     - Any constraints or preferences?
   - Summarize your understanding only if there is meaningful uncertainty.
2. [Explore the codebase](#codebase-exploration) and wait for the code-explorer subagents to return findings.
3. Ask clarifying questions until requirements are clear enough to write the PRD. If unresolved items remain but are not blocking, list them in **Open Questions**.
   - Focus on:
     - Objective and target users
     - Core features and acceptance criteria
     - Tech stack preferences and constraints
     - Boundaries: what to do, ask first about, and never do
4. [Design the architecture and implementation approach](#architecture-design) and wait for the code-architect subagents to return findings.
5. Write the PRD.
6. Save it to `.agents/scratchpad/[feature-name]/prd.md`.

**Important:** Do not write code.

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
4. Deduplicate the results and read the most relevant files.
5. Present only findings that affect the PRD, questions, or likely implementation.

## Architecture Design

**Goal:** Identify implementation options and recommend one.

1. Launch 2-3 parallel `code-architect` subagents, where the number matches feature complexity.
2. Instruct each subagent to invoke the `official-sources` skill so implementation decisions are grounded in current official documentation.
3. Each agent should propose a different approach, such as:
   - Minimal changes
   - Clean architecture
   - Pragmatic balance
4. For each approach, include rationale, trade-offs, risks, and citations.
5. Recommend one approach.
6. Ask the user to choose only if there is a real product or architectural fork. Otherwise, choose the best option and continue.

## PRD Structure

### 1. Introduction / Overview

Briefly describe the feature and the problem it solves.

### 2. Goals

Bullet list of specific, measurable objectives.

### 3. User Stories

Each story must include:

- **Title**
- **Description:** `As a [user], I want [feature] so that [benefit].`
- **Acceptance Criteria:** Verifiable checklist
- **Files likely touched:** Best-effort guess based on code exploration

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
```

**Rules:**

- Acceptance criteria must be specific and testable.
- Do not use vague criteria like "works correctly".
- For any story with UI changes, always include: `Verify in browser using playwright-cli skill`.
- `Files likely touched` is a best-effort estimate, not a guarantee.

### 4. Functional Requirements

Numbered, explicit requirements, for example:

- `FR-1: The system must allow users to...`
- `FR-2: When a user clicks X, the system must...`

### 5. Non-Goals

State what is out of scope.

### 6. Design Considerations (Optional)

Include relevant UI/UX notes, mockups, or reusable components.

### 7. Technical Considerations (Optional)

Include constraints, dependencies, integrations, and performance requirements.

### 8. Architectural Decisions (Optional)

Document key decisions, trade-offs, rationale, alternatives considered, and citations.

### 9. Success Metrics

Explain how success will be measured.

### 10. Open Questions

List any remaining unresolved questions.

**Format:**

```text
- [ ] Question 1?
- [ ] Question 2?
...
```

## Writing Guidance

Assume the reader may be a junior developer or another AI agent.

- Be explicit and unambiguous.
- Avoid jargon or explain it.
- Use numbered requirements.
- Use concrete examples when helpful.

## Output

- **Format:** Markdown
- **Path:** `.agents/scratchpad/[feature-name]/prd.md`

### Path Rules

- This exact path is required.
- Do not use any other scratchpad, temp, workspace, home, tool-default, or session-state path.
- Do not write to `/tmp`, `/var/tmp`, `~/.copilot/`, `/session-state/`, or any alternate directory.
- If the directory does not exist, create it.
- Before finishing, verify the file exists at exactly `.agents/scratchpad/<feature-name>/prd.md`.
- In the final response, include the exact saved path.
- If you cannot write to that exact path, say so and stop.

## Checklist

### Before writing

- [ ] Clarifying questions asked if needed
- [ ] There are no blocking open questions
- [ ] User answers incorporated
- [ ] Relevant code patterns explored
- [ ] Existing patterns preferred over inventing new ones
- [ ] Requirements are clear enough to proceed

### Before saving

- [ ] User stories are small and specific
- [ ] Functional requirements are numbered and unambiguous
- [ ] Non-goals clearly define scope
- [ ] Architectural decisions include rationale and citations where applicable
- [ ] All open questions are listed
- [ ] No code was written

### Final verification

- [ ] Saved at exactly `.agents/scratchpad/<feature-name>/prd.md`
- [ ] No alternate path was used
- [ ] There are no blocking open questions, and any remaining non-blocking questions are listed in the **Open Questions** section.
