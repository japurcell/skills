---
name: doc-to-sop
description: Turn a source document or notes file into a concise, reusable SOP-style skill for a specific audience.
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
when_to_use: Use when the user wants to convert an existing document, notes file, or internal process write-up into a reusable SOP-style skill for a specific audience, with prompts like "turn this doc into an SOP skill" or "make a reusable SOP from these notes".
---

# Doc To SOP

Turn a source document or notes file into a reusable SOP-style skill that can be used across repositories.

## Inputs

- `$source_doc`: Path to the source document, notes file, or workflow write-up.
- `$audience`: The target audience for the SOP, such as support, onboarding, or engineering.

## Goal

Produce a clean, portable SKILL.md draft that captures the repeatable workflow from `$source_doc` for `$audience`, keeps the argument list small and obvious, and ends with clear save and invocation instructions.

## Steps

### 1. Read the source material

Read `$source_doc` closely and identify the actual workflow it describes, including prerequisites, inputs, outputs, decision points, and any audience-specific terminology that should be preserved or simplified for `$audience`.

**Success criteria**: You have a concise set of notes that captures the workflow scope, required inputs, final outputs, and the places where the wording or detail level should change for `$audience`.

### 2. Distill the repeatable workflow

Convert the source material into a short ordered workflow.

- Keep the workflow focused on reading, extracting, and writing.
- Keep the argument list minimal and obvious.
- Do not add shell commands, package installation steps, or tooling steps unless they are clearly part of the source workflow.
- Remove one-off context that would make the result specific to a single repository unless the source explicitly requires it.

**Artifacts**: A draft outline of the SOP skill, including inputs, major steps, output artifact, and hard rules.

**Rules**: Preserve the actual workflow from the source material. Do not inflate it with generic automation or extra operational steps.

**Success criteria**: You have an ordered workflow with explicit inputs, a clear completion artifact, and a short list of rules or constraints that must carry into the final skill.

### 3. Draft the skill

Write the reusable skill in SKILL.md format.

- Add frontmatter with a clear skill name, a one-line description, the minimum required tools, argument metadata, and a strong `when_to_use` trigger description.
- Include `Inputs`, `Goal`, and `Steps` sections.
- Give every step explicit success criteria.
- Keep the instructions portable across repositories unless the source document proves that repo-specific behavior is required.
- Tailor the language and examples so the skill is understandable for `$audience`.

**Artifacts**: Complete SKILL.md draft text.

**Success criteria**: The draft is complete, reusable across repositories, and specific enough that another agent can follow it without needing the original source document open for interpretation.

### 4. Add examples and edge guidance only when needed

Check whether the workflow needs a brief invocation example, audience-specific wording notes, or one or two edge-case constraints.

- Add examples only if they clarify how to use the skill.
- Add edge guidance only if the source material contains real decision points or common failure modes.
- Keep the final skill concise; do not pad it with generic advice.

**Success criteria**: Any added examples or notes make the skill easier to use without distracting from the main workflow.

### 5. Present the final result and save instructions

Return the finished SKILL.md content and include the recommended save path plus the invocation command.

- Recommend a personal skill path when the workflow should work across repositories.
- Show the exact command format needed to invoke the skill.
- Make it easy for the user to tweak wording before saving if they want to refine the final text.

**Success criteria**: The user has the final skill content, knows where to save it, and has an exact invocation command they can use immediately.
