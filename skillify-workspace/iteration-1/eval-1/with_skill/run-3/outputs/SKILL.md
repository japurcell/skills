---
name: doc-to-sop
description: Turn a source document or notes file into a reusable SOP-style skill tailored to a specific audience.
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
when_to_use: Use when the user wants to convert a document, notes file, or repeatable documentation workflow into a reusable SOP-style skill for a specific audience, with trigger phrases like "turn this doc into a skill", "make an SOP from these notes", or "convert this workflow into a reusable skill".
---

# Doc To SOP

Turn an existing document or notes file into a reusable skill that captures a repeatable workflow for a specific audience.

## Inputs

- `$source_doc`: Path to the source document or notes file that describes the workflow.
- `$audience`: The intended audience for the SOP, such as support, onboarding, or engineering.

## Goal

Produce a reusable skill draft from `$source_doc` for `$audience`, keeping the workflow focused on reading, extracting, and writing. The result should be easy to reuse across repositories and should end with a clear save path and invocation command.

## Steps

### 1. Read the source material

Open `$source_doc` and identify the parts that describe the actual repeatable process rather than background context. Pull out the recurring tasks, inputs, outputs, and any decision points that affect how the workflow should run.

**Artifacts**: Extracted workflow notes, candidate inputs, outputs, and decision points.

**Success criteria**:

- The source material has been read closely enough to separate the repeatable workflow from surrounding context.
- The key inputs, outputs, and decision points are captured in working notes.

### 2. Extract the SOP structure for the audience

Translate the source workflow into a concise SOP structure for `$audience`. Keep the argument list small and obvious, and adapt terminology or examples so the instructions are clear for the intended audience.

**Artifacts**: Audience-shaped workflow outline and confirmed argument list.

**Rules**:

- Keep the argument list limited to the inputs that are clearly required.
- Do not add shell commands, package installation steps, or automation that the source workflow did not actually use.

**Success criteria**:

- The workflow is expressed as a short, ordered outline that fits `$audience`.
- The required arguments are clear, minimal, and justified by the source material.

### 3. Draft the skill

Write the SKILL.md content with a clear description, inputs, goal, and ordered steps. Each step should be actionable and include success criteria so the workflow is easy to execute and verify.

**Artifacts**: Complete SKILL.md draft.

**Rules**:

- Preserve the confirmed arguments `$source_doc` and `$audience`.
- Keep the skill centered on reading, extracting, and writing rather than shell automation.

**Success criteria**:

- The draft is complete and usable as a standalone skill.
- Each major step includes success criteria.
- The skill remains general enough to reuse across repositories.

### 4. Add examples or edge notes only when they help

Decide whether the workflow needs a short invocation example or a brief note about edge cases. Add them only if they clarify how to use the skill or prevent likely confusion.

**Rules**:

- Keep extra guidance concise.
- Do not pad the skill with examples or caveats that the source material does not support.

**Success criteria**:

- Any added example or note makes the skill easier to reuse.
- Unnecessary detail has been left out.

### 5. Present the final skill and save instructions

Finish by providing the completed skill content together with the recommended save path and invocation command so the user can keep it as a personal skill.

**Execution**: Terminate

**Success criteria**:

- The final output includes the completed skill content.
- The output states the recommended save path for a personal skill.
- The output includes the invocation command `/doc-to-sop $source_doc $audience`.
