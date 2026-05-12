---
name: doc-to-sop
description: Turn a source document into a concise reusable SOP skill for a specific audience.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit
  - Write
argument-hint: "$source_doc $audience"
arguments:
  - source_doc
  - audience
when_to_use: Use when you want to convert an existing document, notes file, or confirmed workflow summary into a reusable SOP-style skill for a specific audience such as support, onboarding, or engineering. Trigger on requests like "turn this doc into a skill", "make an SOP skill from these notes", or "convert this workflow into a reusable skill".
---

# Doc To SOP

Create a reusable SOP-style skill from existing documentation or notes, keeping the result concise, audience-specific, and portable across repositories.

## Inputs

- `$source_doc`: Path to the source document, notes file, or confirmed summary to transform.
- `$audience`: Intended audience for the SOP, such as support, onboarding, or engineering.

## Goal

Produce a complete `SKILL.md` derived from `$source_doc`, tailored to `$audience`, with a recommended save path, invocation command, and any necessary assumptions.

## Steps

### 1. Read the source material

Open `$source_doc` and identify the core workflow, recurring actions, inputs, outputs, decision points, and hard constraints that should survive in a reusable skill.

**Artifacts**: Working notes covering the workflow, inputs, outputs, constraints, and audience-specific wording.
**Success criteria**:

- The source has been fully reviewed.
- The workflow's purpose, required inputs, and completion artifact are clear.
- Any audience-specific tone or scope constraints are captured.

### 2. Extract the reusable workflow

Reduce the material into the smallest repeatable process that still preserves the real task. Separate durable workflow steps from one-off context, and infer only the minimum argument set needed to run the workflow again.

**Rules**:

- Do not invent shell commands, package installation steps, or automation that do not appear in the source workflow.
- Prefer cross-repo wording unless the source is explicitly repo-specific.
- Keep the argument list small and obvious.
  **Artifacts**: Ordered step list, inferred argument list, success artifact, and hard rules.
  **Success criteria**:
- The workflow is expressed as a clear ordered sequence.
- Inputs, outputs, and decision points are explicit.
- Non-reusable details have been removed or reframed as assumptions.

### 3. Define the generated skill

Choose a concise skill name, one-line description, and default save scope based on the source. Default to a personal skill path when the workflow should follow the user across repositories; use a repo-local path only when the source is clearly project-specific.

**Artifacts**: Generated skill name, description, and recommended save path.
**Success criteria**:

- The generated skill has a clear name and purpose.
- The recommended save path matches the workflow scope.
- The choice of personal versus repo-local placement is justified by the source material.

### 4. Draft the `SKILL.md`

Write a complete `SKILL.md` with frontmatter, inputs, goal, and numbered steps. Tailor wording and examples to `$audience` so the procedure is immediately usable for that group.

**Rules**:

- Every step must include success criteria.
- Emphasize reading, extracting, and writing over shell automation.
- Keep the description concise and the scope clear.
  **Artifacts**: Draft `SKILL.md`.
  **Success criteria**:
- The draft includes frontmatter with name, description, allowed tools, and arguments when needed.
- The steps are concrete and audience-appropriate.
- The generated skill can be used across repositories unless the source explicitly requires repo-local behavior.

### 5. Trim and validate

Review the draft for unnecessary filler, missing edge notes, or invented complexity. Add an example invocation only when it helps execution and is supported by the source material.

**Rules**:

- Do not pad the skill with generic advice.
- Do not add extra arguments for hypothetical cases.
- Keep assumptions explicit instead of silently expanding scope.
  **Success criteria**:
- The final draft covers the real workflow without unnecessary detail.
- Any examples or edge notes improve execution clarity.
- The output remains concise.

### 6. Present final output [human]

Present the completed `SKILL.md`, the recommended save path, the invocation command, and any assumptions. When a live user is present, pause here so they can tweak naming or wording before the file is written.

**Human checkpoint**: Let the user adjust naming, scope, or wording before saving when they want changes.
**Success criteria**:

- The final `SKILL.md` is complete and ready to save.
- The recommended save path is explicit.
- The invocation command is shown in a copyable form.
- Assumptions are listed separately from confirmed facts.
